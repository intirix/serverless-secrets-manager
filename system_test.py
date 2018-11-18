#!/usr/bin/python

import unittest
import db
import system
import json
import sys

class TestSystem(unittest.TestCase):

	def createMockSystem(self):
		mdb = db.MemoryDB()
		obj = system.System()
		obj.setDB(mdb)
		return obj

	def testAddUser(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		self.assertEqual("Lisa",obj.db.getUser("user1")["displayName"])

	def testSetPublicKey(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.setUserPublicKey("user1", "my_public_key", "invalid")
		self.assertEqual("my_public_key",obj.db.getUser("user1")["publicKey"])

	def testGenerateKeysForUser(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.generateKeysForUser("user1","mypassword")
		self.assertEqual(True,len(obj.db.getUser("user1")["publicKey"])>128)
		self.assertEqual(True,len(obj.db.getUser("user1")["encryptedPrivateKey"])>1024)

		pubPem = obj.db.getUser("user1")["publicKey"]
		privPem = obj.getUserPrivateKey("user1","mypassword")

		message = "testMessage"
		sig = obj.crypto.sign(privPem,message)
		self.assertEqual(True,obj.crypto.verify(pubPem,message,sig))

		obj.clearUserPrivateKey("user1")
		self.assertEqual(True, not "encryptedPrivateKey" in obj.db.getUser("user1") or obj.db.getUser("user1")["encryptedPrivateKey"] == None)

	def testAddSecretForSingleUser(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.generateKeysForUser("user1","mypassword")
		pubKey = obj.db.getUser("user1")["publicKey"]
		privKey = obj.getUserPrivateKey("user1","mypassword")

		secret = {"type":"password","url":"www.gmail.com","user":"myuser","password":"mypassword"}
		aesKey = obj.crypto.generateRandomKey()
		hmacKey = obj.crypto.generateRandomKey()
		encryptedSecret = obj.crypto.encrypt(aesKey,json.dumps(secret))
		hmac = obj.crypto.createHmac(hmacKey,encryptedSecret)
		encryptedKey = obj.crypto.encryptRSA(pubKey,aesKey+hmacKey)
		
		sid = obj.addSecret("user1","1",obj.crypto.encode(encryptedKey),encryptedSecret,hmac)

		secretEntry = obj.getSecret(sid)

		#print(json.dumps(secretEntry,indent=2))

		storedEncryptedKey = obj.crypto.decode(secretEntry["users"]["user1"]["encryptedKey"])
		origKeyPair = obj.crypto.decryptRSA(privKey,storedEncryptedKey)
		origKey = origKeyPair[0:32]
		storedHmacKey = origKeyPair[32:]
		storedHmac = secretEntry["hmac"]
		storedEncryptedSecret = secretEntry["encryptedSecret"]


		print("storedHmacKey="+str(storedHmacKey))
		#print("storedHmac="+str(storedHmac))
		print("storedEncryptedSecret="+str(storedEncryptedSecret))

		self.assertEqual(True,obj.crypto.verifyHmac(storedHmacKey,storedEncryptedSecret,storedHmac))
		origSecretText = obj.crypto.decrypt(origKey,storedEncryptedSecret)
		if sys.version_info.major == 3 and type(origSecretText)==bytes:
			origSecretText = origSecretText.decode('utf-8')

		origSecret = json.loads(origSecretText)
		self.assertEqual(secret["password"],origSecret["password"])

	def testSharePassword(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.generateKeysForUser("user1","mypassword")
		obj.addUser("user2","Sarah")
		obj.generateKeysForUser("user2","mypassword2")
		pubKey = obj.db.getUser("user1")["publicKey"]
		privKey = obj.getUserPrivateKey("user1","mypassword")
		pubKey2 = obj.db.getUser("user2")["publicKey"]
		privKey2 = obj.getUserPrivateKey("user2","mypassword2")

		secret = {"type":"password","url":"www.gmail.com","user":"myuser","password":"mypassword"}
		aesKey = obj.crypto.generateRandomKey()
		hmacKey = obj.crypto.generateRandomKey()
		encryptedSecret = obj.crypto.encrypt(aesKey,json.dumps(secret))
		hmac = obj.crypto.createHmac(hmacKey,encryptedSecret)
		encryptedKey = obj.crypto.encryptRSA(pubKey,aesKey+hmacKey)
		
		sid = obj.addSecret("user1","1",obj.crypto.encode(encryptedKey),encryptedSecret,hmac)


		# Share the secret with 'user2'
		encryptedKey2 = obj.crypto.encryptRSA(pubKey2,aesKey+hmacKey)
		obj.shareSecret(sid,"user2",obj.crypto.encode(encryptedKey2))
		secretEntry = obj.getSecret(sid)

		#print(json.dumps(secretEntry,indent=2))

		for userdata in [("user1",privKey),("user2",privKey2)]:

			storedEncryptedKey = obj.crypto.decode(secretEntry["users"][userdata[0]]["encryptedKey"])
			origKeyPair = obj.crypto.decryptRSA(userdata[1],storedEncryptedKey)
			origKey = origKeyPair[0:32]
			storedHmacKey = origKeyPair[32:]
			storedHmac = secretEntry["hmac"]
			storedEncryptedSecret = secretEntry["encryptedSecret"]


			print("storedHmacKey="+str(storedHmacKey))
			print("storedHmac="+str(storedHmac))
			print("storedEncryptedSecret="+str(storedEncryptedSecret))

			self.assertEqual(True,obj.crypto.verifyHmac(storedHmacKey,storedEncryptedSecret,storedHmac))
			origSecretText = obj.crypto.decrypt(origKey,storedEncryptedSecret)
			if sys.version_info.major == 3 and type(origSecretText)==bytes:
				origSecretText = origSecretText.decode('utf-8')

			origSecret = json.loads(origSecretText)
			self.assertEqual(secret["password"],origSecret["password"])





if __name__ == '__main__':
	unittest.main()


