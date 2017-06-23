#!/usr/bin/python

import json
import os

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

	def sync(self):
		return

	def listUsers(self):
		return self.udb


	def addUser(self,username,displayName):
		self.ucounter = self.ucounter+1
		self.udb[username]={"id":self.ucounter,"displayName":displayName}
		return self.ucounter

	def getUser(self,username):
		if username in self.udb:
			return self.listUsers()[username]
		return None

	def updateUserField(self,username,fieldName,value):
		self.udb[username][fieldName]=value

	def removeUserField(self,username,fieldName):
		del self.udb[username][fieldName]

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		self.scounter = self.scounter+1
		self.sdb[self.scounter]={}
		self.sdb[self.scounter]["secretEncryptionProfile"]=secretEncryptionProfile
		self.sdb[self.scounter]["encryptedSecret"]=encryptedSecret
		self.sdb[self.scounter]["hmacKey"]=hmacKey
		self.sdb[self.scounter]["hmac"]=hmac
		self.sdb[self.scounter]["users"]={}
		self.sdb[self.scounter]["users"][owner]={"encryptedKey":encryptedKey,"canWrite":"Y"}
		return self.scounter

	def getSecret(self,sid):
		return self.sdb[sid]

class JsonDB(MemoryDB):
	def __init__(self,path):
		MemoryDB.__init__(self)
		self.path = path

		if os.path.exists(self.path+'.users.json'):
			f = open(self.path+'.users.json','r')
			self.udb = json.load(f)
			f.close()

		if os.path.exists(self.path+'.secrets.json'):
			f = open(self.path+'.secrets.json','r')
			self.sdb = json.load(f)

	def sync(self):
		f = open(self.path+'.users.json','w')
		f.write(json.dumps(self.udb,indent=2))
		f.close()
		f = open(self.path+'.secrets.json','w')
		f.write(json.dumps(self.sdb,indent=2))
		f.close()

