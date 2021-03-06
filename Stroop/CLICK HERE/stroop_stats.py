import dbAdmin
from dbAdmin import dbAdmin
import os, glob, pickle, copy
import stats

colorKey = {"red" : [255, 0, 0], "green" : [0, 255, 0], "blue" : [0, 0, 255], "white" : [255, 255, 255]}

def generateWords():
	abuse = []
	positive = []	
	neutral = []
	Ns = []	
	fakeabuse = []
	fakepositive = []	
	fakeneutral = []
	fakeNs = []	

	f = open(os.path.join(os.getcwd(), "data", "abuse.txt"), 'r')
	for lines in f.readlines():
		abuse.append(lines.strip())
	f.close()

	f = open(os.path.join(os.getcwd(), "data", "positive.txt"), 'r')
	for lines in f.readlines():
		positive.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "neutral.txt"), 'r')
	for lines in f.readlines():
		neutral.append(lines.strip())
	f.close()	
			
	f = open(os.path.join(os.getcwd(), "data", "Ns.txt"))
	for lines in f.readlines():
		Ns.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "fakeabuse.txt"), 'r')
	for lines in f.readlines():
		fakeabuse.append(lines.strip())
	f.close()

	f = open(os.path.join(os.getcwd(), "data", "fakepositive.txt"), 'r')
	for lines in f.readlines():
		fakepositive.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "fakeneutral.txt"), 'r')
	for lines in f.readlines():
		fakeneutral.append(lines.strip())
	f.close()	
			
	f = open(os.path.join(os.getcwd(), "data", "fakeNs.txt"))
	for lines in f.readlines():
		fakeNs.append(lines.strip())
	f.close()	

	return abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs

def classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs):
	if word in abuse:
		return "a"
	elif word in positive:
		return "p"
	elif word in neutral:
		return "n"
	elif word in Ns:
		return "f"
	elif word in fakeabuse:
		return "aD"
	elif word in fakepositive:
		return "pD"
	elif word in fakeneutral:
		return "nD"
	elif word in fakeNs:
		return "fD"	

def populateMemory(db):
	abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs = generateWords()
	globDir = os.path.join(os.getcwd(), "data", "P_*")	
	subDirs = glob.glob(globDir)
	for d in subDirs:
		subFile = os.path.join(d, 'subInfo.pck')
		s = open(subFile, 'r')
		sub = pickle.load(s)
		s.close()
		memoryFile = os.path.join(d, str(sub.number) + "_memory.pck")
		f = open(memoryFile, 'r')
		data = pickle.load(f)
		f.close()
		
		if sub.sex == 1:
			sex = 'female'
		else:
			sex = 'male'

		number = str(sub.number)

		for d in data:
			word = d['word']
			response = d['response']
			category = classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs)
			if category not in ['aD', 'pD', 'nD', 'fD']:
				sql = "SELECT category FROM stroop_results WHERE subject = %s AND word = '%s'" % (number, word)
				#print sql
				category = db.query(sql)[0][0]
			print category
			sql = "INSERT INTO memory_results VALUES(NULL, %s, '%s', '%s', '%s', %s)" % (number, sex, word, category, response)
			#db.query(sql)
			

def populateStroop(db):
	abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs = generateWords()
	globDir = os.path.join(os.getcwd(), "data", "P_*")	
	subDirs = glob.glob(globDir)
	for d in subDirs:
	#d = subDirs[0]	
		subFile = os.path.join(d, 'subInfo.pck')
		s = open(subFile, 'r')
		sub = pickle.load(s)
		s.close()
		stroopFile = os.path.join(d, str(sub.number) + "_stroop_data.pck")
		f = open(stroopFile, 'r')
		data = pickle.load(f)
		f.close()
		
		if sub.sex == 1:
			sex = 'female'
		else:
			sex = 'male'
		
		number = str(sub.number)
		order = 1
		last = 0
		lastcat = ""		
		acount = 0
		pcount = 0
		ncount = 0
		for item in data:
			word = item[0]
			colour = item[1]
			onset = item[2]
			response = item[3]
			rt = response - onset
			category = classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs)
			if category != None:
				if category == 'f':
					last = last + 1
					category = lastcat + "_" + category + str(last)
				else:
					if category == "a":
						acount = acount + 1
						trial = acount					
					elif category == "p":
						pcount = pcount + 1
						trial = pcount
					elif category == "n":
						ncount = ncount + 1
						trial = ncount
					last = 0
					lastcat = category
				sql = """
					INSERT INTO
					stroop_results
					VALUES (NULL, %s, "%s", "%s", %s, "%s", "%s", %s, %s, %s);
					""" % (number, sex, word, trial, category, colour, onset, response, rt)
				print sql
				db.query(sql)

