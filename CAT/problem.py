class Problems:
	def __init__(self, problems=[], sid=666, exp=""):
		"""class which holds a list of Problem objects, args are:
		problems = list of problems
		sid = who these problems belong to
		exp = experiment in which these problems were collected
		"""
		self.problems = problems
		self.sid = sid
		self.exp = exp

	def append(self, problem):
		"""add a problem to the list of problems
		if the problem is already in the list, add to its history
		"""
		inList = False
		for p in self.problems:
			if problems.ns == p.ns:
				p.addResponse(problem.history)
				inList = True
				break

		if not inList:
			self.problems.append(problem)

	def getByStrat(self, strat, ACC=1):
		"""get all [ns, history] for a particular strategy, with the option of correct or 			incorrect, args are:
		strat = string strategy
		ACC = int accuracy
		"""
		problems = []
		for p in self.problems:
			for h in p.history:
				if h['strat'] == strat and h['ACC'] == ACC:
					problems.append([ns, history])

		return problems

	

	def getVerified(self, strat):
		"""get verified problems for a particular strategy
		"""
		problems = []

		for p in self.problems:
			strats = []
			#if the problem has more than 2 responses
			if len(p.history) > 1:
				for h in p.history:
					if h['ACC']:
						strats.append(h['strat'])
				#if all those responses are the desired strategy
				if set(strats) == set(strat):
					problems.append(p)

		return problems

	def getTemp(self, strat):
		"""get temporary problems for a particular strategy
		"""
		problems = []

		for p in self.problems:
			#if there's only one response in the history and its strategy matches
			if len(p.history) == 1 and p.history[0]['strat'] == strat and p.history[0]['ACC']:
				problems.append(p)

		return problems

	def getErratic(self):
		"""get erratically reported problems
		"""
		problems = []
		for p in self.problems:
			strats = []
			#if the problem has more than 2 responses
			if len(p.history) > 1:
				for h in p.history:
					#if the problem was answered correctly
					if h['ACC']:
						strats.append(h['strat'])
				#if there's more than one strategy in the set
				if len(set(strats)) > 1:
					problems.append(p)

		return problems

	def getMeasures(self, measure, strat):
		"""get a particular measure for a particular strategy
		"""
		measures = []

		problems = getByStrat(strat)
		for p in problems:
			measures.append(p[1][measure])		
		
		return measures

	def getSolutions(self, strat):
		"""get the solutions for a particular strategy
		"""
		solutions = []

		problems = getVerified(strat)
		for p in problems:
			solutions.append(p.solution)

		return solutions


class Problem:
	def __init__(self, ns, history=[], keys=['trial', 'RT', 'ACC', 'strat', 'task', 'misfire']):
		"""class which represents an arithmetic problem, args are:
		ns = digits involved
		history = a list of responses dicts to the problem
		key = list of keys expected in the response dicts

		currently only works with +, but support for -, *, / should be added
		"""
		self.ns = ns
		self.ns.sort()
		self.operation = "+" #eventually we'll adjust amend this class to work with other operands
		self.history = history
		self.keys = keys
		self.keys.sort()
		self.analyze()
		self.suggestDistractors()

	def __str__(self):
		output = "%s %s %s" % (self.ns[0], self.operation, self.ns[1])
		return output

	def addResponse(self, response={}):
		"""add a ppt response to this problem"""
		output = ""
		rkeys = response.keys()
		rkeys.sort()
		if rkeys != self.keys:
			output = "Warning: Provided reponse values (%s) != Expected reponse values (%s)" % (rkeys, self.keys)
		
		self.history.append(response)

		return output
			

	def analyze(self):
		"""generate some information about the problem 
		(sol'n, type of heuristic that might be employed, etc...)
		"""
		#get the solution to the problem
		self.n1 = self.ns[0]
		self.n2 = self.ns[1]
		self.solution = eval("%s %s %s" % (self.n1, self.operation, self.n2))

		#let's see whether it requires a carry operation (addition specific)
		n1 = int(str(self.n1)[-1])
		n2 = int(str(self.n2)[-1])

		if (n1 + n2) >= 10:
			self.carry = True
		else:
			self.carry = False

		#let's see whether the operands are odd, even, or mixed
		if (self.n1 % 2) and (self.n2 % 2 ):
			self.parity = "odd"
		elif (self.n1 % 2 == 0) and (self.n2 % 2 == 0):
			self.parity = "even"
		else:
			self.parity = "mixed"
		
	def suggestDistractors(self):
		distractors = []
		
		if self.parity == "mixed":
			distractors.append(1)
			distractors.append(2)
		else:
			distractors.append(2)	

		if self.solution >= 30:
			distractors.append(10)

		self.distractors = distractors

