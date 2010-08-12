#PRT_File.py

#16000 0(model kids
#jitter 

import glob
import os
import random
import pickle

def strip(item):
	item = item.strip()
	item = item.strip("\"")
	return item

class PRTFile:
	def __init__(self, csvFile, settings = "", onset = 16000, offset=1950, checkErrors=False):
		self.settings = settings
		self.onset = onset
		self.offset = offset
		self.checkErrors = checkErrors
		self.processCSV(csvFile)
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
				VARs[k].append(line[index[k]])

		self.fname = "%s.prt" % run
		print self.fname


		self.VARs = VARs

			
	def makePRTDict(self):

		VARs = self.VARs
#		print VARs
		prtDict = {}
		count = 1
		if self.checkErrors:
			prtDict['Error'] = []
		for myCond, onset, offset, subtractor, ACC in zip(VARs['Ratio'], VARs['Problem.OnsetTime'], VARs['Problem.OffsetTime'], VARs['firsttrigger.OffsetTime'], VARs['Problem.ACC']):
	
			if onset != "":
				onset = int(onset) - int(subtractor)
				offset = int(offset) - int(subtractor)
				myCond = float(myCond)
				myCond = round(myCond, 2)				

			
				myCond = "Ratio_%s" % (myCond)
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

csvs = glob.glob("*.csv")

for files in csvs:
	prtFile = PRTFile(files, settings=settings)
	prtFile.writePRT()
