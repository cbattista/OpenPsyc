#dots.py

import sys
import os
import pickle
import time
import random

from VisionEgg.Textures import *
from VisionEgg.Core import *
from VisionEgg.FlowControl import TIME_INDEPENDENT

sys.path.append(os.path.split(os.getcwd())[0])

import experiments
import subject
import shuffler
import CBalance

myArgs = sys.argv

try:
	number = int(myArgs[1])
except:
	number = 666

sub = subject.Subject(number, experiment = "dots")


#SETTINGS

blocks = ["sequential", "paired", "overlapping"]

breakText = "Time for a break.\nPRESS SPACE TO CONTINUE."
break_trial = 60

#total trials
trials = 240

#of the total trials, how many do you want to run (good for testing), put -1 for all
subtrials = 3

#total duration of each dot array, in seconds
dot_duration = 0.75


if os.path.exists("cb.pck"):
	f = open("cb.pck")
	cb = pickle.load(f)
	f.close()
else:
	cb = CBalance.Counterbalance(blocks)

blockOrder = cb.advance()

f = open("cb.pck", "w")
pickle.dump(cb, f)
f.close()

stimLib = "stimuli"
	
screen = get_default_screen()

screen.parameters.bgcolor = (.52, .51, .52)

pygame.init()

trial = 1
	
	
def keyFunc(event):
	global color
	global cDict
	global yellowB
	global blueB
	global trial
	
	correct = cDict[color]

	RT = p.time_sec_since_go
	
	sub.inputData(trial, "RT", RT)
	
	if event.key == pygame.locals.K_LCTRL:
		if yellowB == "Left CTRL" and correct == "yellow":
			sub.inputData(trial, "ACC", 1)
		elif blueB == "Left CTRL" and correct == "blue":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)
	elif event.key == pygame.locals.K_RCTRL:
		if yellowB == "Right CTRL" and correct == "yellow":
			sub.inputData(trial, "ACC", 1)
		elif blueB == "Right CTRL" and correct == "blue":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)

	p.parameters.go_duration = (0.1, 'seconds')

#fixation pause
#show blank screen
fixText, fixCross = experiments.printWord(screen, '+', 60, (0, 0, 0))
pause = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])

blockIns = {}
blockIns['paired'] = "The groups will both appear at the same time."
blockIns['sequential'] = "The groups will appear one after the other."
blockIns['overlapping'] = "The groups will both appear at the same time."
		