def addSubColorData(sub, db = dbAdmin("stroop_study_F07")):
	globDir = os.path.join(os.getcwd(), "colordata", "P_%s" % str(sub.number))	
	d = glob.glob(globDir)[0]
	subFile = os.path.join(d, 'subInfo.pck')
	s = open(subFile, 'r')
	sub = pickle.load(s)
	s.close()
	stroopFile = os.path.join(d, str(sub.number) + "_color_data.pck")
	f = open(stroopFile, 'r')
	data = pickle.load(f)
	f.close()
	
	if sub.sex == 1:
		sex = 'female'
	else:
		sex = 'male'

	number = str(sub.number)

	trial = 0

	for item in data:
		trial = trial + 1
		word = item[0]
		colour = item[1]
		onset = item[2]
		response = item[3]
		rt = response - onset
		sql = """
			INSERT INTO
			color_results
			VALUES (NULL, %s, "%s", "%s", "%s", "%s", %s, %s, %s);
			""" % (number, sex, word, trial, colour, onset, response, rt)
		print sql
		db.query(sql)

def addSubNumberData(sub, db = dbAdmin("stroop_study_F07")):
	globDir = os.path.join(os.getcwd(), "numberdata", "P_%s" % str(sub.number))	
	d = glob.glob(globDir)[0]
	subFile = os.path.join(d, 'subInfo.pck')
	s = open(subFile, 'r')
	sub = pickle.load(s)
	s.close()
	stroopFile = os.path.join(d, str(sub.number) + "_number_data.pck")
	f = open(stroopFile, 'r')
	data = pickle.load(f)
	f.close()
	
	if sub.sex == 1:
		sex = 'female'
	else:
		sex = 'male'

	number = str(sub.number)

	trial = 0

	for item in data:
		trial = trial + 1
		word = item[0]
		colour = item[1]
		onset = item[2]
		response = item[3]
		rt = response - onset
		sql = """
			INSERT INTO
			number_results
			VALUES (NULL, %s, "%s", "%s", "%s", "%s", %s, %s, %s);
			""" % (number, sex, word, trial, colour, onset, response, rt)
		print sql
		db.query(sql)

def addSubData(sub, db = dbAdmin("stroop_study_F07")):
	abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs = generateWords()
	globDir = os.path.join(os.getcwd(), "data", "P_%s" % str(sub.number))	
	d = glob.glob(globDir)[0]
	subFile = os.path.join(d, 'subInfo.pck')
	s = open(subFile, 'r')
	sub = pickle.load(s)
	s.close()
	stroopFile = os.path.join(d, str(sub.number) + "_stroop_data.pck")
	f = open(stroopFile, 'r')
	data = pickle.load(f)
	f.close()
	
	if sub.sex == 1:
		sex = 'female'
	else:
		sex = 'male'
	
	number = str(sub.number)
	order = 1
	last = 0
	lastcat = ""		
	acount = 0
	pcount = 0
	ncount = 0
	for item in data:
		word = item[0]
		colour = item[1]
		onset = item[2]
		response = item[3]
		rt = response - onset
		category = classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs)
		if category != None:
			if category == 'f':
				last = last + 1
				category = lastcat + "_" + category + str(last)
			else:
				if category == "a":
					acount = acount + 1
					trial = acount					
				elif category == "p":
					pcount = pcount + 1
					trial = pcount
				elif category == "n":
					ncount = ncount + 1
					trial = ncount
				last = 0
				lastcat = category
			sql = """
				INSERT INTO
				stroop_results
				VALUES (NULL, %s, "%s", "%s", %s, "%s", "%s", %s, %s, %s);
				""" % (number, sex, word, trial, category, colour, onset, response, rt)
			print sql
			db.query(sql)

