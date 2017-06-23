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

	def parse(self):

		optlist, self.args = getopt.getopt(self.args, 'd')

		self.mode = "rest"

		for o, a in optlist:
			if o=='-d':
				self.mode = "direct"
			else:
				assert False, "unhandled option"

	def init(self):

		if self.mode == 'direct':
			self.system = system.System()
			self.system.setDB(db.JsonDB('./local'))
			self.client = client.Client(client.ClientSystemInterface(self.system))
		else:
			raise(Exception("Mode ["+self.mode+"] not implemented yet"))

		self.system.init()

	def run(self):
		return


if __name__ == "__main__":
	FORMAT = "%(asctime)-15s %(message)s"
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('')
	cli = CLI(sys.argv[1:])
	cli.parse()
	cli.init()
	cli.run()
