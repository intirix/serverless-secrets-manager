#!/usr/bin/python

class System:

	def __init__(self):
		self.db = None

	def setDB(self,db):
		self.db = db

	def addUser(self,username,displayName):
		self.db.addUser(username,displayName)

	def setUserPublicKey(self,username,pem):
		self.db.updateUserField(username,"publicKey",pem)
