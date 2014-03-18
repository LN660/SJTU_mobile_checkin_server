# coding: utf8

import MySQLdb

class DB:
	def __init__(self, mysqldb):
		self.mysqldb = mysqldb

	def query_all(self, sql):
		cur = self.mysqldb.cursor()
		cur.execute(sql)
		res = cur.fetchall()
		cur.close()
		return res

	def execute(self, sql):
		cur = self.mysqldb.cursor()
		try:
			cur.execute(sql)
			self.mysqldb.commit()
		except:
			self.mysqldb.rollback()
		finally:
			cur.close()
		return