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


if __name__ == '__main__':
	unittest.main()


