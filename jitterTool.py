#jitterTool.py
import shuffler
from nitime import fmri
import numpy
import pylab
from graphics import colorDict
import shuffler
import copy

#you will no doubt forget the hrf function's arguments
#nitime.fmri.hrf.gamma_hrf(duration, A=1.0, tau=1.08, n=3, delta=2.05, Fs=1.0)

class jitterTool:
	def __init__(self, events, conditions, trials=40, duration=300, TR=2, hrf_dur=6, sample_res = 3):
		self.TR = TR
		self.duration = duration
		self.pulses = numpy.arange(0, duration+TR, step=TR)
		self.events = events
		self.trials = trials
		self.hrf_dur = hrf_dur
		self.sample_res = sample_res


		self.conditions = conditions
		self.shuffler = shuffler.Shuffler(self.conditions, self.trials)
		self.shuffle()
		self.make()


	def makeTRs(self):
		#draw the TRs on there
		#need a gray box
		self.TRs = [0]
		tr = 0 
		while tr <= self.duration:
			tr += (self.TR * 2)
			self.TRs.append(tr)

	def shuffle(self):
		self.stimList = self.shuffler.shuffle()
		
	def makeEvents(self):
		#first take a look at the events we have
		numevents = len(self.events)
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

		#prepare the dict
		d = {}
		for e in self.events:
			d[e[0]] = {}
			for c in self.conditions:
				d[e[0]][c] = []

		self.HRFs = copy.deepcopy(d)

		while t < self.trials:
			stim = self.stimList[t]

			for e in self.events:
				d[e[0]][stim].append(scanTime)

				if e[0] == 'ISI':
					scanTime += isis[t]
				else:
					scanTime += e[1]
		
			t+=1

			self.times = d

	def calculateHRFs(self):
		#make a dict to hold the hrfs 
		events = self.times.keys()
		
		
		for e in events:
			for c in self.conditions:
				hrfs = numpy.zeros(self.duration * self.sample_res)
				for etime in self.times[e][c]:
					#hrf
					hrf = fmri.hrf.gamma_hrf(self.duration, delta=etime, Fs=self.sample_res)
					if hrfs != None:
						#print len(hrfs)
						if len(hrf) != len(hrfs):
							hrf = numpy.append(hrf, 0)

						hrfs += hrf
					
					else:
						hrfs = hrf					

				#do a column sum and put it into the dict
				self.HRFs[e][c] = hrfs

		#make an array of the timepoints
		self.hrf_times = numpy.linspace(0, self.duration, self.duration * self.sample_res)


	def evaluate(self, e, c):
		emitted = 0
		observed = 0

		for t, h in zip(self.hrf_times, self.HRFs[e][c]):
			emitted += h
	
			TR_num = int(t / (self.TR * 2))
			start = TR_num * self.TR * 2
			stop = start + self.TR

			if t >= start and t <= stop:
				observed += h

		return observed/emitted * 100
		
	def make(self):		
		self.makeEvents()
		self.makeTRs()
		self.calculateHRFs()


	def optimize(self, e, c, cycles=1000):
		best = 0
		for i in range(0, cycles):
			self.shuffle()
			result = self.evaluate(e, c)
			if self.evaluate(e, c) > best:
				best = result
				best_list = self.stimList
		

		self.stimList = best_list	
		self.make()

		f = open("best_lists.txt", "a")
		f.write("%s, %s\n\n" % (best, best_list))	
		f.close()

	def show(self, keys=[]):

		pylab.figure()
		cDict = colorDict()

		for tr in self.TRs:
			pylab.bar([tr], 1, width = self.TR, color='k', alpha=0.2)

		if not keys:
			keys = self.HRFs.keys()

		for k in keys:
			if k != 'ISI':
				for cond in self.conditions:
					pylab.plot(self.hrf_times, self.HRFs[k][cond], label=cond, color=cDict[cond])
					pylab.fill_between(self.hrf_times, self.HRFs[k][cond], color=cDict[cond], alpha=0.5)

		pylab.legend()
		pylab.show()

conditions = ['trained mem', 'trained calc', 'novel mem', 'novel calc']

events = [['prob', 2], ['soln',5], ['ISI']]

jt = jitterTool(events, conditions, sample_res = 5, duration = 300, TR = 2)

jt.optimize('prob', 'trained calc', cycles=10000)

jt.show(['prob'])


