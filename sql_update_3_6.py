import sys
import os
import time
import glob
import re
import getopt
import chardet
import argparse

from string import Template
from common.mySQL_3_6 import SQLProcess
from common.submeterParse_3_6 import CSubmeterParse

sql_template = '''#_*_coding:utf-8_*_
UP_SQL="""

"""
'''

class SQLUpdate:
	def __init__(self, sqlDir):
		self.sqlDir = sqlDir
		
	def connectDB(self, host, user, passwd, dbname, port=3306, charset="utf8", autoCommit=False):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.dbname = dbname
		self.port = int(port)
		self.charset = charset
		
	def updateVersion(self, version):		
		sql = "INSERT INTO version (version) VALUES (%s);" % version
		sql += "\n COMMIT;"
		self.executeSQL(sql)
	
	def getLatestVersion(self):				
		sql = "SELECT VERSION FROM version ORDER BY VERSION DESC LIMIT 1;"
		try:
			db = SQLProcess()
			db.connect(self.host, self.user, self.passwd, self.dbname, self.port, self.charset)	
			row = db.fetchOne(sql)
			db.disConnect()			 #断开连接
			return row[0] if row else "0"
		except Exception as e:			
			print("Get version error: %s" % e)
			return False
			
	def executeSQL(self, sql):		
		if sql == "":
			return 		
		try:
			db = SQLProcess()
			db.connect(self.host, self.user, self.passwd, self.dbname, self.port, self.charset)
			#trsql = sql.decode("gb2312").encode("utf-8");
			#trsql = self.testTransToCharset(sql)
			trsql = sql
			parse = CSubmeterParse(trsql)
			submeter = parse.parseSubmeterSql()
			sub_len = len(submeter)
			if sub_len > 0:
				for lindex in submeter:
					table = lindex['table']
					engine = lindex['engine']
					if '' == engine:
						showsql = "SHOW TABLES LIKE '%s%s';" % (table,'%')
					else:
						showsql = "SELECT TABLE_NAME FROM information_schema.`TABLES` WHERE TABLE_SCHEMA='%s' AND ENGINE='%s' AND TABLE_NAME LIKE '%s%s' ;" % (self.dbname,engine,table,'%')
					print ("showsql:%s\n" % showsql)
					result = db.fetchAll(showsql)
					#print "result:\n"
					#print result
					for tb in result:
						#print "tb:%s\n" % (tb)
						tbstr = "%s" % (tb)
						sql_line_list = lindex['line_list']
						for lsql in sql_line_list:
							lsql = lsql.replace(':sub:',tbstr)
							print_sql = lsql
							#print_sql = lsql.encode('gb2312')
							print ("sub sql:%s" % print_sql)
							db.execute(lsql)
			else:
				#print "trsql:%s\n" % (trsql)
				db.execute(trsql)
				#db.commit()
				db.disConnect()
		except Exception as e:
			assert False, "Update SQL: %s \nError: %s" % (sql, e)
			sys.exit(1)
		
	def testTransToCharset(self, sql, transCharset="utf-8"):
		print('----testTransToCharset=----')
		if sql == "":
			return sql
		try:
			detect = chardet.detect(sql)
			confidence,encoding = detect["confidence"],detect["encoding"]
			print("confidence:%f,encoding:%s" % (confidence,encoding))
			if confidence < 0.9 or encoding == None:
				print("Unable to identify  %s  coding" % sql)
				return sql
			print("sql encoding:%s" % encoding)
			if transCharset == encoding:
				return sql
			#decode函数可以额外增加'ignore'参数忽略错误,因为此字符里面可能含有多种字符集
			trsql = sql.decode(encoding).encode(transCharset)
			return trsql
		except Exception as e:
			assert False, "testTransToCharset SQL: %s \nError: %s" % (sql, e)
		
		return sql

		
	def updateSQL(self, fileName):
		if not os.path.exists(fileName): #是否存在该文件
			print("111--------")
			assert False, "%s not exists!!!" % fileName 
		try:	
			f = open(fileName, "r", encoding='utf-8')
		except Exception as e:
			print("2------")
			print(e)
		content = f.read()
		f.close()
		
		c_up = re.compile(r'UP_SQL="""(.+)"""', re.I | re.M | re.S) 
		s_up = c_up.search(content)
		sql = s_up.groups()[0].strip()  #提取sql语句,移除首尾空格
		print(sql)
		sql += "\n COMMIT;"
		#sql = sql.encode("utf-8");
		self.executeSQL(sql)
		

	def addSQLScript(self):	
		scriptName = input("Please input the script name without datetime:\nLike this:add_table_version\n")
		fileName = "%s_%s.sql" % (time.strftime('%Y%m%d%H%M%S',time.localtime()), scriptName)
		
		if not os.path.exists(self.sqlDir):
			print(self.sqlDir)
			os.mkdir(self.sqlDir)
			
		filePath=os.path.join(self.sqlDir,fileName)
		f = open(filePath, "w", encoding='utf-8')
		f.write(sql_template)
		f.close()
		print("SQL 脚本 %s 创建成功!" % filePath)
	
	def initDatabase(self):
		#检查version表格是否存在，若存在则不初始化数据库，只检查升级
		version_sql = "select `TABLE_NAME` from `INFORMATION_SCHEMA`.`TABLES` where `TABLE_SCHEMA`='%s' and `TABLE_NAME`='version'" % self.dbname
		try:
			db = SQLProcess()
			db.connect(self.host, self.user, self.passwd, self.dbname, self.port, self.charset)
			row = db.fetchOne(version_sql)
			db.disConnect()				
		except Exception as e:
			print(e)
		if row:
			return
	
		fileName = "database.sql"
		fileName = os.path.join(self.sqlDir, fileName)
		if not os.path.exists(fileName):
			assert False, "%s not exists!!!" % fileName
			
		f = open(fileName, "r", encoding='utf-8')
		sql = f.read()
		f.close()
		self.executeSQL(sql)

	def updateSQLScript(self):	
		self.initDatabase()		
		version = self.getLatestVersion()   #获取最后执行的版本号
		print("cur version:",version)
			
		file_list = [f if f[-4:]==".sql" and f.startswith(tuple(['%s' % i for i in range(10)])) else "" for f in os.listdir(self.sqlDir)] #获取文件列表
		#os.listdir 返回指定路径下的文件和文件夹
		#startswith 检测字符串,检测到指定的内容则返回true
		file_dict = {}
		for f in file_list:			
			if f == "":continue
			key = f.split("_")[0]	#截取前面版本号
			if key > version:   #大于数据库存储的版本号,存下来该文件名称
				file_dict[key] = f  
		
		sorted_list = sorted(file_dict.items(), key=lambda file_dict:file_dict[0])  #按版本号大小排序
		#sorted 排序  key,y'lai
		if not sorted_list:
			print("数据库已经是最新版本,不需要升级")
			return
		
		for key, f in sorted_list:
			fileName = os.path.join(self.sqlDir, f) #拼接文件路径
			self.updateSQL(fileName)  #执行sql语句
			self.updateVersion(key)  
		print("数据库升级成功,当前版本号:",sorted_list[-1][0])
		
