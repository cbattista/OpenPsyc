#comparor.py

#single subject training effects

import sys
import problem
import pylab
import numpy
import copy

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid)
post = problem.Problems(DB, sid, exp="post")

pre.name  ="pre"
post.name = "post"

training = ['novel', 'trained']

pylab.figure()

strategies=['mem', 'calc']

plotnum = 1

for strat in strategies:
	RTs=[]
	solns=[]
	labels = []
	for table in [pre, post]:
		for t in training:
			result = table.query({'trained' : t, 'kind':'verified', 'strat': strat})
			rts = []
			solutions = []
			for row in result:
				solution = row['solution']
				r=[]
				for h in row['history']:
					if h['RT'] < 4:
						r.append(h['RT'])
				rts.append(pylab.mean(r))
				solutions.append(solution)

			if rts:
				RTs.append(rts)
				label = "%s %s N=%s" % (table.name, t, len(rts))
				labels.append(label)
				solns.append(solutions)
				print label, pylab.mean(rts), pylab.std(rts)



	colors = []

	pylab.subplot(2,2,plotnum, title=strat)

	for r, l in zip(RTs, labels):
		patches = pylab.hist(r, label = l, alpha=0.5, bins=10)
		colors.append(patches[2][0].get_facecolor())

	pylab.legend()
	plotnum+=1

	pylab.subplot(2, 2, plotnum, title=strat)


	for r, s, l in zip(RTs, solns, labels):
		c = colors.pop(0)
		pylab.scatter(s, r, color=c,  label = l)
		z = numpy.polyfit(s, r, 1)
		p = numpy.poly1d(z)
		ss = copy.deepcopy(s)
		ss.sort()
		pylab.plot(ss,p(ss),color=c)

	#pylab.legend()
	plotnum+=1

pylab.show()
