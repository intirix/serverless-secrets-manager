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
import appdirs
import ConfigParser
import os
import shutil
import base64
from datetime import datetime

class CLI:

	def __init__(self,args):
		self.args = args
		self.crypto = crypto.Crypto()
		self.helper = client.ClientHelper()
		self.password = None
		self.system = None

	def help(self):
		print(sys.argv[0]+" <flags> <command> <arguments>")
		print("Flags:")
		print("  -d - direct mode - Directly contact database instead of going through REST API")
		print("  -k - private key file - Encrypted private key for the user")
		print("  -b - base url - Base URL of the REST service")
		print("  -s - secrets table - Name of the secrets DynamoDB table")
		print("  -t - users table - Name of the users DynamoDB table")
		print("  -j - json database - Path to the local JSON database")
		print("  -p - password - Password used to decrypt")
		print("  -u [username] - user to log in a")
		print("  -c - save config for later")
		print("")
		print("Commands:")
		print("  save-config")
		print("    Save the configuration to make it easier to call the CLI later")
		print("    This is the same as the -c option with no action")
		print("")
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
		print("  create-secret [file]")
		print("    Create a new  secret.  You can add extra fields later")
		print("      file - json file to load as a secret")
		print("        optional - defaults to an empty secret")
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
		print("  share-secret <secretID> <user>")
		print("    Share a secret with another user")
		print("      secretID - ID of the secret")
		print("      user - username to share with")
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
		print("  import-my-encrypted-private-key <filename>")
		print("    Import your encrypted private key so the CLI can use it more easily")
		print("      filename - Filename to write the private key to")
		print("")
		print("  generate-auth-token")
		print("    Generate a token that can be used as a basic auth password")
		print("")
		print("")
		print("Higher level commands:")
		print("")
		print("  change-password <secretID/Website> [password]")
		print("    Alias for: set-secret-field <secretID> password <value>")
		print("      secretID - ID of the secret")
		print("      password - value to set")
		print("")
		print("  find-password <text>")
		print("    Find a password based on the text")
		print("      text - text to search for")
		print("")

	def parseConfig(self):


		try:
			self.mode = self.config.get("server","mode")
		except:
			self.mode = "rest"
		try:
			self.user = self.config.get("server","user")
		except:
			self.user = "admin"
		try:
			self.baseurl = self.config.get("server","baseurl")
		except:
			self.baseurl = None

		try:
			self.privateKeyFile = self.config.get("server","privateKeyFile")
		except:
			self.privateKeyFile = None
		try:
			self.secretsTable = self.config.get("server","secretsTable")
		except:
			self.secretsTable = None
		try:
			self.usersTable = self.config.get("server","usersTable")
		except:
			self.usersTable = None
		try:
			self.jsonPath = self.config.get("server","jsonPath")
		except:
			self.jsonPath = None

		self.privateKey = None

	def parse(self):
		self.parseConfig()

		optlist, self.args = getopt.getopt(self.args, 'du:k:b:s:t:p:j:c')

		saveConfig = False

		for o, a in optlist:
			if o=='-d':
				self.mode = "direct"
				self.config.set("server","mode","direct")
			elif o=='-u':
				self.user = a
				self.config.set("server","user",a)
			elif o=='-b':
				self.baseurl = a
				self.config.set("server","baseurl",a)
			elif o=='-k':
				self.privateKeyFile = a
				self.config.set("server","privateKeyFile",a)
			elif o=='-s':
				self.secretsTable = a
				self.config.set("server","secretsTable",a)
			elif o=='-t':
				self.usersTable = a
				self.config.set("server","usersTable",a)
			elif o=='-p':
				self.password = a
			elif o=='-j':
				self.jsonPath = a
				self.config.set("server","jsonPath",a)
			elif o=='-c':
				saveConfig = True
			else:
				assert False, "unhandled option"

		if len(self.args)==0:
			self.help()
			sys.exit(1)

		if saveConfig:
			self.saveConfig(False)

	def initUserConfig(self):
                self.userConfigDir = appdirs.user_data_dir("ServerLessSecretsManagerCLI","intirix")
		self.userConfigFile = self.userConfigDir+"/userConfig.ini"
		self.config = ConfigParser.SafeConfigParser()
		if os.path.exists(self.userConfigFile):
			self.config.read(self.userConfigFile)
		if not self.config.has_section("server"):
			self.config.add_section("server")


	def saveConfig(self,verbose=False):
		if not os.path.exists(self.userConfigDir):
			if verbose:
				print("Creating directory "+self.userConfigDir)
			os.makedirs(self.userConfigDir)
		if verbose:
			print("Writing configuration to "+self.userConfigFile)
		with open(self.userConfigFile, 'wb') as configfile:
			self.config.write(configfile)


	def init(self):
		if self.mode == 'direct':
			if self.system == None:
				self.system = system.System()
				if self.secretsTable==None or self.usersTable==None:
					if self.jsonPath == None:
						self.system.setDB(db.MemoryDB())
					else:
						self.system.setDB(db.JsonDB(self.jsonPath))
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
		if self.mode == 'direct':
			# direct access doesn't require a password
			self.client.login(self.user,"")
		else:
			if self.privateKeyFile==None:
				print("Logging in with password")
				self.client.login(self.user,self.getPassword())
			else:
				authToken = None
				if "SLSM_AUTH" in os.environ:
					print("Logging in with saved session")
					authToken = base64.b64encode(os.environ["SLSM_AUTH"])
				if authToken == None:
					print("Logging in with private key")
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
		elif command == "save-config":
			print("Saving configuration")
			self.saveConfig(True)
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
			secretValues = [{}]


			if len(self.args)>=1:
				secretValues=[]
				for sf in self.args:
					f = open(sf,"r")
					secretValues.append(json.load(f))
					f.close()

			pubKey = self.client.getUserPublicKey(self.user)
			for secretValue in secretValues:
				aesKey = self.crypto.generateRandomKey()
				hmacKey = self.crypto.generateRandomKey()

				bothKeys = aesKey + hmacKey

				# I don't want to just encrypt {}, I want some randomness in there
				rnd = self.crypto.encode(self.crypto.generateRandomKey())
				secretValue["random"]=rnd

				# Encrypt an empty secret for now
				encryptedSecret = self.crypto.encrypt(aesKey,json.dumps(secretValue))
				encryptedKey = self.crypto.encryptRSA(pubKey,bothKeys)

				hmac = self.crypto.createHmac(hmacKey,encryptedSecret)

				eek = self.crypto.encode(encryptedKey)

				secret = self.client.addSecret(self.user,"1",eek,encryptedSecret,hmac)
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
			storedHmac = secretEntry["hmac"]
			storedEncryptedSecret = secretEntry["encryptedSecret"]

			origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
			origKey = origKeyPair[0:32]
			hmacKey = origKeyPair[32:]

			if not self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):
				raise(Exception("Secret verification failed!"))

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
				storedHmac = secretEntry["hmac"]
				storedEncryptedSecret = secretEntry["encryptedSecret"]

				origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
				origKey = origKeyPair[0:32]
				hmacKey = origKeyPair[32:]

				if self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):

					origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
					if sys.version_info.major == 3 and type(origSecretText)==bytes:
						origSecretText = origSecretText.decode('utf-8')
					origSecret = json.loads(origSecretText)
					del origSecret["random"]
					secrets[sid]=origSecret
				else:
					print("Secret verification failed for "+sid)


		elif command == "find-password":

			if len(self.args)==0:
				self.help()
				raise Exception("Expected argument <text>")

			value = self.args[0]

			privKey = self.getPrivateKey()
			secretEntries = self.client.getSecretsForUser(self.user)


			for sid in secretEntries.keys():
				secretEntry = secretEntries[sid]
				encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
				storedHmac = secretEntry["hmac"]
				storedEncryptedSecret = secretEntry["encryptedSecret"]

				origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
				origKey = origKeyPair[0:32]
				hmacKey = origKeyPair[32:]

				if self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):

					origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
					if sys.version_info.major == 3 and type(origSecretText)==bytes:
						origSecretText = origSecretText.decode('utf-8')
					origSecret = json.loads(origSecretText)
					if origSecret["type"]=="password":
						found = False
						for k in origSecret.keys():
							if str(origSecret[k]).lower().find(value.lower())>=0:
								found = True
						if found:
							del origSecret["random"]
							origSecret["sid"] = sid
							print(json.dumps(origSecret,indent=2))
				else:
					print("Secret verification failed for "+sid)


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

			self.setFieldValue(sid,fieldName,value)

		elif command == "change-password":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected arguments <secretID>")

			# Prompt for the password before prompting for the value
			password = self.getPassword()

			sid = self.findPassword(self.args[0])

			# Get the value after getting the password
			value = None
			if len(self.args)==3:
				value = self.args[2]
			else:
				value = getpass.getpass("Value:")

			self.setFieldValue(sid,"password",value)


		elif command == "share-secret":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected arguments <secretID> and <username>")
			elif len(self.args)==1:
				self.help()
				raise Exception("Expected argument <username>")

			sid = self.args[0]
			user = self.args[1]

			password = self.getPassword()
			privKey = self.getPrivateKey()
			print("Downloading "+user+"'s public key")
			pubKey = self.client.getUserPublicKey(user)
			print("Downloading "+str(sid))
			secretEntry = self.client.getSecret(sid)
			encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
			print("Decrypting "+str(sid)+"'s AES key")
			origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
			origKey = origKeyPair[0:32]
			hmacKey = origKeyPair[32:]
			print("Encrypting "+str(sid)+"'s AES key")
			encryptedKey2 = self.crypto.encryptRSA(pubKey,origKey)
			print("Sharing with "+user)
			self.client.shareSecret(sid,user,self.crypto.encode(encryptedKey2))

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

		elif command == "import-my-encrypted-private-key":
			if len(self.args)==0:
				self.help()
				raise Exception("Expected argument <filename>")
			filename = self.args[0]
			configKey = self.userConfigDir+"/"+self.user+".key"
			if not os.path.exists(self.userConfigDir):
				os.makedirs(self.userConfigDir)
			print("Copying "+filename+" to "+configKey)
			shutil.copyfile(filename,configKey)
			self.privateKeyFile = configKey
			self.config.set("server","privateKeyFile",configKey)
			self.saveConfig(True)

		elif command == "generate-auth-token":
			if self.mode == 'direct':
				print("Auth token unavailable with direct access")
			else:
				if self.privateKeyFile==None:
					print("Auth token requires a private key")
				else:
					authToken = self.helper.generateToken(self.getPrivateKey())
					print("AuthToken: "+authToken)
					print("")
					print("export SLSM_AUTH="+base64.b64encode(authToken).decode('utf-8'))
		else:
			self.help()
			raise Exception("Unknown command: "+command)

	def setFieldValue(self,sid,fieldName,value):
		# First decrypt
		privKey = self.getPrivateKey()
		secretEntry = self.client.getSecret(sid)

		encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
		origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
		origKey = origKeyPair[0:32]
		hmacKey = origKeyPair[32:]
		storedHmac = secretEntry["hmac"]
		storedEncryptedSecret = secretEntry["encryptedSecret"]

		if not self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):
			raise(Exception("Secret verification failed!"))

		origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
		origSecret = json.loads(origSecretText)

		# Set the value
		origSecret[fieldName] = value
		
		# Encrypt the secret
		encryptedSecret = self.crypto.encrypt(origKey,json.dumps(origSecret))
		hmac = self.crypto.createHmac(hmacKey,encryptedSecret)

		self.client.updateSecret(sid,encryptedSecret,hmac)

	def findSid(self,value):

		privKey = self.getPrivateKey()

		secretEntries = self.client.getSecretsForUser(self.user)

		secrets = {}


		for sid in secretEntries.keys():
			secretEntry = secretEntries[sid]
			encryptedKey = self.crypto.decode(secretEntry["users"][self.user]["encryptedKey"])
			storedHmac = secretEntry["hmac"]
			storedEncryptedSecret = secretEntry["encryptedSecret"]

			origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
			origKey = origKeyPair[0:32]
			hmacKey = origKeyPair[32:]

			if self.crypto.verifyHmac(hmacKey,storedEncryptedSecret,storedHmac):

				origSecretText = self.crypto.decrypt(origKey,storedEncryptedSecret)
				if sys.version_info.major == 3 and type(origSecretText)==bytes:
					origSecretText = origSecretText.decode('utf-8')
				origSecret = json.loads(origSecretText)

				if "type" in origSecret and origSecret["type"]=="password":
					for k in origSecret.keys():
						if str(origSecret[k]).lower().find(value.lower())>=0:
							del origSecret["random"]
							del origSecret["password"]
							print(json.dumps(origSecret,indent=2))
							return sid

		return value


if __name__ == "__main__":
	FORMAT = "%(asctime)-15s %(message)s"
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('')
	cli = CLI(sys.argv[1:])
	cli.initUserConfig()
	cli.parse()
	cli.init()
	cli.login()
	cli.run()
