# coding: utf8

import	tornado.web
from datetime import datetime
import logging

from gps import spherical_distance

class BaseHandler(tornado.web.RequestHandler):
	"""RequestHandler Base"""
	def get_current_user(self):
		return self.get_secure_cookie("uid")
	def get_sessionid(self):
		return self.get_secure_cookie('sessionid')

	def handle_filename(self , uid , filename , loc): # loc = "img/" or "audio/"
		format = filename.rsplit('.' , 1)
		s = datetime.now()
		try:
			path = 'data/'+ loc + uid + "%d%d%d%d."%(s.hour,s.minute,s.second,s.microsecond) + format[1]
		except:
			path = 'data/' + loc + uid + "%d%d%d%d"%(s.hour,s.minute,s.second,s.microsecond)
		# unicode error
		return path.encode('utf8')

	@property
	def db(self):
		return self.application.db

"""登陆界面
API:	http://domain:port/login
POST:	{'name':'xxx','password':'xxx'}
HEADER:  {  "Content-type":"application/json",
			"Accept":"text/plain",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" }
RESPONSE:{  "error":0}
error:  0 for success
		1 for invalid password
		2 for password or username can't be empty
"""
class LoginHandler(BaseHandler):
	def post(self):
		try:
			decode_body = json.loads(self.request.body)
			username = decode_body['name']
			password = decode_body['password']
		except:
			self.write({'error':2})
			return
		if (not username) or (not password):
			# password or username can't be empty
			self.write({'error':2})
			return

		uid = self.checkUser(username , password)
		if uid != -1:
			self.set_secure_cookie("uid", str(uid), 1)
			self.write({'error':0})
		else:
			# invalid password
			self.write({'error':1})

	def checkUser(self , username , password):
		info = self.db.query('SELECT PASSWORD,UID FROM USER WHERE USERNAME = \'%s\'' % (username))
		if info:
			t_pass = info[0]['PASSWORD']
			t_uid = info[0]['UID']
			if t_pass == password:
				return t_uid
			else: return -1
		else: return -1

"""用户注册
API:	http://domain:port/login
POST   {'name':'xxx','password':'xxx'}
HEADER {"Content-type":"application/json",
		"Accept":"text/plain",
		"Connection": "Keep-Alive", 
		"Cache-Control": "no-cache" }
RESPONSE:{  "error":}
error:  0 for success
		1 for username exist
		2 for password or username can't be empty
		3 for FACEPP API Error
		4 for SQL Error
"""
class RegisterHandler(BaseHandler):
	def post(self):
		try:
			decode_body = json.loads(self.request.body)
			username = decode_body['name']
			password = decode_body['password']
		except:
			self.write({'error':2})
			return
		if (not username) or (not password):
			# password or username can't be empty
			self.write({'error':2})
			return

		try:
			res = self.insertInfo(username , password)
		except:
			self.wirte({'error':4})
			return

		if res == -1:
			# user exist
			self.write({'error':1})
		else:
			# register success
			self.set_secure_cookie("uid", str(res), 1)
			# try:
			#	 person_create = api.person.create(person_id = res , group_name = u'Students')
			# except APIError,e:
			#	 self.write({'error':3 , 'info':json.loads(e.body)['error']})
			#	 return
			self.write({'error':0})

	def insertInfo(self , username , password):
		find = self.db.query('SELECT UID FROM USER WHERE USERNAME = \'%s\'' % (username))
		if find:
			return -1
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.db.execute('INSERT INTO USER(USERNAME,PASSWORD,CREATETIME) VALUES(\'%s\',\'%s\',\'%s\');' % 
			(username , password ,now))
		info = self.db.query('SELECT UID FROM USER WHERE USERNAME = \'%s\'' % (username))
		uid = info[0]['UID']
		return uid


