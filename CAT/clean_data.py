#clean_data.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

"""
pre = problem.Problems(DB, sid)

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
"""

post = problem.Problems(DB, sid, exp="post")

for pid in post.distinct('id'):
	for row in post.query({'id': pid}):
		l = len(row['history'])
		print pid, l, row['kind']
