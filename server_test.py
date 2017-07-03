import unittest
import db
import system
import json
import server
import client
import logging

class TestServer(unittest.TestCase):

	def createMockSystem(self):
		mdb = db.MemoryDB()
		obj = system.System()
		obj.setDB(mdb)

		f = open("mock_key.pub")
		pub = f.read()
		f.close()

		f = open("mock_key.key")
		epriv = f.read()
		dpriv = client.ClientHelper().decryptPrivateKey("admin",epriv,"password")
		f.close()

		obj.addUser("admin","admin")
		obj.grantAdmin("admin")
		obj.setUserPublicKey("admin",pub,"RSA")
		obj.setUserPrivateKey("admin",epriv)

		return (obj,pub,dpriv)

	def testKeyBasedAuth(self):
		(mysys,pub,priv) = self.createMockSystem()
		srv = server.Server(mysys)

		authToken = client.ClientHelper().generateToken(priv)
		self.assertEqual("admin",srv.validateAuthentication("admin",authToken).user)

	def testPasswordBasedAuthWhenDisabled(self):
		(mysys,pub,priv) = self.createMockSystem()
		srv = server.Server(mysys)

		self.assertEqual(None,srv.validateAuthentication("admin","password"))


	def testPasswordBasedAuthWhenEnabled(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.enablePasswordAuth("admin")
		srv = server.Server(mysys)

		self.assertEqual("admin",srv.validateAuthentication("admin","password").user)


if __name__ == '__main__':
	FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(format=FORMAT)
	unittest.main()


