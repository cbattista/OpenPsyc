import problem
import pylab
import scipy.stats
import matplotlib.mlab as mlab
import sys, os

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools

DB = "CAT3" 

sid = sys.argv[1]


pre_post = problem.Problems(DB, sid=sid, exp="pre_post")

strats = ['strat', ['calc', 'mem']]

kinds = ['kind', ['verified', 'erratic']]

days = ['day', ['pre', 'post']]

trained = ['trained', ['novel', 'trained']]

#IVs and their levels
IVs = [strats, kinds, days, trained]

#DVs
DVs = ['RT']

subject_stats = mongoTools.MongoAdmin(DB).getTable("subject_stats")

subject_stats.remove({'sid': sid})

#Look at main effects of each IV

for dv in DVs:
	for iv in IVs:
		print dv, iv
		#name of the IV
		name = iv[0]
		#levels of the IV
		levels = iv[1]
		#record of dvs for each level for later
		data = {}		
		

		for level in levels:
			row = {}
			row['sid'] = sid
			row[name] = level
			row['DV'] = dv
			row['estimates'] = []
			row['statistics'] = []

			dvs = pre_post.query({name: level}, ['RT'])
			data[level] = dvs

			row['estimates'].append({'mean': pylab.mean(dvs)})
			row['estimates'].append({'std': pylab.std(dvs)})
			row['estimates'].append({'sem': scipy.stats.sem(dvs)})

			if len(dvs) > 8:
				nstat, nsig = scipy.stats.normaltest(dvs)
				row['statistics'].append({'name': 'normal', 'statistic': nstat, 'p': nsig})
				B, bsig = scipy.stats.skewtest(dvs)
				row['statistics'].append({'name': 'skew', 'statistic' : B, 'p' : bsig})
				K, ksig = scipy.stats.kurtosistest(dvs)
				row['statistics'].append({'name': 'kurtosis', 'statistic' : K, 'p' : ksig})

			subject_stats.insert(row)

		#compare the levels of the main	
		row = {}
		row['sid'] = sid
		row['IV'] = name
		row['DV'] = dv
		row['statistics'] = []
		row['estimates'] = []

		if len(levels) == 2:
			T, bsig = scipy.stats.bartlett(data[levels[0]], data[levels[1]])
			W, lsig = scipy.stats.levene(data[levels[0]], data[levels[1]])
			F, fsig = scipy.stats.f_oneway(data[levels[0]], data[levels[1]])
			#H, hsig = scipy.stats.kruskal(data[levels[0]], data[levels[1]])
			row['statistics'].append({'name': 'Bartlett', 'statistic' : T, 'p': bsig})
			row['statistics'].append({'name': 'Levene', 'statistic' : W, 'p' : lsig})
			row['statistics'].append({'name': 'One Way ANOVA', 'statistic' : F, 'p': fsig})
			#row['statistics'].append({'name': 'Kruskal Wallis', 'statistic' : H, 'p' : hsig})
						

