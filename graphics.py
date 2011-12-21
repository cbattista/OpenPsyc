import random

class colorDict(dict):
	def __init__(self, *args, **kwargs):
		self.d = {}

	def __getitem__(self, key):
		if self.d.has_key(key):
			return self.d[key]
		else:
			c1 = random.randint(1, 5) / 10.
			c2 = random.randint(1, 5) / 10.
			c3 = random.randint(1, 5) / 10.

			amplify = random.choice([0, 1, 2])

			color = [c1, c2, c3]
			
			newcol = color[amplify] * 1.5
			if newcol > 1.0:
				newcol = 1.

			color[amplify] = newcol

			self.d[key] = [c1, c2, c3]
			
			

			return self.d[key]
	
	def __setitem__(self, key, value):
		self.d[item] = value

