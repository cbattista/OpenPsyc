import os
import sys

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools

class Problems:
	def __init__(self, DB, sid=666, exp=""):
		"""class which holds a list of Problem objects, args are:
		problems = list of problems
		sid = who these problems belong to
		exp = experiment in which these problems were collected
		"""
		
		self.DB = mongoTools.MongoAdmin(DB)
		self.posts = self.DB.getTable("Problems")
		self.sid = sid
		self.exp = exp

		#counts of the different problems we are holding
		self.counts = {'verifieds' : {}, 'temps' : {}, 'erratics' : {}, 'incorrects' : {}}
		
		#list of the strats that we have available
		self.strats = []

		#list of the different problems that we have		
		self.verifieds = {}
		self.temps = {}
		self.erratics = {}
		self.incorrects = {}
		self.ns = {}

	def append(self, problem):
		"""add a problem to the list of problems
		if the problem is already in the list, add to its history
		"""
		row = self.posts.find({'id' : str(problem)})

		inList = False

		if row:
			row['history'].append(problem.response)
			self.posts.save(row)
		else:
			row['id'] = str(problem)
			for k in problem.row.keys():
				row[k] = problem.row[k]
			row['sid'] = self.sid
			row['exp'] = self.exp
			print row
			self.posts.save(row)		

		self.classify(row['id'])

	def classify(self, p_id):
		"""for a given problem, add it to the appropriate list
		and also update the list of counts 
		"""

		#first let's see if it's incorrect
		classification = ""

		for row in self.posts.find():
			print row

		row = self.posts.find_one({'id' : str(p_id)})

		history = row['history']

		strat = history[0]['strat']

		if self.isIncorrect(history):
			classification = "incorrects"
		elif self.isErratic(history):
			classification = "erratics"
			#in this case, the strat may be composed of multiple strategies
			strats = ""
			for h in history:
				strat = "%s-%s" % (strat, h['strat'])
			strat = strat.lstrip("-")
		elif self.isTemporary(history):
			classification = "temps"
		elif self.isVerified(history):
			classification = "verifieds"
		else:
			classification = "unknown"

		row['classification'] = classification
		row['strat'] = strat

		self.posts.save(row)

	def count(self, query):
		c = self.posts.count(query)
		return c

	def isIncorrect(self, history):
		"""determine whether a problem has ever
		been answered incorrectly
		"""
		ACCs = []
		for h in history:
			ACCs.append(h['ACC'])

		if set(ACCs) != set(['1']):
			return True
		else:
			return False

	def isErratic(self, history):
		"""determine whether strategy report for a 
		problem is erratic or not
		returns True/False
		"""
		strats = []
		for h in history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) > 1 and (set(ACCs) == set(['1'])):
			return True
		else:
			return False
	
	def isTemporary(self, history):
		"""determine whether this is a 'temporary' problem
		i.e., whether it's only been answered once (and that answer was correct)
		return True/False
		"""
		if len(history) == 1 and history['ACC'] == 1:
			return True
		else:
			return False

	def isVerified(self, history):
		"""determine whether this problem has had its strategy verified
		returns true/false and if true the verified strategy
		"""
		strats = []
		for h in history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) == 1 and (set(ACCs) == set(['1'])):
			return True
		else:
			return False



class Problem:
	def __init__(self, ns, response={}, keys=['trial', 'RT', 'ACC', 'strat', 'task', 'misfire']):
		"""class which represents an arithmetic problem, args are:
		ns = digits involved
		history = a list of responses dicts to the problem
		key = list of keys expected in the response dicts

		currently only works with +, but support for -, *, / should be added
		"""
		self.row = {}
		ns.sort()
		self.row['ns'] = ns
		self.row['history'] = []
		self.keys = keys
		self.keys.sort()

		if response:
			self.addResponse(response)

		self.row['operation'] = "+"#eventually we'll adjust amend this class to work with other operands
		self.analyze()
		self.suggestDistractors()

	def __str__(self):
		output = "%s %s %s" % (self.row['ns'][0], self.row['operation'], self.row['ns'][1])
		return output

	def addResponse(self, response={}):
		"""add a ppt response to this problem"""
		output = ""
		rkeys = response.keys()
		rkeys.sort()
		if rkeys != self.keys:
			output = "Warning: Provided reponse values (%s) != Expected reponse values (%s)" % (rkeys, self.keys)
		
		self.row['history'].append(response)

	def analyze(self):
		"""generate some information about the problem 
		(sol'n, type of heuristic that might be employed, etc...)
		"""
		#get the solution to the problem
		self.n1 = self.row['ns'][0]
		self.n2 = self.row['ns'][1]

		self.row['n1'] = self.n1
		self.row['n2'] = self.n2

		self.row['solution'] = eval("%s %s %s" % (self.n1, self.row['operation'], self.n2))

		#let's see whether it requires a carry operation (addition specific)
		n1 = int(str(self.n1)[-1])
		n2 = int(str(self.n2)[-1])

		if (n1 + n2) >= 10:
			self.row['carry'] = True
		else:
			self.row['carry'] = False

		#let's see whether the operands are odd, even, or mixed
		if (self.n1 % 2) and (self.n2 % 2 ):
			self.row['parity'] = "odd"
		elif (self.n1 % 2 == 0) and (self.n2 % 2 == 0):
			self.row['parity'] = "even"
		else:
			self.row['parity'] = "mixed"
		
	def suggestDistractors(self):
		distractors = []
		
		if self.row['parity'] == "mixed":
			distractors.append(1)
			distractors.append(2)
		else:
			distractors.append(2)	

		if self.row['solution'] >= 30:
			distractors.append(10)

		self.row['distractors'] = distractors

