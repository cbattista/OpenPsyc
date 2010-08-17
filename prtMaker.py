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
	def __init__(self, theFile, settings = "", onset = 16000, offset=1950, checkErrors=False, eprime=True):
		self.settings = settings
		self.onset = onset
		self.offset = offset
		self.checkErrors = checkErrors
		if not eprime:
			self.processCSV(theFile)
		else:
			self.processEPrime(theFile)
		self.makePRTDict()
		self.setColors()
		self.makePRT()

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
		print txt
		f = open(txt, 'r')
		lines = map(strip, f.readlines())

		print lines[0]

		i1 = lines.index("*** Header Start ***")
		i2 = lines.index("*** Header End ***")

		print i1, i2

		header = lines[i1+1:i2]

		info = {}

		data = {}

		for h in header:
			frags = h.split(":")
			frags = map(strip, frags)
			key = frags[0]
			value = frags[1]

			info[key] = StringToType(value)

		i1 = lines.index("*** LogFrame Start ***")



		dataLines = lines[i1 + 1:]

		VARs = {}
		index = {}

		first = True

		for d in dataLines:
			hindex = 0
			if d.count(":"):
				frags = d.split(":")
				frags = map(strip, frags)
				k = frags[0]
				value = frags[1]

				print k, value

				if first:
					index[k] = hindex
					VARs[k] = []
					hindex = hindex + 1
				
				try:
					VARs[k].append(StringToType(value))
				except:
					pass
		
			elif d == "*** LogFrame End ***":
				first = False

		print VARs
				
		self.VARs = VARs
		self.fname = "%s_%s_%s.prt" % (info['Subject'], info['Experiment'], info['Session'])

			
	def makePRTDict(self):

		VARs = self.VARs
#		print VARs
		prtDict = {}
		count = 1
		if self.checkErrors:
			prtDict['Error'] = []
		for myCond, onset, jitter in zip(VARs['Condition'], VARs['SymbolPresentation.OnsetTime'], VARs['Jitter']):
	
			subtractor = self.onset
	
			if onset != "":
				onset = onset - subtractor
				offset = onset + self.offset
				myCond = myCond

				myString = "%s %s" % (onset, offset)
		
				if self.checkErrors:

					if prtDict.has_key(myCond):
						if int(ACC):
							prtDict[myCond].append(myString)
						else:
							prtDict['Error'].append(myString)
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
			print l1
			print l2

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
		#print prtDict
		prtDict = self.prtDict

		keys = prtDict.keys()
		keys.sort()

		prtString = "NrOfConditions:   %i\n\n" % len(keys)

		#print self.codeDict

		for k in keys:
			values = prtDict[k]
			#print k
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

for files in theFiles:
	prtFile = PRTFile(files, settings=settings, checkErrors=False)
	prtFile.writePRT()
