#jitterTool.py
import shuffler

class jitterTool:
	def __init__(self, events=24, offsets=12, TR=1.98):
		#how many events to jitter around
		self.events = events
		#how many different offsets to used
		self.offsets = offsets
		#TR time
		self.TR = 1.98
		self.make()

	def make(self):
		increments = self.TR / self.offsets
		jitters = [increments]
		for i in range(1, self.offsets):
			jitters.append(jitters[i-1] + increments)

		self.jitters = jitters

	def shuffle(self):
		size = self.events / self.offsets
		la = shuffler.ListAdder(self.jitters, size)
		jList = la.shuffle()
		self.jitterList= jList
		return jList