for block in blockOrder:

	print "creating instructions..."
	
	if os.path.exists("colButton.pck"):
		f = open("colButton.pck", "r")
		col = pickle.load(f) 
		col.reverse()
		f.close()
	else:
		col = ["Left CTRL", "Right CTRL"]

	f = open("colButton.pck", "w")
	pickle.dump(col, f)
	f.close()


	yellowB = col[0]
	blueB = col[1]

	
	instructionText = "In this experiment you will see 2 groups of dots.\n%s\n  Each group will be either yellow or blue.  Your job is to choose which group has more dots in it.\n\nPress %s for yellow.\nPress %s for blue.\n\nPRESS SPACE TO CONTINUE." % (blockIns[block], yellowB, blueB)


	print "entering block %s" % block
	ratios = shuffler.Condition([.83, .8, .75, .5, .33, .25], "ratio", 6)
	seeds = shuffler.Condition([4, 5, 6, 7, 8], "seed", 6)
	size = shuffler.Condition(["con", "incon"], "size", 5)
	exemplars = shuffler.Condition([1, 2, 3, 4], "exemplar", 20)
		
	order = ["large", "small"]
	color = ["C1", "C2"]

	cDict = {}
	cDict["C1"] = "blue"
	cDict["C2"] = "yellow"
	print "loading ratio/seed/seize/exemplar order..."
	myShuffler = shuffler.MultiShuffler([ratios, seeds, size, exemplars], trials)
	stimList = myShuffler.shuffle()

	sides = shuffler.Condition(order, "sides", 5)
	colors = shuffler.Condition(color, "colors", 6)

	print "loading sides/colors order..."
	csShuffler = shuffler.MultiShuffler([sides, colors], trials)
	csList = csShuffler.shuffle()
	
	print "loading pause durations..."
	pauseTimes = [.250, .350, .450, .550, .650, .750] * 40
	random.shuffle(pauseTimes)


	print "creating stimulus displays windows..."
	if block == "overlapping" or block == "sequential":
		x = screen.size[0] / 2
		y = screen.size[1] / 2

		mt = Texture(Image.open("mask.BMP"))
		ms = TextureStimulus(texture = mt, position = (x, y), anchor = 'center')
		mv = Viewport(screen=screen, stimuli=[ms])
		mask = Presentation(go_duration = (0.5, 'seconds'), viewports=[mv])
	else:

		x = screen.size[0] / 4
		y = screen.size[1] / 2

		print x

		mt1 = Texture(Image.open("mask.BMP"))
		mt2 = Texture(Image.open("mask.BMP"))
		ms1 = TextureStimulus(texture = mt1, position = (x, y), anchor = 'center')
		ms2 = TextureStimulus(texture = mt2, position = (x * 3, y), anchor = 'center')
		mv = Viewport(screen=screen, stimuli=[ms1, ms2])
		mask = Presentation(go_duration = (0.5, 'seconds'), viewports=[mv])
		

	print "Beginning block now..."
	experiments.showInstructions(screen, instructionText, textcolor=(0, 0, 0))

	for stim, cs, pauseTime in zip(stimList[:subtrials], csList[:subtrials], pauseTimes[:subtrials]):
		pause.parameters.go_duration = (pauseTime, 'seconds')
		pause.go()

		ratio = getattr(stim, "ratio")
		n1 = getattr(stim, "seed")
		n2 = int(n1 * 1/ratio)
		size = getattr(stim, "size")
		exemplar = getattr(stim, "exemplar")
		
		side = getattr(cs, "sides")
		color = getattr(cs, "colors")
		
		sub.inputData(trial, "ACC", "NA")
		sub.inputData(trial, "RT", "NA")
		sub.inputData(trial, "block", block)
		sub.inputData(trial, "ratio", ratio)
		sub.inputData(trial, "n1", n1)
		sub.inputData(trial, "n2", n2)
		sub.inputData(trial, "sizectrl", size)
		sub.inputData(trial, "exemplar", exemplar)
		sub.inputData(trial, "order", side)
		sub.inputData(trial, "largecolor", cDict[color])
		sub.inputData(trial, "yellowButton", yellowB)
		sub.inputData(trial, "blueButton", blueB)
		sub.inputData(trial, "pauseTime", pauseTime)		

		if block == "overlapping":
			fname = "%s_%s_%s_%s_%s_OL.bmp" % (ratio, n1, color, size, exemplar)
						
			t = Texture(Image.open(os.path.join(stimLib, fname)))
			s = TextureStimulus(texture = t, position = (x, y), anchor = 'center')
			v = Viewport(screen=screen, stimuli=[s])
			p = Presentation(go_duration = (dot_duration, 'seconds'), viewports=[v])
			p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
			p.go()
			
			mask.go()
		
		else:
			if side == "large":
				fname1 = "%s_%s_%s_%s_%s_S2.bmp" % (ratio, n1, color, size, exemplar)
				fname2 = "%s_%s_%s_%s_%s_S1.bmp" % (ratio, n1, color, size, exemplar)
			else:
				fname1 = "%s_%s_%s_%s_%s_S1.bmp" % (ratio, n1, color, size, exemplar)
				fname2 = "%s_%s_%s_%s_%s_S2.bmp" % (ratio, n1, color, size, exemplar)
				
			####
			t1 = Texture(Image.open(os.path.join(stimLib,fname1)))
			t2 = Texture(Image.open(os.path.join(stimLib,fname2)))

			if block == "sequential":
				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x, y), anchor = 'center')	

				#create viewports
				v1 = Viewport(screen=screen, stimuli=[s1])
				v2 = Viewport(screen=screen, stimuli=[s2])
				
				p1 = Presentation(go_duration=(dot_duration, 'seconds'), viewports=[v1])
				mask.go()
				p = Presentation(go_duration=(dot_duration, 'seconds'), viewports=[v2])
				mask.go()
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p1.go()
				p.go()

				
				
			else:
				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x * 3, y), anchor = 'center')	

				v = Viewport(screen=screen, stimuli=[s1,s2])
				p = Presentation(go_duration=(dot_duration, 'seconds'), viewports=[v])
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p.go()

				mask.go()

		trial += 1
		sub.printData()

		if trial % break_trial == 0 and trial != trials:
			experiments.showInstructions(screen, breakText)

