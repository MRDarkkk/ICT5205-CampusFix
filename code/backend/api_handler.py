"""CampusFix API Lambda. Python 3.13 / boto3 available in AWS Lambda runtime.
No credentials in source. API Gateway JWT authorizer protects admin routes.
"""
import base64
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
DDB = boto3.resource("dynamodb")
S3 = boto3.client("s3")
SQS = boto3.client("sqs")
TABLE = DDB.Table(os.environ.get("ISSUES_TABLE", "UNSET"))
PHOTO_BUCKET = os.environ.get("PHOTO_BUCKET", "")
QUEUE_URL = os.environ.get("QUEUE_URL", "")
CATEGORIES = {"plumbing", "electrical", "it", "furniture", "safety", "other"}
PRIORITIES = {"low", "medium", "high"}
STATUSES = {"open", "in_progress", "resolved"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ID_PATTERN = re.compile(r"^ISS-[0-9a-f]{32}$")
PHOTO_PATTERN = re.compile(r"^uploads/[0-9a-f]{32}\.(jpg|png|webp)$")


def _json_default(value):
    return float(value) if isinstance(value, Decimal) else str(value)


def response(status, data):
    return {"statusCode": status, "headers": {"content-type": "application/json", "cache-control": "no-store"},
            "body": json.dumps(data, default=_json_default)}


def error(status, message):
    return response(status, {"error": message})


def payload(event):
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    if len(raw.encode("utf-8")) > 20000:
        raise ValueError("Request body is too large")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


def str_field(data, name, limit, required=True):
    value = data.get(name, "")
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    value = value.strip()
    if (required and not value) or len(value) > limit:
        raise ValueError(f"{name} must be 1–{limit} characters" if required else f"{name} exceeds {limit} characters")
    return value


def is_staff(event):
    jwt = ((event.get("requestContext") or {}).get("authorizer") or {}).get("jwt") or {}
    claims = jwt.get("claims") or {}
    groups = claims.get("cognito:groups", [])

    if isinstance(groups, list):
        return "staff" in groups

    if isinstance(groups, str):
        names = [
            name.strip().strip("[]").strip('"').strip("'")
            for name in groups.split(",")
        ]
        return "staff" in names

    return False


def validate_photo(key):
    if not isinstance(key, str) or not PHOTO_PATTERN.fullmatch(key):
        raise ValueError("Invalid photo key")
    try:
        metadata = S3.head_object(Bucket=PHOTO_BUCKET, Key=key)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
            raise ValueError("Photo upload was not found") from exc
        raise
    if metadata.get("ContentType") not in CONTENT_TYPES or not 1 <= metadata.get("ContentLength", 0) <= MAX_IMAGE_SIZE:
        raise ValueError("Photo must be JPEG, PNG or WebP and no larger than 5 MB")
    return key


def create_issue(event):
    body = payload(event)
    title = str_field(body, "title", 120)
    description = str_field(body, "description", 1000)
    location = str_field(body, "location", 120)
    category = str_field(body, "category", 30).lower()
    priority = str_field(body, "priority", 10).lower()
    if category not in CATEGORIES or priority not in PRIORITIES:
        raise ValueError("Invalid category or priority")
    photo_key = body.get("photo_key")
    if photo_key is not None:
        photo_key = validate_photo(photo_key)
    now = datetime.now(timezone.utc).isoformat()
    issue_id = "ISS-" + uuid.uuid4().hex
    item = {"issue_id": issue_id, "entity_type": "ISSUE", "title": title,
            "description": description, "location": location, "category": category,
            "priority": priority, "status": "open", "created_at": now, "updated_at": now}
    if photo_key:
        item["photo_key"] = photo_key
    TABLE.put_item(Item=item, ConditionExpression="attribute_not_exists(issue_id)")
    queued = True
    try:
        SQS.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"event_id": uuid.uuid4().hex,
                        "event_type": "issue_created", "issue_id": issue_id, "category": category}))
    except ClientError:
        LOG.exception("Notification enqueue failed for issue %s", issue_id)
        queued = False
    return response(201, {"issue_id": issue_id, "status": "open", "notification_queued": queued})


