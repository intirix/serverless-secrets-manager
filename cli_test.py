#!/usr/bin/python

import unittest
import json
import sys
import ConfigParser
from cli import CLI

class MockCLI(CLI):

	def initUserConfig(self):
		self.config = ConfigParser.SafeConfigParser()
		self.config.add_section("server")


class TestCLI(unittest.TestCase):

	def testCLI(self):
		cli = MockCLI(['-d','-u','admin','-p','password','export-user-encrypted-private-key','admin','unittest.key'])
		cli.initUserConfig()
		cli.parse()
		cli.init()
		cli.login()
		cli.run()
		cli.args=['-d','-u','admin','-p','password','-k','unittest.key','create-secret']
		cli.initUserConfig()
		cli.parse()
		cli.login()
		cli.run()
		cli.args=['-d','-u','admin','-p','password','-k','unittest.key','get-my-secrets']
		cli.initUserConfig()
		cli.parse()
		cli.login()
		cli.run()



if __name__ == '__main__':
	unittest.main()
