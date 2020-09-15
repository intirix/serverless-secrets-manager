from behave import given, when
import basicauth
import lambda_functions
import json


@given(u'"{user}" will log in with password "{password}"')
def step_impl(context, user, password):
    context.event["headers"]["Authorization"] = basicauth.encode(user, password)


@when(u'I "{method}" "{path}"')
def step_impl(context, method, path):
    context.event["path"] = path
    context.event["resource"] = path
    context.event["httpMethod"] = method
    context.event["requestContext"]["path"] = path
    context.event["requestContext"]["resourcePath"] = path
    context.event["requestContext"]["httpMethod"] = method

    context.resp = lambda_functions.single_func(context.event, None)
    # print(str(context.resp))
    print(json.dumps(context.resp, indent=2))


@given(u'path parameter "{name}" is set to "{value}"')
def step_impl(context, name, value):
    context.event["pathParameters"][name] = value


@given(u'POST body field "{name}" is set to "{value}"')
def step_impl(context, name, value):
    body = {}
    if context.event["body"] is not None:
        body = json.loads(context.event["body"])
    body["name"] = value
    context.event["body"] = json.dumps(body, indent=2)
    context.event["headers"]["Content-Type"] = "application/json"


@given(u'query string parameter "{name}" is set to "{value}"')
def step_impl(context, name, value):
    context.event["queryStringParameters"][name] = value


@given(u'POST body is "{body}"')
def step_impl(context, body):
    context.event["body"] = body


@then(u'I get a "{code}" response code')
def step_impl(context, code):
    assert context.resp["statusCode"] == int(code)


@then(u'I get response header "{name}" of "{value}"')
def step_impl(context, name, value):
    assert context.resp["headers"][name] == value
