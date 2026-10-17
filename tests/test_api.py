"""Offline tests. No AWS calls are made."""
import importlib
import json
import os
import sys
from unittest.mock import MagicMock

os.environ.update(AWS_ACCESS_KEY_ID="TESTONLY", AWS_SECRET_ACCESS_KEY="TESTONLY",
                  AWS_DEFAULT_REGION="ap-southeast-2", AWS_EC2_METADATA_DISABLED="true",
                  ISSUES_TABLE="offline", PHOTO_BUCKET="offline-photos", QUEUE_URL="offline-queue")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code", "backend")))
api = importlib.import_module("api_handler")


def event(method, path, body=None, staff=False, query=None):
    return {"requestContext": {"http": {"method": method}, "authorizer": {"jwt": {"claims": {"cognito:groups": "[staff]" if staff else ""}}}},
            "rawPath": path, "body": json.dumps(body) if body is not None else "", "queryStringParameters": query}


def body(out):
    return json.loads(out["body"])


def valid_issue(**fields):
    return {"title": "Leaking tap", "description": "Leak near water station", "location": "Library Level 1",
            "category": "plumbing", "priority": "medium", **fields}


def test_create_issue_and_enqueue(monkeypatch):
    table = MagicMock(); monkeypatch.setattr(api, "TABLE", table)
    queue = MagicMock(); monkeypatch.setattr(api, "SQS", queue)
    out = api.lambda_handler(event("POST", "/issues", valid_issue()), None)
    assert out["statusCode"] == 201
    assert body(out)["issue_id"].startswith("ISS-")
    assert body(out)["notification_queued"] is True
    assert table.put_item.call_count == 1
    assert queue.send_message.call_count == 1
    stored = table.put_item.call_args.kwargs["Item"]
    assert stored["status"] == "open" and stored["entity_type"] == "ISSUE"


def test_reject_invalid_category_and_missing_field(monkeypatch):
    monkeypatch.setattr(api, "TABLE", MagicMock())
    bad = api.lambda_handler(event("POST", "/issues", valid_issue(category="alien")), None)
    missing = valid_issue(); missing.pop("location")
    absent = api.lambda_handler(event("POST", "/issues", missing), None)
    assert bad["statusCode"] == 400
    assert absent["statusCode"] == 400


def test_reject_invalid_json_and_oversize():
    assert api.lambda_handler({**event("POST", "/issues"), "body":"{bad"},None)["statusCode"] == 400
    assert api.lambda_handler(event("POST", "/issues", {"huge":"x" * 21000}),None)["statusCode"] == 400


def test_public_lookup_limited_fields(monkeypatch):
    issue_id='ISS-'+'a'*32
    table=MagicMock(); table.get_item.return_value={"Item":{**valid_issue(),"issue_id":issue_id,"status":"open",
        "created_at":"now","updated_at":"now","photo_key":"uploads/private.jpg","email":"secret@example.com"}}
    monkeypatch.setattr(api,"TABLE",table)
    out=api.lambda_handler(event('GET','/issues/'+issue_id),None)
    assert out['statusCode']==200
    assert 'photo_key' not in body(out) and 'email' not in body(out)


def test_missing_issue_is_404(monkeypatch):
    table=MagicMock(); table.get_item.return_value={}
    monkeypatch.setattr(api,'TABLE',table)
    assert api.lambda_handler(event('GET','/issues/'+'ISS-'+'b'*32),None)['statusCode']==404
    assert api.lambda_handler(event('GET','/issues/not-valid'),None)['statusCode']==404


def test_staff_routes_rejected_without_jwt(monkeypatch):
    table=MagicMock(); monkeypatch.setattr(api,'TABLE',table)
    assert api.lambda_handler(event('GET','/admin/issues'),None)['statusCode']==403
    assert api.lambda_handler(event('PATCH','/admin/issues/'+'ISS-'+'a'*32, {'status':'resolved'}),None)['statusCode']==403
    table.query.assert_not_called()


def test_staff_list_and_status_update(monkeypatch):
    table=MagicMock(); table.query.return_value={"Items":[{"issue_id":"ISS-1","status":"open"}]}
    table.update_item.return_value={"Attributes":{"status":"resolved"}}
    monkeypatch.setattr(api,'TABLE',table)
    out=api.lambda_handler(event('GET','/admin/issues',staff=True,query={'status':'open'}),None)
    assert out['statusCode']==200 and body(out)['count']==1
    out=api.lambda_handler(event('PATCH','/admin/issues/'+'ISS-'+'a'*32,{'status':'resolved'},staff=True),None)
    assert out['statusCode']==200 and body(out)['status']=='resolved'
    assert table.update_item.called


def test_photo_presign_rejects_bad_mime(monkeypatch):
    s3=MagicMock(); monkeypatch.setattr(api,'S3',s3)
    out=api.lambda_handler(event('POST','/uploads/presign',{'content_type':'application/pdf'}),None)
    assert out['statusCode']==400
    s3.generate_presigned_post.assert_not_called()


def test_photo_presign_and_photo_validation(monkeypatch):
    s3=MagicMock(); s3.generate_presigned_post.return_value={'url':'https://s3.example.test','fields':{'key':'abc'}}
    s3.head_object.return_value={'ContentType':'image/png','ContentLength':345}
    monkeypatch.setattr(api,'S3',s3)
    out=api.lambda_handler(event('POST','/uploads/presign',{'content_type':'image/png'}),None)
    assert out['statusCode']==200
    key=body(out)['photo_key']
    assert key.startswith('uploads/') and key.endswith('.png')
    assert api.validate_photo(key)==key


def test_photo_lookup_is_admin_only(monkeypatch):
    iid='ISS-'+'a'*32
    table=MagicMock(); table.get_item.return_value={'Item':{'photo_key':'uploads/key.jpg'}}
    s3=MagicMock(); s3.generate_presigned_url.return_value='https://private.example/photo'
    monkeypatch.setattr(api,'TABLE',table); monkeypatch.setattr(api,'S3',s3)
    assert api.lambda_handler(event('GET','/admin/issues/'+iid+'/photo'),None)['statusCode']==403
    assert api.lambda_handler(event('GET','/admin/issues/'+iid+'/photo',staff=True),None)['statusCode']==200


def test_unexpected_route_is_404():
    assert api.lambda_handler(event('GET','/unsupported'),None)['statusCode']==404

def test_staff_group_exact_match_regression():
    cases = [
        ("[staff]", True),
        (["staff"], True),
        ("[operations, staff]", True),
        ("[ex-staff]", False),
        ("former-staff", False),
        ("staff-admin", False),
        (["former-staff"], False),
        ("", False),
    ]

    for group_claim, expected in cases:
        request = event("GET", "/admin/issues")
        request["requestContext"]["authorizer"]["jwt"]["claims"]["cognito:groups"] = group_claim
        assert api.is_staff(request) is expected, repr(group_claim)

    request = event("GET", "/admin/issues")
    request["requestContext"]["authorizer"]["jwt"]["claims"]["cognito:groups"] = "[ex-staff]"
    assert api.lambda_handler(request, None)["statusCode"] == 403
