#!/usr/bin/python

import system
import db
import client
import server
import logging
import json
import base64

class LambdaCommon:

	def __init__(self):
		self.log = logging.getLogger("Lambda")
		self.system = system.System()
		self.db = db.CacheDB(db.DynamoDB("secrets-users","secrets-secrets"))
		self.system.setDB(self.db)
		self.system.init()
		self.client = client.Client(client.ClientSystemInterface(self.system))
		self.server = server.Server(self.system)
		self.resp = None
		self.ctx = None
		self.mockUser = "admin"

	def _response401(self):
		self.resp = {"statusCode":401}

	def authenticate(self,event):
		if self.mockUser!=None:
			self.ctx = self.server.mockAuthentication(self.mockUser)
			return
		if event==None or not "headers" in event or event["headers"]==None or not "Authorization" in event["headers"]:
			self._response401()
			return

		self.ctx = self.server.validateAuthenticationHeader(event["headers"]["Authorization"])
		if self.ctx == None:
			self._response401()
			return

	def getResponse(self):
		return self.resp

def get_body(event):
	if not "body" in event:
		return None

	if event["body"]==None:
		return None

	if "isBase64Encoded" in event and event["isBase64Encoded"]==True:
		return base64.b64decode(event["body"])

	return event["body"]

def matches(event,meth,path):
	if event==None:
		return False

	if not "httpMethod" in event or meth != event["httpMethod"]:
		return False

	if "requestContext" in event and "resourcePath" in event["requestContext"]:
		return path == event["requestContext"]["resourcePath"]

	return False

def single_func(event, context):
	print(json.dumps(event,indent=2))
	if matches(event,"GET","/users"):
		return list_users(event, context)

	if matches(event,"GET","/users/{username}"):
		return get_user(event, context)

	if matches(event,"PUT","/users/{username}"):
		return update_user(event, context)

	if matches(event,"POST","/users/{username}"):
		return create_user(event, context)

	if matches(event,"GET","/users/{username}/keys/public"):
		return get_user_public_key(event, context)

	if matches(event,"PUT","/users/{username}/keys/public"):
		return set_user_public_key(event, context)

	if matches(event,"POST","/users/{username}/keys/public"):
		return set_user_public_key(event, context)

	if matches(event,"POST","/users/{username}/keys"):
		return generate_user_keys(event, context)

	if matches(event,"GET","/users/{username}/keys/private/encrypted"):
		return get_user_private_key_encrypted(event, context)

	if matches(event,"PUT","/users/{username}/keys/private/encrypted"):
		return set_user_private_key_encrypted(event, context)

	if matches(event,"POST","/users/{username}/keys/private/encrypted"):
		return set_user_private_key_encrypted(event, context)

	if matches(event,"GET","/users/{username}/secrets"):
		return get_user_secrets(event, context)

	if matches(event,"GET","/secrets/{sid}"):
		return get_secret(event, context)

	if matches(event,"PUT","/secrets/{sid}"):
		return update_secret(event, context)

	if matches(event,"POST","/secrets"):
		return add_secret(event, context)

	return {"statusCode":404}

def list_users(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		return {"statusCode":200,"body":json.dumps(obj.server.listUsers(obj.ctx),indent=2)}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def get_user(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		return {"statusCode":200,"body":json.dumps(obj.server.getUser(obj.ctx,user),indent=2)}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def update_user(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		body = get_body(event)
		if obj.server.updateUser(obj.ctx,user,body):
			return {"statusCode":200,"body":json.dumps(obj.server.getUser(obj.ctx,user),indent=2)}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def set_user_public_key(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		body = get_body(event)
		keyType = self.server.getPublicKeyType(body)
		if obj.server.setUserPublicKey(obj.ctx,user,body,keyType):
			return {"statusCode":200,"body":json.dumps(obj.server.getUser(obj.ctx,user),indent=2)}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def create_user(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		body = get_body(event)
		if obj.server.updateUser(obj.ctx,user,body):
			if obj.server.addUser(obj.ctx,user,body):
				return {"statusCode":201,"body":json.dumps(obj.server.getUser(obj.ctx,user),indent=2)}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def get_user_public_key(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		pem = obj.server.getUserPublicKey(obj.ctx,user)
		return {"statusCode":200,"body":pem,"headers":{"Content-Type":"application/x-pem-file"}}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def get_user_private_key_encrypted(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		data = obj.server.getUserEncryptedPrivateKey(obj.ctx,user)
		b64 = base64.b64encode(data)
		return {"statusCode":200,"body":b64,"headers":{"Content-Type":"application/octet-stream"},"isBase64Encoded":True}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def generate_user_keys(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		body = get_body(event).strip()

		
		generate=False
		if "queryStringParameters" in event and "generate" in event["queryStringParameters"]:
			generate = "true"==event["queryStringParameters"]["generate"]

		if generate:
			pem = obj.server.generateKeysForUser(obj.ctx,user,body)
			return {"statusCode":200,"body":pem,"headers":{"Content-Type":"application/x-pem-file"}}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def set_user_private_key_encrypted(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		body = get_body(event)
		if obj.server.setUserEncryptedPrivateKey(obj.ctx,user,body):
			return {"statusCode":200,"body":json.dumps(obj.server.getUser(obj.ctx,user),indent=2)}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def get_user_secrets(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		user = event["pathParameters"]["username"]
		return {"statusCode":200,"body":json.dumps(obj.server.getMySecrets(obj.ctx,user),indent=2)}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def get_secret(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		sid = event["pathParameters"]["sid"]
		return {"statusCode":200,"body":json.dumps(obj.server.getSecret(obj.ctx,sid),indent=2)}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def update_secret(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		sid = event["pathParameters"]["sid"]
		body = get_body(event)
		if obj.server.updateSecret(obj.ctx,sid,body):
			return {"statusCode":200,"body":json.dumps(obj.server.getSecret(obj.ctx,sid),indent=2)}
		return {"statusCode":404}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}

def add_secret(event, context):
	obj = LambdaCommon()
	obj.authenticate(event)
	if obj.getResponse() != None:
		return obj.getResponse()

	try:
		body = get_body(event)
		sid = obj.server.addSecret(obj.ctx,body)
		return {"statusCode":201,"body":json.dumps(obj.server.getSecret(obj.ctx,sid),indent=2)}
	except server.AccessDeniedException, e:
		obj.log.exception("Access Denied")
		return {"statusCode":403}
	except:
		obj.log.exception("Error")
		return {"statusCode":500}
	return {"statusCode":404}


FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT)

