#buildTrainingSet.py

import sys
import os
import glob
import dbAdmin

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")

db = dbAdmin.dbAdmin("CAT")

f = open("P_%s.csv" % number, "w")

strategies = ["calc", "mem"]

for strategy in strategies:
	if strategy == "calc":
		orderby = "DESC"
	elif strategy == "mem":
		orderby = "ASC"


	sql = "SELECT n1, n2, RT, ACC FROM pre_table WHERE number = %s AND strategy = '%s' ORDER BY (n1 + n2) %s" % (number, strategy, orderby)

	probList = []
	fullList = []

	for n1, n2, RT, acc in db.query(sql):
		#print n1, n2, RT
		prob = [n1, n2]
		prob.sort()

		if int(acc):
			fullList.append(prob)
			if prob not in probList:
				bad = 0
				for pref in probList:
					if prob[0] in pref or prob[1] in pref:
						bad = 1
				if not bad:
					probList.append(prob)
		else:
			probList.append(prob)

	quit = 0

	while not quit:
		if len(probList) >= 15:
			quit = 1

		if len(fullList):
			prob = fullList.pop()
		
			if prob not in probList:
				probList.append(prob)

		else:
			prob = "NA"
			probList.append(prob)

	probList = probList[:15]

	for p in probList:
		line = "%s,%s,%s,%s\n" % (p[0], p[1], number, strategy)
		f.write(line)

f.close()

try:
	db.close()
except:
	pass
