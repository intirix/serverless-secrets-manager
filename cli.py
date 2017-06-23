#!/usr/bin/python

import getopt
import sys
import client
import system
import db
import logging

class CLI:

	def __init__(self,args):
		self.args = args

	def help(self):
		print(sys.argv[0]+" <flags> <command> <arguments>")
		print("Flags:")
		print("  -d - direct mode - Directly contact database instead of going through REST API")
		print("")
		print("Commands:")
		print("  list-users - List the users")
		print("")

	def parse(self):

		optlist, self.args = getopt.getopt(self.args, 'd')

		self.mode = "rest"

		for o, a in optlist:
			if o=='-d':
				self.mode = "direct"
			else:
				assert False, "unhandled option"

		if len(self.args)==0:
			self.help()
			sys.exit(1)

	def init(self):

		if self.mode == 'direct':
			self.system = system.System()
			self.system.setDB(db.JsonDB('./local'))
			self.client = client.Client(client.ClientSystemInterface(self.system))
		else:
			raise(Exception("Mode ["+self.mode+"] not implemented yet"))

		self.system.init()

	def login(self):
		# Only valid for REST, which isn't implemented yet
		return

	def run(self):

		command = self.args[0]

		if command == "list-users":
			print("Users:")
			print("")
			for user in self.client.listUsers():
				print(user)
		else:
			self.help()
			raise Exception("Unknown command: "+command)


if __name__ == "__main__":
	FORMAT = "%(asctime)-15s %(message)s"
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('')
	cli = CLI(sys.argv[1:])
	cli.parse()
	cli.init()
	cli.login()
	cli.run()
