#!/usr/bin/python3

import sys, os
from PyQt5.QtCore import pyqtProperty, QObject, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtCore import QAbstractListModel, QSortFilterProxyModel
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine, QQmlApplicationEngine
import threading
import client
import traceback
import crypto
import json

def addField(v,d,field):
	if field in d:
		v = v + str(d[field])
	return v

def makeSortString(d):
	ret = ""
	if "website" in d:
		ret = addField(ret,d,"website").replace("www.","")
	elif "address" in d:
		ret = addField(ret,d,"address").replace("www.","")
	else:
		ret = "zzz_"
	ret = addField(ret,d,"loginName")
	ret = ret.upper()
	return ret

class Session:

	def __init__(self):
		self.clearSession()

	def clearSession(self):
		self._url = None
		self._user = None
		self._password = None
		self._encryptedPrivateKey = None
		self._authToken = None
		self.client = None
		self._privKey = None
		self._secrets = None
		self._passwords = []
		self._passwordsModCounter = 0
		self._lock = threading.Lock()
		self._categories = {}

class PasswordModel(QAbstractListModel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self._modCounter = 0
		self._data = []

	def rowCount(self,parent):
		return len(self._getdata())

	def data(self,index,role):
		return self._getdata()[index.row()]

	def _getdata(self):
		with Midtier.session._lock:
			if self._modCounter < Midtier.session._passwordsModCounter:
				print("Refreshing model from "+str(self._modCounter)+" to "+str(Midtier.session._passwordsModCounter))
				self._modCounter = Midtier.session._passwordsModCounter
				self._data = sorted(Midtier.session._passwords,key=lambda x:makeSortString(x))
		return self._data

class MyProxyModel(QSortFilterProxyModel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSourceModel(PasswordModel(parent))
		self.setDynamicSortFilter(True)


	def lessThan(self,mileft,miright):
		left = sourceModel().data(mileft)
		right = sourceModel().data(miright)

		leftstr = ""
		rightstr = ""

		leftstr = addField("",left,"website")
		leftstr = addField(leftstr,left,"loginName")

		rightstr = addField("",right,"website")
		rightstr = addField(rightstr,right,"loginName")

		print("comparing "+leftstr.upper() + " with " + rightstr.upper())

		return leftstr.upper() < rightstr.upper()


class Midtier(QObject):


	error = pyqtSignal(str,arguments=["error"])
	sigMessage = pyqtSignal(str,name="message",arguments=["message"])
	sigDownloadKey = pyqtSignal(str,name="downloadKey",arguments=["encryptedPrivateKey"])
	sigDownloadSecrets = pyqtSignal(name="downloadSecrets")
	sigDecryptedSecret = pyqtSignal(dict,name="decryptedSecret")

	def __init__(self, parent=None):
		super().__init__(parent)
		self.helper = client.ClientHelper()
		self.crypto = crypto.Crypto()
		self.model = PasswordModel(self)

	@pyqtProperty('QString')
	def url(self):
		return Midtier.session._url

	@url.setter
	def url(self, url):
		Midtier.session._url = url


	@pyqtProperty('QString')
	def user(self):
		return Midtier.session._user

	@user.setter
	def user(self, user):
		Midtier.session._user = user

	@pyqtProperty('QString')
	def password(self):
		return Midtier.session._password

	@password.setter
	def password(self, password):
		Midtier.session._password = password

	@pyqtProperty('QString')
	def authToken(self):
		return Midtier.session._authToken

	@authToken.setter
	def authToken(self, authToken):
		Midtier.session._authToken = authToken

	@pyqtProperty('QString')
	def encryptedPrivateKey(self):
		return Midtier.session._encryptedPrivateKey

	@encryptedPrivateKey.setter
	def encryptedPrivateKey(self, encryptedPrivateKey):
		Midtier.session._encryptedPrivateKey = encryptedPrivateKey

	@pyqtSlot()
	def clearSession(self):
		Midtier.session = Session()
		self.sigMessage.emit("")

	@pyqtSlot()
	def getSecrets(self):
		threading.Thread(target=(lambda: self._getSecrets())).start()

	def _getSecrets(self):
		try:
			Midtier.session.client = client.Client(client.ClientRestInterface(Midtier.session._url))
			if self._login():
				self.sigMessage.emit("Generating token")
				Midtier.session._authToken = self.helper.generateToken(Midtier.session._privKey)
				Midtier.session.client.login(Midtier.session._user,Midtier.session._authToken)
				self.sigMessage.emit("Downloading secrets")
				Midtier.session._secrets = Midtier.session.client.getSecretsForUser(Midtier.session._user)
				self.sigDownloadSecrets.emit()
		except Exception as e:
			traceback.print_exc()
			self.sigMessage.emit("")
			self.error.emit(str(e))

	@pyqtSlot()
	def decryptSecrets(self):
		threading.Thread(target=(lambda: self._decryptSecrets())).start()

	def _decryptSecrets(self):
		self.sigMessage.emit("Decrypting secrets")
		numSecrets = len(Midtier.session._secrets)
		count = 0
		user = Midtier.session._user
		privKey = Midtier.session._privKey
		failed = 0
		for key in Midtier.session._secrets.keys():
			count = count + 1
			self.sigMessage.emit("Decrypting secret "+str(count+1)+"/"+str(numSecrets))
			try:
				esecret = Midtier.session._secrets[key]
				#print("key="+str(esecret))

				if "users" in esecret and user in esecret["users"]:
					encryptedKey = self.crypto.decode(esecret["users"][user]["encryptedKey"])
				encryptedSecret = esecret["encryptedSecret"]
				origKey = self.crypto.decryptRSA(privKey,encryptedKey)
				origSecretText = self.crypto.decrypt(origKey,encryptedSecret)
				origSecret = json.loads(origSecretText.decode('utf-8'))
				origSecret["sid"]=key
				if "type" in origSecret:
					if origSecret["type"]=="password":
						with Midtier.session._lock:
							self.updatePasswordCategoryInfo(origSecret)
							Midtier.session._passwords.append(origSecret)
							Midtier.session._passwordsModCounter += 1
					elif origSecret["type"]=="passwordCategories":
						print(json.dumps(origSecret,indent=2))
						if "categories" in origSecret:
							with Midtier.session._lock:
								Midtier.session._categories = origSecret["categories"]
								for password in Midtier.session._passwords:
									self.updatePasswordCategoryInfo(password)
				else:
					print(json.dumps(origSecret,indent=2))
				self.sigDecryptedSecret.emit(origSecret)
			except:
				failed = failed + 1
				traceback.print_exc()

		if failed == 1:
			self.sigMessage.emit("Failed to deccrypt one secret")
		elif failed > 1:
			self.sigMessage.emit("Failed to deccrypt "+str(failed)+" secrets")
		else:
			self.sigMessage.emit("")

	def updatePasswordCategoryInfo(self,password):
		password["categoryLabel"]="Unknown"
		password["categoryBackground"]="Transparent"
		password["categoryForeground"]="Transparent"

		if "category" in password and password["category"] in Midtier.session._categories:
			catInfo = Midtier.session._categories[password["category"]]
			password["categoryBackground"]='#'+catInfo["backgroundColor"].upper()
			password["categoryLabel"]=catInfo["label"]

			# http://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
			# Counting the perceptive luminance - human eye favors green color...
			bg = password["categoryBackground"]
			r = 0.299 *int(bg[1:3],16)
			g = 0.587 *int(bg[3:5],16)
			b = 0.114 *int(bg[5:8],16)
			a = 1.0 - ( ( r + g + b ) / 255.0 )
			if a < 0.5:
				password["categoryForeground"] = "#000000"
			else:
				password["categoryForeground"] = "#FFFFFF"
			



	@pyqtSlot()
	def downloadPrivateKey(self):
		threading.Thread(target=(lambda: self._downloadPrivateKey())).start()

	def _downloadPrivateKey(self):
		try:
			self.sigMessage.emit("Logging in with password")
			Midtier.session.client = client.Client(client.ClientRestInterface(Midtier.session._url))
			Midtier.session.client.login(Midtier.session._user,Midtier.session._password)
			Midtier.session._encryptedPrivateKey = Midtier.session.client.getUserPrivateKey(Midtier.session._user,Midtier.session._password).decode('ascii')
			self.sigDownloadKey.emit(Midtier.session._encryptedPrivateKey)
		except Exception as e:
			traceback.print_exc()
			self.clearSession()
			self.error.emit(str(e))

	@pyqtSlot()
	def login(self):
		threading.Thread(target=(lambda: self._login())).start()

	def _login(self):
		try:
			Midtier.session._privKey = self.helper.decryptPrivateKey(Midtier.session._user,Midtier.session._encryptedPrivateKey,Midtier.session._password)
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
	basepath = os.path.abspath(basepath)

	qmlRegisterType(Midtier, 'CPMQ', 1, 0, 'Midtier')
	qmlRegisterType(MyProxyModel, 'CPMQ', 1, 0, 'PasswordModel')
	Midtier.session = Session()

	engine = QQmlApplicationEngine()
	rootContext = engine.rootContext()
	rootContext.setContextProperty("qmlBasePath",basepath+'/ui')

	print("qmlBasePath="+basepath)
	qmlFile = basepath+'/ui/main.qml'
	print("Loading "+qmlFile)
	engine.load(QUrl(qmlFile))

	sys.exit(app.exec_())

