from moto import mock_dynamodb2
import boto3


def before_scenario(context, scenario):
    context.mocks = {}
    context.mocks["dynamodb"] = mock_dynamodb2()
    context.mocks["dynamodb"].start()
    context.clients = {}
    context.clients["dynamodb"] = boto3.client("dynamodb")
    context.clients["dynamodb"].create_table(
        AttributeDefinitions=[{"AttributeName": "username", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "username", "KeyType": "HASH"}],
        TableName="secrets-users",
    )
    context.clients["dynamodb"].create_table(
        AttributeDefinitions=[{"AttributeName": "sid", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "sid", "KeyType": "HASH"}],
        TableName="secrets-secrets",
    )
    context.state = {}
    context.resp = {}


def after_scenario(context, scenario):
    for k in context.mocks.keys():
        context.mocks[k].stop()
