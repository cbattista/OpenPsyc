import os
import sys

sys.path.append(os.path.split(os.getcwd())[0])

import mongoTools
import problem

class TrainingBuilder:
	def __init__(self, problems, setSize=20):
		self.problems = problems
		self.setSize = setSize

		self.f = open("P_%s.csv" % self.problems.sid, 'w')
		self.build('mem')
		self.build('calc')
		self.f.close()

	def build(self, strat):
		rows = self.problems.query({'strat': strat, 'kind': 'verified'})

		rows = rows.sort('solution')

		trainingProbs = []

		#want to come up with a roughly balanced set of solution sizes (trained vs untrained)
		count = 1
		for row in rows:
			#every other problem should be added to the list
			if count % 2:
				trainingProbs.append(row)
				row['trained'] = 'trained'
			else:
				row['trained'] = 'novel'

			self.problems.posts.save(row)

			count += 1	

		for p in trainingProbs[:self.setSize]:
			line = "%s, %s, %s, %s, %s\n" % (problems.sid, p['n1'], p['n2'], p['strat'], p['solution']) 
			self.f.write(line)

problems = problem.Problems("CAT3", sys.argv[1])

b = TrainingBuilder(problems)

