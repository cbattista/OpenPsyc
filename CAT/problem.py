import os
import sys

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools
import random

class Problems:
	def __init__(self, DB, sid=666, exp="", clear=False):
		"""class which holds a list of Problem objects, args are:
		problems = list of problems
		sid = who these problems belong to
		exp = experiment in which these problems were collected
		"""
		
		self.DB = mongoTools.MongoAdmin(DB)
		if not exp:
			self.posts = self.DB.getTable("%s_problems" % sid)
		else:
			self.posts = self.DB.getTable("%s_%s_problems" % (sid, exp))
		self.sid = sid
		self.exp = exp

		if clear:
			self.posts.remove({})

	def __str__(self):
		heaps = self.count({'kind':'temp'})
		calcs = self.count({'kind':'verified', 'strat':'calc'})
		mems = self.count({'kind':'verified', 'strat':'mem'})
		tcalcs = self.count({'kind':'temp', 'strat':'calc'})
		tmems = self.count({'kind':'temp', 'strat':'mem'}) 
		output = "mem: (%s)%s, calc: (%s)%s, heap: %s\n" % (tmems, mems, tcalcs, calcs, heaps)
		return output

	def getCounts(self, q = {}):
		output = {}
		if not q:
			output['heap'] = self.count({'kind':'temp'})
			output['calc'] = self.count({'kind':'verified', 'strat':'calc'})
			output['mem'] = self.count({'kind':'verified', 'strat':'mem'})
			output['tcalc'] = self.count({'kind':'temp', 'strat':'calc'})
			output['tmem'] = self.count({'kind':'temp', 'strat':'mem'}) 
		else:
			output = self.count(q)

		return output		

	def append(self, problem):
		"""add a problem to the list of problems
		if the problem is already in the list, add to its history
		"""
		row = self.posts.find_one({'id' : str(problem)})

		if row:
			print "appending to existing problem: %s" % row['id']
			h = row['history']
			for r in problem.row['history']:
				h.append(r)
			print h
			row['history'] = h
			self.posts.save(row)
		else:
			row = {}
			row['id'] = str(problem)
			for k in problem.row.keys():
				row[k] = problem.row[k]
			row['sid'] = self.sid
			row['exp'] = self.exp
			self.posts.save(row)		

		self.classify(row['id'])

	def stratReport(self, s='mem'):
		q = {'strat': s, 'kind' : {'$ne': 'erratic'}}

		#RTs = self.distinct('RT', q)
		ns = self.distinct('n1', q)
		ns += self.distinct('n2', q)
		#ACCs = self.distinct('ACC', q)
		solutions = self.distinct('solution', q)

		#operand range
		opRange = [min(ns), max(ns)]	

		#solution range
		solRange = [min(solutions), max(solutions)]
		"""
		#RT
		RT = sum(RTs) / len(RTs)

		#ACC
		ACC = sum(ACCs) / len(ACCs)
		"""
		return opRange, solRange

	def suggestProblem(self, kind='mem'):
		if kind == 'mem':
			ops, sols = self.stratReport('mem')
		elif kind == 'calc':
			ops, sols = self.stratReport('calc')
		else:
			raise Exception("I need either mem or calc you gave %s" % kind)

		badProblem = True
		
		while badProblem:
			print "Generating a %s" % kind
			n1 = random.choice(range(ops[0], ops[-1]+ 1))
			n2 = random.choice(range(ops[0], ops[-1]+ 1))
			solution = n1 + n2

			#is the size appropriate?
			if solution >= sols[0] and solution <= sols[1]:
				size = True
			else:
				size = False

			p = Problem([n1, n2])

			#have we seen this problem before
			if self.haveProblem(p):
				novel = False
			else:
				novel = True

			print p, novel, size

			if size and novel:
				badProblem = False

		return Problem([n1, n2])

	def getTemp(self, kind =""):
		if not kind:
			verify = random.choice(["calc", "mem"])
		else:
			verify = kind

		ids = self.distinct('id', {'strat': verify, 'kind':'temp'})
		if ids:
			pid = random.choice(ids)
			problem = self.get(pid)
			return problem
		else:
			return None

	def haveProblem(self, problem):
		row = self.posts.find_one({'id':str(problem)})

		if row:
			return True
		else:
			return False

	def classifyAll(self):
		for pid in self.posts.distinct('id'):
			self.classify(pid)


	def classify(self, p_id):
		#first let's see if it's incorrect
		kind = ""

		row = self.posts.find_one({'id' : str(p_id)})

		history = row['history']

		strat = history[0]['strat']

		if self.isIncorrect(history):
			kind = "incorrect"
		elif self.isErratic(history):
			kind = "erratic"
			#in this case, the strat may be composed of multiple strategies
			strats = ""
			for h in history:
				strat = "%s-%s" % (strat, h['strat'])
			strat = strat.lstrip("-")
		elif self.isTemporary(history):
			kind = "temp"
		elif self.isVerified(history):
			kind = "verified"
		else:
			kind = "unknown"

		row['kind'] = kind
		row['strat'] = strat

		self.posts.save(row)		

	def get(self, pid):
		problem = self.posts.find_one({'id' : pid})
		p = Problem([0, 0])
		p.row = problem
		return p

	def count(self, query={}):
		c = self.posts.find(query).count()
		return c

	def find(self, query={}, field=[]):
		if field:
			results = self.posts.find(query, fields = field)
			if len(field) == 1:
				rows = []
				for r in results:
					rows.append(r[field[0]])
			else:
				rows = results		

		else:
			rows = self.posts.find(query)
		return rows

	#accomodating some legacy code
	def query(self, query={}, field=[]):
		self.find(query, field)

	def update(self, query={}, update={}):
		if query:
			self.posts.update(query, update, multi=True)
		else:
			self.posts.update({}, document=update, multi=True)

	def save(self, row):
		self.posts.save(row)

	def distinct(self, field, query = {}):
		if query:
			items = self.posts.find(query).distinct(field)
		else:
			items = self.posts.distinct(field)
		return items

	def isIncorrect(self, history):
		"""determine whether a problem has ever
		been answered incorrectly
		"""
		ACCs = []
		for h in history:
			ACCs.append(h['ACC'])

		if set(ACCs) != set([1]):
			return True
		else:
			return False

	def isErratic(self, history):
		"""determine whether strategy report for a 
		problem is erratic or not
		returns True/False
		"""
		strats = []
		ACCs = []
		for h in history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) > 1 and (set(ACCs) == set([1])):
			return True
		else:
			return False
	
	def isTemporary(self, history):
		"""determine whether this is a 'temporary' problem
		i.e., whether it's only been answered once (and that answer was correct)
		return True/False
		"""
		if len(history) == 1 and history[0]['ACC'] == 1:
			return True
		else:
			return False

	def isVerified(self, history):
		"""determine whether this problem has had its strategy verified
		returns true/false and if true the verified strategy
		"""
		ACCs = []
		strats = []
		for h in history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) == 1 and (set(ACCs) == set([1])):
			return True
		else:
			return False


