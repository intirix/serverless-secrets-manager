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

	def encrypt(self,key,message):
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(key, AES.MODE_CFB, iv)
		encrypted = iv + cipher.encrypt(message)
		encoded = base64.b64encode(encrypted)
		return encoded

	def decrypt(self,key,encrypted):
		decoded = base64.b64decode(encrypted)
		iv = decoded[0:AES.block_size]
		emsg = decoded[AES.block_size:]
		cipher = AES.new(key, AES.MODE_CFB, iv)
		decrypted = cipher.decrypt(emsg)
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

