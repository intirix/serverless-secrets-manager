#!/usr/bin/python

import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import logging
import json

import system
import db
import client
import server

PORT = 8000

def matches(path,components):
	parts = path.split('?')[0].split('/')

	if len(parts) == len(components)+2:
		for i in range(0,len(components)):
			if components[i]!=None and components[i]!=parts[i+2]:
				return False

		return True


	return False

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def _send_response(self,code):
		self.send_response(code)
		self.send_header("Connection", "close")
		self.end_headers()

	def do_GET(self):
		log = logging.getLogger("httpHandler")
		ctx = server.Context("admin")

		resp = None
		parts = self.path.split('?')[0].split('/')
		iface = self.server.serverIface

		if matches(self.path,["v1","users"]):
			resp = iface.listUsers(ctx)
		elif matches(self.path,["v1","users",None]):
			resp = iface.getUser(ctx,parts[4])

		if resp == None:
			self._send_response(404)
		else:
			self.send_response(200)
			self.send_header("Connection", "close")
			self.send_header("Content-Type","application/json")
			self.end_headers()
			self.wfile.write(json.dumps(resp,indent=2))

	def do_POST(self):
		log = logging.getLogger("httpHandler")
		ctx = server.Context("admin")

		content_len = int(self.headers.getheader('content-length', 0))
		post_body = self.rfile.read(content_len)
		parts = self.path.split('?')[0].split('/')
		iface = self.server.serverIface

		if matches(self.path,["v1","users",None]):
			user = parts[4]
			iface.addUser(ctx,user,post_body)
			self._send_response(201)
		else:
			log.warn("Unknown path: "+self.path, "parts="+str(parts))


if __name__ == '__main__':
	FORMAT = "%(asctime)-15s %(message)s"
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('')


	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class(("", PORT), MyHandler)

	httpd.system = system.System()
	httpd.system.setDB(db.JsonDB('./local'))
	httpd.client = client.Client(client.ClientSystemInterface(httpd.system))
	httpd.serverIface = server.Server(httpd.system)


	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()

