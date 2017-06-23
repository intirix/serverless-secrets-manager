#!/usr/bin/python

import crypto
import logging

class System:

	def __init__(self):
		self.db = None
		self.crypto = crypto.Crypto()
		self.log = logging.getLogger("System")
		self.log.setLevel(logging.DEBUG)

	def setDB(self,db):
		self.db = db

	def init(self):
		if self.db.getUser("admin")==None:
			self.log.warn("Creating admin user with default password")
			self.addUser("admin","admin")
			self.generateKeysForUser("admin","password")

	def addUser(self,username,displayName):
		self.log.info("Creating user "+username)
		self.db.addUser(username,displayName)
		self.db.sync()

	def listUsers(self):
		return self.db.listUsers()

	def setUserPublicKey(self,username,pem):
		self.log.info("Changing the public key for "+username)
		self.db.updateUserField(username,"publicKey",pem)
		self.db.sync()

	def setUserPrivateKey(self,username,key):
		self.log.info("Changing the private key for "+username)
		self.db.updateUserField(username,"encryptedPrivateKey",key)
		self.db.sync()

	def generateKeysForUser(self,username,password):
		self.log.info("Generating keys for "+username)
		key = self.crypto.keyStretchPassword(username,password)
		(priv,pub) = self.crypto.generatePublicPrivateKeys()
		self.setUserPublicKey(username,pub)

		encryptedPriv = self.crypto.encrypt(key,priv)
		self.setUserPrivateKey(username,encryptedPriv)
		self.db.sync()

	def getUserPrivateKey(self,username,password):
		self.log.warn("Retriving private key for "+username)
		key = self.crypto.keyStretchPassword(username,password)
		encryptedPriv = self.db.getUser(username)["encryptedPrivateKey"]
		priv = self.crypto.decrypt(key,encryptedPriv)
		return priv

	def clearUserPrivateKey(self,username):
		self.log.info("Removing private key for "+username)
		self.db.removeUserField(username,"encryptedPrivateKey")
		self.db.sync()

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		self.log.info("Adding secret for "+owner+", hmac="+hmac)
		sid = self.db.addSecret(owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac)
		self.db.sync()
		return sid

	def updateSecret(self,sid,encryptedSecret,hmac):
		self.log.info("Updating secret "+sid)
		self.db.updateSecret(sid,encryptedSecret,hmac)
		self.db.sync()

	def getSecret(self,sid):
		return self.db.getSecret(sid)

	def getSecretsForUser(self,user):
		return self.db.getSecretsForUser(user)

	def doesUserHaveWriteAccess(self,username,sid):
		entry = self.getSecret(sid)
		if username in entry["users"]:
			userEntry = entry["users"][username]
			return "canWrite" in userEntry and "Y" == userEntry["canWrite"]


