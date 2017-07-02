import unittest
import db
import system
import json
import server
import client

class TestServer(unittest.TestCase):

	def createMockSystem(self):
		mdb = db.MemoryDB()
		obj = system.System()
		obj.setDB(mdb)

		f = open("mock_key.pub")
		pub = f.read()
		f.close()

		f = open("mock_key.key")
		priv = f.read()
		priv = client.ClientHelper().decryptPrivateKey("admin",priv,"password")
		f.close()

		obj.addUser("admin","admin")
		obj.grantAdmin("admin")
		obj.setUserPublicKey("admin",pub,"RSA")
		obj.setUserPrivateKey("admin",priv)

		return (obj,pub,priv)

	def testKeyBasedAuth(self):
		(mysys,pub,priv) = self.createMockSystem()
		srv = server.Server(mysys)

		authToken = client.ClientHelper().generateToken(priv)
		srv.validateAuthentication("admin",authToken)


if __name__ == '__main__':
	unittest.main()


