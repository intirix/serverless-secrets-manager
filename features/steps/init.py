from behave import given

import lambda_functions


@given(u"I have installed the system")
def step_impl(context):
    lambda_functions._singleton = lambda_functions.LambdaCommon(
        context.clients["dynamodb"]
    )
    context.lambda_common = lambda_functions._singleton
    context.system = context.lambda_common.system
    context.event = {}
    context.event["headers"] = {}
    context.event["requestContext"] = {}
    context.event["pathParameters"] = {}
    context.event["queryStringParameters"] = {}
    context.event["body"] = None
    context.event["isBase64Encoded"] = False
