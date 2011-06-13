#testProblem.py

import unittest
import random
import problem

problems = []
nsList = []
DB = "testing"
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
	nsList.append(ns)
	#print p, history

class TestProblems(unittest.TestCase):
	def setUp(self):
		self.Problems = problem.Problems(DB, clear=True)

	def test_append(self):
		for p in problems:
			self.Problems.append(p)
		self.assertTrue(self.Problems.count() >= 1)

	def test_count(self):
		for p in problems:
			self.Problems.append(p)
		c = self.Problems.count()
		self.assertTrue(c == 5)

	def test_distinct(self):
		for p in problems:
			self.Problems.append(p)
		items = self.Problems.distinct('kind')
		self.assertTrue(type(items) == list)
		items = self.Problems.distinct('kind', {'strat': 'mem'})
		self.assertTrue(type(items) == list)

	def test_classify(self):
		m = 0
		p1 = problem.Problem([3,4], {'trial':1, 'strat': 'mem', 'ACC':1, 'RT': 400, 'misfire':m})
		p2 = problem.Problem([4,3], {'trial':2, 'strat': 'mem', 'ACC':1, 'RT': 450, 'misfire':m})
		self.Problems.append(p1)
		c = self.Problems.distinct('kind')[0]
		self.assertTrue(c == 'temp')
		self.Problems.append(p2)
		c = self.Problems.distinct('kind')[0]
		self.assertTrue(c == 'verified')
		p3 = problem.Problem([3,4], {'trial':3, 'strat': 'calc', 'ACC': 1, 'RT': 500, 'misfire':m})
		self.Problems.append(p3)
		c = self.Problems.distinct('kind')[0]
		self.assertTrue(c == 'erratic')
		p4 = problem.Problem([3,4], {'trial':3, 'strat': 'calc', 'ACC': 0, 'RT': 500, 'misfire':m})
		self.Problems.append(p4)
		c = self.Problems.distinct('kind')[0]
		self.assertTrue(c == 'incorrect')

		

if __name__ == '__main__':
    unittest.main()
		
