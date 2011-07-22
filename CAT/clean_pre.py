#clean_data.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid)
pre_clean = problem.Problems(DB, sid, "pre_clean", clear=True)

for pid in pre.distinct('id'):
	for row in pre.query({'id': pid}):
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
			row['history'] = newHist

			pre.save(row)

for pid in pre.distinct('id'):
	for row in pre.query({'id': pid}):
		l = len(row['history'])
		print pid, l, row['kind'], row['strat'], row['n1'], row['n2'], row['ns']
		ns = [row['n1'], row['n2']]
		ns.sort()
		prob = problem.Problem(ns)
		print prob
		for h in row['history']:
			prob.addResponse(h)

		pre_clean.append(prob)


pre_clean.classifyAll()

