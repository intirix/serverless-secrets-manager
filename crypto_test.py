#!/usr/bin/python

import crypto
import unittest

class TestCrypto(unittest.TestCase):

	def testHmac(self):
		obj=crypto.Crypto()
		key=obj.generateRandomKey()
		hmac=obj.createHmac(key,"hello")
		self.assertEqual(True,obj.verifyHmac(key,"hello",hmac))

	def testUnicodeWithScrypt(self):
		obj=crypto.Crypto()
		self.assertEqual(True,obj.keyStretchPassword(u"test",u"password")!=None)


if __name__ == '__main__':
	unittest.main()

