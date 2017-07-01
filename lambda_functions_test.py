#!/usr/bin/python

import unittest
import lambda_functions

class TestHandler(unittest.TestCase):

	def testInvalidEvents(self):
		self.assertEqual(False, lambda_functions.matches(None,"GET","/users"))
		self.assertEqual(False, lambda_functions.matches({},"GET","/users"))
		self.assertEqual(False, lambda_functions.matches({"requestContext":{}},"GET","/users"))

	def testSimpleMatches(self):
		self.assertEqual(True, lambda_functions.matches({"httpMethod":"GET","requestContext":{"resourcePath":"/users"}},"GET","/users"))
		self.assertEqual(False, lambda_functions.matches({"httpMethod":"GET","requestContext":{"resourcePath":"/users"}},"POST","/users"))



if __name__=="__main__":
	unittest.main()
