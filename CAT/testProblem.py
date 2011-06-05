#testProblem.py

import unittest
import random
import problem

problems = []

trial = 0

while trial < 50:
	trial += 1
	strat = random.choice(['mem', 'calc'])
	ns = random.choice([[2,4], [12,14], [25,26], [7, 9], [4, 32]])
	ACC = random.choice([1, 1, 1, 1, 0])
	RT = random.randrange(500, 1500, 5)
	misfire = random.choice([0,0,0,0,0])
	history = {'trial':trial, 'strat':strat, 'ACC':ACC, 'RT':RT, 'misfire':misfire}
	p = problem.Problem(ns, history)
	problems.append(p)

class TestProblems(unittest.TestCase):
	def setUp(self):
		self.Problems = problem.Problems()

	def testClassify(self):
		p = problems[0]
		self.Problems.classify(p)
		self.assertTrue(p.history[0]['strat'] in self.Problems.strats)

	"""
	def testAppend(self):
		for p in problems:
			self.Problems.append(p)
		assertTrue(len(self.Problems.problems) >= 1)
	"""

if __name__ == '__main__':
    unittest.main()
		
