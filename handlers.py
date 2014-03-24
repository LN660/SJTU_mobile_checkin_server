# coding: utf8

'''
Handlers of Http Requests

DetectCreateHandler,
DetectResultHandler,
CheckStatusHandler,
JaLoginHandler,
JaLogoutHandler,
FaceppHandler,
FaceRegisterHandler,
SpeechTrainHandler,
SpeechDetectHandler,
UploadLocationHandler
'''

import os
import json
import string
import logging
import string
import random
import urllib
import urllib2
import json

from datetime import datetime

import	tornado.web
import tornado.httpclient

import faceppKit
import jaccount
import sv
from gps import spherical_distance

import settings


class BaseHandler(tornado.web.RequestHandler):
	"""RequestHandler Base"""
	def get_current_user(self):
		return self.get_secure_cookie("uid")
	def get_sessionid(self):
		return self.get_secure_cookie('sessionid')

	#FIXME
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
			self.write(data)
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
		self.write('\n')
		self.write(profile)
		chiname = profile['chinesename']
		username = profile['uid']
		dept = profile['dept']
		if not info:
			# FACE++
			try:
				logging.debug('add to facc++')
				url = faceppKit.CreatePerson(uid,u'Students')
				logging.debug(url)
				response = urllib2.urlopen(url)
				person_create = response.read()
				self.write(person_create)
			except urllib2.URLError, e:
				if not hasattr(e, "code"):
					raise
				self.add_header('error',3)
				self.add_header('info',json.loads(e.read())['error'])
				logging.debug(e)
				self.write({'error':3 , 'info':e.read()})
			sql = "INSERT INTO USER(UID,USERNAME,CHINAME,DEPARTMENT,LOCID,CREATETIME)\
				VALUES(%s,\'%s\',\'%s\',\'%s\',1,\'%s\')" % (uid,username,chiname,dept,now)
			res = self.db.execute(sql)
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

"""speech train API
API http://localhost:8000/svtrain
POST:	http://localhost:8000/svtrain
		{"voice1":voice
		"voice2":voice
		"voice3":voice
		}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":}
error:	0 for success
		1 for not login
		2:newSVEngine error
		3:speaker adapt basic failed
		-1 for failure in train
"""
class SpeechTrainHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			logging.info("error:1;info:not login")
			self.write({"error":1})
			return

		uid = self.current_user
		# upload file
		uploadfile = self.request.files.get('voice1')
		file1 = self.handle_filename(uid , uploadfile[0]['filename'] , 'audio/')
		audio1 = file1.split('/')[2]
		picfile = open(file1,"wb")
		picfile.write(uploadfile[0]['body'])
		picfile.close()

		uploadfile = self.request.files.get('voice2')
		file2 = self.handle_filename(uid , uploadfile[0]['filename'] , 'audio/')
		audio2 = file2.split('/')[2]
		picfile = open(file2,"wb")
		picfile.write(uploadfile[0]['body'])
		picfile.close()

		uploadfile = self.request.files.get('voice3')
		file3 = self.handle_filename(uid , uploadfile[0]['filename'] , 'audio/')
		audio3 = file3.split('/')[2]
		picfile = open(file3,"wb")
		picfile.write(uploadfile[0]['body'])
		picfile.close()

		ret = sv.train(uid, file1, file2, file3)

		logging.debug(ret)
		if ret: return

		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.db.execute('UPDATE USER SET AUDIOENGINE = \'%s.bin\' WHERE UID = %s;' % (uid , uid))
		self.db.execute('INSERT INTO AUDIO(OWNER,AUDIOHASH,CREATETIME) VALUES(\'%s\',\'%s\',\'%s\');' % (uid , audio1 ,now))
		self.db.execute('INSERT INTO AUDIO(OWNER,AUDIOHASH,CREATETIME) VALUES(\'%s\',\'%s\',\'%s\');' % (uid , audio2 ,now))
		self.db.execute('INSERT INTO AUDIO(OWNER,AUDIOHASH,CREATETIME) VALUES(\'%s\',\'%s\',\'%s\');' % (uid , audio3 ,now))
		self.write({"error": 0})

