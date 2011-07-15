import problem
import pylab
import scipy.stats
import matplotlib.mlab as mlab
import sys, os

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools

DB = "CAT3" 

sid = sys.argv[1]


p = problem.Problems(DB, sid=sid)

strats = ['calc', 'mem']

kinds = ['verified', 'temp', 'erratic', 'incorrect']

posts = mongoTools.MongoAdmin(DB).getTable("subject_stats")
#posts.remove({})

row = {}
row['sid'] = sid


d = {}
for k in kinds:
	d[k] = {}
	row[k] = {}
	row[k] = {'tests' : []}
	testNorm = False
	for s in strats:
		row[k][s] = {'tests': []}		
		
		d[k][s] = {}
		d[k][s]['RTs'] = []
		d[k][s]['solutions'] = []
		rows = p.query({'kind' : k, 'strat' : s})
		RTs = []
		solutions = []
		for r in rows:
			for h in r['history']:
				
				if h['RT'] <= 4.5:
					d[k][s]['RTs'].append(h['RT'])
					d[k][s]['solutions'].append(r['solution'])

		if d[k][s]['RTs']:
			#make histogram & test normality
			RTs = d[k][s]['RTs']
			if len(RTs) >= 8:
				testNorm = True
				nstat, nsig = scipy.stats.normaltest(RTs)
				row[k][s]['tests'].append({'name': 'normaltest', 'statistic': nstat, 'p': nsig})
				B, bsig = scipy.stats.skewtest(RTs)
				row[k][s]['tests'].append({'name': 'skew', 'statistic' : B, 'p' : bsig})
				K, ksig = scipy.stats.kurtosistest(RTs)
				row[k][s]['tests'].append({'name': 'kurtosis', 'statistic' : K, 'p' : ksig})
			else:
				norm = ", N < 8"
				testNorm = False
	
	#do a levene's
	if testNorm:
		T, bsig = scipy.stats.bartlett(d[k]['calc']['RTs'], d[k]['mem']['RTs'])
		W, lsig = scipy.stats.levene(d[k]['calc']['RTs'], d[k]['mem']['RTs'])
		row[k]['tests'].append({'name': 'Barlett', 'statistic' : T, 'p': bsig})
		row[k]['tests'].append({'name': 'Levene', 'statistic' : W, 'p' : lsig})

posts.insert(row)

#how many plots?
newkinds = []
for k in kinds:
	if d[k]['mem']['RTs'] or d[k]['calc']['RTs']:
			newkinds.append(k)

newkinds = list(set(newkinds))
numplots = len(newkinds)

plotnum = 0

pylab.figure(figsize=[8,8])
pylab.title("PPT %s" % sid)

#now lets make 'em

prop = {'size': 10}

for k in newkinds:
	mems = d[k]['mem']
	calcs = d[k]['calc']

	if mems['RTs'] or calcs['RTs']:
		mlabel = "mem N=%s" % len(mems['RTs'])
		clabel = "calc N=%s" % len(calcs['RTs'])

		#histogram
		plotnum += 1
		pylab.subplot("%i2%i" % (numplots, plotnum), title = k)
		if mems['RTs']:
			pylab.hist(mems['RTs'], 50, label=mlabel, alpha=0.5)
		if calcs['RTs']:		
			pylab.hist(calcs['RTs'], 50, label=clabel, alpha=0.5)
		pylab.legend(prop=prop)

		#scatterplot
		plotnum += 1
		pylab.subplot("%i2%i" % (numplots, plotnum), title = k)
		if mems['RTs']:
			pylab.scatter(mems['RTs'], mems['solutions'], color='b', label =mlabel)
		if calcs['RTs']:
			pylab.scatter(calcs['RTs'], calcs['solutions'], color='g', label = clabel)
		pylab.legend(prop=prop)		


pylab.savefig("SS_%s.png" % sid)


