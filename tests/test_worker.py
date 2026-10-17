import json
import os
import sys
import importlib
from unittest.mock import MagicMock

os.environ.update(AWS_ACCESS_KEY_ID='TESTONLY',AWS_SECRET_ACCESS_KEY='TESTONLY',AWS_DEFAULT_REGION='ap-southeast-2',
                  AWS_EC2_METADATA_DISABLED='true',EVENTS_TABLE='offline-events',TOPIC_ARN='arn:aws:sns:ap-southeast-2:123456789012:offline')
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','code','backend')))
worker=importlib.import_module('notification_worker')


def test_worker_publishes_once_for_single_message(monkeypatch):
    table=MagicMock();sns=MagicMock()
    monkeypatch.setattr(worker,'TABLE',table);monkeypatch.setattr(worker,'SNS',sns)
    event={'Records':[{'messageId':'m1','body':json.dumps({'event_id':'e1','event_type':'issue_created','issue_id':'ISS-123','category':'plumbing'})}]}
    result=worker.lambda_handler(event,None)
    assert result == {'batchItemFailures':[]}
    table.put_item.assert_called_once()
    sns.publish.assert_called_once()
    table.update_item.assert_called_once()


def test_worker_malformed_record_returns_partial_failure(monkeypatch):
    result=worker.lambda_handler({'Records':[{'messageId':'m2','body':'NOT JSON'}]},None)
    assert result == {'batchItemFailures':[{'itemIdentifier':'m2'}]}


def test_worker_skips_already_sent_event(monkeypatch):
    from botocore.exceptions import ClientError
    table=MagicMock(); sns=MagicMock()
    table.put_item.side_effect=ClientError({'Error':{'Code':'ConditionalCheckFailedException','Message':'duplicate'}},'PutItem')
    table.get_item.return_value={'Item':{'status':'sent'}}
    monkeypatch.setattr(worker,'TABLE',table);monkeypatch.setattr(worker,'SNS',sns)
    message={'event_id':'e1','event_type':'issue_created','issue_id':'ISS-123','category':'it'}
    result=worker.lambda_handler({'Records':[{'messageId':'m1','body':json.dumps(message)}]},None)
    assert result=={'batchItemFailures':[]}
    sns.publish.assert_not_called()
