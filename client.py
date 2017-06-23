#!/usr/bin/python



class ClientSystemInterface:

	def __init__(self,system):
		self.system = system

	def login(self,username,password):
		return



class Client:

	def __init__(self,iface):
		self.iface = iface

	def login(self,username,password):
		self.username = username
		return




