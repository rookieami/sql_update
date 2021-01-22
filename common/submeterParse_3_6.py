#_*_coding:utf-8_*_

class CSubmeterParse:
	def __init__(self,sql):
		self.mSql = sql
		
	def parseSubmeterSql(self):
		if self.mSql=='':
			return self.mSql
		#print self.mSql
		return self.__parseSubmeterSql(self.mSql,0)
		
	def __parseSubmeterSql(self,sql,begin):
		key_b = "sub_begin:"
		key_b_len = len(key_b)
		key_engine = "sub_engine:"
		key_engine_len = len(key_engine)
		key_e = "sub_end"
		key_e_len = len(key_e)
		start = 0
		sql_len = len(sql)
		parse_list = []
		try:
			while (1):
				dic_pair = self.__checkSubmeterPair( sql,start,key_b,key_b_len,key_e,key_e_len,key_engine,key_engine_len )
				if dic_pair['res'] < 1:
					#print ("submeter pair failed \n")
					#print (dic_pair)
					#print ("\n")
					break
				line_sql = dic_pair['sql']
				#print ("line_sql:\n%s\n" % (line_sql))
				parse_line_sql = self.__parseSubmeterSqlLine(dic_pair)
				end_k = dic_pair['end_k']
				line_len = len(parse_line_sql)
				dic_pair['line_list'] = []
				if line_len == 0:
					dic_pair['line_list'].append(sql[end_k:sql_len])
					parse_list.append(dic_pair)
					break
				dic_pair['line_list'] = parse_line_sql
				parse_list.append(dic_pair)
				start = end_k
				if start >= sql_len:
					break	
		except Exception as e:
			assert False, "parse submeter failed SQL: %s \nError: %s" % (sql, e)
			
		return parse_list
	
	def __checkSubmeterPair(self,sql,start,key_b,key_b_len,key_e,key_e_len,key_engine,key_engine_len):
		dic = {'start_k':0,'end_k':0,'start':0,'end':0,'sql':'','table':'','res':0,'line':0,'engine':''}
		if sql == '':
			dic['line'] = 77
			return dic
		spos = sql.find(key_b,start)
		if spos < 0:
			#print ("sql:%s \n key_b:%s \n start:%d " % (sql,key_b,start))
			dic['line'] = 81
			return dic
		dic['start_k'] = spos
		epos = sql.find(key_e,spos)
		if epos < 0:
			print ("submeter form must be %s \n sql content \n %s \n spos:%d \n" % (key_b,key_e,start,spos))
			dic['line'] = 87
			return dic
		dic['end_k'] = epos+key_e_len+1
		table_start = spos+key_b_len
		table_end = sql.find('\n',table_start)
		tablename = ''
		rl = len(sql)
		if table_end < 0:
			tablename = sql[table_start:rl]
			dic['table'] = tablename
			dic['line'] = 97
			return dic
		else:
			tablename = sql[table_start:table_end]
		dic['table'] = tablename
		table_len = table_end - table_start
		if rl <= table_end+1:
			dic['line'] = 104
			return dic
		engine_pos = sql.find(key_engine,table_end+1)
		if engine_pos > -1:
			engine_pos += key_engine_len
			table_end = sql.find('\n',engine_pos)
			engine = sql[engine_pos:table_end]
			dic['engine'] = engine
		dic['sql'] = sql[table_end+1:epos]
		dic['start'] = table_end+1
		dic['end'] = epos
		dic['res'] = 1
		return dic
			
		
	
	def __parseSubmeterSqlLine(self,dic):
		tablename = dic['table']
		start = dic['start']
		end = dic['end']
		sql = dic['sql']
		sql_len = end-start
		rp_key = ':sub:'
		curindex = 0
		#print ("sql_len:%d\n" % sql_len)
		line = []
		while (1):
			linepos = sql.find('\n',curindex)
			#print ("curindex:%d linepos:%d\n" % (curindex,linepos))
			if linepos < 0:
				ctsql = sql[curindex:sql_len]
				ctsql = ctsql.replace( rp_key, tablename )
				line.append( ctsql )
				break
			ctsql = sql[curindex:linepos]
			#print ("cutsql:%s\n tablename:%s\n" % ctsql,tablename)
			#ctsql = ctsql.replace( rp_key, tablename )
			line.append( ctsql )
			curindex = linepos+1
			if curindex >= sql_len:
				break
		return line
			
		
	
		
		
