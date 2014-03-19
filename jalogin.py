# coding: utf8

import logging
import urllib
import string
import random
from datetime import datetime

import settings
from basic import BaseHandler
import jaccount

"""用户JACCOUNT LOGIN
API:	http://localhost:port/jalogin
RESPONSE:{  "error":0}
0:success
1:hacking attempt
3:face++ person_create error
"""
class JaLoginHandler(BaseHandler):
	def get(self):
		if not self.get_arguments('jatkt'):
			"""redirect to jaccount login page"""
			uaBaseURL="http://jaccount.sjtu.edu.cn/jaccount/"
			returl = 'http://'+settings.HOST+':'+str(settings.PORT)+'/jalogin'
			iv = string.join(random.sample('1234567890abcdef',8),'')
			self.set_secure_cookie('iv' , iv , None)
			redirectURL =  uaBaseURL + "jalogin?sid="+settings.SITE_ID+"&returl="+jaccount.encrypt(returl,iv)+"&se="+jaccount.encrypt(iv,iv)
			self.redirect(redirectURL)
		else:
			"""read the return info from jaccount login page"""
			try:
				if len(self.get_argument('jatkt')) == 0:
					raise tornado.web.HTTPError(404)
			except TypeError:
				raise tornado.web.HTTPError(404)
			iv = self.get_secure_cookie('iv')
			jatkt = self.get_argument('jatkt')
			data = jaccount.decrypt(jatkt,iv)
			data = jaccount.find(data,ur'ja[\s\S]*')

			ProfileData = jaccount.parse_data(data)

			if ProfileData['ja3rdpartySessionID'] != iv:
				self.add_header('error',1)
				return

			self._update_user(ProfileData)
			self.set_secure_cookie('uid' , ProfileData['id'] , None)
			
			chiname = urllib.quote(ProfileData['chinesename'])
			# logging.info(chiname.__class__)
			self.set_cookie('chiname' , chiname , None)
			# logging.info(self.cookies)
			self.add_header('error',0)

	def _update_user(self , profile):
		uid = profile['id']
		info = self.db.query_all('SELECT UID,LOCID,DEPARTMENT,CHINAME FROM USER WHERE UID = %s;' % (uid))
		logging.debug(info)
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		chiname = profile['chinesename']
		username = profile['uid']
		dept = profile['dept']
		if not info:
			sql = "INSERT INTO USER(UID,USERNAME,CHINAME,DEPARTMENT,LOCID,CREATETIME)\
				VALUES(%s,\'%s\',\'%s\',\'%s\',1,\'%s\')" % (uid,username,chiname,dept,now)
			logging.debug(sql)
			res = self.db.execute(sql)
			
			# FACE++
			try:
				url = faceppKit.CreatePerson(uid,u'Students')
				response = urllib2.urlopen(url)
				person_create = response.read()
			except urllib2.URLError, e:
				if not hasattr(e, "code"):
					raise
				self.add_header('error',3)
				self.add_header('info',json.loads(e.read())['error'])
				# self.write({'error':3 , 'info':json.loads(e.read())['error']})
		else:
			info=info[0]
			if (not info['LOCID']) or (not info['DEPARTMENT']) or(not info['CHINAME']):
				sql="UPDATE USER SET USERNAME=\'%s\',LOCID=1,DEPARTMENT=\'%s\',CHINAME=\'%s\' WHERE UID=%s;" %\
					(username,dept,chiname,uid)
				res=self.db.execute(sql)

"""用户JACCOUNT LOGOUT
API:	http://localhost:port/jalogout
RESPONSE:{  "error":0}
"""			
class JaLogoutHandler(BaseHandler):
	def get(self):
		if self.current_user:
			uaBaseURL="http://jaccount.sjtu.edu.cn/jaccount/"
			returl = 'http://'+domain+':'+str(port)
			iv = self.get_secure_cookie('iv')
			redirectURL =  uaBaseURL + "ulogout?sid="+siteID+"&returl="+encrypt(returl,iv)
			self.clear_all_cookies()
			self.redirect(redirectURL)
			return
		else:
			self.write({"error":1})
			return









