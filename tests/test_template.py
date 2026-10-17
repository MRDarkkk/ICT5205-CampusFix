"""Offline structure checks; NOT a replacement for SAM validation in AWS."""
from pathlib import Path
import yaml


class CFLoader(yaml.SafeLoader):
    pass


def parse_tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {suffix: value}


CFLoader.add_multi_constructor('!', parse_tag)
TEMPLATE = yaml.load((Path(__file__).parent.parent/'deploy'/'template.yaml').read_text(), Loader=CFLoader)


def test_minimum_cloud_resource_structure():
    r=TEMPLATE['Resources']
    assert TEMPLATE['Transform']=='AWS::Serverless-2016-10-31'
    assert len(r)>=19
    for name in ('IssuesTable','ApiFunction','NotificationWorker','NotificationQueue','NotificationDLQ',
                 'NotificationTopic','CampusApi','FrontendDistribution','WebsiteBucket','PhotoBucket',
                 'StaffUserPool','StaffUserPoolClient','StaffGroup','NotificationEventsTable'):
        assert name in r


def test_private_s3_and_authorized_admin_routes():
    r=TEMPLATE['Resources']
    for name in ('WebsiteBucket','PhotoBucket'):
        flags=r[name]['Properties']['PublicAccessBlockConfiguration']
        assert all(flags.values())
    events=r['ApiFunction']['Properties']['Events']
    for name in ('AdminList','AdminUpdate','AdminPhoto'):
        assert events[name]['Properties']['Auth']['Authorizer']=='StaffJwt'


def test_worker_has_sqs_and_limited_iam():
    r=TEMPLATE['Resources']
    assert r['NotificationWorker']['Properties']['Events']['Queue']['Type']=='SQS'
    policy=r['ApiFunction']['Properties']['Policies'][0]['Statement']
    actions={action for statement in policy for action in statement['Action']}
    assert 's3:*' not in actions and 'dynamodb:*' not in actions


def test_code_uri_points_to_real_files():
    root=Path(__file__).parent.parent/'deploy'
    for fn in ('ApiFunction','NotificationWorker'):
        props=TEMPLATE['Resources'][fn]['Properties']
        assert (root/props['CodeUri']/props['Handler'].split('.')[0]).with_suffix('.py').exists()
