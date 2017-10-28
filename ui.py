#!/usr/bin/python3

import sys, os
import signal

if getattr(sys, 'frozen', False):
	print(sys._MEIPASS)

from PyQt5.QtCore import pyqtProperty, QObject, QUrl, pyqtSlot, pyqtSignal
from PyQt5.QtCore import QAbstractListModel, QSortFilterProxyModel, QTimer
from PyQt5.QtGui import QGuiApplication, QClipboard, QIcon
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine, QQmlApplicationEngine
import threading
import client
import traceback
import crypto
import json
import time
import datetime

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

def makeSearchString(d):
	ret = ""
	if "website" in d:
		ret = " " + addField(ret,d,"website").replace("www.","")
	elif "address" in d:
		ret = " " + addField(ret,d,"address").replace("www.","")
	ret = " " + addField(ret,d,"loginName")
	ret = " " + addField(ret,d,"notes")
	return ret.lower()


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
		self._categoriesList = []
		self._users = {}

class PasswordInfo(QObject):
	sigChanged = pyqtSignal(name="passwordInfoChanged")
	def __init__(self, parent=None):
		super().__init__(parent)
		self._sid = None

	@pyqtProperty('QString',notify=sigChanged)
	def sid(self):
		return self._sid

	@sid.setter
	def sid(self, sid):
		print("Setting sid="+sid)
		self._sid = sid
		for password in Midtier.session._passwords:
			if sid == password["sid"]:
				self._password = password
				print("Emitting changed signal")
				self.sigChanged.emit()

	@pyqtProperty('QString',notify=sigChanged)
	def categoryLabel(self):
		try:
			return self._password["categoryLabel"]
		except:
			return "Unknown"

	@pyqtProperty('QString',notify=sigChanged)
	def categoryBackground(self):
		try:
			return self._password["categoryBackground"]
		except:
			return "#000000"

	@pyqtProperty('QString',notify=sigChanged)
	def categoryForeground(self):
		try:
			return self._password["categoryForeground"]
		except:
			return "#FFFFFF"

	@pyqtProperty('QString',notify=sigChanged)
	def website(self):
		try:
			return self._password["website"]
		except:
			return ""

	@pyqtProperty('QString',notify=sigChanged)
	def address(self):
		try:
			return self._password["address"]
		except:
			return self.website()

	@pyqtProperty(bool,notify=sigChanged)
	def passwordHasNumbers(self):
		try:
			return any(char.isdigit() for char in self._password["password"])
		except:
			return False

	@pyqtProperty(bool,notify=sigChanged)
	def passwordHasUpper(self):
		try:
			return any(char.isupper() for char in self._password["password"])
		except:
			return False

	@pyqtProperty(bool,notify=sigChanged)
	def passwordHasLower(self):
		try:
			return any(char.islower() for char in self._password["password"])
		except:
			return False

	@pyqtProperty(bool,notify=sigChanged)
	def passwordHasSpecial(self):
		try:
			return any(not char.isalnum() for char in self._password["password"])
		except:
			return False

	@pyqtProperty('QString',notify=sigChanged)
	def password(self):
		try:
			return self._password["password"]
		except:
			return ""

	@pyqtProperty('QString',notify=sigChanged)
	def passwordStars(self):
		try:
			return ( "*" * 8 ) + "{" + str(len(self._password["password"])) + "}"
		except:
			return ""

	@pyqtProperty('QString',notify=sigChanged)
	def loginName(self):
		try:
			return self._password["loginName"]
		except:
			return ""

	@pyqtProperty('QString',notify=sigChanged)
	def dateChanged(self):
		try:
			return self._password["dateChanged"]
		except:
			return ""

	@pyqtProperty('QString',notify=sigChanged)
	def notes(self):
		try:
			return self._password["notes"]
		except:
			return ""

