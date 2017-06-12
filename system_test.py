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
		self.assertEqual("Lisa",obj.db.listUsers()["user1"]["displayName"])


if __name__ == '__main__':
	unittest.main()


