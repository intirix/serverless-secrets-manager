#!/usr/bin/python

import crypto
import unittest
from datetime import datetime

class TestCrypto(unittest.TestCase):

	def testHmac(self):
		obj=crypto.Crypto()
		key=obj.generateRandomKey()
		hmac=obj.createHmac(key,"hello")
		self.assertEqual(True,obj.verifyHmac(key,"hello",hmac))

	def testBase64(self):
		obj=crypto.Crypto()
		token = datetime.utcnow().isoformat()

		encoded = obj.encode(token)
		self.assertEqual(token,obj.decode(encoded).decode('utf-8'))

	def testSignatureVerification(self):
		obj=crypto.Crypto()

		f = open("mock_key.pub")
		pub = f.read()
		f.close()

		f = open("mock_key.key")
		epriv = f.read()

		aesKey = obj.keyStretchPassword("admin","password")
		dpriv = obj.decrypt(aesKey,epriv)
		f.close()

		token = datetime.utcnow().isoformat()

		signedToken = obj.sign(dpriv,token)
		print("signedToken="+str(signedToken))

		self.assertEqual(True,obj.verify(pub,token,signedToken))


	def testUnicodeWithScrypt(self):
		obj=crypto.Crypto()
		self.assertEqual(True,obj.keyStretchPassword(u"test",u"password")!=None)


if __name__ == '__main__':
	unittest.main()

