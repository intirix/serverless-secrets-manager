#!/usr/bin/python

import unittest
import db


class TestMemoryDB(unittest.TestCase):

	def testAddUser(self):
		obj=db.MemoryDB()
		self.assertEqual(0,len(obj.listUsers()))
		obj.addUser("user1","Sally")
		self.assertEqual(1,len(obj.listUsers()))



if __name__ == '__main__':
	unittest.main()