def useage():
	print("Please choose the option you wanna to do!\n A: Add SQL script\n U: Update SQL")

def usage():
	parser = argparse.ArgumentParser()  #创建解析器
	parser.parse_args()  #解析参数
	

def	main():
	try:  
		#getopt.getopt()
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "sql_dir=", "host=", "user=", "passwd=", "dbname=", "port=","charset="])
		
		sqlDir = None
		host = None
		user = None
		passwd = None
		dbName = None
		port = None
		charset = None
		
		for opt, arg in opts:  
			if opt in ("-h", "--help"):  
				usage()
				sys.exit(1)
			elif opt == "--sql_dir":
				sqlDir = arg
			elif opt == "--host":  
				host = arg
			elif opt == "--user":
				user = arg
			elif opt == "--passwd":
				passwd = arg
			elif opt == "--dbname":
				dbName = arg
			elif opt == "--port":
				port = arg
			elif opt == "--charset":
				charset = arg
			else:  
				print("%s  ==> %s"%(opt, arg))         

	except getopt.GetoptError as e:  
		print("getopt error!")
		usage()
		sys.exit(1) 


	try:
		userOption = input("%s\nPlease choose the option you wanna to do!\n A: Add SQL script\n U: Update SQL\n%s\n " % ("=" * 50, "=" * 50))
		o = userOption.upper()
		
		if o == "A":
			p = SQLUpdate(sqlDir)		
			p.addSQLScript()
			return
		elif o == "U":
			p = SQLUpdate(sqlDir) #初始化类
			p.connectDB(host, user, passwd, dbName, port, charset, False) #连接数据库
			p.updateSQLScript()			 
		else:
			print("未定义的操作:%s" % o)
	except Exception as e:
		print(e)
	
	
if __name__ == "__main__":
	main()
		
	
		
	
	