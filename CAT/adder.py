#! /usr/env/python

import os
import sys
import random
sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools

class Adder:
	def __init__(self, DB, table, sid):
		self.DB = mongoTools.MongoAdmin(DB)
		self.posts = self.DB.getTable(table).posts
		self.sid = sid				
		self.analyze()

	def respond(self, query):
		query.update({'sid': self.sid})
		row = self.posts.find_one(query)
		
		if row:
			rt = row['RT']
			acc = row['ACC']
			if not acc:
				side = row['dist_side']
			else:
				if row['dist_side'] == 'l':
					side = 'r'
				elif row['dist_side'] == 'r':
					side = 'l'
			strat = row['strat']

		else:
			n1 = query['n1']
			n2 = query['n2']
			acc = 1
			if n1 > self.limit or n2 > self.limit:
				strat = 'calc'
			else:
				strat = 'mem'
			rt = self.rts[strat] + (random.random() * 100)


	def analyze(self):
		#get the ranges of mem
		rows =self.posts.find({'cur_strat':'mem'}, {'solution':1})
		print soln
		self.limit = soln / 2	
	
		mems = self.posts.find({'strat':'mem'}, {'RT':1})
		calcs = self.posts.find({'strat':'calc'}, {'RT':1})
		
		self.rts = {}
		self.rts['calc'] = sum(calcs) / len(calcs)
		self.rts['mem'] = sum(mems) / len(mem)
