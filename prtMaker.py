#PRT_File.py

#16000 0(model kids
#jitter 

import glob
import os
import random
import pickle

def StringToType(value):
	if value.isdigit():
		val = int(value)
		
	elif value.count('.') == 1:
		val = value.split('.')
		if val[0].isdigit() and val[1].isdigit():
			val = float(value)

	else:
		val = value

	return val

def strip(item):
	item = item.strip()
	item = item.strip("\"")
	return item

class PRTFile:
	def __init__(self, theFile, settings = "", onset = 16000, offset=1950, checkErrors=False, source="eprime"):
		self.settings = settings
		self.onset = onset
		self.offset = offset
		self.checkErrors = checkErrors
		if source == "csv":
			self.processCSV(theFile)
			self.makePRTDict()
			self.setColors()
			self.makePRT()
			self.writePRT()

		elif source == "eprime":
			self.processEPrime(theFile)
			self.makePRTDict()
			self.setColors()
			self.makePRT()
			self.writePRT()

		elif source == "database":
			self.loadFromDB(theFile[0], theFile[1])

	def processCSV(self, csv):
		f = open(csv, 'r')
		lines = f.readlines()

		run = os.path.basename(csv)
		run = run.split('.')[0]

		#self.jitter = self.jitterCodes[run]
		self.jitter = None

		#get the headers, make the variables
		headers = lines[0].split(',')
		headers = map(strip, headers)
		VARs = {}
		index = {}
		for k in headers:
			index[k] = headers.index(k)
			VARs[k] = []

		for line in lines[1:]:
			line = line.split(',')
			line = map(strip, line)
			for k in VARs.keys():
				#print k
				VARs[k].append(StringToType(line[index[k]]))

		self.fname = "%s.prt" % run
		self.VARs = VARs

	def processEPrime(self, txt):
		f = open(txt, 'r')
		lines = map(strip, f.readlines())
		f.close()


		i1 = lines.index("*** Header Start ***")
		i2 = lines.index("*** Header End ***")


		header = lines[i1+1:i2]

		info = {}

		data = {}

		for h in header:
			frags = h.split(":")
			frags = map(strip, frags)
			key = frags[0]
			value = frags[1]

			info[key] = StringToType(value)

		rows = []

			
		i1 = lines.index("*** LogFrame Start ***")

		dataLines = lines[i1 + 1:]

		VARs = {}
		index = {}

		first = True

		
		row = {}
		
		for d in dataLines:
			hindex = 0
			if d.count(":"):
				frags = d.split(":")
				frags = map(strip, frags)
				k = frags[0]
				value = frags[1]

				if first:
					index[k] = hindex
					VARs[k] = []
					hindex = hindex + 1

				row[k] = StringToType(value)
				if k == "Procedure":
					print value
					


			elif d == "*** LogFrame End ***":
				first = False
				rows.append(row)
				row = {}

		self.VARs = VARs
		self.rows = rows
		self.fname = "%s_%s_%s.prt" % (info['Subject'], info['Experiment'], info['Session'])

	def loadFromDB(self, dbName, table, s_id="Subject"):
		import mongoTools
		db = mongoTools.MongoAdmin(dbName)
		p = db.getTable(table).posts

		subjects = p.distinct(s_id)

		keys = mongoTools.GetKeys(p)

		for s in subjects:
			VARs = {}

			for k in keys:
				VARs[k.replace('_', '.')] = []

			count = 0
			
			result = p.find({s_id : s})

			for r in result:			
				for k in keys:
					newKey = k.replace('_', '.')
					if k in r.keys():
						VARs[newKey].append(r[k])
					else:
						VARs[newKey].append('')
			
			#print VARs

			self.VARs = VARs
			self.fname = "%s.prt" % s

			self.makePRTDict()
			self.setColors()
			self.makePRT()
			self.writePRT()


	def makePRTDict(self):
		catch=["6cr","6c2r", "6r", "6tr"]
		null = ["6c", "6c2", "6", "6t"]
		VARs = self.VARs

		prtDict = {}
		AVcount = 1
		AVCcount = 1
		if self.checkErrors:
			prtDict['Error'] = []
	
		lastRow = self.rows[-1]
		wait = lastRow['Wait1.RTTime']

		for row in self.rows:

			if row.has_key('Deviant'):
				deviant = row['Deviant']
			else:
				deviant = "0"
				
			if row.has_key('Procedure'):
				proc = row['Procedure']
			else:
				proc = "NOPROC"
				
			if row.has_key('DevTrial.OnsetTime'):
				onset = row['DevTrial.OnsetTime'] - wait
			else:
				onset = ""
		

			print deviant
			if onset != "":

				if deviant[0] in catch:
					myCond="catch"
				elif deviant[0] in null:
					myCond = "null"					
				else:
					deviant = int(deviant[0][0])
					if deviant==1 or deviant==3:
						myCond="0.5"
					elif deviant==4 or deviant==9:
						myCond="0.66"
					elif deviant==5 or deviant==8:
						myCond="0.75"

				offset=onset+1600

				myString = "%s %s" % (onset, offset)

				if self.checkErrors:

					if prtDict.has_key(myCond):
						if int(ACC):
							prtDict[myCond].append(myString)
						else:
							prtDict['Error' % exp].append(myString)
					else:
						if int(ACC):
							prtDict[myCond]= [myString]
						else:
							prtDict[myCond] = []
							prtDict['Error'].append(myString)

				else:
					if prtDict.has_key(myCond):
						prtDict[myCond].append(myString)
					else:
						prtDict[myCond]= [myString]
						

		self.prtDict = prtDict


	#generate a list of colours from the prtDict
	def setColors(self):
		if not os.path.exists("conditions.col"):
			codeDict = {}
			for k in self.prtDict.keys():
				R = random.randint(0, 255)
				G = random.randint(0, 255)
				B = random.randint(0, 255)
				codeDict[k] = "Color: %s %s %s" % (R, G, B)
			f = open("conditions.col", 'w')
			pickle.dump(codeDict, f)
			f.close()
		else:
			f = open("conditions.col", 'r')
			codeDict = pickle.load(f)
			f.close()
			l1 = self.prtDict.keys()
			l2 = codeDict.keys()
			l1.sort()
			l2.sort()

			if l1 != l2:
				print "Keys don't match"
				os.remove("conditions.col")
				codeDict = {}
				for k in self.prtDict.keys():
					R = random.randint(0, 255)
					G = random.randint(0, 255)
					B = random.randint(0, 255)
					codeDict[k] = "Color: %s %s %s" % (R, G, B)
				f = open("conditions.col", 'w')
				pickle.dump(codeDict, f)
				f.close()

		self.codeDict = codeDict

	def writePRT(self):
		f = open(self.fname, "w")
		f.write(self.settings)
		f.write(self.prtString)
		f.close()
		print "%s created succesfully" % self.fname

	def makePRT(self):
		prtDict = self.prtDict

		keys = prtDict.keys()
		keys.sort()

		prtString = "NrOfConditions:   %i\n\n" % len(keys)


		for k in keys:
			values = prtDict[k]
			prtString = "%s%s\n%i\n\n" % (prtString, k, len(values))
			if values:
				for v in values:
					prtString = "%s%s\n" % (prtString, v)
				prtString = "%s\n%s\n\n" % (prtString, self.codeDict[k])
			else:
				prtString = "%s%s\n\n" % (prtString, self.codeDict[k])       

		self.prtString = prtString



#MAIN PROGRAM LOOP

settings = """FileVersion:       1\n\nResolutionOfTime:   msec\n\nExperiment:         Child_SCE\n\nBackgroundColor:    0 0 0\nTextColor:          255 255 255\nTimeCourseColor:    255 255 255\nTimeCourseThick:    3\nReferenceFuncColor: 0 0 80\nReferenceFuncThick: 3\n\n"""

theFiles = glob.glob("*.txt")
for theFile in theFiles:
	prtFile = PRTFile(theFile, source="eprime", settings=settings, checkErrors=False)
print theFiles
