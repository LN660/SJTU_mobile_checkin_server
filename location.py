# coding=gbk
# $File: location.py
# $Date: Fri Mar 2 1:09:27 2013 +0800
# $Author: ronnie.alonso@gmail.com
#
#      0. You just DO WHAT THE FUCK YOU WANT TO. 
import tornado.web
import tornado.httpclient
import os,json,string
import logging
from datetime import *
from basic import BaseHandler


"""LocationRegisterHandler API
API http://localhost:8000/registerlocation
POST:   http://localhost:8000/registerlocation
	{
		'locid':1 //1 for SJTU
	}
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie}
"""
class LocationRegisterHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			self.write({"error":1})
			return
		decode_body = json.loads(self.request.body)
		locid = decode_body['locid']
		uid = self.current_user

		self.db.execute('UPDATE USER SET LOCID = %d WHERE UID = %s;' % (locid , uid))
		self.write({'error':0})