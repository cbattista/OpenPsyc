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

for kind in ['verified', 'erratic']:
	for trained in ['novel', 'trained']:
		d = {}
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
					strats = []
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
						strats.append(strategy)
						t += 1
						lastTrial = copy.deepcopy(h['trial'])
	
					if not d.has_key(str(pid)):
						d[str(pid)] = [[], [], [], solution]
	
					d[pid][0] += xs[:2]
					d[pid][1] += ys[:2]
					d[pid][2] += strats[:2]

			tableCount += 2


		for pid in d.keys(): 
			#plot dots
			xs = d[pid][0]
			ys = d[pid][1]
			strats = d[pid][2]
			solution = d[pid][3]
			for X, Y, strategy in zip(xs, ys, strats):
				pylab.scatter(X, Y, marker=mdict[strategy], color=cdict[strategy], alpha=0.75, s=solution/2)

			#plot connector
			pylab.plot(xs, ys, color=cdict[strats[-1]], lw=solution/10, ls='--', alpha=0.25)


		pylab.xlim([0.5, 4.5])
		pylab.ylim([0.0, 2.5])
		pylab.xticks([1.5, 3.5], ['pre', 'post'])


		plotnum+=1

"""		
					if len(ys) >= 2 and ys[1] > ys[0]:
						linestyle=':'
					else:
						linestyle='--'
					pylab.plot(xs[:2], ys[:2], marker=mdict[strategy], color=cdict[strategy], alpha=0.25, ms=solution/2, )
"""

pylab.savefig("P_%s_training.png" % sid)

