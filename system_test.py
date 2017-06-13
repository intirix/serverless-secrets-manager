#!/usr/bin/python

import unittest
import db
import system


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

if __name__ == '__main__':
	unittest.main()