class Problem:
	def __init__(self, ns, response={}, keys=['trial', 'RT', 'ACC', 'strat', 'task', 'misfire'], operation = '+'):
		"""class which represents an arithmetic problem, args are:
		ns = digits involved
		history = a list of responses dicts to the problem
		key = list of keys expected in the response dicts

		currently only works with +, but support for -, *, / should be added
		"""
		if operation not in ['+', 'x', '*']:
			print "I can't do %s yet (sorry), going to do + instead" % operation
			self.operation = '+'
		else:
			if operation == 'x':
				self.operation = '*'
			else:
				self.operation = operation

		self.row = {}
		ns.sort()
		self.row['ns'] = ns
		self.row['history'] = []
		self.keys = keys
		self.keys.sort()

		if response:
			self.addResponse(response)

		self.row['operation'] = self.operation
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


		if self.operation == '+':
			#let's see whether it requires a carry operation (addition specific)
			n1 = int(str(self.n1)[-1])
			n2 = int(str(self.n2)[-1])

			if (n1 + n2) >= 10:
				self.row['carry'] = True
			else:
				self.row['carry'] = False

		#let's see whether the operands are odd, even, or mixed
		if (self.n1 % 2) and (self.n2 % 2):
			self.row['parity'] = "odd"
		elif (self.n1 % 2 == 0) and (self.n2 % 2 == 0):
			self.row['parity'] = "even"
		else:
			self.row['parity'] = "mixed"
		
	def suggestDistractors(self):
		distractors = []
		
		if self.row['parity'] == "mixed":
			distractors += ['+1', '+2', '-1', '-2']			
		else:
			distractors += ['+2', '-2']	

		if self.row['solution'] >= 30:
			distractors += ['+10', '-10']

		if self.operation == "*":
			distractors += ['+%s' % self.n1, '-%s' % self.n1, '+%s' % self.n2, '-%s' % self.n2]

		self.row['distractors'] = distractors
	

	def getDistractor(self):
		#DISTRACTOR CONFIG

		dist = random.choice(self.row['distractors'])
			
		distractor = eval("%s %s" % (self.row['solution'], dist))

		return distractor
