#showprogress

#A problem's progress

import sys
import problem
import pylab
import numpy
import copy

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid)
post = problem.Problems(DB, sid, exp="post")

mdict = {}
mdict['calc'] = 'o'
mdict['mem'] = 's'
cdict = {}
cdict['calc'] = [0, .2, .8]
cdict['mem'] = [.8, .2, 0]
pylab.figure(figsize=[8,8])

plotnum = 1

for trained in ['novel', 'trained']:
	for kind in ['verified', 'erratic']:
		pylab.subplot(2,2,plotnum, title = "%s %s" % (trained, kind))
		tableCount = 0
		for table in [pre, post]:
			for pid in table.distinct('id'):
				problem = table.query({'id': pid, 'trained' : trained, 'kind':kind})
				problem.sort('history.trial', 1)

				for row in problem:
					t = 1
					strat = row['strat']
					solution = row['solution']
					xs = []
					ys = []
					lastTrial = 0
					for h in row['history']:
						strategy = h['strat']
						if h['RT'] < 2.5:
							if lastTrial == h['trial']:
								ys[-1] = h['RT']
								t-= 1
							else:
								ys.append(h['RT'])
								xs.append(t + tableCount)
						t += 1
						lastTrial = copy.deepcopy(h['trial'])
		
					if len(ys) >= 2 and ys[1] > ys[0]:
						linestyle=':'
					else:
						linestyle='--'
					pylab.plot(xs[:2], ys[:2], marker=mdict[strategy], color=cdict[strategy], alpha=0.25, ms=solution/2, lw=solution/6, ls=linestyle)
					pylab.xlim([0.5, 4.5])
					pylab.ylim([0.0, 2.5])
					pylab.xticks([1.5, 3.5], ['pre', 'post'])
			tableCount += 2
		plotnum+=1

pylab.savefig("P_%s_training.png" % sid)
