"""SQS-triggered worker; best-effort event-id dedupe using DynamoDB.
SQS/SNS are at-least-once: an interruption between SNS publish and marking an
idempotency record sent can still cause duplicates. No exactly-once claim.
"""
import json
import logging
import os
import time
import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
SNS = boto3.client("sns")
TABLE = boto3.resource("dynamodb").Table(os.environ.get("EVENTS_TABLE", "UNSET"))
TOPIC_ARN = os.environ.get("TOPIC_ARN", "")


def handle_message(msg):
    if msg.get("event_type") != "issue_created":
        raise ValueError("Unexpected event type")
    event_id, issue_id, category = msg["event_id"], msg["issue_id"], msg["category"]
    if not all(isinstance(x, str) for x in (event_id, issue_id, category)) or not issue_id.startswith("ISS-"):
        raise ValueError("Invalid notification data")
    now = int(time.time())
    try:
        TABLE.put_item(Item={"event_id": event_id, "status": "processing", "lease_until": now + 45,
                             "expires_at": now + 7 * 86400},
                       ConditionExpression="attribute_not_exists(event_id) OR (#s = :processing AND lease_until < :now)",
                       ExpressionAttributeNames={"#s": "status"},
                       ExpressionAttributeValues={":now": now, ":processing": "processing"})
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
            raise
        prior = TABLE.get_item(Key={"event_id": event_id}, ConsistentRead=True).get("Item", {})
        if prior.get("status") == "sent":
            LOG.info("Skipping already published event %s", event_id)
            return
        raise RuntimeError("Event is being processed; retry later") from exc
    try:
        SNS.publish(TopicArn=TOPIC_ARN, Subject="CampusFix new maintenance issue",
                    Message=f"New campus issue: {issue_id}\nCategory: {category}\nView through the protected staff dashboard.")
    except Exception:
        TABLE.delete_item(Key={"event_id": event_id},
                          ConditionExpression="#s = :processing",
                          ExpressionAttributeNames={"#s": "status"},
                          ExpressionAttributeValues={":processing": "processing"})
        raise
    TABLE.update_item(Key={"event_id": event_id}, UpdateExpression="SET #s = :sent",
                      ExpressionAttributeNames={"#s": "status"},
                      ExpressionAttributeValues={":sent": "sent"})
    LOG.info("Notification published for %s", issue_id)


def lambda_handler(event, context):
    failures = []
    for record in event.get("Records", []):
        try:
            handle_message(json.loads(record["body"]))
        except Exception:
            LOG.exception("Unable to process SQS message")
            failures.append({"itemIdentifier": record.get("messageId", "unknown")})
    return {"batchItemFailures": failures}
