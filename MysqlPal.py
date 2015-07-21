#!/usr/bin/env python
#coding:utf-8

import MySQLdb
import ConfigParser

class MysqlPal:
	"""docstring for ClassName"""
	def __init__(self,database):
		self.connect(database)

	def connect(self,database):
		#读取配置文件
		cf = ConfigParser.ConfigParser()
		cf.read("config.ini")
		host = cf.get(database,"host")
		user = cf.get(database,"user")
		passwd = cf.get(database,"password")
		db = cf.get(database,"database")
		port = cf.get(database,"port")
		#连接
		self.conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,port=int(port),charset="utf8")
		self.conn.autocommit(True)
		self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
	def close(self):
		self.cursor.close()
		self.conn.close()
		return
	def get(self,sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()
	def getOne(self,sql):
		self.cursor.execute(sql)
		return self.cursor.fetchone()
	def execSql(self,sql):
		cursor = self.conn.cursor()
		result = cursor.execute(sql)
		cursor.close()
		return [result,cursor.fetchall()]
	'''==================分类分割线====================='''

	def makeSql(self,sqltype,table,criteria):
		if sqltype == 'count':
			sql = "SELECT COUNT(1) FROM %s "%table
			if criteria and criteria.get('count'):
				sql = "SELECT COUNT(%s) FROM %s "%(criteria.get('count'),table)
		elif sqltype == 'select':
			sql = "SELECT * FROM %s "%table
			if criteria and criteria.get('select'):
				sql = "SELECT %s FROM %s "%(criteria.get('select'),table)
		elif sqltype == 'delete':
			sql = "DELETE FROM %s "%table
		elif sqltype == 'update':
			if criteria.get('update'):
				sql = "UPDATE %s SET %s "%(table,criteria.get('update'))
		if criteria:
			if criteria.get('where'):
				sql += " WHERE %s"%criteria.get('where')
			if criteria.get('groupby'):
				sql += " GROUP BY %s"%criteria.get('groupby')
			if criteria.get('having'):
				sql += " HAVING %s"%criteria.get('having')
			if criteria.get('orderby'):
				sql += " ORDER BY %s"%criteria.get('orderby')
			if criteria.get('limit'):
				sql += " limit %s"%criteria.get('limit')
		return sql
	
	def count(self,table,criteria=None):
		cursor = self.conn.cursor()
		sql = self.makeSql('count',table,criteria)
		cursor.execute(sql)
		result = cursor.fetchone()
		cursor.close()
		return result[0]

	def delete(self,table,criteria=None):
		sql = self.makeSql('delete',table,criteria)
		return self.cursor.execute(sql)
	
	def find(self,table,criteria=None):
		sql = self.makeSql('select',table,criteria)
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def findOne(self,table,criteria=None):
		sql = self.makeSql('select',table,criteria)
		self.cursor.execute(sql)
		return self.cursor.fetchone()

	def save(self,table,data):
		column = value = ''
		for i in data:
			column += "`%s`,"%i
			value += "'%s',"%data.get(i)
		column = column.strip(',')
		value = value.strip(',')
		sql = "INSERT INTO %s (%s) VALUES (%s)"%(table,column,value)
		return self.cursor.execute(sql)

	def update(self,table,data,criteria=dict()):
		column = ''
		for i in data:
			column += "`%s`='%s',"%(i,data.get(i))
		criteria['update'] = column.strip(',')
		sql = self.makeSql('update',table,criteria)
		return self.cursor.execute(sql)

if __name__ == '__main__':
	mp = MysqlPal('mysql')
	print mp.getOne('SELECT * FROM invite_stat')
	print mp.get('SELECT * FROM interview_stat')
	print mp.execSql('SELECT COUNT(1) FROM interview_stat')
	
	criteria = {'select':'id,activity_name',
				'count':'distinct state',
				'where':'state = 1',
				'orderby':'id',
				'limit':'5',
				'groupby':'id',
				}
	print mp.count('invite_stat')
	print mp.find('activity',criteria)
	print mp.findOne('activity',criteria)
	print mp.count('activity',criteria)
	data = {'activity_name':'test',
			'start_time':'2015-04-08',
			'end_time':'2015-04-22'}
	print mp.save('activity',data)
	print mp.update('activity',data,{'where':'id=19'})
	mp.close()