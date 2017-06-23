#!/usr/bin/python


class Context:

	def __init__(self,user):
		self.user = user



class Server:

	def __init__(self,system):
		self.system = system

	def _getUserData(self,obj):
		ret = {}
		for key in [ "displayName", "publicKey" ]:
			if key in obj:
				ret[key] = obj[key]
		return ret

	def listUsers(self,ctx):
		ret = {}
		data = self.system.listUsers()

		for user in data.keys():
			ret[user]=self._getUserData(data[user])
		return ret

	def getUser(self,ctx,user):
		data = self.system.getUser(user)
		if data==None:
			return None
		return self._getUserData(data)
