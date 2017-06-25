#!/usr/bin/python

import json
import crypto
import accessrules
import logging

class Context:

	def __init__(self,user):
		self.user = user

class AccessDeniedException(Exception):
	pass


class Server:

	def __init__(self,system):
		self.system = system
		self.crypto = crypto.Crypto()
		self.rules = accessrules.AccessRules(self.system)
		self.log = logging.getLogger("server")

	def validateAuthentication(self,username,password):
		try:
			if self.system.getUser(username)==None:
				self.log.warn("Unknown user: "+username)
			elif self.rules.isEnabled(username):
				data = json.loads(password)
				token = data["token"]
				signedToken = data["signed"]
				pub = self.system.getUserPublicKey(username)
				if self.crypto.verify(pub,token,signedToken):
					return Context(username)
				else:
					self.log.warn("Failed to verify authentication for "+username)
			else:
				self.log.warn("Disabled user "+username+" attempted to login")
		except:
			self.log.exception("Failed login for user: "+username)
		return None

	def validateAuthenticationHeader(self,header):
		if header != None and header.find("Basic ")==0:
			try:
				(user,password) = self.crypto.decode(header.split(' ')[1]).split(':',1)
				return self.validateAuthentication(user,password)
			except:
				self.log.exception("Failed login for user: "+username)
		return None

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

	def generateKeysForUser(self,ctx,user,password):
		if not self.rules.canChangeUserKeys(ctx.user,user):
			raise AccessDeniedException()
		self.system.generateKeysForUser(user,password)
		return self.system.getUser(user)["publicKey"]

	def getPublicKeyType(self,pub):
		return self.crypto.getPublicKeyType(pub)

	def getUserEncryptedPrivateKey(self,ctx,user):
		if not self.rules.canUserExportPrivateKey(ctx.user,user):
			raise AccessDeniedException()
		data = self.system.getUser(user)
		if data != None and "encryptedPrivateKey" in data:
			return data["encryptedPrivateKey"]
		return None

	def getUserPublicKey(self,ctx,user):
		if not self.rules.canUserExportPublicKey(ctx.user,user):
			raise AccessDeniedException()
		data = self.system.getUser(user)
		if data != None and "publicKey" in data:
			return data["publicKey"]
		return None

	def setUserPublicKey(self,ctx,user,pem,keyType):
		if not self.rules.canChangeUserKeys(ctx.user,user):
			raise AccessDeniedException()
		return self.system.setUserPublicKey(user,pem,keyType)

	def setUserEncryptedPrivateKey(self,ctx,user,data):
		if not self.rules.canChangeUserKeys(ctx.user,user):
			raise AccessDeniedException()
		return self.system.setUserPrivateKey(user,data)

	def addUser(self,ctx,user,post_body):
		if not self.rules.canCreateUser(ctx.user):
			raise AccessDeniedException()
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

		if self.rules.canUpdateUserProfile(ctx.user,user):
			if "displayName" in data:
				self.system.setUserDisplayName(user,data["displayName"])

		if self.rules.canChangeUserKeys(ctx.user,user):
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

	def getMySecrets(self,ctx,user):
		if ctx.user==user:
			return self.system.getSecretsForUser(ctx.user)
		return None
		



