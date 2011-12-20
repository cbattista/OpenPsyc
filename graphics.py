import random

class colorDict(dict):
	def __init__(self, *args, **kwargs):
		self.d = {}

	def __getitem__(self, key):
		if self.d.has_key(key):
			return self.d[key]
		else:
			c1 = random.randint(0, 10) / 10.
			c2 = random.randint(0, 10) / 10.
			c3 = random.randint(0, 10) / 10.
			self.d[key] = [c1, c2, c3]
			return self.d[key]
	
	def __setitem__(self, key, value):
		self.d[item] = value

