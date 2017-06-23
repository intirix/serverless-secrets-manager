#!/usr/bin/python

import unittest
import db
import system
import json


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
		obj.setUserPublicKey("user1", "my_public_key")
		self.assertEqual("my_public_key",obj.db.getUser("user1")["publicKey"])

	def testGenerateKeysForUser(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.generateKeysForUser("user1","mypassword")
		self.assertEqual(True,len(obj.db.getUser("user1")["publicKey"])>128)
		self.assertEqual(True,len(obj.db.getUser("user1")["privateKey"])>1024)

		pubPem = obj.db.getUser("user1")["publicKey"]
		privPem = obj.getUserPrivateKey("user1","mypassword")

		message = "testMessage"
		sig = obj.crypto.sign(privPem,message)
		self.assertEqual(True,obj.crypto.verify(pubPem,message,sig))

		obj.clearUserPrivateKey("user1")
		self.assertEqual(True, not "privateKey" in obj.db.getUser("user1") or obj.db.getUser("user1")["privateKey"] == None)

	def testAddSecretForSingleUser(self):
		obj = self.createMockSystem()
		obj.addUser("user1","Lisa")
		obj.generateKeysForUser("user1","mypassword")
		pubKey = obj.db.getUser("user1")["publicKey"]
		privKey = obj.getUserPrivateKey("user1","mypassword")

		secret = {"type":"password","url":"www.gmail.com","user":"myuser","password":"mypassword"}
		aesKey = obj.crypto.generateRandomKey()
		encryptedSecret = obj.crypto.encrypt(aesKey,json.dumps(secret))
		encryptedKey = obj.crypto.encryptRSA(pubKey,aesKey)
		
		sid = obj.addSecret("user1","1",encryptedKey,encryptedSecret)

		secretEntry = obj.getSecret(sid)

		origKey = obj.crypto.decryptRSA(privKey,secretEntry["users"]["user1"]["encryptedKey"])
		origSecretText = obj.crypto.decrypt(origKey,secretEntry["encryptedSecret"])
		origSecret = json.loads(origSecretText)
		self.assertEqual(secret["password"],origSecret["password"])


if __name__ == '__main__':
	unittest.main()


