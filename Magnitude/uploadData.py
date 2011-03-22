import sys
import random

sys.path.append('/home/cogdev/code/OpenPsyc/')

import mongoTools

#UPLOAD THE DATA FROM pre test AND THEN TRAIN

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")

fileName = "pre/pre_%s*.csv" % number
dbName = "magnitude"
tableName = "pre"

db = mongoTools.MongoAdmin(dbName)

reader = mongoTools.ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=True)

posts = db.getTable("pre").posts

t_posts = db.getTable("training_sets").posts

p_posts = db.getTable("post_sets").posts

f = open("P_%s.csv" % number, "w")

#GENERATE A TRAINING SET FROM THE pre test data

t_posts.remove({'s_id':number})
p_posts.remove({'s_id':number})

probList = []
fullList = []

#TRAINED CALC PROBLEMS

s = 'calc'
t_num = 20

result = posts.find({'strategy' : s, 's_id' : int(number), 'verified' : 1})
for r in result:
	n1 = r['n1']
	n2 = r['n2']
	ns = [n1, n2]
	ns.sort()

	fullList.append(ns)

	"""
	if ns not in probList:
		bad = 0
		for pref in probList:
			if ns[0] in pref or ns[1] in pref:
				bad = 1
				
		if not bad:
			probList.append(ns)
	"""

quit = 0

while not quit:
	if len(probList) >= t_num:
		quit = 1
		
	if len(fullList):
		ns = fullList.pop(0)

		print ns

		if ns not in probList:
			print ns
			probList.append(ns)
		else:
			print "Repeat detected!"
	
probList = probList[:t_num]

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
#random.shuffle(probList)
for p in probList[:t_num]:
	row = {}
	row['s_id'] = number
	row['n1'] = p[0]
	row['n2'] = p[1]
	row['orig_strat'] = s
	row['trained'] = 'trained'
	p_posts.insert(row)

postList = []

###UNTRAINED MEM PROBLEMS

s = "mem"

result = posts.find({'strategy' : s, 's_id' : int(number), 'verified' : 1})
for r in result:
	n1 = r['n1']
	n2 = r['n2']
	ns = [n1, n2]
	ns.sort()
	if ns not in probList:
		postList.append(ns)
		
random.shuffle(postList)

#10 problems for the post training list and verification list
for p in postList[:t_num]:
	row = {}
	row['s_id'] = number
	row['n1'] = p[0]
	row['n2'] = p[1]
	row['orig_strat'] = s
	row['trained'] = "novel"
	p_posts.insert(row)

f.close()

