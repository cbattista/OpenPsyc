#jitterTool.py
import shuffler
from nitime import fmri
import numpy
import pylab
from graphics import colorDict

#you will no doubt forget the hrf function's arguments
#nitime.fmri.hrf.gamma_hrf(duration, A=1.0, tau=1.08, n=3, delta=2.05, Fs=1.0)

class jitterTool:
	def __init__(self, events, trials=25, duration=300, TR=2, hrf_dur=6, sample_res = 3):
		self.TR = TR
		self.duration = duration
		self.pulses = numpy.arange(0, duration+TR, step=TR)
		self.events = events
		self.trials = trials
		self.hrf_dur = hrf_dur
		self.sample_res = sample_res
		self.makeEvents()
		self.makeTRs()
		self.calculateHRFs()


	def makeTRs(self):
		#draw the TRs on there
		#need a gray box
		self.TRs = [0]
		tr = 0 
		while tr <= self.duration:
			tr += (self.TR * 2)
			self.TRs.append(tr)
		

	def makeEvents(self):
		#first take a look at the events we have
		numevents = len(events)
		labels = []		
		stimTime = 0

		for e in events:
			if e[0] != 'ISI':
				stimTime += e[1]
	
		stimTime = stimTime * self.trials
		isiTime = self.duration - stimTime

		avg_isi = isiTime / self.trials
		half_duration = self.hrf_dur / 2		

		isis = numpy.linspace(avg_isi - half_duration, avg_isi + half_duration, self.trials)
		numpy.random.shuffle(isis)

		times = {}
		
		scanTime = 0

		t = 0
		while t < self.trials:
			for e in events:
				if times.has_key(e[0]):
					times[e[0]].append(scanTime)
				else:
					times[e[0]] = [scanTime]

				if e[0] == 'ISI':
					scanTime += isis[t]
				else:
					scanTime += e[1]
		
			t+=1

			self.times = times

	def calculateHRFs(self):
		#make a dict to hold the hrfs 
		events = self.times.keys()
		HRFs = {}
		
		for e in events:

			hrfs = None
			for trial in range(0, self.trials):
				#hrf
				hrf = fmri.hrf.gamma_hrf(self.duration, delta=self.times[e][trial], Fs=self.sample_res)
				if trial:
					#print len(hrfs)
					if len(hrf) != len(hrfs):
						hrf = numpy.append(hrf, 0)

					hrfs += hrf
					
				else:
					hrfs = hrf					

			#do a column sum and put it into the dict
			HRFs[e] = hrfs

		#make an array of the timepoints
		self.hrf_times = numpy.linspace(0, self.duration, self.duration * self.sample_res)

		self.HRFs = HRFs

	def evaluate(self):
		for k in self.HRFs.keys():

			emitted = 0
			observed = 0

			for t, h in zip(self.hrf_times, self.HRFs[k]):
				emitted += h
			
				TR_num = int(t / (self.TR * 2))
				start = TR_num * self.TR * 2
				stop = start + self.TR

				if t >= start and t <= stop:
					observed += h

			print k, (observed/emitted * 100), observed, emitted
			

	def show(self):

		pylab.figure()
		cDict = colorDict()

		for k in self.times.keys():
			c = cDict[k]
			for etime in self.times[k]:
				pylab.plot([etime, etime], [0, 1.1], color=c)

		for k in self.HRFs.keys():
			if k != 'ISI':
				#pylab.plot(self.hrf_times, self.HRFs[k], label=k, color=cDict[k])
				pylab.fill_between(self.hrf_times, self.HRFs[k], color=cDict[k], alpha=0.5)

		for tr in self.TRs:
			pylab.bar([tr], 1, width = self.TR, color='k', alpha=0.2)

		#pylab.legend()

		pylab.show()

events = [['prob', 2], ['soln',5], ['ISI']]

jt = jitterTool(events, sample_res = 5, duration = 300, TR = 2)

jt.evaluate()

#jt.show()


