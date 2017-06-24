#!/usr/bin/python


class AccessRules:

	def __init__(self,system):
		self.system = system

	def isEnabled(self,user):
		data = self.system.getUser(user)
		return data!=None and data["enabled"]=="Y"

	def isAdmin(self,user):
		data = self.system.getUser(user)
		return data!=None and data["admin"]=="Y"

	def canGrantAdmin(self,user):
		return self.isEnabled(user) and self.isAdmin(user)

	def canCreateUser(self,user):
		return self.isEnabled(user) and self.isAdmin(user)

	def canChangeUserKeys(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )

	def canUserExportPublicKey(self,ruser,auser):
		return self.isEnabled(ruser)

	def canUserExportPrivateKey(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )









