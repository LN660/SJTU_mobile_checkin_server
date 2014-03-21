# coding: utf8

import os
import logging
import settings as server_settings

import tornado.web
import tornado.httpserver
import tornado.ioloop
import MySQLdb
import MySQLdb.cursors

import database
from admin import AddAdminHandler, DefaultRuleHandler, AdminIndexHandler, TimeQueryHandler, MapQueryHandler, SettingHandler, DeleteAdminHandler, ManageHandler, RuleHandler, CheckHandler, StudentEditHandler, StudentHandler, adminHandler, AdminJaLoginHandler, AdminJaLogoutHandler
from handlers import DetectCreateHandler , DetectResultHandler ,CheckStatusHandler, JaLoginHandler, JaLogoutHandler, FaceppHandler, FaceRegisterHandler, SpeechTrainHandler, SpeechDetectHandler, UploadLocationHandler
from basic import LoginHandler , RegisterHandler
from location import LocationRegisterHandler

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			# Mobile API
			(r"/jalogin", JaLoginHandler),
			(r"/jalogout",JaLogoutHandler),
			(r"/faceverify" , FaceppHandler),
			(r"/faceregister" , FaceRegisterHandler),
			(r"/svdetect" , SpeechDetectHandler),
			(r"/svtrain", SpeechTrainHandler),
			(r"/detectcreate", DetectCreateHandler),
			(r"/getdetectresult" , DetectResultHandler),
			(r"/uploadlocation", UploadLocationHandler),
			(r"/registerlocation", LocationRegisterHandler),
			(r"/checkstatus" , CheckStatusHandler),

			# Admin
			(r"/admin", adminHandler),
			(r"/admin/jalogin" , AdminJaLoginHandler),
			(r"/admin/logout" , AdminJaLogoutHandler),
			(r"/admin/index" , AdminIndexHandler),

			# Admin API
			(r"/admin/student", StudentHandler),
			(r"/admin/student/edit", StudentEditHandler),
			(r"/admin/checkin",CheckHandler),
			(r"/admin/default_rule", DefaultRuleHandler),
			(r"/admin/rule", RuleHandler),
			(r"/admin/manage", ManageHandler),
			(r"/admin/addadmin" , AddAdminHandler),
			(r"/admin/manage/delete", DeleteAdminHandler),
			(r"/admin/setting", SettingHandler),
			(r"/admin/map_stat/search", MapQueryHandler),
			(r"/admin/time_stat/([0-9]+)", TimeQueryHandler)
		]

		settings = dict(
			template_path = os.path.join(server_settings.ROOT_DIR, "templates"),
			static_path = os.path.join(server_settings.ROOT_DIR, 'static'),
			cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
			debug = True,
		)
		tornado.web.Application.__init__(self , handlers , **settings)
		self.db = database.DB(MySQLdb.connect(
			host="0.0.0.0", 
			user=server_settings.DB_USERNAME, 
			passwd=server_settings.DB_PASSWORD,
			db="mobile_checkin",
			cursorclass=MySQLdb.cursors.DictCursor))


if __name__ == '__main__':
	LOGGING_LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
	logging.basicConfig(level=LOGGING_LEVELS.get(server_settings.LOGGING_LEVEL, logging.NOTSET))
	port = 8888
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()




