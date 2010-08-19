import Tkinter
from Tkinter import *
from VisionEgg.GUI import *
import time
import pickle

class Subject:
	def __init__(self, number="unknown", session="unknown", run="unknown"):		
		self.number = number
		self.session = session
		self.run = run
		self.date = time.localtime()
		#create dictionary to hold trial results
		self.fname = "%s_%s_%s_%s.csv" % (number, session, run, self.date)
		self.results = {}

	def inputData(self, trial, condition, value):
		trial = str(trial)
		print "ADDING %s, %s, %s" % (trial, condition, value)
		if self.results.has_key(trial):
			data = self.results[trial]
			data[condition] = value
			self.results[trial] = data
		else:
			data = {}
			data[condition] = value
			self.results[trial] = data					


	def printData(self):	
		trials = self.results.keys()
		intTrials = []
		for t in trials:
			intTrials.append(int(t))
		intTrials.sort()
		trials = []
		for t in intTrials:
			trials.append(str(t))
		f = open(self.fname, "w")
		for t in trials:
			line = t
			trial = self.results[t]
			trialKeys = trial.keys()
			trialKeys.sort()
			header = "trial"
			for tk in trialKeys:
				header = "%s,%s" % (header, tk)
				line = "%s,%s" % (line, trial[tk])
			header = header + "\n"			
			line = line + "\n"
			if t == "1":
				f.write(header)
			f.write(line)
		f.close()

	def preserve(self):
		f = open("%s.sub" % self.number, "w")
		pickle.dump(self, f)
		f.close()

class subjectInfoGui(AppWindow):
	def __init__(self,master=None,**cnf):

		AppWindow.__init__(self,master,**cnf)
		self.winfo_toplevel().title('Enter some participant Info')
		self.pack(expand=1,fill=Tkinter.BOTH)

		# Get the Participant Number
		Tkinter.Label(self,text="Subject Number:").pack()
		self.participantNumber = Tkinter.StringVar()
		self.participantEntry = Tkinter.Entry(self,textvariable=self.participantNumber).pack(expand=1,fill=Tkinter.X)

		Tkinter.Label(self,text="Session Number:").pack()
		self.sessionNumber = Tkinter.StringVar()
		self.sessionEntry = Tkinter.Entry(self,textvariable=self.sessionNumber).pack(expand=1,fill=Tkinter.X)

		Tkinter.Label(self,text="Run Number:").pack()
		self.runNumber = Tkinter.StringVar()
		self.runEntry = Tkinter.Entry(self,textvariable=self.runNumber).pack(expand=1,fill=Tkinter.X)
		
		Tkinter.Label(self,text="Number of Trials:").pack()
		self.trials = Tkinter.StringVar()
		self.trialsEntry = Tkinter.Entry(self,textvariable=self.trials).pack(expand=1,fill=Tkinter.X)

		# Go button
		self.gobutton = Tkinter.Button(self,text="Begin Experiment",command=self.go).pack()

	
	def go(self, master=None,**cnf):

		theText = "Subject Number: %s\nSession Number: %s\nRun Number: %s\n" % (str(self.participantNumber.get()), str(self.sessionNumber.get()), str(self.runNumber.get()))

		AppWindow.__init__(self,master,**cnf)
		self.winfo_toplevel().title('Check Info')
		self.pack(expand=1,fill=Tkinter.BOTH)

		#show the info
		Tkinter.Label(self,text=theText).pack()	
		Tkinter.Button(self,text="Yes, Begin Experiment",command=self.reallyGo).pack()
		Tkinter.Button(self,text="No, re-enter Information", command=self.__init__).pack()
		
	
	def reallyGo(self):
		#save the pickled subject data
		subNum = self.participantNumber.get()
		run = self.runNumber.get()
		session = self.sessionNumber.get()
		trials = self.trials.get()
		if trials == "":
			trials = 20
		f = open("subInfo.pck", "w")
		subData = [subNum, session, run]		
		pickle.dump(subNum, f)
		pickle.dump(run, f)
		pickle.dump(session, f)
		pickle.dump(trials, f)
		f.close()
		#now we must remove the Tk widgets, yay
		self.destroy()
		self.master.destroy()
		self.quit()
						
			
