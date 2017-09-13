#!/usr/bin/python3

import sys, os
from PyQt5.QtCore import pyqtProperty, QObject, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine, QQmlApplicationEngine
import threading
import client
import traceback


class Midtier(QObject):


	error = pyqtSignal(str,arguments=["error"])
	sigMessage = pyqtSignal(str,name="message",arguments=["message"])
	sigDownloadKey = pyqtSignal(str,name="downloadKey",arguments=["encryptedPrivateKey"])


	def __init__(self, parent=None):
		super().__init__(parent)
		self.helper = client.ClientHelper()
		self.clearSession()

	@pyqtProperty('QString')
	def url(self):
		return self._url

	@url.setter
	def url(self, url):
		self._url = url


	@pyqtProperty('QString')
	def user(self):
		return self._user

	@user.setter
	def user(self, user):
		self._user = user

	@pyqtProperty('QString')
	def password(self):
		return self._password

	@password.setter
	def password(self, password):
		self._password = password

	@pyqtProperty('QString')
	def authToken(self):
		return self._authToken

	@authToken.setter
	def authToken(self, authToken):
		self._authToken = authToken

	@pyqtProperty('QString')
	def encryptedPrivateKey(self):
		return self._encryptedPrivateKey

	@encryptedPrivateKey.setter
	def encryptedPrivateKey(self, encryptedPrivateKey):
		self._encryptedPrivateKey = encryptedPrivateKey

	@pyqtSlot()
	def clearSession(self):
		self._url = None
		self._user = None
		self._pass = None
		self._encryptedPrivateKey = None
		self._authToken = None
		self.client = None
		self._privKey = None
		self._secrets = None
		self.sigMessage.emit("")

	@pyqtSlot()
	def getSecrets(self):
		threading.Thread(target=(lambda: self._getSecrets())).start()

	def _getSecrets(self):
		try:
			self.client = client.Client(client.ClientRestInterface(self._url))
			if self._login():
				self.sigMessage.emit("Generating token")
				self._authToken = self.helper.generateToken(self._privKey)
				self.client.login(self._user,self._authToken)
				self.sigMessage.emit("Downloading secrets")
				self._secrets = self.client.getSecretsForUser(self._user)
				self.sigMessage.emit("Decrypting secrets")
				print(self._secrets)
		except Exception as e:
			traceback.print_exc()
			self.sigMessage.emit("")
			self.error.emit(str(e))

	@pyqtSlot()
	def downloadPrivateKey(self):
		threading.Thread(target=(lambda: self._downloadPrivateKey())).start()

	def _downloadPrivateKey(self):
		try:
			self.sigMessage.emit("Logging in with password")
			self.client = client.Client(client.ClientRestInterface(self._url))
			self.client.login(self._user,self._password)
			self._encryptedPrivateKey = self.client.getUserPrivateKey(self._user,self._password).decode('ascii')
			self.sigDownloadKey.emit(self._encryptedPrivateKey)
		except Exception as e:
			traceback.print_exc()
			self.clearSession()
			self.error.emit(str(e))

	@pyqtSlot()
	def login(self):
		threading.Thread(target=(lambda: self._login())).start()

	def _login(self):
		try:
			self._privKey = self.helper.decryptPrivateKey(self._user,self._encryptedPrivateKey,self._password)
			return True
		except Exception as e:
			traceback.print_exc()
			self.clearSession()
			self.error.emit(str(e))
		return False



if __name__ == '__main__':
	app = QGuiApplication(sys.argv)

	basepath = os.path.dirname(sys.argv[0])
	if len(basepath)==0:
		basepath="."

	qmlRegisterType(Midtier, 'Midtier', 1, 0, 'Midtier')

	engine = QQmlApplicationEngine()
	qmlFile = basepath+'/ui/main.qml'
	print("Loading "+qmlFile)
	engine.load(QUrl(qmlFile))

	sys.exit(app.exec_())