def get_issue(issue_id):
    if not ID_PATTERN.fullmatch(issue_id):
        return error(404, "Issue not found")
    item = TABLE.get_item(Key={"issue_id": issue_id}).get("Item")
    if not item:
        return error(404, "Issue not found")
    # Public lookup returns a limited record; no photo URL or staff identity.
    allowed = ("issue_id", "title", "location", "category", "priority", "status", "created_at", "updated_at")
    return response(200, {name: item[name] for name in allowed if name in item})


def presign_upload(event):
    body = payload(event)
    mime = str_field(body, "content_type", 30)
    if mime not in CONTENT_TYPES:
        raise ValueError("Only JPEG, PNG and WebP photos are supported")
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[mime]
    key = f"uploads/{uuid.uuid4().hex}.{ext}"
    info = S3.generate_presigned_post(
        Bucket=PHOTO_BUCKET, Key=key,
        Fields={"Content-Type": mime},
        Conditions=[["content-length-range", 1, MAX_IMAGE_SIZE + 32768], {"Content-Type": mime}],
        ExpiresIn=300)
    return response(200, {"upload_url": info["url"], "fields": info["fields"],
                          "photo_key": key, "max_bytes": MAX_IMAGE_SIZE, "expires_seconds": 300})


def admin_list(event):
    params = event.get("queryStringParameters") or {}
    status = params.get("status", "")
    if status and status not in STATUSES:
        raise ValueError("Invalid status filter")
    limit = int(params.get("limit", "25"))
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    from boto3.dynamodb.conditions import Key
    if status:
        query = {"IndexName": "status-created-index", "KeyConditionExpression": Key("status").eq(status)}
    else:
        query = {"IndexName": "entity-created-index", "KeyConditionExpression": Key("entity_type").eq("ISSUE")}
    # Bounded query. Dashboard states clearly that counters apply to returned page.
    items = TABLE.query(**query, Limit=limit, ScanIndexForward=False).get("Items", [])
    return response(200, {"items": items, "count": len(items), "page_limit": limit})


def admin_photo(issue_id):
    if not ID_PATTERN.fullmatch(issue_id):
        return error(404, "Issue not found")
    item = TABLE.get_item(Key={"issue_id": issue_id}).get("Item")
    if not item or not item.get("photo_key"):
        return error(404, "Photo not found")
    url = S3.generate_presigned_url("get_object", Params={"Bucket": PHOTO_BUCKET,
                                   "Key": item["photo_key"]}, ExpiresIn=120)
    return response(200, {"url": url, "expires_seconds": 120})


def admin_update(event, issue_id):
    if not ID_PATTERN.fullmatch(issue_id):
        return error(404, "Issue not found")
    body = payload(event)
    status = str_field(body, "status", 20)
    if status not in STATUSES:
        raise ValueError("Status must be open, in_progress or resolved")
    now = datetime.now(timezone.utc).isoformat()
    try:
        result = TABLE.update_item(
            Key={"issue_id": issue_id},
            UpdateExpression="SET #status = :status, updated_at = :now",
            ConditionExpression="attribute_exists(issue_id)",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": status, ":now": now},
            ReturnValues="ALL_NEW")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return error(404, "Issue not found")
        raise
    return response(200, {"issue_id": issue_id, "status": status, "updated_at": now})


def lambda_handler(event, context):
    http = (event.get("requestContext") or {}).get("http") or {}
    method = http.get("method", "")
    path = event.get("rawPath", "")
    try:
        if method == "POST" and path == "/issues":
            return create_issue(event)
        if method == "POST" and path == "/uploads/presign":
            return presign_upload(event)
        if method == "GET" and path.startswith("/issues/"):
            return get_issue(path[len("/issues/"):])
        if path == "/admin/issues" and method == "GET":
            if not is_staff(event):
                return error(403, "Staff access required")
            return admin_list(event)
        if path.startswith("/admin/issues/") and path.endswith("/photo") and method == "GET":
            if not is_staff(event):
                return error(403, "Staff access required")
            return admin_photo(path[len("/admin/issues/"):-len("/photo")])
        if path.startswith("/admin/issues/") and method == "PATCH":
            if not is_staff(event):
                return error(403, "Staff access required")
            return admin_update(event, path[len("/admin/issues/"):])
        return error(404, "Route not found")
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return error(400, str(exc))
    except ClientError:
        LOG.exception("AWS service error")
        return error(500, "An internal service error occurred")
    except Exception:
        LOG.exception("Unexpected API error")
        return error(500, "An internal error occurred")