"""face regeister API
API http://localhost:8000/faceregister
POST:	http://localhost:8000/faceregister
		{"pic":picture_file}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":
			"faceid":}

error:	0 for success
		1 for face unrecogized
		2 for not login
		3 for face_add error
		4 for already register
Cookie should contain the response set-cookie from the sever when user login(important!)
the client_cookie can get from the server's response
example:	HTTP Request HEADER		
			{"Content-type":"image/jpeg",
			"Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
"""
class FaceRegisterHandler(BaseHandler):
	@tornado.web.asynchronous
	def handle_request(self,response):
		if response.error:
			logging.info(response.error)
			self.write({'error':1})
			self.finish()
			return
		else:
			face_detect = json.loads(response.body)
			# print face_detect
			if face_detect['face'] == []:
				logging.info('error:5;info:No face is detected')
				self.write({'error':5,'info':'No face is detected'})
				self.finish()
				return
			else:
				self.tmp_face1 = face_detect['face'][0]['face_id']

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_request=faceppKit.AddFace(self.uid,self.tmp_face1)
		http_client.fetch(http_request, callback=self.handle_request2)

	def handle_request2(self,response):
		add_face=json.loads(response.body)
		# print add_face

		if (not add_face.has_key("success")):
			self.write({"error":3})

		elif (add_face["success"] == True):
			self.db.execute("UPDATE USER SET IMAGESAMPLE = \'%s\' WHERE UID = %s" % (self.tmp_face1 , self.uid))
			self.write({"error":0,"faceid":self.tmp_face1})

		else:
			self.write({"error":3})
			
		self.finish()

	@tornado.web.asynchronous
	def post(self):
		if not self.current_user:
			self.write({"error":2})
			self.finish()
			return
		query = self.db.execute("SELECT IMAGESAMPLE FROM USER WHERE UID = %s" % (self.current_user))
		if query:
			self.write({"error":4})
			self.finish()
			return
		self.uid = self.current_user
		uploadfile = self.request.files.get('pic')

		img_binary = uploadfile[0]['body']
		img_name = uploadfile[0]['filename'].encode('utf8')
		tmp_path = self.handle_filename(self.uid , img_name , 'img/')
		picfile = open(tmp_path,"wb")
		picfile.write(img_binary)
		picfile.close()

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_request=faceppKit.FaceDetect(img_binary,img_name)
		http_client.fetch(http_request, callback=self.handle_request)

"""speech detect API
API http://localhost:8000/svdetect
POST:	http://localhost:8000/svdetect
		{"voice":voice}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":}
error:	0 for success
		1 for not login
		2 for not accepted
		4 for user not initialize audio
		5 for no sessionid
		-1 for failure in detect process
"""
class SpeechDetectHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			self.write({"error":1})
			return
		uid = self.current_user
		if (not self.get_sessionid()):
			self.write({"error":5})
			return
		sessionid = int(self.get_sessionid())

		uploadfile = self.request.files.get('voice')
		tmp_path = self.handle_filename(uid , uploadfile[0]['filename'] , 'audio/')
		audio_name = tmp_path.split('/')[2]
		picfile = open(tmp_path,"wb")
		picfile.write(uploadfile[0]['body'])
		picfile.close()

		query = self.db.query("SELECT AUDIOENGINE FROM USER WHERE UID = %s" % (uid))
		if (not query) or (query[0]['AUDIOENGINE'] == None):
			logging.info("error:4;info:no initial audio engine")
			self.write({"error":4})
			return

		ret = sv.detect(uid, tmp_path)
		if ret != -1:
			self.db.execute('UPDATE DETECT SET AUDIOHASH = \'%s\', AUDIODETECT = %f WHERE SESSIONID=%d;' % (audio_name ,ret,sessionid))
			logging.info("error:0;	similarity:	%f" % (ret))
			self.write({"error": 0})
			return
		else:
			logging.info("error:-1;info:failure in detect")
			self.write({"error": -1})
			return

"""face verification API
API http://localhost:8000/faceverify
POST:	http://localhost:8000/faceverify
		{"pic":picture_file}
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error":
			"similarity":}
error:	0 for success
		1 for FACEPP APIError
		2 for not login
		3 for not face
		4 for no sessionid
Cookie should contain the response set-cookie from the sever when user login(important!)
example:	HTTP Request HEADER		
			{"Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache",
			"Cookie": client_cookie }
"""
class FaceppHandler(BaseHandler):
	@tornado.web.asynchronous
	def handle_request(self,response):
		if response.error:
			logging.info(response.error)
			self.write({'error':1})
			self.finish()
			return
		else:
			face_detect = json.loads(response.body)
			if face_detect['face'] == []:
				logging.info('error:3;info:NO FACE')
				self.write({'error':3 , 'info':'NO FACE'})
				self.finish()
				return
			else:
				tmp_face1 = face_detect['face'][0]['face_id']

			info = self.db.query('SELECT IMAGESAMPLE FROM USER WHERE UID = %d' % (string.atoi(self.uid)))
			tmp_face2 = info[0]['IMAGESAMPLE']

			http_client = tornado.httpclient.AsyncHTTPClient()
			http_request=faceppKit.FaceCompare(tmp_face1,tmp_face2)
			http_client.fetch(http_request, callback=self.handle_request2)

	def handle_request2(self,response):
		response=json.loads(response.body)

		if response.has_key("similarity"):
			similarity = float(response["similarity"])
			self.db.execute('UPDATE DETECT SET FACEHASH=\'%s\' , FACEDETECT=%f WHERE SESSIONID=%d;' % (self.filename , similarity , self.sessionid))
			logging.info('error:0;	similarity:	%f' % similarity)
			self.write({"error":0,"similarity":similarity})
		else:
			logging.info('error:3;info:no similarity')
			self.write({"error":1})
			
		self.finish() 

	@tornado.web.asynchronous
	def post(self):
		if not self.current_user:
			logging.info('error:2;info:not login')
			self.write({"error":2})
			self.finish()
			return
		if (not self.get_secure_cookie("sessionid")):
			logging.info('error:4;info:not create')
			self.write({"error":4})
			self.finish()
			return
		self.sessionid = int(self.get_sessionid())
		self.uid = self.current_user

		uploadfile = self.request.files.get('pic')
		img_binary = uploadfile[0]['body']
		img_name = uploadfile[0]['filename'].encode('gbk')
		tmp_path = self.handle_filename(self.uid , img_name , 'img/')
		self.filename = tmp_path.split('/')[2]
		picfile = open(tmp_path,"wb")
		picfile.write(img_binary)
		picfile.close()

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_request=faceppKit.FaceDetect(img_binary,img_name)
		http_client.fetch(http_request, callback=self.handle_request)

