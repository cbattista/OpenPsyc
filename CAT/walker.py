#walker.py
from problem import *
import random

class Walker:
	"""
	gives you random problems with operands between 1 and maxOp(int)
	"""

	def __init__(self, maxOp=50, minOp = 2, direction="up", stepSize=[1,2,3,4], cycles=1, *args, **kwargs):
		self.maxOp = maxOp
		self.minOp = minOp
		self.direction = direction
		self.stepSize = stepSize
		self.ns = [minOp, minOp]
		self.cycles = cycles
		self.ccount = 0.0

	def setNs(self):
		n1 = self.ns[0]
		n2 = self.ns[1]
		if self.direction == "up":
			n1 += random.choice(self.stepSize)
			n2 += random.choice(self.stepSize)
			#if we've reached our maximum operand size
			if n1 >= self.maxOp and n2 >= self.maxOp:
				self.direction = "down"
				self.ccount += 0.5
				

		if self.direction == "down":
			n1 -= random.choice(self.stepSize)
			n2 -= random.choice(self.stepSize)

			n1 = abs(n1)
			n2 = abs(n2)

			if n1 == 0:
				n1 = random.choice(self.stepSize)
			if n2 == 0:
				n2 = random.choice(self.stepSize)

			if n1 < self.minOp and n2 < self.minOp:
				self.direction = "up"
				self.ccount += 0.5

		self.ns = [n1, n2]

	def next(self):
		self.setNs()
		#if there is a desired amount of cycles
		if self.cycles:
			if self.ccount < self.cycles:
				return Problem(self.ns)
			else: 
				return None
		else:
			return Problem(self.ns)

	def reset(self):
		##
		self.ccount = 0.0

class LineWalker(Walker):
	"""
	walks up and down a particular number's list of operands
	"""
	def __init__(self, number=10, *args, **kwargs):
		Walker.__init__(self, *args, **kwargs)
		self.number = number
		self.n = self.minOp

	def setNs(self):
		if self.direction == "up":
			self.n += random.choice(self.stepSize)

			if self.n > self.maxOp:
				self.direction = "down"
				self.ccount += 0.5

		if self.direction == "down":
			self.n -= random.choice(self.stepSize)
			
			if self.n < self.minOp:
				self.direction = "up"
				self.ccount += 0.5

			self.n = self.n

		self.ns = [self.n, self.number]

class RangeWalker(Walker):
	"""
	walks up and down a particular range of operands
	"""
	def __init__(self, range1, range2, *args, **kwargs):
		Walker.__init__(self, *args, **kwargs)
		#we're actually going to use two LineWalkers to make this happen
		self.w1 = LineWalker(maxOp=range1[1], minOp=range1[0], number=1, cycles=0)
		self.w2 = LineWalker(maxOp=range2[1], minOp=range2[0], number=1, cycles=0)
					
	def setNs(self):
		n1 = self.w1.next().row['ns'][1]
		n2 = self.w2.next().row['ns'][1]
		self.ns = [n1, n2]


class Walkers:
	"""polls a group of walkers for problems
	"""

	def __init__(self, walkers):
		self.walkers = walkers

	def next(self):
		random.shuffle(self.walkers)

		for w in self.walkers:
			p = w.next()
			if p:
				return p

		return None				


