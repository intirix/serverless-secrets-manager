#!/usr/bin/python

import json

class Context:

	def __init__(self,user):
		self.user = user



class Server:

	def __init__(self,system):
		self.system = system

	def _getUserData(self,obj):
		ret = {}
		for key in [ "displayName", "publicKey" ]:
			if key in obj:
				ret[key] = obj[key]
		return ret

	def listUsers(self,ctx):
		ret = {}
		data = self.system.listUsers()

		for user in data.keys():
			ret[user]=self._getUserData(data[user])
		return ret

	def getUser(self,ctx,user):
		data = self.system.getUser(user)
		if data==None:
			return None
		return self._getUserData(data)


	def addUser(self,ctx,user,post_body):
		displayName = user

		data = {}
		if len(post_body)>0:
			data = json.loads(post_body)
			if "displayName" in data:
				displayName = data["displayName"]

		self.system.addUser(user,displayName)

		if "publicKey" in data:
			self.system.setUserPublicKey(user,data["publicKey"])
		if "encryptedPrivateKey" in data:
			self.system.setUserPrivateKey(user,data["encryptedPrivateKey"])

	def updateUser(self,ctx,user,post_body):
		data = {}
		if len(post_body)>0:
			data = json.loads(post_body)

		if "displayName" in data:
			self.system.setUserDisplayName(user,data["displayName"])
		if "publicKey" in data:
			self.system.setUserPublicKey(user,data["publicKey"])
		if "encryptedPrivateKey" in data:
			self.system.setUserPrivateKey(user,data["encryptedPrivateKey"])
		return True


	def addSecret(self,ctx,post_body):
		data = {}
		if len(post_body)>0:
			data = json.loads(post_body)

		encryptedKey = data["encryptedKey"]
		hmacKey = data["hmacKey"]
		encryptedSecret = data["encryptedSecret"]
		hmac = data["hmac"]

		return self.system.addSecret(ctx.user,"1",encryptedKey,hmacKey,encryptedSecret,hmac)

	def updateSecret(self,ctx,sid,post_body):
		data = {}
		if len(post_body)>0:
			data = json.loads(post_body)

		encryptedSecret = data["encryptedSecret"]
		hmac = data["hmac"]

		return self.system.updateSecret(sid,encryptedSecret,hmac)

	def getSecret(self,ctx,sid):
		ret = self.system.getSecret(sid)
		ret["sid"] = sid
		return ret
		