"""Upload Location API
API http://localhost:8000/uploadlocation
POST:   http://localhost:8000/uploadlocation
	{
		'latitude':latitude,
		'longitude':longitude
	}
HEADER:  {  "Accept":"application/json",
            "Connection": "Keep-Alive", 
            "Cache-Control": "no-cache" ,
            "Cookie": client_cookie
            }
RESPONSE:{  "error":0}
error:  0 for success
        1 for not login
        2 for no longitude or latitude
        3 for no sessionid
"""
class UploadLocationHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			self.write({"error":1})
			return
		if (not self.get_sessionid()):
			self.write({"error":3})
			return
		sessionid = int(self.get_sessionid())
		try:
			decode_body = json.loads(self.request.body)
			longitude = float(decode_body['longitude'])
			latitude = float(decode_body['latitude'])
		except Exception, e:
			logging.debug(e)
			self.write({'error':2})
			return
		# print latitude,longitude
		self.db.execute('UPDATE DETECT SET LATITUDE=%f , LONGITUDE=%f WHERE SESSIONID = %d;' % 
		(latitude ,longitude , sessionid))
		self.write({'error':0})
		return

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

"""DetectCreate API
API http://domain:port/detectcreate
POST:   http://domain:port/detectcreate
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error": }
error:  0 for success
		1 for SQL error
		2 for not login
return_cookies will have an ||sessionid|| to detect
"""
class DetectCreateHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			self.write({"error":2})
			return
		uid = self.current_user
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		try:
			self.db.execute('INSERT INTO DETECT(OWNER,DETECTTIME) VALUES(\'%s\',\'%s\');' % 
				(uid ,now))
			info = self.db.query('SELECT SESSIONID FROM DETECT WHERE OWNER = \'%s\' AND DETECTTIME = \'%s\'' % 
			  (uid , now))
			sessionid = info[0]['SESSIONID']
		except:
			self.write({"error":1})
			return
		self.set_secure_cookie("sessionid", str(sessionid), 1)
		self.write({"error":0})
		return

"""DetectResult API
API http://domain:port/getdetectresult
POST:   http://domain:port/getdetectresult
HEADER:  {  "Accept":"application/json",
			"Connection": "Keep-Alive", 
			"Cache-Control": "no-cache" ,
			"Cookie": client_cookie}
RESPONSE:{  "error": 0}
error:  0 for success
		1 for fail
		2 for not login
		3 for no sessionid
		4 for empty SQL result
		5 for SQL error
	6 for not enough detect info
"""
class DetectResultHandler(BaseHandler):
	def get(self):
		if (not self.current_user):
			self.write({"error":2})
			return
		if (not self.get_sessionid()):
			self.write({"error":3})
			return
		uid = self.current_user
		sessionid = self.get_secure_cookie("sessionid")
		result = self.evaluation(uid,sessionid)
		self.write({"error":result})
			
		
	def evaluation(self , uid , sessionid):
		info = self.db.query('SELECT FACEDETECT,AUDIODETECT,LATITUDE,LONGITUDE,DETECTTIME FROM DETECT WHERE OWNER = %s AND SESSIONID = %s;' % 
			(uid , sessionid))
		if (not info):
			return 4

		info = info[0]
		timedetect =  info['DETECTTIME']
		facedetect = info['FACEDETECT']
		audiodetect = info['AUDIODETECT']
		loc_detect = [info['LATITUDE'] , info['LONGITUDE']]
		if (facedetect == None) or (audiodetect==None) or (loc_detect==None):
			return 6

		info = self.db.query('SELECT * FROM LOCATION L,USER U WHERE L.LOCID = U.LOCID AND U.UID = %s;' % (uid))
		if (not info):
			return 4
		info = info[0]
		loc_init = [info['LATITUDE'],info['LONGITUDE']]
		loc_name = info['LOCATIONNAME']
		starttime = info['STARTTIME']
		termitime = info['TERMITIME']

		dis = spherical_distance(loc_detect , loc_init)
		logging.debug(dis)
		tim = starttime <= timedetect and timedetect <= termitime
		
		if (dis <= 4) and (facedetect >= 60) and (audiodetect > 0.6) and (tim):
			detect_status=0
		else:
			detect_status=1

		try:
			sql = "UPDATE DETECT SET STATUS=%d WHERE OWNER = %s AND SESSIONID = %s;"\
			 % (detect_status,uid,sessionid)
			info=self.db.execute(sql)
		except:
			return 5

		return detect_status











