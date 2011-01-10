import sys

sys.path.append('/home/cogdev/code/OpenPsyc/')

from mongoTools import ReadTable

#UPLOAD THE DATA FROM pre test AND THEN TRAIN

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")

fileName = "pre/pre*%s.csv" % number
dbName = "magnitude"
tableName = "production_pre"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=False)

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

result = posts.find({'strategy' : 'calc', 's_id' : int(number), 'verified' : 1})
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
		probList.append(prob)

probList = probList[:20]

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
for p in probList[:20]:
	row = {}
	row['s_id'] = number
	row['n1'] = p[0]
	row['n2'] = p[1]
	row['orig_strat'] = s
	row['trained'] = 'trained'
	v_posts.insert(row)
	p_posts.insert(row)

postList = []

###UNTRAINED MEM PROBLEMS

result = posts.find({'strategy' : 'mem', 's_id' : int(number), 'verified' : 1})
for r in result:
	n1 = r['n1']
	n2 = r['n2']
	ns = [n1, n2]
	ns.sort()
	if ns not in probList:
		postList.append(ns)
		
random.shuffle(postList)

#10 problems for the post training list and verification list
for p in postList[:20]:
	row = {}
	row['s_id'] = number
	row['n1'] = p[0]
	row['n2'] = p[1]
	row['orig_strat'] = s
	row['trained'] = "novel"
	p_posts.insert(row)
	v_posts.insert(row)

f.close()

