#buildTrainingSet.py

import sys
import os
import glob
import mongoTools
import random

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")

db = mongoTools.MongoAdmin("CAT2")

posts = db.getTable("production_pre").posts

t_posts = db.getTable("training_sets").posts

v_posts = db.getTable("ver_sets").posts

p_posts = db.getTable("post_sets").posts

f = open("P_%s.csv" % number, "w")

t_posts.remove({'s_id':number})
v_posts.remove({'s_id':number})
p_posts.remove({'s_id':number})

strategies = ["calc", "mem"]

#for r in posts.find():
#	print r

print number

for s in strategies:
	probList = []
	fullList = []

	result = posts.find({'strategy' : s, 's_id' : int(number), 'verified' : 1})
	for r in result:
		n1 = r['n1']
		n2 = r['n2']
		ns = [n1, n2]
		ns.sort()

		fullList.append(ns)
		if ns not in probList:
			bad = 0
			for pref in probList:
				if ns[0] in pref or ns[1] in pref:
					bad = 1
					
			if not bad:
				probList.append(ns)
	quit = 0
	
	while not quit:
		if len(probList) >= 20:
			quit = 1
			
		
		if len(fullList):
			ns = fullList.pop()
			if ns not in probList:
				probList.append(ns)
		else:
			prob = "NA"
			probList.append(ns)

	probList = probList[:20]
	
	#add the problems to the training set, output them
	for p in probList:
		row = {}
		row['s_id'] = number
		row['n1'] = p[0]
		row['n2'] = p[1]
		row['strategy'] = s
		t_posts.insert(row)
		line = "%s,%s,%s,%s\n" % (p[0], p[1], number, s)
		f.write(line)

	#add the problems to the verification set, output them
	random.shuffle(probList)
	for p in probList[:10]:
		row = {}
		row['s_id'] = number
		row['n1'] = p[0]
		row['n2'] = p[1]
		row['orig_strat'] = s
		row['trained'] = 'trained'
		v_posts.insert(row)
		p_posts.insert(row)

	postList = []

	#print probList

	#now get some untrained problems
	result = posts.find({'strategy' : s, 's_id' : int(number), 'verified' : 1})
	for r in result:
		n1 = r['n1']
		n2 = r['n2']
		ns = [n1, n2]
		ns.sort()
		if ns not in probList:
			postList.append(ns)
			
	print postList		
			
	random.shuffle(postList)

	for p in postList[:10]:
		row = {}
		row['s_id'] = number
		row['n1'] = p[0]
		row['n2'] = p[1]
		row['orig_strat'] = s
		row['trained'] = "novel"
		p_posts.insert(row)
		v_posts.insert(row)
		
	for p in postList[10:20]:
		row = {}
		row['s_id'] = number
		row['n1'] = p[0]
		row['n2'] = p[1]
		row['orig_strat'] = s
		row['trained'] = "novel"
		p_posts.insert(row)


f.close()

