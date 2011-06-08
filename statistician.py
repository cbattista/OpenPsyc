from rpy2.robjects.vectors import DataFrame
import rpy2.robjects as robjects

from mongoTools import MongoAdmin
import random

class Statistician():
	def __init__(self, db):
		#initialize a lookup, dataFile table of terms
		self.db = MongoAdmin(db)
		self.hypotheses = ["It was expected that ", "It was predicted that "]
		self.interpretations = ["This is probably because", "This could be due to "]
		self.acceptnull = ["Contrary to the hypothesis, however ", "Against prediction,", "Contrary to expectation, "]
		self.rejectnull = ["as predicted", "as expected"]
		self.signs = {'>' : 'greater than', '<' : 'less than', '==' : 'equal to'}

	def translate(self, term, units=False):
		#if a string return the available translation
		output = ""

		posts = self.db.getTable('factors').posts
		if type(term) == str:
			row = posts.find_one({'name': term})
			print row
			if row:
				output = row['label']
			else:
				output = term

			if units:
				output += " %s" % row['units']

		#if a list/tree get all available translations
		elif type(term) == list:
			output = "%s" % self.translate(term[0])
			for t in term[1:]:
				output += " and %s" % self.translate(t)
		#otherwise just return a string of the term
		else:
			output = str(term)

		return output

	def describeFactor(self, factor):
		posts = self.db.getTable('factors').posts

		if type(factor) == str:
			row = posts.find_one({'name': factor})
		else:
			row = posts.find_one({'name': factor[0]})

		return None



	def parseAssertion(self, hyp, measure, tense="future"):
		tenses = {}
		tenses['future'] = 'would be'
		tenses['past'] = 'was'
		output = ""
		if hyp == "?":
			pass	
		else:
			for s in [">", "<", "=="]:
				if s in hyp:
					frags = hyp.split(s)
					output += "%s %s %s %s %s %s" % (self.translate(frags[0]), measure, tenses[tense], self.signs[s], self.translate(frags[1]), measure) 
					#now we should sort the fragments in ascending order and ditch the sign
					if s == ">":
						frags.reverse()

		return output, s, frags			
	
	def interpret(self, factors, measure, model, dataFile, condition={}):
		posts = self.db.getTable('hypotheses').posts		
		
		q = condition
		for f in factors:		
			q[f] = unicode('TARGET')
		

		row = posts.find_one(q)
		
		output = ""

		if row:
			hyp = random.choice(self.hypotheses)
			if row.has_key(measure):
				assertion, s, frags = self.parseAssertion(row[measure], measure)	
				output += "%s%s.\n" % (hyp, assertion)
				result = self.compareMeans(dataFile, model, frags, factors, measure)		
				if result:
					output += result

		output += "\n"
		return output

	def hypothesize(self, factors, measure, condition={}):
		posts = self.db.getTable('hypotheses').posts		
		
		q = condition
		for f in factors:		
			q[f] = unicode('TARGET')
		

		row = posts.find_one(q)
		
		output = ""

		if row:
			hyp = random.choice(self.hypotheses)
			if row.has_key(measure):
				assertion, s, frags = self.parseAssertion(row[measure], measure)
				output += "%s %s." % (random.choice(self.hypotheses), assertion)

		return output	

	def attachData(self, dataFile):
		argString = "read.table(\"output/%s\", header=T, sep=\",\")" % dataFile


		df = robjects.r(argString)
		robjects.r.attach(df)
		return df


	def correlate(self, m1, m2, dataFile, siglevel = 0.05):

		df = self.attachData(dataFile)

		cor = robjects.r("cor.test(%s, %s)" % (m1, m2))

		p = cor.rx2("p.value")
		p = p[0]
		r = cor.rx2("estimate")
		r = r[0]

		if p <= siglevel:
			sig = True
		else:
			sig = False

		return sig, r, p

	def anova(self, model, dataFile, siglevel = 0.05, within = False):	
		df = self.attachData(dataFile)
		argString = 'aov(%s)' % model
 
		aov = robjects.r(argString)

		summary = robjects.r("summary")
		result = summary(aov)
		ew = result.rx2('Error: Within')

		F = ew[0][3][0]
		p = ew[0][4][0]	

		if p <= siglevel:
			sig = True
		else:
			sig = False
		
		return sig, F, p

	def ttest(self, model, dataFile, siglevel = 0.05):
		df = self.attachData(dataFile)
		
		model = model.split('+')[0]

		result = robjects.r('t.test(%s)' % model)

		p = result.rx2('p.value')
		t = result.rx2('statistic')
		e = result.rx2('estimate')


		if p[0] < siglevel:
			sig = True
		else:
			sig = False		

		return sig, t[0], p[0]
	

	def compareMeans(self, dataFile, model, levels, factors, measure):
		df = self.attachData(dataFile)
		means = robjects.r('tapply(%s, %s, mean)' % (measure, factors[0]))
		sds = robjects.r('tapply(%s, %s, sd)' % (measure, factors[0]))

		d = {}

		largest = 0
		largeNum = 0

		for l in levels:
			m = means.rx2(l)
			sd = sds.rx2(l)
			if m[0] > largeNum:
				largest = l
				largeNum = m[0] 
			
			d[l] = {'mean': m[0], 'sd' : sd[0]}		
		
		output = ""

		meanString = ""
		for k in d.keys():
			meanString += "%s(M=%2.2f, SD=%2.2f) and " % (self.translate(k), d[k]['mean'], d[k]['sd'])
		meanString = meanString.rstrip(' and ')

		sig, F, p = self.anova(model, dataFile)
		f_result = "F=%2.2f, p<%0.2f" %(F, p)
		if sig:
			output += "The F test passed, with %s.  " % (f_result) 

			if len(levels) == 2:
				output += "A t test was conducted, comparing the means of %s.  " % meanString
				sig, t, p = self.ttest(model, dataFile)
				result = "t = %2.2f, p<%0.2f" % (t, p)
				if sig and largest == levels[1]:
					output += "This passed with %s, %s.  " % (result, random.choice(self.rejectnull))
				elif sig:
					output += "This passed but in the wrong direction, with %s.  Looks like we called that one pretty badly.  " % result
				else:
					if t != "nan":
						if largest == levels[1]:
							output += "The t test did not pass.  That the mean %s of %s was the larger mean (as was predicted), though this difference was non-significant.  " % (measure, levels[1])
						else:
							output += "The t test did not pass, with %s.  " % result 


			else:
				print "Tukey's HSD Time!"
		else:
			if str(F) != "nan":
				output += "The F test did not pass, with %s.  " % (f_result) 
				if largest == levels[1]:
					output += "However, the mean %s of %s was the larger mean (as expected), though this difference was non-significant." % (measure, levels[1])

		output += "\n"

		return output
