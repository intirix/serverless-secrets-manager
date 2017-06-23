#!/usr/bin/python

import unittest
import httpserver

class TestHandler(unittest.TestCase):

	def testSimpleMatches(self):
		self.assertEqual(False, httpserver.matches("/",["v1","login"]))
		self.assertEqual(True, httpserver.matches("/SecretsManager/v1/login",["v1","login"]))

	def testPathParamMatches(self):
		self.assertEqual(False, httpserver.matches("/",["v1","user",None]))
		self.assertEqual(True, httpserver.matches("/SecretsManager/v1/users/myuser",["v1","users",None]))
		self.assertEqual(False, httpserver.matches("/SecretsManager/v1/users/myuser",["v1","users",None,"publicKey"]))
		self.assertEqual(False, httpserver.matches("/SecretsManager/v1/secrets/1",["v1","users",None]))

if __name__=="__main__":
	unittest.main()
