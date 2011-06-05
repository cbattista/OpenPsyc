#human.py
from mongoTools import MongoAdmin
import random
import statistician

class Human():
	#Human class - turns weird computer talk into normal person talk
	def __init__(self, db):
		#initialize a lookup table of terms
		self.db = MongoAdmin(db)
		self.hypotheses = ["It was expected that ", "It was predicted that "]
		self.interpret = ["This is probably because", "This could be due to "]
		self.acceptnull = ["Contrary to the hypothesis, however ", "Against prediction,", "Contrary to expectation, "]
		self.rejectnull = ["This was as expected.", "This was as  predicted."]
		self.signs = {'>' : 'greater than', '<' : 'less than', '==' : 'equal to'}

	def translate(self, term):
		#if a string return the available translation
		posts = self.db.getTable('factors').posts
		if type(term) == str:
			row = posts.find_one({'name': term})
			if row:
				return row['label']
			else:
				return term
		#if a list/tree get all available translations
		elif type(term) == list:

			output = "%s" % self.translate(term[0])
			for t in term[1:]:
				output += " and %s" % self.translate(t)

			return output
		#otherwise just return a string of the term
		else:
			return str(term)

	def parseAssertion(self, hyp, measure, tense="future"):
		tenses = {}
		tenses['future'] = 'would be'
		tenses['past'] = 'was'
		output = ""
		if hyp == "?":
			pass	
		else:
			for s in [">", "<", "=="]:
				if s in hyp:
					frags = hyp.split(s)
					output += "%s %s %s %s %s %s" % (self.translate(frags[0]), measure, tenses[tense], self.signs[s], self.translate(frags[1]), measure) 
					#now we should sort the fragments in ascending order and ditch the sign
					if s == ">":
						frags.reverse()

		return output, s, frags			
	

	def hypothesize(self, factors, measure, model, dataFile, condition={}, result=""):
		posts= self.db.getTable('hypotheses').posts		
		
		q = condition
		for f in factors:		
			q[f] = unicode('TARGET')
		

		row = posts.find_one(q)
		
		output = ""


		if row:
			hyp = random.choice(self.hypotheses)
			if row.has_key(measure):
				assertion, s, frags = self.parseAssertion(row[measure], measure)	
				output += "%s%s.\n" % (hyp, assertion)
				nerd = statistician.Statistician(dataFile)
				result = nerd.compareMeans(model, frags, factors, measure)		
				if result:
					output += result

		output += "\n"
		print output
		return output
	
