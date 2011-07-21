import problem
import pylab
import scipy.stats
import matplotlib.mlab as mlab
import sys, os

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools

DB = "CAT3" 

sid = sys.argv[1]


pre = problem.Problems(DB, sid=sid)
post = problem.Problems(DB, sid=sid, exp="post")

pre.name= "pre"
post.name="post"

strats = ['calc', 'mem']

kinds = ['verified', 'erratic']

posts = mongoTools.MongoAdmin(DB).getTable("subject_stats")
#posts.remove({})

row = {}
row['sid'] = sid

for p in [pre, post]:
	
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
			if k != 'erratic':
				rows = p.query({'kind' : k, 'strat' : s})
			else:
				rows = p.query({'kind' : k})
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

	row['day'] = p.name
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
	pylab.title("PPT %s %s" % (sid, p.name))

	#now lets make 'em
	mdict = {}
	mdict['calc'] = 'o'
	mdict['mem'] = 's'
	cdict = {}
	cdict['calc'] = [0, .2, .8]
	cdict['mem'] = [.8, .2, 0]
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
				pylab.hist(mems['RTs'], 50, label=mlabel, alpha=0.5, color=cdict['mem'])
			if calcs['RTs']:		
				pylab.hist(calcs['RTs'], 50, label=clabel, alpha=0.5, color=cdict['calc'])
			pylab.legend(prop=prop)

			#scatterplot
			plotnum += 1
			pylab.subplot("%i2%i" % (numplots, plotnum), title = k)
			if mems['RTs']:
				pylab.scatter(mems['RTs'], mems['solutions'], color=cdict['mem'], marker=mdict['mem'], label =mlabel, alpha=0.5)
			if calcs['RTs']:
				pylab.scatter(calcs['RTs'], calcs['solutions'], color=cdict['calc'], marker=mdict['calc'], label = clabel, alpha=0.5)
			pylab.legend(prop=prop)		


	pylab.savefig("SS_%s_%s.png" % (sid, p.name))


