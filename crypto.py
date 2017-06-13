#!/usr/bin/python

import scrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64

class Crypto:

	def keyStretchPassword(self,salt,password,buflen=32):
		key = scrypt.hash(password=password,salt=salt,buflen=buflen)
		return key

	def generatePublicPrivateKeys(self):
		rng = Random.new().read
		RSAkey = RSA.generate(2048, rng)
		pubkey = RSAkey.publickey()
		publicPem = pubkey.exportKey()
		privatePem = RSAkey.exportKey()
		return (privatePem,publicPem)

	def pad(self,s):
		# https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
		return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

	def unpad(self,s):
		# https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
		return s[:-ord(s[len(s)-1:])]

	def encrypt(self,key,message):
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(key, AES.MODE_CBC, iv)
		encrypted = iv + cipher.encrypt(self.pad(message))
		encoded = base64.b64encode(encrypted)
		return encoded

	def decrypt(self,key,encrypted):
		decoded = base64.b64decode(encrypted)
		iv = decoded[0:AES.block_size]
		emsg = decoded[AES.block_size:]
		cipher = AES.new(key, AES.MODE_CBC, iv)
		decrypted = self.unpad(cipher.decrypt(emsg))
		return decrypted

	def sign(self,priv,message):
		rng = Random.new().read
		h = SHA256.new(message).digest()
		rsapriv = RSA.importKey(priv)
		signature = rsapriv.sign(h, rng)
		return signature

	def verify(self,pub,message,signature):
		rsapub = RSA.importKey(pub)
		h = SHA256.new(message).digest()
		return rsapub.verify(h, signature)

