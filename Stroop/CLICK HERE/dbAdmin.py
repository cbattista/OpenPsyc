#dbAdmin.py

import sqlite

class dbAdmin:
	def __init__(self, name):
		name = ":" + name + ":"		
		self.con = sqlite.connect(name)
		self.cur = self.con.cursor()

	def query(self, sql):
		self.cur.execute(sql)
		self.con.commit()
		result = self.cur.fetchall()
		return result

	def getSubjects(self, table):
		sql = """
			SELECT DISTINCT(subject)
			FROM 
			%s
			""" % table
		result = self.query(sql)
		subjects = []
		for item in result:
			subjects.append(item[0])
		subjects.sort()
		return subjects

	def getSex(self, subject, table):
		sql = """SELECT DISTINCT(sex) from %s WHERE subject = %s""" % (table, str(subject))
		result = self.query(sql)[0][0]
		return result

	def getDistinct(self, what, table):
		sql = """
			SELECT DISTINCT(%s)
			FROM 
			%s WHERE category = 'a' OR category = 'p' OR category = 'n'
			""" % (what, table)
		result = self.query(sql)
		items = []
		for item in result:
			items.append(item[0])
		items.sort()
		return items
	
	def addColumn(db, table, column, colType):
		sql = "ALTER TABLE %s ADD COLUMN %s %s" % (table, column, colType)
		db.query(sql)

	

