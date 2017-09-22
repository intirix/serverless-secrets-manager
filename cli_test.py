#!/usr/bin/python

import unittest
import json
import sys
from cli import CLI


class TestCLI(unittest.TestCase):

	def testCLI(self):
		cli = CLI(['-d','-u','admin','-p','password','export-user-encrypted-private-key','admin','unittest.key'])
		cli.parse()
		cli.init()
		cli.login()
		cli.run()
		cli.args=['-d','-u','admin','-p','password','-k','unittest.key','create-secret']
		cli.parse()
		cli.login()
		cli.run()
		cli.args=['-d','-u','admin','-p','password','-k','unittest.key','get-my-secrets']
		cli.parse()
		cli.login()
		cli.run()



if __name__ == '__main__':
	unittest.main()
