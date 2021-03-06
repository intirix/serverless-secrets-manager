#!/usr/bin/python

import json
import crypto
import accessrules
import logging
import traceback
import basicauth


class Context:
    def __init__(self, user):
        self.user = user
        self.admin = False


class AccessDeniedException(Exception):
    pass


class Server:
    def __init__(self, system):
        self.system = system
        self.crypto = crypto.Crypto()
        self.rules = accessrules.AccessRules(self.system)
        self.log = logging.getLogger("server")

    def createContext(self, username):
        self.log.info("Creating context for " + username)
        ctx = Context(username)
        if self.rules.isAdmin(username):
            ctx.admin = True
        return ctx

    def mockAuthentication(self, username):
        self.log.warning("Mocking user " + username)
        return self.createContext(username)

    def validateAuthentication(self, username, password):
        try:
            if self.system.getUser(username) == None:
                self.log.warning("Unknown user: " + username)
            elif self.rules.isEnabled(username):
                userdata = self.system.getUser(username)

                data = None

                if self.rules.canAuthenticateWithPassword(username):
                    try:
                        privKey = self.system.getUserPrivateKey(username, password)
                        if privKey != None:
                            return self.createContext(username)
                    except:
                        traceback.print_exc()
                        # ignore and move on to the next auth type
                        pass
                else:
                    try:
                        data = json.loads(password)
                    except json.decoder.JSONDecodeError as e:
                        self.log.warning(
                            "%s attempted password authenticaion when password authentication is disabled: %s"
                            % (username, e)
                        )
                        return None

                # The data might have already been parsed
                if data is None:
                    data = json.loads(password)
                token = data["token"]
                signedToken = data["signed"]
                pub = self.system.getUserPublicKey(username)
                if self.crypto.verify(pub, token, signedToken):
                    return self.createContext(username)
                else:
                    self.log.warning("Failed to verify authentication for " + username)
            else:
                self.log.warning("Disabled user " + username + " attempted to login")
        except:
            self.log.exception("Failed login for user: " + username)
        return None

    def validateAuthenticationHeader(self, header):
        if header != None and header.find("Basic ") == 0:
            user = ""
            try:
                (user, password) = basicauth.decode(header)
                return self.validateAuthentication(user, password)
            except:
                self.log.exception("Failed login for user: " + user)
        return None

    def _getUserData(self, ctx, user, obj):
        ret = {}
        attrList = ["displayName"]
        if self.rules.canUserExportPrivateKey(ctx.user, user):
            attrList.append("encryptedPrivateKey")
        if self.rules.canUserExportPublicKey(ctx.user, user):
            attrList.append("publicKey")
            attrList.append("keyType")
        if self.rules.canUserSeeAttributes(ctx.user, user):
            attrList.append("enabled")
            attrList.append("passwordAuth")

        for key in attrList:
            if key in obj:
                ret[key] = obj[key]

        return ret

    def listUsers(self, ctx):
        ret = {}
        data = self.system.listUsers()

        for user in data.keys():
            ret[user] = self._getUserData(ctx, user, data[user])
        return ret

    def getUser(self, ctx, user):
        data = self.system.getUser(user)
        if data == None:
            return None
        return self._getUserData(ctx, user, data)

    def generateKeysForUser(self, ctx, user, password):
        if not self.rules.canChangeUserKeys(ctx.user, user):
            raise AccessDeniedException()
        self.system.generateKeysForUser(user, password)
        userdata = self.system.getUser(user)
        return userdata["publicKey"]

    def getPublicKeyType(self, pub):
        return self.crypto.getPublicKeyType(pub)

    def getUserEncryptedPrivateKey(self, ctx, user):
        if not self.rules.canUserExportPrivateKey(ctx.user, user):
            raise AccessDeniedException()
        data = self.system.getUser(user)
        if data != None and "encryptedPrivateKey" in data:
            return data["encryptedPrivateKey"]
        return None

    def getUserPublicKey(self, ctx, user):
        if not self.rules.canUserExportPublicKey(ctx.user, user):
            raise AccessDeniedException()
        data = self.system.getUser(user)
        if data != None and "publicKey" in data:
            return data["publicKey"]
        return None

    def setUserPublicKey(self, ctx, user, pem, keyType):
        if not self.rules.canChangeUserKeys(ctx.user, user):
            raise AccessDeniedException()
        return self.system.setUserPublicKey(user, pem, keyType)

    def setUserEncryptedPrivateKey(self, ctx, user, data):
        if not self.rules.canChangeUserKeys(ctx.user, user):
            raise AccessDeniedException()
        return self.system.setUserPrivateKey(user, data)

    def addUser(self, ctx, user, post_body):
        if not self.rules.canCreateUser(ctx.user):
            raise AccessDeniedException()
        displayName = user

        data = {}
        if len(post_body) > 0:
            data = json.loads(post_body)
            if "displayName" in data:
                displayName = data["displayName"]

        self.system.addUser(user, displayName)

        if "publicKey" in data:
            self.system.setUserPublicKey(user, data["publicKey"])
        if "encryptedPrivateKey" in data:
            self.system.setUserPrivateKey(user, data["encryptedPrivateKey"])
        return True

    def hasDataChanged(self, oldData, newData, key):
        if key in oldData and key in newData:
            return oldData[key] != newData[key]
        return False

    def updateUser(self, ctx, user, post_body):
        oldData = self.getUser(ctx, user)
        data = {}
        if len(post_body) > 0:
            data = json.loads(post_body)

        if self.rules.canUpdateUserProfile(ctx.user, user):
            if self.hasDataChanged(oldData, data, "displayName"):
                self.system.setUserDisplayName(user, data["displayName"])
            if self.hasDataChanged(oldData, data, "passwordAuth"):
                if data["passwordAuth"] == "Y":
                    self.system.enablePasswordAuth(user)
                elif data["passwordAuth"] == "N":
                    self.system.disablePasswordAuth(user)

        if self.hasDataChanged(oldData, data, "enabled"):
            if data["enabled"] == "Y" and self.rules.canUserEnableUser(ctx.user, user):
                self.system.enableUser(user)
            elif data["enabled"] == "N" and self.rules.canUserDisableUser(
                ctx.user, user
            ):
                self.system.disableUser(user)

        if self.rules.canChangeUserKeys(ctx.user, user):
            if self.hasDataChanged(oldData, data, "publicKey") and "keyType" in data:
                self.system.setUserPublicKey(user, data["publicKey"], data["keyType"])
            if self.hasDataChanged(oldData, data, "encryptedPrivateKey"):
                self.system.setUserPrivateKey(user, data["encryptedPrivateKey"])
        return True

    def addSecret(self, ctx, post_body):
        data = {}
        if len(post_body) > 0:
            data = json.loads(post_body)

        encryptedKey = None
        if "encryptedKey" in data:
            encryptedKey = data["encryptedKey"]
        else:
            encryptedKey = data["users"][ctx.user]["encryptedKey"]
        encryptedSecret = data["encryptedSecret"]
        hmac = data["hmac"]

        sid = self.system.addSecret(ctx.user, "1", encryptedKey, encryptedSecret, hmac)

        if "users" in data:
            for user in data["users"].keys():
                if user != ctx.user:
                    self.system.shareSecret(
                        sid, user, data["users"][user]["encryptedKey"]
                    )

        return sid

    def shareSecret(self, ctx, sid, user, post_body):
        if not self.system.doesUserHaveShareAccess(ctx.user, sid):
            raise AccessDeniedException()

        data = {}
        if len(post_body) > 0:
            data = json.loads(post_body)
        encryptedKey = data["encryptedKey"]
        self.system.shareSecret(sid, user, encryptedKey)
        ret = self.system.getSecret(sid)
        ret["sid"] = sid
        return ret

    def unshareSecret(self, ctx, sid, user):
        if not self.system.doesUserHaveUnshareAccess(ctx.user, sid):
            raise AccessDeniedException()

        self.system.unshareSecret(sid, user)
        ret = self.system.getSecret(sid)
        ret["sid"] = sid
        return ret

    def updateSecret(self, ctx, sid, post_body):
        if not self.system.doesUserHaveWriteAccess(ctx.user, sid):
            raise AccessDeniedException()

        data = {}
        if len(post_body) > 0:
            data = json.loads(post_body)

        encryptedSecret = data["encryptedSecret"]
        hmac = data["hmac"]

        return self.system.updateSecret(sid, encryptedSecret, hmac)

    def getSecret(self, ctx, sid):
        if not self.system.doesUserHaveReadAccess(ctx.user, sid):
            raise AccessDeniedException()
        ret = self.system.getSecret(sid)
        ret["sid"] = sid
        return ret

    def getMySecrets(self, ctx, user):
        if ctx.user == user:
            return self.system.getSecretsForUser(ctx.user)
        return None
