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
		self.log = logging.getLogger("DynamoDB")
		self.usersTable = usersTable
		self.secretsTable = secretsTable

		# For unit testing
		if self.usersTable!=None:
			self.client = boto3.client('dynamodb')

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
			if username==None:
				self.log.exception("Could not parse user entry for unknown user")
			else:
				self.log.exception("Could not parse user entry for "+username)

		# only add the data if we parse the required fields
		if data != None and "displayName" in data:
			return (username,data)
		return (None,None)

	def _processSecret(self,item):
		data = None
		sid = "unknown"

		requiredFields = []
		requiredFields.append("hmac")
		requiredFields.append("hmacKey")
		requiredFields.append("encryptedSecret")
		requiredFields.append("secretEncryptionProfile")

		try:
			sid = item["sid"]["S"]

			data = {"users":{}}
			for key in requiredFields:
				if not key in item:
					raise(Exception("Secret "+sid+" is missing "+key))
				elif not "S" in item[key]:
					raise(Exception("Secret "+sid+" had the wrong datatype for "+key))
				else:
					data[key] = item[key]["S"]

			if "users" in item:
				for user in item["users"]["M"].keys():
					uitem = item["users"]["M"][user]["M"]
					udata = {"canWrite":"N","canShare":"N","canUnshare":"N"}
					try:
						for key in ["encryptedKey"]:
							if not key in uitem:
								raise(Exception("Secret "+sid+" is missing "+key+" for user "+user))
							elif not "S" in uitem[key]:
								raise(Exception("Secret "+sid+" had the wrong datatype for "+key+" for user "+user))
							else:
								udata[key] = uitem[key]["S"]


						for key in ["canWrite","canShare","canUnshare"]:
							if key in uitem and "S" in uitem[key]:
								udata[key] = uitem[key]["S"]

						data["users"][user] = udata
					except:
						self.log.exception("Could not parse secret entry user info for "+sid+" - "+user)

			return (sid,data)
		except:
			self.log.exception("Could not parse secret entry for "+sid)

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
			return self._processUser(resp["Item"])[1]
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
		return uid

	def updateUserField(self,username,fieldName,value):
		data={fieldName:{"Value":{"S":value},"Action":"PUT"}}
		resp = self.client.update_item(TableName=self.usersTable,Key={"username":{"S":username}},AttributeUpdates=data)
		return True

	def removeUserField(self,username,fieldName):
		data={fieldName:{"Action":"DELETE"}}
		resp = self.client.update_item(TableName=self.usersTable,Key={"username":{"S":username}},AttributeUpdates=data)
		return True

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		sid = str(uuid.uuid4())
		item={}
		item["sid"]={"S":sid}
		item["secretEncryptionProfile"]={"S":str(secretEncryptionProfile)}
		item["encryptedSecret"]={"S":encryptedSecret}
		item["hmacKey"]={"S":hmacKey}
		item["hmac"]={"S":hmac}
		item["users"]={"M":{}}
		item["users"]["M"][owner]={"M":{}}
		item["users"]["M"][owner]["M"]["encryptedKey"]={"S":encryptedKey}
		item["users"]["M"][owner]["M"]["canWrite"]={"S":"Y"}
		item["users"]["M"][owner]["M"]["canShare"]={"S":"Y"}
		item["users"]["M"][owner]["M"]["canUnshare"]={"S":"Y"}
		self.client.put_item(TableName=self.secretsTable,Item=item)
		return sid

	def updateSecret(self,sid,encryptedSecret,hmac):
		data={}
		data["encryptedSecret"]={"Value":{"S":encryptedSecret},"Action":"PUT"}
		data["hmac"]={"Value":{"S":hmac},"Action":"PUT"}
		resp = self.client.update_item(TableName=self.secretsTable,Key={"sid":{"S":sid}},AttributeUpdates=data)
		return True

	def getSecret(self,sid):
		resp = self.client.get_item(TableName=self.secretsTable,Key={"sid":{"S":sid}})
		if resp != None and "Item" in resp:
			return self._processSecret(resp["Item"])[1]
		return None

	def getSecretsForUser(self,user):
		items = self.client.scan(TableName=self.secretsTable)["Items"]
		ret = {}

		for item in items:
			(sid,data) = self._processSecret(item)
			if data != None and "users" in data and user in data["users"]:
				ret[sid] = data
		return ret


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
		self.sdb[sid]["users"][owner]={"encryptedKey":encryptedKey,"canWrite":"Y","canShare":"Y","canUnshare":"Y"}
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

class CacheDB(MemoryDB):
	def __init__(self,child):
		MemoryDB.__init__(self)
		self.child = child
		self._refreshAllUsers()

	def _refreshAllUsers(self):
		self.udb = self.child.listUsers()

	def _refreshUser(self,user):
		self.udb[user] = self.child.getUser(user)

	def listUsers(self):
		return json.loads(json.dumps(self.udb))

	def addUser(self,username,displayName):
		ret = self.child.addUser(username,displayName)
		self._refreshUser(username)
		return ret

	def updateUserField(self,username,fieldName,value):
		ret = self.child.updateUserField(username,fieldName,value)
		self._refreshUser(username)
		return ret

	def removeUserField(self,username,fieldName):
		ret = self.child.removeUserField(username,fieldName)
		self._refreshUser(username)
		return ret

	def addSecret(self,owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac):
		return self.child.addSecret(owner,secretEncryptionProfile,encryptedKey,hmacKey,encryptedSecret,hmac)

	def updateSecret(self,sid,encryptedSecret,hmac):
		return self.child.updateSecret(sid,encryptedSecret,hmac)

	def getSecret(self,sid):
		return self.child.getSecret(sid)

	def getSecretsForUser(self,user):
		return self.child.getSecretsForUser(user)

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