def makeHeaders(table):
	#which headers do we need to make
	#1 - abuse1, afollow11, afollow12, afollow13, abuse2, afollow21, afollow22, afollow23, abuse3, ...
	key = []	
	d = {}

	if table == "stroop_results":

		for word in ["a", "p", "n"]:
			for trial in ["1","2","3","4","5","6","7"]:
				myDict = copy.deepcopy(d)
				myDict['value'] = word + trial
				myDict['category'] = "'%s'" % word
				myDict['trial'] = int(trial)
				key.append(myDict)			
				for follow in ["1","2","3"]:
					myDict = copy.deepcopy(d)				
					myDict['value'] = word+trial+"f"+follow
					myDict['category'] = "'%s_f%s'" % (word, follow)
					myDict['trial'] = int(trial)
					key.append(myDict)
		print key
		return key

	elif table == "color_results" or table == "number_results":
		sql = "SELECT DISTINCT(trial) FROM %s" % table
		for trial in db.query(sql):
			myDict = copy.deepcopy(d)
			myDict['value'] = "n%i" % trial[0]
			myDict['trial'] = trial[0]
			key.append(myDict)
		print key
		return key

	else:
		print "Error : No such table"	


def makeMemoryHeaders():
	d = {}
	headers = []
	d['subject'] = ''
	for word in ["a", "p", "n", "a_f1", "p_f1", "n_f1", "aD", "pD", "nD", "fD"]:
		d[word] = ''
		headers.append(word)
	return d, headers

def writeAllMemory(db):
	d, headers = makeMemoryHeaders()	
	myHeaders = copy.deepcopy(headers)
	myHeaders.insert(0, 'subject')
	fileWriter = FileWriter(filename="AllParticipantMemory.txt")
	fileWriter.writeHeaderList(myHeaders)	
	
	subs = db.getSubjects("stroop_results")

	for sub in subs:
		myDict = copy.deepcopy(d)
		d['subject'] = str(sub)
		for h in headers:
			sql = """SELECT AVG(response) FROM memory_results WHERE subject = %s AND category = '%s'""" % (str(sub), h)
			avgResponse = db.query(sql)[0][0]
			d[h] = avgResponse
		line = []
		for h in myHeaders:
			line.append(d[h])
	
		fileWriter.writeList(line)

def addSubMemoryData(sub, db=dbAdmin("stroop_study_F07")):
	abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs = generateWords()
	number = str(sub.number)
	d = os.path.join(os.getcwd(), "data", "P_%s" % number)	
	subFile = os.path.join(d, 'subInfo.pck')
	s = open(subFile, 'r')
	sub = pickle.load(s)
	s.close()
	memoryFile = os.path.join(d, str(sub.number) + "_memory.pck")
	f = open(memoryFile, 'r')
	data = pickle.load(f)
	f.close()
	
	if sub.sex == 1:
		sex = 'female'
	else:
		sex = 'male'

	for d in data:
		word = d['word']
		response = d['response']
		category = classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs)
		if category not in ['aD', 'pD', 'nD', 'fD']:
			sql = "SELECT category FROM stroop_results WHERE subject = %s AND word = '%s'" % (number, word)
			#print sql
			#print db.query(sql)
			category = db.query(sql)[0][0]
		#print category
		sql = "INSERT INTO memory_results VALUES(NULL, %s, '%s', '%s', '%s', %s)" % (number, sex, word, category, response)
		#print sql
		db.query(sql)

def makeWordList(db):
	header = {}
	key = []

	for h in ['a', 'p', 'n', 'rt']:
		d = copy.deepcopy(header)
		d['value'] = h
		key.append(d)

	fileWriter = FileWriter(key, "wordList.txt")

	fileWriter.writeHeaders('word')

	words = db.getDistinct("word", "stroop_results")
	for word in words:
		sql = "SELECT AVG(rt), category FROM %s where word = '%s'" % ("stroop_results", word)
		result = db.query(sql)
		rt = result[0][0]
		category = result[0][1]
		if category == 'a':
			line=[word,1,0,0,rt]
		elif category =='p':
			line=[word,0,1,0,rt]
		elif category =='n':
			line=[word,0,0,1,rt]
		fileWriter.writeList(line)

