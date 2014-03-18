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
from jalogin import JaLoginHandler
from basic import CheckStatusHandler
from sv import SpeechTrainHandler,SpeechDetectHandler


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			# Mobile API
			(r"/jalogin", JaLoginHandler),
			(r"/checkstatus", CheckStatusHandler),
			(r"/svdetect" , SpeechDetectHandler),
			(r"/svtrain", SpeechTrainHandler),
			# Admin
			# Admin API
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




