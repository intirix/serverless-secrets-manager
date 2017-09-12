#!/usr/bin/python

import scrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Hash import HMAC
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import base64
import os
import sys
import binascii

from datetime import datetime, timedelta
import time

class Crypto:

	def keyStretchPassword(self,salt,password,buflen=32):
		# scrypt doesn't support unicode salts and passwords
		# I don't know if this is the proper way to handle this
		# I think I might want to do a length check so that I fail
		# when something funny is going on
		if sys.version_info.major == 2:
			if type(salt)==unicode:
				salt=salt.encode('ascii','replace')
			if type(password)==unicode:
				password=password.encode('ascii','replace')

		key = scrypt.hash(password=password,salt=salt,buflen=buflen)
		return key

	def generateRandomKey(self,buflen=32):
		return os.urandom(buflen)

	def generatePublicPrivateKeys(self):
		rng = Random.new().read
		RSAkey = RSA.generate(2048, rng)
		pubkey = RSAkey.publickey()
		publicPem = pubkey.exportKey()
		privatePem = RSAkey.exportKey(pkcs=8)
		return (privatePem,publicPem)

	def pad(self,s):
		# https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
		padnum = AES.block_size - len(s) % AES.block_size
		mypad = (AES.block_size - len(s) % AES.block_size) * chr(padnum)
		if sys.version_info.major == 2:
			return s + mypad
		else:
			ret = None
			if sys.version_info.major == 3 and type(s)==str:
				ret = bytearray(s.encode('utf-8'))
			else:
				ret = bytearray(s)
			for i in range(0,padnum):
				ret.append(padnum)
			return bytes(ret)

	def unpad(self,s):
		# https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
		return s[:-ord(s[len(s)-1:])]

	def encode(self,data):
		if sys.version_info.major == 3:
			if type(data)==str:
				data = data.encode('utf-8')
			return base64.b64encode(data).decode('utf-8')

		return base64.b64encode(data)

	def decode(self,data):
		return base64.b64decode(data)

	def encrypt(self,key,message):
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(key, AES.MODE_CBC, iv)
		encrypted = iv + cipher.encrypt(self.pad(message))
		encoded = base64.b64encode(encrypted)
		return encoded

	def decrypt(self,key,encrypted):
		print("encrypted="+str(encrypted))
		decoded = base64.b64decode(encrypted)
		iv = decoded[0:AES.block_size]
		emsg = decoded[AES.block_size:]
		cipher = AES.new(key, AES.MODE_CBC, iv)
		decrypted = self.unpad(cipher.decrypt(emsg))
		return decrypted

	def getAscii(self,message):
		msg = message
		if sys.version_info.major == 2 and type(msg)==unicode:
			msg = str(msg)
		elif sys.version_info.major == 3 and type(msg)==str:
			msg = msg.encode('utf-8')
		return msg

	def sign(self,priv,message):
		rng = Random.new().read
		h = SHA256.new(self.getAscii(message))
		print("sign hash="+str(h.hexdigest()))
		rsapriv = RSA.importKey(priv)
		signer = PKCS1_v1_5.new(rsapriv)
		sig = signer.sign(h)
		print("out sig="+str(binascii.hexlify(sig)))
		return self.encode(sig)

	def getPublicKeyType(self,pub):
		try:
			RSA.importKey(pub)
			return "RSA"
		except:
			return "unknown"

	def verify(self,pub,message,signature):
		print("msg="+message)
		print("sig="+signature)
		rsapub = RSA.importKey(pub)
		h = SHA256.new(self.getAscii(message))
		print("sign hash="+str(h.hexdigest()))
		verifier = PKCS1_v1_5.new(rsapub)
		#sig = self.decode(signature)
		print("type of signature is "+str(type(signature)))
		sig = base64.b64decode(signature.encode('utf-8'))
		tmp = base64.b64encode(sig)
		print("in sig="+str(binascii.hexlify(sig))+" for "+signature +" from "+str(tmp))
		return verifier.verify(h, sig)

	def encryptRSA(self,key,message):
		rsapub = RSA.importKey(key)
		cipher = PKCS1_OAEP.new(rsapub,SHA256)
		ciphertext = cipher.encrypt(message)
		return ciphertext

	def decryptRSA(self,key,ciphertext):
		rsapriv = RSA.importKey(key)
		cipher = PKCS1_OAEP.new(rsapriv,SHA256)
		message = cipher.decrypt(ciphertext)
		return message

	def createHmac(self,key,message):
		h = HMAC.new(key,self.getAscii(message),SHA256)
		return h.hexdigest()

	def verifyHmac(self,key,message,mac):
		mac2 = self.createHmac(key,message)

		compareKey = self.generateRandomKey()
		
		mac1b = self.createHmac(compareKey,mac)
		mac2b = self.createHmac(compareKey,mac2)
		return mac1b == mac2b

def lambda_selftest(event,context):
	obj=Crypto()


	start = datetime.utcnow()
	t1 = time.time()
	(privatePem,publicPem)=obj.generatePublicPrivateKeys()
	t2 = time.time()
	dt2 = t2 - t1
	print(str(dt2)+"s to generate RSA key")

	key = obj.keyStretchPassword("salt1234","mypassword")
	t3 = time.time()
	dt3 = t3 - t2
	print(str(dt3)+"s to stretch password")

	message = "the quick fox jumped over the lazy dog"

	cipher = obj.encrypt(key,message)
	t4 = time.time()
	dt4 = t4 - t3
	print(str(dt4)+"s to AES encrypt message")

	orig = obj.decrypt(key,cipher)
	t5 = time.time()
	dt5 = t5 - t4
	print(str(dt5)+"s to AES decrypt message")

	sig = obj.sign(privatePem,message)
	t6 = time.time()
	dt6 = t6 - t5
	print(str(dt6)+"s to RSA sign message")

	obj.verify(publicPem,message,sig)
	t7 = time.time()
	dt7 = t7 - t6
	print(str(dt7)+"s to RSA verify message")

	keyCipher = obj.encryptRSA(publicPem,key)
	t8 = time.time()
	dt8 = t8 - t7
	print(str(dt8)+"s to RSA encrypt AES key")

	origKey = obj.decryptRSA(privatePem,keyCipher)
	t9 = time.time()
	dt9 = t9 - t8
	print(str(dt9)+"s to RSA decrypt AES key")


	decryptionsPerSecond=1 / ( dt9 + dt5 )
	print(str(decryptionsPerSecond)+" decryptions/second")



if __name__ == '__main__':
	lambda_selftest(None,None)