def allWords():
	abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs = generateWords()
	wordList = abuse + positive + neutral + Ns
	distractorList = fakeabuse + fakepositive + fakeneutral + fakeNs

	return wordList, distractorList

def printStroopWordResults(db=dbAdmin("stroop_study_F07")):
	subs = db.getSubjects("stroop_results")
	words, slug = allWords()
	wordDict = {}
	
	fileWriter = FileWriter(filename = "All_Stroop_Words.txt")
	fileWriter.writeHeaderList(["subject"] + words)

	for sub in subs:
		d = copy.deepcopy(wordDict)
		for word in words:
			d[word] = ''
		for word in words:
			sql = """SELECT rt FROM stroop_results WHERE subject = %s and word = '%s'""" % (sub, word)
			rt = db.query(sql)
			try:
				d[word] = rt[0][0]
			except:
				pass
		timeList = [str(sub)]
	
		for word in words:
			timeList.append(d[word])

		fileWriter.writeList(timeList)

def printMemoryWords(db=dbAdmin("stroop_study_F07")):
	subs = db.getSubjects("memory_results")
	target, distractor = allWords()
	
	words = target + distractor

	wordDict = {}

	fileWriter = FileWriter(filename = "All_Memory_Words.txt")
	fileWriter.writeHeaderList(["subject"] + words)

	for sub in subs:
		d = copy.deepcopy(wordDict)
		for word in words:
			d[word] = ''
		for word in words:
			sql = """SELECT response FROM memory_results WHERE subject = %s and word = '%s'""" % (sub, word)
			response = db.query(sql)
			try:
				d[word] = response[0][0]
			except:
				pass
		timeList = [str(sub)]
		
		for word in words:
			timeList.append(d[word])

		fileWriter.writeList(timeList)


def makeFollowWordList(db, table):
	d = {}
	
	header = {}
	key = []

	for h in ['a', 'p', 'n', 'rt']:
		d = copy.deepcopy(header)
		d['value'] = h
		key.append(d)

	fileWriter = FileWriter(key, "followWordList.txt")

	fileWriter.writeHeaders('word')

	d = {}

	words = db.getDistinct("word", "stroop_results")
	for word in words:
		d[word] = ''

	subs = db.getSubjects("stroop_results")

	for sub in subs:
		for word in words:		
			sql = """SELECT
					trial, category FROM %s WHERE word = '%s' AND SUBJECT = %s
				""" % (table, word, sub)
			result = db.query(sql)
			trial = result[0][0]
			category = result[0][1]
			cat = category+"_f1"
			sql = """SELECT rt FROM %s where category = '%s' AND trial = %s AND SUBJECT = %s""" % (table, cat, trial, sub)
			#print sql
			result = db.query(sql)
			if d[word]:
				rt = (d[word][0] + result[0][0]) / 2
				d[word] = [rt, category]
			else:
				d[word] = [result[0][0], category]

	myList = []
	for word in words:
		category = d[word][1]
		rt = d[word][0]
		if category == 'a':
			line=[word,1,0,0,rt]
		elif category =='p':
			line=[word,0,1,0,rt]
		elif category =='n':
			line=[word,0,0,1,rt]
		fileWriter.writeList(line)

	

