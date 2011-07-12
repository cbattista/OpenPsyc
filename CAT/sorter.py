import problem
import pylab
import scipy.stats
import matplotlib.mlab as mlab

DB = "CAT3" 

sid = 5

p = problem.Problems(DB, sid=sid)

strats = ['calc', 'mem']

kinds = ['verified', 'temp', 'erratics', 'incorrect']

d = {}
for k in kinds:
	d[k] = {}
	for s in strats:
		print "s: %s, k: %s" % (s, k)
		d[k][s] = {}
		d[k][s]['RTs'] = []
		d[k][s]['solutions'] = []
		rows = p.query({'kind' : k, 'strat' : s})
		RTs = []
		solutions = []
		for r in rows:
			for h in r['history']:
				
				if h['RT'] <= 2.5:
					d[k][s]['RTs'].append(h['RT'])
					d[k][s]['solutions'].append(r['solution'])

		if d[k][s]['RTs']:
			#make histogram & test normality
			RTs = d[k][s]['RTs']

			print "Average RT: %0.2f, SD=%0.2f, N=%i" % (pylab.mean(RTs), pylab.std(RTs), len(RTs))
			if len(RTs) >= 8:
				nstat, nsig = scipy.stats.normaltest(RTs)
				print "Normality: %0.2f, p < %0.2f"  % (nstat, nsig)
			else:
				print "Can't test for normality when N < 8"


#how many plots?
newkinds = []
for k in kinds:
	if d[k]['mem']['RTs'] or d[k]['calc']['RTs']:
			newkinds.append(k)

newkinds = list(set(newkinds))
numplots = len(newkinds)

plotnum = 0

pylab.figure()
pylab.title("PPT %s" % sid)

#now lets make 'em

for k in newkinds:
	mems = d[k]['mem']
	calcs = d[k]['calc']

	if mems['RTs'] or calcs['RTs']:
		mlabel = "mem N=%s" % len(mems['RTs'])
		clabel = "calc N=%s" % len(calcs['RTs'])

		#histogram
		plotnum += 1
		pylab.subplot("%i2%i" % (numplots, plotnum), title = k)
		pylab.hist(mems['RTs'], 50, label=mlabel, alpha=0.5)
		pylab.hist(calcs['RTs'], 50, label=clabel, alpha=0.5)
		pylab.legend()

		#scatterplot
		plotnum += 1
		pylab.subplot("%i2%i" % (numplots, plotnum), title = k)
		pylab.scatter(mems['RTs'], mems['solutions'], color='b', label =mlabel)
		pylab.scatter(calcs['RTs'], calcs['solutions'], color='g', label = clabel)
		pylab.legend()		


pylab.show()


