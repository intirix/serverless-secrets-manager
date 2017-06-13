#!/usr/bin/python


class DBInterface:

	def listUsers(self):
		raise Exception("Not implemented")

	def addUser(self,username,displayName):
		raise Exception("Not implemented")


class MemoryDB(DBInterface):
	def __init__(self):
		self.db = {}
		self.counter = 0


	def listUsers(self):
		return self.db


	def addUser(self,username,displayName):
		self.counter = self.counter+1
		self.db[username]={"id":self.counter,"displayName":displayName}

	def getUser(self,username):
		return self.listUsers()[username]

	def updateUserField(self,username,fieldName,value):
		self.db[username][fieldName]=value

	def removeUserField(self,username,fieldName):
		del self.db[username][fieldName]