class FileWriter:
	def __init__(self, key=[], filename=""):
		self.filename = filename
		self.key = key		
		self.path = os.path.join(os.getcwd(), "data", self.filename)
		self.headers = []
		for d in self.key:
			self.headers.append(d['value'])
		self.headers.sort()


	def writeHeaders(self, case):
		f = open(self.path, 'w')		
		f.write(case+",")
		f.write(self.headers[0])	
		for i in range(1, len(self.headers)):
			f.write("," + self.headers[i])
		f.write("\n")
		f.close()

	def writeHeaderList(self, myList):
		f = open(self.path, 'w')
		f.write(str(myList[0]))	
		for i in range(1, len(myList)):
			f.write("," + str(myList[i]))
		f.write("\n")
		f.close()


	def writeList(self, myList):
		f = open(self.path, 'a')
		f.write(str(myList[0]))	
		for i in range(1, len(myList)):
			f.write("," + str(myList[i]))
		f.write("\n")
		f.close()

	def writeSubjectData(self, db, select, table, subject, all):
		columns = self.key[0].keys()
		columns.remove('value')

		sex = db.getSex(subject, table)
		if sex == "male":
			s = 2
		elif sex == "female":
			s = 1

		rtList = [subject, s]

		total = db.query("SELECT COUNT(*) FROM %s WHERE subject = %s" % (table, subject))[0][0]
		correct = db.query("SELECT SUM(incorrect) FROM %s WHERE subject = %s" % (table, subject))[0][0]

		
		if correct:
			percCorrect = float(correct) / float(total) * 100.0
		else:
			percCorrect = 0.0


		print subject, correct, total, percCorrect


		for item in self.key:
			sql = "SELECT %s, incorrect FROM %s WHERE subject = %s" % (select, table, subject)

			for c in columns:			
				sql = sql + """ AND %s = %s """ % (c, item[c])

			#print sql

			result, incorrect = db.query(sql)[0]

			if all:
				rtList.append(result)
			else:
				if incorrect:
					rtList.append("NA")
				else:
					rtList.append(result)

		rtList.append(percCorrect)

		self.writeList(rtList)
	
def writeAllSubjects(db, table, all=False):
	subList = db.getSubjects(table)
	if all:
		string = "_allresps"
	else:	
		string = "_corresps"
	
	fileWriter = FileWriter(makeHeaders(table), "All_%s_data%s.txt" % (table, string))
	fileWriter.writeHeaders("subject, sex")
	for sub in subList:
		fileWriter.writeSubjectData(db, "rt", table, sub, all)

def calculateZ(db, table):
	subList = db.getSubjects(table)
	for s in subList:
		d = {}
		sql = "SELECT ROWID, RT, incorrect FROM %s WHERE subject = %s" % (table, s)
		for rowid, RT, incorrect in db.query(sql):
			if not incorrect:
				d[str(rowid)] = RT

		avg = stats.mean(d.values())
		std = stats.samplestdev(d.values())
		for rowid in d.keys():
			z = d[rowid] - avg / std
			sql = "UPDATE %s SET zscore = %f WHERE ROWID = %s" % (table, z, rowid)
			db.query(sql)
			
def wordSummary(db, table):
	f = open("wordSummary_%s.txt" % table, 'w')
	d = {}
	header = "word, length, rtAVG, rtSTD, total, percCorrect\n"
	f.write(header)
	wordList = []
	sql = "SELECT DISTINCT(word) FROM %s" % table
	for w in db.query(sql):
		wordList.append(w[0])
		
	for word in wordList:
		sql = "SELECT RT FROM %s WHERE word = '%s' AND incorrect = 0" % (table, word)
		wordLen = len(word)
		rtList = []
		zList = []

		for rt in db.query(sql):
			rtList.append(rt[0])

		rtAVG = stats.mean(rtList)
		rtSTD = stats.samplestdev(rtList)


		total = db.query("SELECT COUNT(*) FROM %s WHERE word = '%s'" % (table, word))[0][0]
		percCorrect = float(len(rtList)) / float(total) * 100.0

		print len(rtList), total

		myString = "%s, %i, %f, %f, %i, %f\n" % (word, wordLen, rtAVG, rtSTD, total, percCorrect)
		print myString
		f.write(myString)


	f.close()


def addGrades(db, table, gradeSheet):
	f = open(os.path.join("errors", gradeSheet), 'r')
	for line in f.readlines():
		grades = line.split(',')
		t = 1
		subject = grades.pop(0)
		for g in grades:
			sql = "UPDATE %s SET incorrect = %s WHERE subject = %s AND trial = %i" % (table, g, subject, t)
			t = t + 1
			print sql
			db.query(sql)

