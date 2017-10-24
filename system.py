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
			self.grantAdmin("admin")
			self.enablePasswordAuth("admin")
			self.generateKeysForUser("admin","password")
		return True

	def addUser(self,username,displayName):
		self.log.info("Creating user "+username)
		ret = self.db.addUser(username,displayName)
		self.db.sync()
		return ret

	def listUsers(self):
		return self.db.listUsers()

	def getUser(self,user):
		return self.db.getUser(user)

	def setUserDisplayName(self,username,displayName):
		self.log.info("Changing display name for "+username)
		self.db.updateUserField(username,"displayName",displayName)
		self.db.sync()
		return True

	def grantAdmin(self,username):
		self.log.info("Granting admin access to "+username)
		self.db.updateUserField(username,"admin","Y")
		self.db.sync()
		return True

	def revokeAdmin(self,username):
		self.log.info("Revoking admin access from "+username)
		self.db.updateUserField(username,"admin","N")
		self.db.sync()
		return True

	def enableUser(self,username):
		self.log.info("Enabling user "+username)
		self.db.updateUserField(username,"enabled","Y")
		self.db.sync()
		return True

	def disableUser(self,username):
		self.log.info("Disabling user "+username)
		self.db.updateUserField(username,"enabled","N")
		self.db.sync()
		return True

	def enablePasswordAuth(self,username):
		self.log.info("Enabling password auth for user "+username)
		self.db.updateUserField(username,"passwordAuth","Y")
		self.db.sync()
		return True

	def disablePasswordAuth(self,username):
		self.log.info("Disabling password auth for user "+username)
		self.db.updateUserField(username,"passwordAuth","N")
		self.db.sync()
		return True

	def getUserPublicKey(self,username):
		data = self.getUser(username)
		if data != None and "publicKey" in data:
			return data["publicKey"]
		return None

	def setUserPublicKey(self,username,pem,keyType):
		self.log.info("Changing the public key for "+username)
		self.db.updateUserField(username,"publicKey",pem)
		self.db.updateUserField(username,"keyType",keyType)
		self.db.sync()
		return True

	def setUserPrivateKey(self,username,key):
		self.log.info("Changing the private key for "+username)
		self.db.updateUserField(username,"encryptedPrivateKey",key)
		self.db.sync()
		return True

	def generateKeysForUser(self,username,password):
		self.log.info("Generating keys for "+username)
		key = self.crypto.keyStretchPassword(username,password)
		(priv,pub) = self.crypto.generatePublicPrivateKeys()
		self.setUserPublicKey(username,pub,"RSA")

		encryptedPriv = self.crypto.encrypt(key,priv)
		#print("new priv key="+str(encryptedPriv))
		self.setUserPrivateKey(username,encryptedPriv)
		self.db.sync()
		return True

	def getUserPrivateKey(self,username,password):
		self.log.warning("Retriving private key for "+username)
		key = self.crypto.keyStretchPassword(username,password)
		encryptedPriv = self.db.getUser(username)["encryptedPrivateKey"]
		#print("epriv="+str(encryptedPriv))
		priv = self.crypto.decrypt(key,encryptedPriv)
		return priv

	def clearUserPrivateKey(self,username):
		self.log.info("Removing private key for "+username)
		self.db.removeUserField(username,"encryptedPrivateKey")
		self.db.sync()
		return True

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,encryptedSecret,hmac):
		self.log.info("Adding secret for "+owner+", hmac="+hmac)
		sid = self.db.addSecret(owner,secretEncryptionProfile,encryptedKey,encryptedSecret,hmac)
		self.db.sync()
		return sid

	def updateSecret(self,sid,encryptedSecret,hmac):
		self.log.info("Updating secret "+sid)
		self.db.updateSecret(sid,encryptedSecret,hmac)
		self.db.sync()
		return True

	def shareSecret(self,sid,user,encryptedKey):
		self.log.info("Sharing secret "+sid+" to "+user)
		self.db.shareSecret(sid,user,encryptedKey)
		self.db.sync()
		return True

	def getSecret(self,sid):
		return self.db.getSecret(sid)

	def getSecretsForUser(self,user):
		return self.db.getSecretsForUser(user)

	def doesUserHaveWriteAccess(self,username,sid):
		entry = self.getSecret(sid)
		if username in entry["users"]:
			userEntry = entry["users"][username]
			return "canWrite" in userEntry and "Y" == userEntry["canWrite"]
		return False


