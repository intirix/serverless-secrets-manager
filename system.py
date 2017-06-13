#!/usr/bin/python

import crypto

class System:

	def __init__(self):
		self.db = None
		self.crypto = crypto.Crypto()

	def setDB(self,db):
		self.db = db

	def addUser(self,username,displayName):
		self.db.addUser(username,displayName)

	def setUserPublicKey(self,username,pem):
		self.db.updateUserField(username,"publicKey",pem)

	def setUserPrivateKey(self,username,key):
		self.db.updateUserField(username,"privateKey",key)

	def generateKeysForUser(self,username,password):
		key = self.crypto.keyStretchPassword(username,password)
		(priv,pub) = self.crypto.generatePublicPrivateKeys()
		self.setUserPublicKey(username,pub)

		encryptedPriv = self.crypto.encrypt(key,priv)
		self.setUserPrivateKey(username,encryptedPriv)

	def getUserPrivateKey(self,username,password):
		key = self.crypto.keyStretchPassword(username,password)
		encryptedPriv = self.db.getUser(username)["privateKey"]
		priv = self.crypto.decrypt(key,encryptedPriv)
		return priv