def writeByCategory(db, table):
	f = open("%s_by_category.txt" % table, "w")
	subList = db.getSubjects(table)

	for subject in subList:

		sex = db.getSex(subject, table)
		if sex == "male":
			se = 2
		elif sex == "female":
			se = 1

		f.write(str(subject) + "," + str(se) + ",")


		total = db.query("SELECT COUNT(*) FROM %s WHERE subject = %s" % (table, subject))[0][0]
		correct = db.query("SELECT SUM(incorrect) FROM %s WHERE subject = %s" % (table, subject))[0][0]

		
		if correct:
			percCorrect = float(correct) / float(total) * 100.0
		else:
			percCorrect = 0.0

		sql = "SELECT category, RT, zscore, incorrect FROM %s WHERE subject = %s" % (table, subject)
		d = {}

		for cat, RT, zscore, incorrect in db.query(sql):
			if d.has_key(cat):
				pass
			else:
				d[cat] = []


			if incorrect == 0 and zscore <= 3 and zscore >= -3:
				#print s, cat, RT, zscore, incorrect
				d[cat].append(RT)

		key = d.keys()
		key.sort()
		string = ""
		for k in key:
			print k
			if d[k]:
				avg = stats.mean(d[k])
				std = stats.samplestdev(d[k])
			else:
				avg = "NA"
				std = "NA"

			string = string + "," + str(avg) + "," + str(std)
		
		f.write(string)
		f.write("," + str(percCorrect) + "\n")

	f.close()
		

def writeByTrial(db, table):
	f = open("%s_by_trial.txt" % table, "w")
	subList = db.getSubjects(table)

	for subject in subList:

		sex = db.getSex(subject, table)
		if sex == "male":
			se = 2
		elif sex == "female":
			se = 1

		f.write(str(subject) + "," + str(se) + ",")


		total = db.query("SELECT COUNT(*) FROM %s WHERE subject = %s" % (table, subject))[0][0]
		correct = db.query("SELECT SUM(incorrect) FROM %s WHERE subject = %s" % (table, subject))[0][0]

		
		if correct:
			percCorrect = float(correct) / float(total) * 100.0
		else:
			percCorrect = 0.0


		baseID = db.query("SELECT MIN(ROWID) FROM %s WHERE subject = %s" % (table, subject))[0][0]


		sql = "SELECT ROWID, RT, zscore, incorrect FROM %s WHERE subject = %s" % (table, subject)


		d = {}

		for rowid, RT, zscore, incorrect in db.query(sql):
			trial = rowid - baseID + 1
			if d.has_key(trial):
				pass
			else:
				d[trial] = "NA"


			if incorrect == 0 and zscore <= 3 and zscore >= -3:
				#print s, cat, RT, zscore, incorrect
				d[trial] = RT

		key = d.keys()
		key.sort()
		print key
		string = ""
		for k in key:
			print "t" + str(k)

			if d[k]:
				avg = d[k]
			else:
				avg = "NA"

			string = string + "," + str(avg)
		
		f.write(string)
		f.write("," + str(percCorrect) + "\n")

	f.close()


db = dbAdmin("stroop_study_F07")
table = "stroop_results"

writeByTrial(db, table)

#for t in ["number_results", "color_results", "stroop_results"]:
#	db.addColumn(t, "zscore", "REAL")

#calculateZ(db, table)
#wordSummary(db, table)

#addGrades(db, "stroop_results", "emot_errors.csv")

#createStroop(db)
#createMemory(db)

#populateStroop(db)

#sql = "DROP COLUMN mr_id FROM stroop_results;"

#sql = "DELETE FROM stroop_results where subject = 666"

#sql = "DROP TABLE stroop_results;"

#sql = "SELECT subject, category, AVG(rt) FROM stroop_results GROUP BY subject, category;"

#sql = """SELECT category, trial, AVG(rt), COUNT(*) FROM stroop_results WHERE rt < 1 GROUP BY trial, category;"""

#print db.query("SELECT DISTINCT(category) FROM stroop_results")

#populateMemory(db)

#writeAllSubjects(db, table, all = False)

#writeAllMemory(db)

#printMemoryWords()

#printStroopWordResults()

#allWords()

#makeWordList(db)

#makeFollowWordList(db,"stroop_results")

#print subList

#print result

#print len(headers), len(key)
