#makePostList.py

import sys
import dbAdmin

db = dbAdmin.dbAdmin("CAT")

myArgs = sys.argv

number = myArgs[1]

#get the trained problems
f = open("P_%s.csv" % number, "r")

probList = []

for line in f.readlines():
	l = line.split(',')
	n1 = int(l[0])
	n2 = int(l[1])
	probList.append([n1, n2])

#now get some untrained problems
strategies = ["calc", "mem"]
for strategy in strategies:
	if strategy == "calc":
		orderby = "DESC"
	elif strategy == "mem":
		orderby = "ASC"

	sql = "SELECT n1, n2 FROM pre_table WHERE number = %s AND strategy = '%s' ORDER BY (n1 + n2) %s" % (number, strategy, orderby)

	untrained = []

	for n1, n2 in db.query(sql):
		#print n1, n2, RT
		prob = [int(n1), int(n2)]
		prob.sort()
	
		bad = 0
		for pref in probList:
			print pref
			if prob[0] in pref and prob[1] in pref:
				bad = 1
		if not bad:
			untrained.append(prob)

	quit = 0

	untrained = untrained[:15]

	probList = probList + untrained

f = open("p%s_post.csv" % str(myArgs[1]), "w")

for p in probList:
	f.write("%s,%s\n" % (p[0], p[1]))

f.close()

try:
	db.close()
except:
	pass
