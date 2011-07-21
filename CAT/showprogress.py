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
cdict['calc|mem'] = [.8, .2, .8]
cdict['mem|calc'] = [.8, .2, .8]
pylab.figure(figsize=[14,8])

plotnum = 1

for kind in ['verified', 'erratic']:
	for trained in ['novel', 'trained']:
		d = {}
		pylab.subplot(2,4,plotnum, title = "%s %s" % (trained, kind))
		tableCount = 0
		for table in [pre, post]:
			pylab.plot([2.5, 2.5], [0, 2.5], 'k:')
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

		#plot trial breakdown
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
		pylab.ylim([0.3, 3])
		pylab.xticks([1.5, 3.5], ['pre', 'post'])

		plotnum += 1


	#plot conversion histogram
	for trained in ['novel', 'trained']:
		conv = {}
		for pid in post.distinct('id', {'kind': kind, 'trained' : trained}):
			problem = post.query({'id': pid})
			for row in problem:
				if row.has_key('conversion'):
					if not conv.has_key(row['conversion']):
						conv[row['conversion']] = {'RTs' : [], 'solutions' : []}
					solution = row['solution']
					for h in row['history']:
						conv[row['conversion']]['RTs'].append(h['RT'])
						conv[row['conversion']]['solutions'].append(solution)

		pylab.subplot(2,4, plotnum, title="%s %s conversion" % (trained, kind))
		for convert in conv.keys():
			if cdict.has_key(convert):
				color = cdict[convert]
			else:
				color = [0, 0, 0]
			pylab.scatter(conv[convert]['solutions'], conv[convert]['RTs'], alpha=0.5, color=color, label="%s (%s)" % (convert,len(conv[convert]['RTs'])))

		pylab.ylabel('RT')
		pylab.xlabel('solution')
		pylab.ylim(0.3, 3)
		pylab.legend(prop= {'size': 10})

		plotnum+=1
"""		
					if len(ys) >= 2 and ys[1] > ys[0]:
						linestyle=':'
					else:
						linestyle='--'
					pylab.plot(xs[:2], ys[:2], marker=mdict[strategy], color=cdict[strategy], alpha=0.25, ms=solution/2, )
"""

pylab.savefig("SS_%s_training.png" % sid)

