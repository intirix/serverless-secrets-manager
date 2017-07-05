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

	def testUserCanChangeOwnDisplayName(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("nonadmin","nonadmin")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"displayName":"my name"})))
		self.assertEqual("my name",srv.getUser(ctx,"nonadmin")["displayName"])

	def testUserCannotChangeSomeoneElsesDisplayName(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("nonadmin","nonadmin")
		mysys.addUser("nonadmin2","nonadmin2")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin2")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"displayName":"my name"})))
		self.assertEqual("nonadmin",srv.getUser(ctx,"nonadmin")["displayName"])

	def testUserCanChangeOwnPasswordAuth(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("nonadmin","nonadmin")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"passwordAuth":"Y"})))
		self.assertEqual("Y",srv.getUser(ctx,"nonadmin")["passwordAuth"])
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"passwordAuth":"N"})))
		self.assertEqual("N",srv.getUser(ctx,"nonadmin")["passwordAuth"])

	def testUserCannotChangeSomeoneElsesPasswordAuth(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("nonadmin","nonadmin")
		mysys.addUser("nonadmin2","nonadmin2")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin2")
		selfctx = srv.mockAuthentication("nonadmin")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"passwordAuth":"Y"})))
		self.assertEqual("N",srv.getUser(selfctx,"nonadmin")["passwordAuth"])

	def testUserCannotEnableSelf(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("admin","admin")
		mysys.grantAdmin("admin")
		mysys.addUser("nonadmin","nonadmin")
		mysys.disableUser("nonadmin")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin")
		adminctx = srv.mockAuthentication("admin")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"enabled":"Y"})))
		self.assertEqual("N",srv.getUser(adminctx,"nonadmin")["enabled"])

	def testUserCanDisableSelf(self):
		(mysys,pub,priv) = self.createMockSystem()
		mysys.addUser("admin","admin")
		mysys.grantAdmin("admin")
		mysys.addUser("nonadmin","nonadmin")
		srv = server.Server(mysys)
		ctx = srv.mockAuthentication("nonadmin")
		adminctx = srv.mockAuthentication("admin")
		self.assertEqual(True,srv.updateUser(ctx,"nonadmin",json.dumps({"enabled":"N"})))
		self.assertEqual("N",srv.getUser(adminctx,"nonadmin")["enabled"])


if __name__ == '__main__':
	FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(format=FORMAT)
	unittest.main()


