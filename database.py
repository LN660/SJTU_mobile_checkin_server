# coding: utf8

'''
MySql Database Helpers

'''

import MySQLdb

class DB:
	def __init__(self, mysqldb):
		self.mysqldb = mysqldb
		cur = self.mysqldb.cursor()
		cur.execute("SET NAMES 'utf8';")
		cur.close()

	def query_all(self, sql):
		cur = self.mysqldb.cursor()
		cur.execute(sql)
		res = cur.fetchall()
		cur.close()
		return res

	def query(self, sql):
		return self.query_all(sql)

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