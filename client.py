#!/usr/bin/python

import requests


class ClientSystemInterface:

	def __init__(self,system):
		self.system = system

	def login(self,username,password):
		return

	def listUsers(self):
		return self.system.listUsers()

	def addUser(self,user,display):
		return self.system.addUser(user,display)

	def generateKeysForUser(self,user,password):
		self.system.generateKeysForUser(user,password)

	def getUserPrivateKey(self,user,password):
		return self.system.getUserPrivateKey(user,password)

	def canCreateUser(self,user):
		# Direct access always can create users
		return True

	def canUserReadSecret(self,user,sid):
		entry = self.system.getSecret(sid)
		return user in entry["users"]

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		return self.system.addSecret(owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac)

	def getSecret(self,sid):
		return self.system.getSecret(sid)

	def getSecretsForUser(self,user):
		return self.system.getSecretsForUser(user)

	def updateSecret(self,sid,encryptedSecret,hmac):
		self.system.updateSecret(sid,encryptedSecret,hmac)

class ClientRestInterface:

	def __init__(self,baseurl):
		self.baseurl = baseurl

	def login(self,username,password):
		self.username = username
		self.password = password

	def listUsers(self):
		r = requests.get(self.baseurl+"/v1/users",auth=(self.username,self.password))
		r.raise_for_status()
		return r.json()

	def getSecret(self,sid):
		r = requests.get(self.baseurl+"/v1/secrets/"+sid,auth=(self.username,self.password))
		r.raise_for_status()
		return r.json()

	def getSecretsForUser(self,user):
		r = requests.get(self.baseurl+"/v1/users/"+user+"/secrets",auth=(self.username,self.password))
		r.raise_for_status()
		return r.json()

	def canUserReadSecret(self,user,sid):
		# Delegate to the server
		return True

class Client:

	def __init__(self,iface):
		self.iface = iface

	def login(self,username,password):
		self.username = username
		return self.iface.login(username,password)

	def listUsers(self):
		return self.iface.listUsers()

	def getUserPublicKey(self,user):
		return self.listUsers()[user]["publicKey"]

	def getUserPrivateKeyEncrypted(self,user):
		return self.listUsers()[user]["encryptedPrivateKey"]

	def getUserPrivateKey(self,user,password):
		return self.iface.getUserPrivateKey(user,password)

	def addUser(self,user,display):
		if self.iface.canCreateUser(self.username):
			return self.iface.addUser(user,display)

	def generateKeysForUser(self,user,password):
		self.iface.generateKeysForUser(user,password)

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		return self.iface.addSecret(owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac)

	def getSecret(self,sid):
		if self.iface.canUserReadSecret(self.username,sid):
			return self.iface.getSecret(sid)
		else:
			raise(Exception("Access denied"))

	def getSecretsForUser(self,user):
		return self.iface.getSecretsForUser(user)

	def updateSecret(self,sid,encryptedSecret,hmac):
		self.iface.updateSecret(sid,encryptedSecret,hmac)

