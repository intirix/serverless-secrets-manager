#!/usr/bin/python

import unittest
import db
import system


class TestSystem(unittest.TestCase):

	def createMockSystem(self):
		mdb = db.MemoryDB()
		obj = system.System()
		obj.setDB(mdb)

	def testAddUser(self):
		obj = self.createMockSystem()


if __name__ == '__main__':
	unittest.main()


