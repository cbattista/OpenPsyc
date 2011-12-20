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
		self.make()
		self.calculateHRFs()

	def make(self):
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

		times = []
		labels = []
		
		scanTime = 0

		t = 0
		while t < self.trials:
			for e in events:
				times.append(scanTime)

				if e[0] == 'ISI':
					scanTime += isis[t]
				else:
					scanTime += e[1]
		
				labels.append(e[0])
			t+=1

		self.times = times
		self.labels = labels

	def calculateHRFs(self):
		#make a dict to hold the hrfs 
		events = list(set(self.labels))
		HRFs = {}
		
		for e in events:

			hrfs = None
			for trial in range(0, self.trials):
				#hrf
				hrf = fmri.hrf.gamma_hrf(self.duration, delta=self.times[trial*3], Fs=self.sample_res)
				if trial:
					#print len(hrfs)
					if len(hrf) != len(hrfs):
						hrf = numpy.append(hrf, 0)

					hrfs += hrf
					
				else:
					hrfs = hrf					

			#do a column sum and put it into the dict
			HRFs[e] = hrfs

		self.HRFs = HRFs


	def show(self):

		pylab.figure()

		cDict = colorDict()

		for etime, label in zip(self.times, self.labels):
			c = cDict[label]
			pylab.plot([etime, etime], [0, 1.1], color=c)

		#make an array of the timepoints
		t = numpy.linspace(0, self.duration, self.duration * self.sample_res)
		
		for k in self.HRFs.keys():		
			pylab.plot(t, self.HRFs[k], label=k)
		#print self.HRFs

		pylab.show()

events = [['prob', 2], ['soln',4], ['ISI']]

jt = jitterTool(events, sample_res = 3)

jt.show()
