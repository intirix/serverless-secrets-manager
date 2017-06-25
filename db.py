#!/usr/bin/python

import json
import os
import uuid
import boto3
import logging

class DBInterface:

	def listUsers(self):
		raise Exception("Not implemented")

	def addUser(self,username,displayName):
		raise Exception("Not implemented")

class DynamoDB(DBInterface):
	def __init__(self,usersTable,secretsTable):
		self.usersTable = usersTable
		self.secretsTable = secretsTable
		self.client = boto3.client('dynamodb')
		self.log = logging.getLogger("DynamoDB")

	def sync(self):
		return

	def _processUser(self,item):
		data = None
		username = None
		try:
			username = item["username"]["S"]

			data = {}
			data["admin"] = "N"
			data["enabled"] = "N"
			data["displayName"] = item["displayName"]["S"]

			for key in [ "publicKey", "keyType", "encryptedPrivateKey", "admin", "enabled" ]:
				if key in item and "S" in item[key]:
					data[key] = item[key]["S"]
		except:
			self.log.exception("Could not parse entry for "+username)

		# only add the data if we parse the required fields
		if data != None and "displayName" in data:
			return (username,data)
		return (None,None)

	def listUsers(self):
		items = self.client.scan(TableName=self.usersTable)["Items"]
		ret = {}

		for item in items:
			(username,data) = self._processUser(item)
			if data != None:
				ret[username] = data
		return ret

	def getUser(self,username):
		resp = self.client.get_item(TableName=self.usersTable,Key={"username":{"S":username}})
		if resp != None and "Item" in resp:
			return self._processUser(resp["Item"])
		return None

	def addUser(self,username,displayName):
		uid = str(uuid.uuid4())
		item = {}
		item["username"]={"S":username}
		item["id"]={"S":uid}
		item["admin"]={"S":"N"}
		item["enabled"]={"S":"Y"}
		item["displayName"]={"S":displayName}
		self.client.put_item(TableName=self.usersTable,Item=item)
		return True

	def updateUserField(self,username,fieldName,value):
		data={fieldName:{"Value":{"S":value},"Action":"PUT"}}
		resp = self.client.update_item(TableName=self.usersTable,Key={"username":{"S":username}},AttributeUpdates=data)
		return True

	def removeUserField(self,username,fieldName):
		data={fieldName:{"Action":"DELETE"}}
		resp = self.client.update_item(TableName=self.usersTable,Key={"username":{"S":username}},AttributeUpdates=data)
		return True

class MemoryDB(DBInterface):
	def __init__(self):
		self.udb = {}
		self.sdb = {}

	def sync(self):
		return

	def listUsers(self):
		return json.loads(json.dumps(self.udb))


	def addUser(self,username,displayName):
		uid = str(uuid.uuid4())
		self.udb[username]={"id":uid,"displayName":displayName,"admin":"N","enabled":"Y"}
		return uid

	def getUser(self,username):
		if username in self.udb:
			return json.loads(json.dumps(self.listUsers()[username]))
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
		return json.loads(json.dumps(self.sdb[sid]))

	def getSecretsForUser(self,user):
		ret = {}

		for sid in self.sdb.keys():
			if user in self.sdb[sid]["users"]:
				ret[sid]=self.sdb[sid]

		return json.loads(json.dumps(ret))

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

