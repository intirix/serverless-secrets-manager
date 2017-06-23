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


class Client:

	def __init__(self,iface):
		self.iface = iface

	def login(self,username,password):
		self.username = username
		return

	def listUsers(self):
		return self.iface.listUsers()

	def addUser(self,user,display):
		return self.iface.addUser(user,display)


