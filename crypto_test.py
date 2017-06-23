#!/usr/bin/python

import crypto
import unittest

class TestCrypto(unittest.TestCase):

	def testHmac(self):
		obj=crypto.Crypto()
		key=obj.generateRandomKey()
		hmac=obj.createHmac(key,"hello")
		self.assertEqual(True,obj.verifyHmac(key,"hello",hmac))



if __name__ == '__main__':
	unittest.main()

