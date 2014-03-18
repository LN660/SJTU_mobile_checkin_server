# coding: utf8

import	tornado.web

class BaseHandler(tornado.web.RequestHandler):
	"""RequestHandler Base"""
	def get_current_user(self):
		return self.get_secure_cookie("uid")
	def get_sessionid(self):
		return self.get_secure_cookie('sessionid')
	@property
	def db(self):
		return self.application.db


"""check user status
API:	
GET: http://domain:port/checkstatus
HEADER:  {  "Content-type":"application/json",
			"Accept":"text/plain",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache",
			"Cookie": client_cookie }
RESPONSE:{  "error":0}
error:  
	-1 for need to register
	0 for success
	1 for not login
	2 for SQL error
"""
class CheckStatusHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.write({"error":2})
			return
		uid = self.current_user
		try:
			info = self.db.query_all('SELECT IMAGESAMPLE,AUDIOENGINE,LOCID FROM USER WHERE UID = %s;' % (uid))
			res = info[0]
			if(res['IMAGESAMPLE'] != None and res['AUDIOENGINE']!=None and res['LOCID']!=None):
				res['error'] = 0
			else:
				res['error'] = -1
			self.write(res)
			return
		except:
			self.write({"error":2})
			return 


