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

	def canAuthenticateWithPassword(self,user):
		data = self.system.getUser(user)
		return data!=None and data["passwordAuth"]=="Y"

	def canGrantAdmin(self,user):
		return self.isEnabled(user) and self.isAdmin(user)

	def canCreateUser(self,user):
		return self.isEnabled(user) and self.isAdmin(user)

	def canUpdateUserProfile(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )

	def canChangeUserKeys(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )

	def canUserExportPublicKey(self,ruser,auser):
		return self.isEnabled(ruser)

	def canUserExportPrivateKey(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )

	def canUserSeeAttributes(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )

	def canUserEnableUser(self,ruser,auser):
		return self.isEnabled(ruser) and self.isAdmin(ruser)

	def canUserDisableUser(self,ruser,auser):
		return self.isEnabled(ruser) and ( ruser==auser or self.isAdmin(ruser) )







