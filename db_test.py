#!/usr/bin/python

import unittest
import db
import logging


class TestMemoryDB(unittest.TestCase):
    def testAddUser(self):
        obj = db.MemoryDB()
        self.assertEqual(0, len(obj.listUsers()))
        obj.addUser("user1", "Sally")
        self.assertEqual(1, len(obj.listUsers()))

    def testGetUserWhenUserDoesNotExist(self):
        obj = db.MemoryDB()
        self.assertEqual(None, obj.getUser("doesNotExist"))


class TestDynamoDB(unittest.TestCase):
    def testProcessUserIsNoneSafe(self):
        obj = db.DynamoDB(None, None)

        self.assertEqual(None, obj._processUser(None)[0])

    def testProcessUserWithMinimalFields(self):
        obj = db.DynamoDB(None, None)

        entry = {"username": {"S": "myuser"}, "displayName": {"S": "my user"}}
        (username, data) = obj._processUser(entry)
        self.assertEqual("myuser", username)
        self.assertEqual("my user", data["displayName"])

    def testProcessSecretIsNoneSafe(self):
        obj = db.DynamoDB(None, None)

        self.assertEqual(None, obj._processSecret(None)[0])

    def testprocessSecretWithMissingFields(self):
        obj = db.DynamoDB(None, None)

        entry = {}
        entry["sid"] = {"S": "21"}
        entry["hmac"] = {"S": "1234"}
        entry["encryptedSecret"] = {"S": "ksdfji2oj"}

        (sid, data) = obj._processSecret(entry)
        self.assertEqual(None, sid)

    def testProcessSecretWithMinimalFields(self):
        obj = db.DynamoDB(None, None)

        entry = {}
        entry["sid"] = {"S": "21"}
        entry["hmac"] = {"S": "1234"}
        entry["encryptedSecret"] = {"S": "ksdfji2oj"}
        entry["secretEncryptionProfile"] = {"S": "1"}

        (sid, data) = obj._processSecret(entry)
        self.assertEqual("21", sid)

    def testProcessSecretWithUserInfoDefaultAccess(self):
        obj = db.DynamoDB(None, None)

        entry = {}
        entry["sid"] = {"S": "21"}
        entry["hmac"] = {"S": "1234"}
        entry["encryptedSecret"] = {"S": "ksdfji2oj"}
        entry["secretEncryptionProfile"] = {"S": "1"}
        entry["users"] = {"M": {}}
        entry["users"]["M"]["myuser"] = {"M": {}}
        entry["users"]["M"]["myuser"]["M"]["encryptedKey"] = {"S": "sdfewf2"}

        (sid, data) = obj._processSecret(entry)

        self.assertEqual("21", sid)
        self.assertEqual("N", data["users"]["myuser"]["canShare"])

    def testProcessSecretWithUserInfoAdminAccess(self):
        obj = db.DynamoDB(None, None)

        entry = {}
        entry["sid"] = {"S": "21"}
        entry["hmac"] = {"S": "1234"}
        entry["encryptedSecret"] = {"S": "ksdfji2oj"}
        entry["secretEncryptionProfile"] = {"S": "1"}
        entry["users"] = {"M": {}}
        entry["users"]["M"]["myuser"] = {"M": {}}
        entry["users"]["M"]["myuser"]["M"]["encryptedKey"] = {"S": "sdfewf2"}
        entry["users"]["M"]["myuser"]["M"]["canWrite"] = {"S": "Y"}
        entry["users"]["M"]["myuser"]["M"]["canShare"] = {"S": "Y"}
        entry["users"]["M"]["myuser"]["M"]["canUnshare"] = {"S": "Y"}

        (sid, data) = obj._processSecret(entry)

        self.assertEqual("21", sid)
        self.assertEqual("Y", data["users"]["myuser"]["canWrite"])
        self.assertEqual("Y", data["users"]["myuser"]["canShare"])
        self.assertEqual("Y", data["users"]["myuser"]["canUnshare"])


if __name__ == "__main__":
    # FORMAT = "%(asctime)-15s %(message)s"
    # logging.basicConfig(format=FORMAT)
    unittest.main()
