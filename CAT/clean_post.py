#clean_data.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

post = problem.Problems(DB, sid, exp="post")

post_clean = problem.Problems(DB, sid, "post_clean", clear=True)

for pid in post.distinct('id'):
	for row in post.query({'id': pid}):
		l = len(row['history'])
		ns = [row['n1'], row['n2']]
		ns.sort()
		prob = problem.Problem(ns)
		for h in row['history']:
			prob.addResponse(h)

		post_clean.append(prob)

print "#####"


for pid in post_clean.distinct('id'):
	for row in post_clean.query({'id': pid}):
		l = len(row['history'])
		print pid, l, row['kind']
		if l > 2:
			newHist = []
			trials = []
			for h in row['history']:
				if h['trial'] in trials:
					pass
				else:
					newHist.append(h)
					trials.append(h['trial'])
			row['history'] = newHist[:2]
			print newHist
			post_clean.save(row)
		
post_clean.classifyAll()


