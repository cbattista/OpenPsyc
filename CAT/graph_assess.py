from problem import *
import pylab

db = "mri_test"

###COLLECT SUBJECT INFO
myArgs = sys.argv

try:
	sid = str(myArgs[1])
except:
	sid = 666

problems = Problems(db, sid, "addition")

pylab.figure()
pylab.grid()

counts = problems.getCounts()

print counts

n1s = problems.distinct('n1')
n2s = problems.distinct('n2')

xs = []
ys = []
colors = []
markers = []
RTs = []

for problem in problems.find():
	for h in problem['history']:
		if h['strat'] == 'calc':
			c = 'r'
		else:
			c = 'g'
		
		if h['ACC'] == 0:
			m = 'x'
		else:
			m = 'o'

		rt = h['RT']

		if rt < 10:
			xs.append(problem['n1'])
			ys.append(problem['n2'])
			colors.append(c)
			markers.append(m)
			RTs.append(rt)

ma = max(RTs)

norms = []
for rt in RTs:
	n = rt / ma
	norms.append(n)

for x, y, n, c, m in zip(xs, ys, norms, colors, markers):
	pylab.scatter([x], [y], n * 800, c, marker=m, alpha=0.5)
	pylab.scatter([y], [x], n * 800, c, marker=m, alpha=0.5)

#c=colors, marker=markers[1], s=sizes, alpha=0.5)

ns = n1s + n2s

pylab.xticks(ns)
pylab.yticks(ns)

mi = min(ns)
ma = max(ns)

#draw mirror axis
pylab.plot([mi, ma], [mi, ma], color='k', alpha=0.5)

#draw marker lines
for i in [10, 20, 30, 40, 50]:
	pylab.plot([i, i], [mi, ma], color='k', alpha=0.5)
	pylab.plot([mi, ma], [i, i], color='k', alpha=0.5)


pylab.xlim([min(ns) - 1, max(ns) + 1])
pylab.ylim([min(ns) - 1, max(ns) + 1])

pylab.xlabel('small number')
pylab.ylabel('big number')

pylab.title("%s's results" % sid)

pylab.show()

