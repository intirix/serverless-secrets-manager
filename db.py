#!/usr/bin/python


class DBInterface:

	def listUsers(self):
		raise Exception("Not implemented")

	def addUser(self,username,displayName):
		raise Exception("Not implemented")


class MemoryDB(DBInterface):
	def __init__(self):
		self.udb = {}
		self.sdb = {}
		self.ucounter = 0
		self.scounter = 0;


	def listUsers(self):
		return self.udb


	def addUser(self,username,displayName):
		self.ucounter = self.ucounter+1
		self.udb[username]={"id":self.ucounter,"displayName":displayName}
		return self.ucounter

	def getUser(self,username):
		return self.listUsers()[username]

	def updateUserField(self,username,fieldName,value):
		self.udb[username][fieldName]=value

	def removeUserField(self,username,fieldName):
		del self.udb[username][fieldName]

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,encryptedSecret):
		self.scounter = self.scounter+1
		self.sdb[self.scounter]={"secretEncryptionProfile":secretEncryptionProfile,"encryptedSecret":encryptedSecret,"users":{}}
		self.sdb[self.scounter]["users"][owner]={"encryptedKey":encryptedKey}
		return self.scounter

	def getSecret(self,sid):
		return self.sdb[sid]

