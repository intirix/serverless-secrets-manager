#!/usr/bin/python



class ClientSystemInterface:

	def __init__(self,system):
		self.system = system

	def login(self,username,password):
		return

	def listUsers(self):
		return self.system.listUsers()

	def addUser(self,user,display):
		return self.system.addUser(user,display)

	def canCreateUser(self,user):
		# Direct access always can create users
		return True


class Client:

	def __init__(self,iface):
		self.iface = iface

	def login(self,username,password):
		self.username = username
		return self.iface.login(username,password)

	def listUsers(self):
		return self.iface.listUsers()

	def addUser(self,user,display):
		if self.iface.canCreateUser(self.username):
			return self.iface.addUser(user,display)


