from behave import given
import json

@given(u"I will create a secret")
def step_impl(context):
    context.secret = {}


@given(u'the secret field "{name}" is set to "{value}"')
def step_impl(context, name, value):
    context.secret[name] = value


@given(u'user "{username}" encrypts the secret into the POST data')
def step_impl(context, username):
    pubKey = context.system.getUserPublicKey(username)
    aesKey = context.crypto.generateRandomKey()
    hmacKey = context.crypto.generateRandomKey()

    bothKeys = aesKey + hmacKey

    # I don't want to just encrypt {}, I want some randomness in there
    rnd = context.crypto.encode(context.crypto.generateRandomKey())
    context.secret["random"] = rnd

    # Encrypt an empty secret for now
    encryptedSecret = context.crypto.encrypt(aesKey, json.dumps(context.secret))
    encryptedKey = context.crypto.encryptRSA(pubKey, bothKeys)

    hmac = context.crypto.createHmac(hmacKey, encryptedSecret)

    eek = context.crypto.encode(encryptedKey)

    body = {}
    if context.event["body"] is not None:
        body = json.loads(context.event["body"])
    body["hmac"] = hmac
    body["encryptedKey"] = eek
    body["encryptedSecret"] = encryptedSecret
    context.event["body"] = json.dumps(body, indent=2)
    context.event["headers"]["Content-Type"] = "application/json"

@given(u'user "{username}" re-encrypts the secret into the POST data')
def step_impl(context, username):
    aesKey = context.aesKey
    hmacKey = context.hmacKey

    bothKeys = aesKey + hmacKey

    # Encrypt an empty secret for now
    encryptedSecret = context.crypto.encrypt(aesKey, json.dumps(context.secret))

    hmac = context.crypto.createHmac(hmacKey, encryptedSecret)

    body = {}
    if context.event["body"] is not None:
        body = json.loads(context.event["body"])
    body["hmac"] = hmac
    body["encryptedSecret"] = encryptedSecret
    context.event["body"] = json.dumps(body, indent=2)
    context.event["headers"]["Content-Type"] = "application/json"

@given(u'user "{username}" has created a secret')
def step_impl(context, username):
    pubKey = context.system.getUserPublicKey(username)
    aesKey = context.crypto.generateRandomKey()
    hmacKey = context.crypto.generateRandomKey()

    bothKeys = aesKey + hmacKey

    # I don't want to just encrypt {}, I want some randomness in there
    rnd = context.crypto.encode(context.crypto.generateRandomKey())
    context.secret = {}
    context.secret["random"] = rnd

    # Encrypt an empty secret for now
    encryptedSecret = context.crypto.encrypt(aesKey, json.dumps(context.secret))
    encryptedKey = context.crypto.encryptRSA(pubKey, bothKeys)

    hmac = context.crypto.createHmac(hmacKey, encryptedSecret)

    eek = context.crypto.encode(encryptedKey)

    context.sid = context.system.addSecret(username, "1", eek, encryptedSecret, hmac)
    context.aesKey = aesKey
    context.hmacKey = hmacKey

@given(u'path parameter "{name}" is the secret id')
def step_impl(context, name):
    context.event["pathParameters"][name] = context.sid

