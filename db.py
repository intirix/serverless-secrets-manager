#!/usr/bin/python

import json
import os
import uuid

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
		sid = str(uuid.uuid4())
		self.sdb[sid]={}
		self.sdb[sid]["secretEncryptionProfile"]=secretEncryptionProfile
		self.sdb[sid]["encryptedSecret"]=encryptedSecret
		self.sdb[sid]["hmacKey"]=hmacKey
		self.sdb[sid]["hmac"]=hmac
		self.sdb[sid]["users"]={}
		self.sdb[sid]["users"][owner]={"encryptedKey":encryptedKey,"canWrite":"Y"}
		return sid

	def updateSecret(self,sid,encryptedSecret,hmac):
		self.sdb[sid]["encryptedSecret"]=encryptedSecret
		self.sdb[sid]["hmac"]=hmac

	def getSecret(self,sid):
		return self.sdb[sid]

	def getSecretsForUser(self,user):
		ret = {}

		for sid in self.sdb.keys():
			if user in self.sdb[sid]["users"]:
				ret[sid]=self.sdb[sid]

		return ret

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

