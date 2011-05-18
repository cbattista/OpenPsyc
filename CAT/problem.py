class Problem:
	def __init__(self, ns, history=[], keys=['ACC', 'RT', 'strat', 'task']):
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


x = Problem([5, 6])
print x.distractors

y = Problem([28, 42])
print y.distractors

z = Problem([13, 13])
print z.distractors

