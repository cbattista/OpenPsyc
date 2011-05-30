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

		#counts of the different problems we are holding
		self.counts = {'verifieds' : {}, 'temps' : {}, 'erratics' : {}, 'incorrects' : {}}
		
		#list of the different problems that we have		
		self.verifieds = {}
		self.temps = {}
		self.erratics = {}
		self.incorrects = {}

	def append(self, problem):
		"""add a problem to the list of problems
		if the problem is already in the list, add to its history
		"""
		inList = False
		for p in self.problems:
			if problems.ns == p.ns:
				p.addResponse(problem.history)
				inList = True
				self.classify(p)
				break

		#if it's not in the list, then let's add it
		if not inList:
			self.problems.append(problem)
			self.classify(problem)

	def classify(self, problem):
		"""for a given problem, add it to the appropriate list
		and also update the list of counts 
		"""

		#first let's see if it's incorrect
		classification = ""

		lists = ["incorrects", "erratics", "temps", "verifieds"]

		strat = problem.history[0]['strat']

		if self.isInccorect(problem):
			classification = "incorrects"
		elif self.isErratic(problem):
			classification = "erratics"
			#in this case, the strat may be composed of multiple strategies
			strats = ""
			for h in problem.history:
				strat = "%s-%s" % (strat, h['strat'])
			strat = strat.lstrip("-")
		elif self.isTemporary(problem):
			classification = "temps"
		elif self.isVerified(problem):
			classification = "verifieds"
		else:
			classification = "unknown"


		if classification != "unknown":
			#add the problem to the appropriate list
			the_list = eval("self.%s['%s']" % (classification, strat))
			the_list.append(problem)
			#increment the appropriate count
			exec("self.counts['%s']['%s'] += 1" % (classification, strat))

		if classification != "unknown":
			lists.remove(classification)

		#now check for the existence of the problem in the other lists and remove if necessary
		for l in lists:
			the_list = eval("self.%s" % l)
			
			if the_list[strat].has_key(str(problem)):
				del the_list[str(problem)]
				#decrement the appropriate count
				exec("self.counts['%s']['%s'] -= 1" % (l, strat))

	def getCounts(self):
		#get the amount of incorrects and erratics (easy)
		self.counts['incorrects'] = len(self.incorrects)
		self.counts['erratics'] = len(self.erratics)
		#get the amount of temps and verifieds for each strategy (harder)
	
		td = {}
		for p in self.temps:
			strat = p.history[0]['strat']
			if td.has_key(strat):
				td[strat] += 1
			else:
				td[strat] = 1

		self.counts['temps'] = td

		vd = {}
		for p in self.verifieds:
			strat = p.history[0]['strat']
			if vd.has_key(strat):
				vd[strat] += 1
			else:
				vd[strat] = 1

		self.counts['']



	def isIncorrect(self, problem):
		"""determine whether a problem has ever
		been answered incorrectly
		"""
		ACCs = []
		for h in p.history:
			ACCs.append(h['ACC'])

		if set(ACCs) != set(['1']):
			return True
		else:
			return False

	def isErratic(self, problem):
		"""determine whether strategy report for a 
		problem is erratic or not
		returns True/False
		"""
		strats = []
		for h in p.history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) > 1 and (set(ACCs) == set(['1'])):
			return True
		else:
			return False
	
	def isTemporary(self, problem):
		"""determine whether this is a 'temporary' problem
		i.e., whether it's only been answered once (and that answer was correct)
		return True/False
		"""
		if len(p.history) == 1 and p.history['ACC'] == 1:
			return True
		else:
			return False

	def isVerified(self, problem):
		"""determine whether this problem has had its strategy verified
		returns true/false and if true the verified strategy
		"""
		strats = []
		for h in p.history:
			strats.append(h['strat'])
			ACCs.append(h['ACC'])

		if len(set(strats)) == 1 and (set(ACCs) == set(['1'])):
			return True
		else:
			return False

	def getByStrat(self, strat, ACC=1):
		"""get all [ns, history] for a particular strategy, with the option of correct or incorrect, args are:
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

		self.counts['verified'][strat] = len(problems)

		return problems

	def getTemp(self, strat):
		"""get temporary problems for a particular strategy
		"""
		problems = []

		for p in self.problems:
			#if there's only one response in the history and its strategy matches
			if len(p.history) == 1 and p.history[0]['strat'] == strat and p.history[0]['ACC']:
				problems.append(p)
		
		self.counts['temp'][strat] = len(problems)

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

		self.counts['erratic'] = len(problems)
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

