#!/usr/bin/python

import unittest
import db
import system
import accessrules
import json


class TestAccessRules(unittest.TestCase):
    def createMock(self):
        mdb = db.MemoryDB()
        obj = system.System()
        obj.setDB(mdb)
        return accessrules.AccessRules(obj)

    def testAdminUser(self):
        obj = self.createMock()
        obj.system.init()
        self.assertEqual(True, obj.isAdmin("admin"))
        self.assertEqual(True, obj.canCreateUser("admin"))
        self.assertEqual(True, obj.canGrantAdmin("admin"))

    def testNonAdmin(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(False, obj.isAdmin("nonadmin"))
        self.assertEqual(False, obj.canCreateUser("nonadmin"))

    def testDisabledAdminCannotCreateUser(self):
        obj = self.createMock()
        obj.system.addUser("admin2", "admin2")
        obj.system.grantAdmin("admin2")
        self.assertEqual(True, obj.canCreateUser("admin2"))
        obj.system.disableUser("admin2")

    def testDisabledAdminCannotGrantAdminAccess(self):
        obj = self.createMock()
        obj.system.addUser("admin2", "admin2")
        obj.system.grantAdmin("admin2")
        self.assertEqual(True, obj.canGrantAdmin("admin2"))
        obj.system.disableUser("admin2")
        self.assertEqual(False, obj.canGrantAdmin("admin2"))

    def testDisabledUserCannotChangeOwnKeys(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.disableUser("nonadmin")
        self.assertEqual(False, obj.canChangeUserKeys("nonadmin", "nonadmin"))

    def testUserCanChangeOwnProfile(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canUpdateUserProfile("nonadmin", "nonadmin"))

    def testNonAdminUserCannotChangeSomeoneElsesProfile(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        self.assertEqual(False, obj.canUpdateUserProfile("nonadmin", "nonadmin2"))

    def testAdminCanChangeSomeoneElsesProfile(self):
        obj = self.createMock()
        obj.system.addUser("admin2", "admin2")
        obj.system.grantAdmin("admin2")
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canUpdateUserProfile("admin2", "nonadmin"))

    def testUserCanChangeOwnKeys(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canChangeUserKeys("nonadmin", "nonadmin"))

    def testNonAdminUserCannotChangeSomeoneElsesKeys(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        self.assertEqual(False, obj.canChangeUserKeys("nonadmin", "nonadmin2"))

    def testAdminCanChangeSomeoneElsesKeys(self):
        obj = self.createMock()
        obj.system.addUser("admin2", "admin2")
        obj.system.grantAdmin("admin2")
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canChangeUserKeys("admin2", "nonadmin"))

    def testUserCanExportTheirOwnKeys(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canUserExportPublicKey("nonadmin", "nonadmin"))
        self.assertEqual(True, obj.canUserExportPrivateKey("nonadmin", "nonadmin"))

    def testNonAdminUserCanExportSomeoneElsesPublicKey(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        self.assertEqual(True, obj.canUserExportPublicKey("nonadmin", "nonadmin2"))

    def testNonAdminUserCannotExportSomeoneElsesPrivateKey(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        self.assertEqual(False, obj.canUserExportPrivateKey("nonadmin", "nonadmin2"))

    def testAdminUserCanExportSomeoneElsesKeys(self):
        obj = self.createMock()
        obj.system.addUser("admin2", "admin2")
        obj.system.grantAdmin("admin2")
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canUserExportPublicKey("admin2", "nonadmin"))
        self.assertEqual(True, obj.canUserExportPrivateKey("admin2", "nonadmin"))

    def testDisabledUserCannotExportSomeoneElsesPublicKey(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        obj.system.disableUser("nonadmin")
        self.assertEqual(False, obj.canUserExportPrivateKey("nonadmin", "nonadmin"))

    def testUserCanSeeTheirOwnAttributes(self):
        obj = self.createMock()
        obj.system.addUser("admin", "admin")
        obj.system.grantAdmin("admin")
        obj.system.addUser("nonadmin", "nonadmin")
        self.assertEqual(True, obj.canUserSeeAttributes("nonadmin", "nonadmin"))
        self.assertEqual(True, obj.canUserSeeAttributes("admin", "admin"))

    def testUserCannotSeeSomeoneElsesAttributes(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("nonadmin2", "nonadmin2")
        self.assertEqual(False, obj.canUserSeeAttributes("nonadmin", "nonadmin2"))
        self.assertEqual(False, obj.canUserSeeAttributes("nonadmin2", "nonadmin"))

    def testAdminCanSeeSomeoneElsesAttributes(self):
        obj = self.createMock()
        obj.system.addUser("nonadmin", "nonadmin")
        obj.system.addUser("admin", "admin")
        obj.system.grantAdmin("admin")
        self.assertEqual(True, obj.canUserSeeAttributes("admin", "nonadmin"))


if __name__ == "__main__":
    unittest.main()
