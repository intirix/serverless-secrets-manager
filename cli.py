#!/usr/bin/python

import getopt
import sys
import client
import system
import db
import logging
import getpass
import crypto
import json
from datetime import datetime

class CLI:

	def __init__(self,args):
		self.args = args
		self.crypto = crypto.Crypto()
		self.helper = client.ClientHelper()

	def help(self):
		print(sys.argv[0]+" <flags> <command> <arguments>")
		print("Flags:")
		print("  -d - direct mode - Directly contact database instead of going through REST API")
		print("  -k - private key file - Encrypted private key for the user")
		print("  -b - base url - Base URL of the REST service")
		print("  -s - secrets table - Name of the secrets DynamoDB table")
		print("  -t - users table - Name of the users DynamoDB table")
		print("  -u [username] - user to log in a")
		print("")
		print("Commands:")
		print("  list-users")
		print("    Lists users")
		print("")
		print("  add-user <user> [displayName]")
		print("    Add a user")
		print("      user - username")
		print("      displayName - what get's displayed to users")
		print("        optional - defaults to username")
		print("")
		print("  generate-key-for-user <user>")
		print("    Generate a key for a user.  Will prompt for new password")
		print("      user - username")
		print("")
		print("  create-secret")
		print("    Create a new (empty) secret.  You can add extra fields later")
		print("")
		print("  get-secret <secretID>")
		print("    Get a secret (requires a private key)")
		print("      secretID - ID of the secret")
		print("")
		print("  get-my-secrets")
		print("    Gets all secrets that the user has access to (requires a private key)")
		print("")
		print("  set-secret-field <secretID> <fieldName> [value]")
		print("    Set a field inside of the secret (requires a private key)")
		print("      secretID - ID of the secret")
		print("      fieldName - name of the field to set")
		print("      value - value to set")
		print("        optional - will prompt for value if not provided")
		print("")
		print("  export-user-public-key [user] [filename]")
		print("    Export a user's public key")
		print("      user - The user who's public key should be exported")
		print("        optional - defaults to the logged in user")
		print("      filename - Filename to write the public key to")
		print("        optional - if left out, the public key will be written to the console")
		print("")
		print("  export-user-encrypted-private-key [user] [filename]")
		print("    Export a user's encrypted private key")
		print("      user - The user who's encrypted private key should be exported")
		print("        optional - defaults to the logged in user")
		print("      filename - Filename to write the encrypted private key to")
		print("        optional - if left out, the encrypted private key will be written to the console")
		print("")
		print("  export-my-private-key [filename]")
		print("    Export your private key in unencrypted form")
		print("      filename - Filename to write the private key to")
		print("        optional - if left out, the private key will be written to the console")
		print("")

	def parse(self):

		optlist, self.args = getopt.getopt(self.args, 'du:k:b:s:t:')

		self.mode = "rest"
		self.user = "admin"
		self.baseurl = None
		self.privateKeyFile = None
		self.privateKey = None
		self.secretsTable = None
		self.usersTable = None

		for o, a in optlist:
			if o=='-d':
				self.mode = "direct"
			elif o=='-u':
				self.user = a
			elif o=='-b':
				self.baseurl = a
			elif o=='-k':
				self.privateKeyFile = a
			elif o=='-s':
				self.secretsTable = a
			elif o=='-t':
				self.usersTable = a
			else:
				assert False, "unhandled option"

		if len(self.args)==0:
			self.help()
			sys.exit(1)

	def init(self):

		if self.mode == 'direct':
			self.system = system.System()
			if self.secretsTable==None or self.usersTable==None:
				self.system.setDB(db.JsonDB('./local'))
			else:
				mydb = db.CacheDB(db.DynamoDB(self.usersTable,self.secretsTable))
				self.system.setDB(mydb)
			self.client = client.Client(client.ClientSystemInterface(self.system))
			self.system.init()
		else:
			if self.baseurl == None:
				self.help()
				raise(Exception("-b required for rest mode"))
			self.client = client.Client(client.ClientRestInterface(self.baseurl))


	def login(self):
		print("Logging in as user: "+self.user)
		self.password = None
		if self.mode == 'direct':
			# direct access doesn't require a password
			self.client.login(self.user,"")
		else:
			if self.privateKeyFile==None:
				self.client.login(self.user,self.getPassword())
			else:
				authToken = self.helper.generateToken(self.getPrivateKey())
				self.client.login(self.user,authToken)

	def getPassword(self):
		if self.password == None:
			self.password = getpass.getpass("Password:")
		return self.password

	def getPrivateKey(self):
		if self.privateKey == None:
			if self.privateKeyFile != None:
				f = open(self.privateKeyFile,"r")
				encryptedPrivateKey = f.read()
				f.close()

				self.privateKey = self.helper.decryptPrivateKey(self.user,encryptedPrivateKey,self.getPassword())
			else:
				self.privateKey = self.client.getUserPrivateKey(self.user,self.getPassword())
		return self.privateKey

	def run(self):

		command = self.args[0]
		self.args = self.args[1:]

		if command == "list-users":
			print("Users:")
			print("")
			for user in self.client.listUsers():
				print(user)
		elif command == "add-user":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected argument <user>")
			user = self.args[0]
			display = user
			if len(self.args)==2:
				display = self.args[1]

			self.client.addUser(user,display)
		elif command == "generate-key-for-user":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected argument <user>")
			user = self.args[0]

			newPass = getpass.getpass("User's New Password:")
			self.client.generateKeysForUser(user,newPass)

		elif command == "create-secret":

			pubKey = self.client.getUserPublicKey(self.user)
			aesKey = self.crypto.generateRandomKey()
			hmacKey = self.crypto.generateRandomKey()

			# I don't want to just encrypt {}, I want some randomness in there
			rnd = self.crypto.encode(self.crypto.generateRandomKey())

			# Encrypt an empty secret for now
			encryptedSecret = self.crypto.encrypt(aesKey,json.dumps({"random":rnd}))
			encryptedKey = self.crypto.encryptRSA(pubKey,aesKey)

			hmac = self.crypto.createHmac(hmacKey,encryptedSecret)

			eek = self.crypto.encode(encryptedKey)
			ehk = self.crypto.encode(hmacKey)

			secret = self.client.addSecret(self.user,"1",eek,ehk,encryptedSecret,hmac)
			sid = secret["sid"]

			print("Secret ID: "+str(sid))

		elif command == "get-secret":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected argument <secretID>")

			sid = self.args[0]

			privKey = self.getPrivateKey()

			secretEntry = self.client.getSecret(sid)


			encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
			hmacKey = self.crypto.decode(secretEntry["hmacKey"])
			storedHmac = secretEntry["hmac"]
			storedEncryptedSecret = secretEntry["encryptedSecret"]

			if not self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):
				raise(Exception("Secret verification failed!"))

			origKey = self.crypto.decryptRSA(privKey,encryptedKey)
			origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
			origSecret = json.loads(origSecretText)
			del origSecret["random"]

			print(json.dumps(origSecret,indent=2))

		elif command == "get-my-secrets":
			privKey = self.getPrivateKey()

			secretEntries = self.client.getSecretsForUser(self.user)

			secrets = {}


			for sid in secretEntries.keys():
				secretEntry = secretEntries[sid]
				encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
				hmacKey = self.crypto.decode(secretEntry["hmacKey"])
				storedHmac = secretEntry["hmac"]
				storedEncryptedSecret = secretEntry["encryptedSecret"]

				if self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):

					origKey = self.crypto.decryptRSA(privKey,encryptedKey)
					origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
					origSecret = json.loads(origSecretText)
					del origSecret["random"]
					secrets[sid]=origSecret
				else:
					print("Secret verification failed for "+sid)


			print(json.dumps(secrets,indent=2))

		elif command == "set-secret-field":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected arguments <secretID> and <fieldName>")
			elif len(self.args)==1:
				self.help()
				raise Exception("Expected argument <fieldName>")


			sid = self.args[0]
			fieldName = self.args[1]

			# Prompt for the password before prompting for the value
			password = self.getPassword()


			# Get the value after getting the password
			value = None
			if len(self.args)==3:
				value = self.args[2]
			else:
				value = getpass.getpass("Value:")


			# First decrypt
			privKey = self.getPrivateKey()
			secretEntry = self.client.getSecret(sid)


			encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
			hmacKey = self.crypto.decode(secretEntry["hmacKey"])
			storedHmac = secretEntry["hmac"]
			storedEncryptedSecret = secretEntry["encryptedSecret"]

			if not self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):
				raise(Exception("Secret verification failed!"))

			aesKey = self.crypto.decryptRSA(privKey,encryptedKey)
			origSecretText = self.crypto.decrypt(aesKey,storedEncryptedSecret)
			origSecret = json.loads(origSecretText)

			# Set the value
			origSecret[fieldName] = value
			
			# Encrypt the secret
			encryptedSecret = self.crypto.encrypt(aesKey,json.dumps(origSecret))
			hmac = self.crypto.createHmac(hmacKey,encryptedSecret)

			self.client.updateSecret(sid,encryptedSecret,hmac)

		elif command == "export-user-public-key":
			exuser = self.user
			filename = None
			if len(self.args)>0:
				exuser = self.args[0]
				if len(self.args)>1:
					filename = self.args[1]

			pubKey = self.client.getUserPublicKey(exuser)

			if filename == None:
				print(pubKey)
			else:
				print("Writing public key to "+filename)
				f = open(filename,"w")
				f.write(pubKey)
				f.close()

		elif command == "export-user-encrypted-private-key":
			exuser = self.user
			filename = None
			if len(self.args)>0:
				exuser = self.args[0]
				if len(self.args)>1:
					filename = self.args[1]

			privKey = self.client.getUserPrivateKeyEncrypted(exuser)

			if filename == None:
				print(privKey)
			else:
				print("Writing encrypted private key to "+filename)
				f = open(filename,"w")
				f.write(privKey)
				f.close()
		elif command == "export-my-private-key":
			exuser = self.user
			filename = None
			if len(self.args)>0:
				exuser = self.args[0]
				if len(self.args)>1:
					filename = self.args[1]

			privKey = self.getPrivateKey()

			if filename == None:
				print(privKey)
			else:
				print("Writing encrypted private key to "+filename)
				f = open(filename,"w")
				f.write(privKey)
				f.close()

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