class PasswordModel(QAbstractListModel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self._modCounter = 0
		self._data = []

	def rowCount(self,parent):
		return len(self._getdata())

	def data(self,index,role):
		ret = self._getdata()[index.row()]
		if role==1:
			ret = makeSearchString(ret)
		#print("data("+str(index.row())+","+str(role)+")="+str(ret))
		return ret

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
		self.setFilterRegExp("")
		self.setFilterRole(1)

	@pyqtProperty('QString')
	def filterString(self):
		return self.filterRegExp().pattern()

	@filterString.setter
	def filterString(self, f):
		self.setFilterRegExp(f.lower())

class MyCategoryProxyModel(QSortFilterProxyModel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSourceModel(CategoryModel(parent))
		self.setDynamicSortFilter(True)


class Midtier(QObject):


	error = pyqtSignal(str,arguments=["error"])
	sigMessage = pyqtSignal(str,name="message",arguments=["message"])
	sigDownloadKey = pyqtSignal(str,name="downloadKey",arguments=["encryptedPrivateKey"])
	sigDownloadSecrets = pyqtSignal(name="downloadSecrets")
	sigDecryptedSecret = pyqtSignal(dict,name="decryptedSecret")
	sigNewPassword = pyqtSignal(str,name="newPassword",arguments=["sid"])
	sigUsersListed = pyqtSignal(name="usersListed")

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

	@pyqtProperty('QVariant')
	def categories(self):
		return sorted(Midtier.session._categoriesList,key=lambda x:x["text"])

	@pyqtProperty('QVariant')
	def otherUsers(self):
		other = []
		for username in Midtier.session._users.keys():
			if username != Midtier.session._user:
				other.append({'username':username,'name':Midtier.session._users[username]['displayName']})
		print("userUsers="+str(other))
		return other

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
				self.sigMessage.emit("Finished downloading secrets")
				self.sigDownloadSecrets.emit()
		except Exception as e:
			traceback.print_exc()
			self.sigMessage.emit("")
			self.error.emit(str(e))

	@pyqtSlot(str)
	def addPassword(self,value):
		print("addPassword()")
		threading.Thread(target=(lambda: self._addPassword(value))).start()

	def _addPassword(self,value):
		try:
			obj = json.loads(value)
			print(str(obj))
			user = Midtier.session._user
			self.sigMessage.emit("Downloading public key")
			self._yield()
			pubKey = Midtier.session.client.getUserPublicKey(user)
			self.sigMessage.emit("Generating random keys")
			self._yield()
			aesKey = self.crypto.generateRandomKey()
			hmacKey = self.crypto.generateRandomKey()
			bothKeys = aesKey + hmacKey
			rnd = self.crypto.encode(self.crypto.generateRandomKey())
			secretValue={}
			secretValue["random"]=rnd
			secretValue["website"]=obj["website"]
			secretValue["address"]=obj["url"]
			secretValue["loginName"]=obj["username"]
			secretValue["password"]=obj["password"]
			secretValue["type"]="password"
			secretValue["category"]="0"
			secretValue["userCategory"]={}
			for cat in Midtier.session._categoriesList:
				try:
					if cat["text"]==obj["category"]:
						secretValue["category"]=cat["id"]
						secretValue["userCategory"][user]=cat["id"]
				except:
					pass
			secretValue["notes"]=""
			secretValue["dateChanges"]=datetime.date.today().isoformat()
			self.sigMessage.emit("Encrypting password")
			self._yield()
			encryptedSecret = self.crypto.encrypt(aesKey,json.dumps(secretValue))
			encryptedKey = self.crypto.encryptRSA(pubKey,bothKeys)
			hmac = str(self.crypto.createHmac(hmacKey,encryptedSecret))
			eek = str(self.crypto.encode(encryptedKey))
			self.sigMessage.emit("Uploading encrypted password")
			self._yield()
			secret = Midtier.session.client.addSecret(user,"1",eek,encryptedSecret.decode("utf-8") ,hmac)
			sid = secret["sid"]
			secretValue["sid"] = sid
			print("Secret ID: "+str(sid))

			self.sigMessage.emit("Successfully uploaded encrypted password")
			with Midtier.session._lock:
				self.updatePasswordCategoryInfo(secretValue)
				Midtier.session._passwords.append(secretValue)
				Midtier.session._passwordsModCounter += 1

			self.sigNewPassword.emit(sid)
		except Exception as e:
			traceback.print_exc()
			self.sigMessage.emit("")
			self.error.emit(str(e))

	@pyqtSlot(str,str)
	def shareSecret(self,sid,username):
		threading.Thread(target=(lambda: self._shareSecret(sid,username))).start()

	def _shareSecret(self,sid,username):
		try:
			client = Midtier.session.client
			self.sigMessage.emit("Downloading "+username+"'s public key")
			pubKey = client.getUserPublicKey(username)
			privKey = Midtier.session._privKey
			self.sigMessage.emit("Downloading latest secret")
			secretEntry = client.getSecret(sid)
			encryptedKey = self.crypto.decode(secretEntry["users"][Midtier.session._user]["encryptedKey"])
			self.sigMessage.emit("Decrypting the AES key")
			origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
			origKey = origKeyPair[0:32]
			hmacKey = origKeyPair[32:]
			self.sigMessage.emit("Encrypting the AES key for "+username)
			encryptedKey2 = self.crypto.encryptRSA(pubKey,origKey)
			self.sigMessage.emit("Sharing the secret "+username)
			client.shareSecret(sid,username,self.crypto.encode(encryptedKey2))
			self.sigMessage.emit("Shared the secret "+username)

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
				origKeyPair = self.crypto.decryptRSA(privKey,encryptedKey)
				origKey = origKeyPair[0:32]
				origSecretText = self.crypto.decrypt(origKey,encryptedSecret)
				origSecret = json.loads(origSecretText.decode('utf-8'))
				origSecret["sid"]=key
				if "userCategory" in origSecret and user in origSecret["userCategory"]:
					origSecret=origSecret["userCategory"][user]

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
								Midtier.session._categoriesList = []
								for catId in Midtier.session._categories.keys():
									catObj = {"id": catId}
									catObj["text"] = Midtier.session._categories[catId]["label"]
									Midtier.session._categoriesList.append(catObj)
								for password in Midtier.session._passwords:
									self.updatePasswordCategoryInfo(password)
				else:
					print(json.dumps(origSecret,indent=2))
				self.sigDecryptedSecret.emit(origSecret)
				if count % 10 == 0:
					self._yield()
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

		catInfo=None
		if "category" in password and password["category"] in Midtier.session._categories:
			catInfo = Midtier.session._categories[password["category"]]


		if catInfo != None:
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
	def listUsers(self):
		print("listUsers()")
		threading.Thread(target=(lambda: self._listUsers())).start()

	def _listUsers(self):
		try:
			Midtier.session._users=Midtier.session.client.listUsers()
			print("users="+str(Midtier.session._users))
			self.sigUsersListed.emit()
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

	@pyqtSlot(str)
	def updateClipboard(self,value):
		QGuiApplication.clipboard().setText(value)
		QGuiApplication.clipboard().setText(value,QClipboard.Selection)
		self.sigMessage.emit("Copied to clipboard")

	def _yield(self):
		# Release the GIL
		time.sleep(0.1)

def sigint_handler(*args):
	sys.stderr.write('\r')
	QGuiApplication.quit()

if __name__ == '__main__':
	signal.signal(signal.SIGINT, sigint_handler)
	app = QGuiApplication(sys.argv)

	# Get the interpreter to run so that the signal handler will actually
	# execute when the user hits control-c
	# https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
	timer = QTimer()
	timer.start(500)  # You may change this if you wish.
	timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

	# Get the correct basepath in all scenarios
	if getattr(sys, 'frozen', False):
		basepath = sys._MEIPASS
	else:
		basepath = os.path.dirname(os.path.realpath(__file__))
	if len(basepath)==0:
		basepath="."
	basepath = os.path.abspath(basepath).replace('\\','/')
	if basepath.find(':')>0:
		basepath = 'file:///'+basepath

	qmlRegisterType(Midtier, 'CPMQ', 1, 0, 'Midtier')
	qmlRegisterType(MyProxyModel, 'CPMQ', 1, 0, 'PasswordModel')
	qmlRegisterType(PasswordInfo, 'CPMQ', 1, 0, 'PasswordInfo')
	Midtier.session = Session()
	#if os.name!='nt':
	app.setWindowIcon(QIcon(basepath + '/ui/icon.png'))
	print("Using icon: "+basepath + '/ui/icon.png')
	#else:
		#app.setWindowIcon(QIcon(basepath + '/ui/icon.ico'))
		#print("Using icon: "+basepath + '/ui/icon.ico')

	engine = QQmlApplicationEngine()

	# for the pyinstaller-extracted qml system imports
	engine.addImportPath(basepath+'/_qml')
	rootContext = engine.rootContext()
	rootContext.setContextProperty("qmlBasePath",basepath+'/ui')

	print("QML Import dirs: "+str(engine.importPathList()))

	qmlFile = basepath+'/ui/main.qml'
	print("Loading "+qmlFile)
	engine.load(QUrl(qmlFile))

	sys.exit(app.exec_())

