#_*_coding:utf-8_*_

import sys
import os
import time
import MySQLdb

class SQLProcess:
	def __init__(self):
		self.conn = None
		self.cursor = None
	
	def connect(self, host, user, passwd, dbname, port, charset="utf8", autoCommit=False):
		try:
			self.conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname, port=port,charset=charset)
		except MySQLdb.Error as e:
			print("Connect Error %d: %s" % (e.args[0], e.args[1]))
			sys.exit(1)
			
		self.cursor = self.conn.cursor()
		self.conn.autocommit(autoCommit)
		
	def isConnected(self):
		return self.conn != None

	def disConnect(self):
		if self.cursor:
			self.cursor.close()
			self.cursor = None
		if self.conn:
			self.conn.close()
			self.conn = None
	
	def execute(self, sql):
		try:
			#while self.cursor.nextset(): pass
			self.cursor.execute(sql)
		except MySQLdb.Error as e:
			print("Execute Error %d: %s" % (e.args[0], e.args[1]))
			sys.exit(1)
			
	def fetchOne(self, sql):
		try:
			self.execute(sql)
			return self.cursor.fetchone()
		except MySQLdb.Error as e:
			print("Error %d: %s" % (e.args[0], e.args[1]))
			sys.exit(1)
		
	def fetchMany(self, sql, size):
		try:
			self.execute(sql)
			return self.cursor.fetchmany(size)
		except MySQLdb.Error as e:
			print("Error %d: %s" % (e.args[0], e.args[1]))
			sys.exit(1)
	
	def fetchAll(self, sql):
		try:
			self.execute(sql)
			return self.cursor.fetchall()
		except MySQLdb.Error as e:
			print ("Error %d: %s" % (e.args[0], e.args[1]))
			sys.exit(1)
		
	def selectDB(self, dbName):
		self.conn.select_db(dbName)

	def commit(self):
		self.conn.commit()
		
	def rollback(self):
		self.conn.rollback()

	def setAutoCommit(self, autoCommit=False):
		self.conn.autocommit(autoCommit)
		
#if __name__ == "__main__":
	#db = SQLProcess()
	#db.connect("localhost", "root", "root", "ksgamedb", 3306)
	#sql = "SELECT * FROM user limit 0, 1"
	#row = db.fetchOne(sql)
	#print row
	#db.disConnect()
	
	