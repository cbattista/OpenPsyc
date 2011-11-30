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

		xs.append(problem['n1'])
		ys.append(problem['n2'])
		colors.append(c)
		markers.append(m)
		RTs.append(rt)

ma = max(RTs)

sizes = []
for rt in RTs:
	n = rt / ma
	sizes.append(n * 200)

pylab.scatter(xs, ys, c=colors, marker=markers[1], s=sizes, alpha=0.5)

pylab.xticks(n1s)
pylab.yticks(n2s)

pylab.xlim([min(n1s) - 1, max(n1s) + 1])
pylab.ylim([min(n2s) - 1, max(n2s) + 1])

pylab.xlabel('small number')
pylab.ylabel('big number')

pylab.title("%s's results" % sid)

pylab.show()

