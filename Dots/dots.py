#dots.py

import sys
import os
import pickle
from VisionEgg.Textures import *
from VisionEgg.Core import *

sys.path.append("c:\code\OpenPsyc")

import experiments
import subject
import shuffler
import CBalance

sub = subject.Subject(1, experiment = "dots")

blocks = ["sequential", "paired", "overlapping"]

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

stimLib = "stimLib"

if os.path.exists("colButton.pck"):
	f = open("colButton.pck")
	col = pickle.load(f)
	f.close()
else:
	col = [1, 2]

yellowB = col[0]
blueB = col[1]

f = open("colButton.pck", "w")
col.reverse()
pickle.dump(col, f)
f.close()
	
screen = get_default_screen()

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
	
	if event.key == pygame.locals.K_1:
		if yellowB == 1 and correct == "yellow":
			sub.inputData(trial, "ACC", 1)
		elif blueB == 1 and correct == "blue":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)
	elif event.key == pygame.locals.K_2:
		if yellowB == 2 and correct == "yellow":
			sub.inputData(trial, "ACC", 1)
		elif blueB == 2 and correct == "blue":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)

for block in blockOrder:
	
	ratios = shuffler.Condition([.3, .4, .5, .6, .7, .8], "ratio", 6)
	seeds = shuffler.Condition([4, 5, 6, 7, 8], "seed", 6)
	size = shuffler.Condition(["SC", "NSC"], "size", 5)
	exemplars = shuffler.Condition([1, 2, 3, 4], "exemplar", 20)
	
	order = ["large", "small"]
	color = ["C1", "C2"]
	trials = 240

	cDict = {}
	cDict["C1"] = "blue"
	cDict["C2"] = "yellow"
	
	myShuffler = shuffler.MultiShuffler([ratios, seeds, size, exemplars], trials)
	sideShuffler = shuffler.Shuffler(order, trials, 3)
	colorShuffler = shuffler.Shuffler(color, trials, 3)
	
	stimList = myShuffler.shuffle()
	sideList = sideShuffler.shuffle()
	colorList = colorShuffler.shuffle()

	instructionText = "In this experiment you will see 2 groups of dots, 1 yellow, and 1 blue.\nYour job is to indicate which group has more dots in it.\nPress %s for yellow, press %s for blue.\nPRESS SPACE TO CONTINUE." % (yellowB, blueB)
		
	experiments.showInstructions(screen, instructionText)
	
	for stim, order, color in zip(stimList, sideList, colorList):
		ratio = getattr(stim, "ratio")
		n1 = getattr(stim, "seed")
		n2 = int(n1 * 1/ratio)
		size = getattr(stim, "size")
		exemplar = getattr(stim, "exemplar")
		
		sub.inputData(trial, "ACC", "NA")
		sub.inputData(trial, "RT", "NA")
		sub.inputData(trial, "block", block)
		sub.inputData(trial, "ratio", ratio)
		sub.inputData(trial, "n1", n1)
		sub.inputData(trial, "n2", n2)
		sub.inputData(trial, "sizectrl", size)
		sub.inputData(trial, "exemplar", exemplar)
		sub.inputData(trial, "order", order)
		sub.inputData(trial, "largecolor", cDict[color])
		sub.inputData(trial, "yellowButton", yellowB)
		sub.inputData(trial, "blueButton", blueB)
		
		if block == "overlapping":
			fname = "%s_%s_%s_%s_%s_OL_%s.bmp" % (ratio, n1, n2, exemplar, color, size)
						
			t = Texture(Image.open(os.path.join(stimLib, fname)))
			x = screen.size[0] / 2
			y = screen.size[1] / 2
			s = TextureStimulus(texture = t, position = (x, y), anchor = 'center')
			v = Viewport(screen=screen, stimuli=[s])
			p = Presentation(go_duration = (0.5, 'seconds'), viewports=[v])
			p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
			p.go()
		
		else:
			if order == "large":
				fname1 = "%s_%s_%s_%s_%s_S2_%s.bmp" % (ratio, n1, n2, exemplar, color, size)
				fname2 = "%s_%s_%s_%s_%s_S1_%s.bmp" % (ratio, n1, n2, exemplar, color, size)
			else:
				fname1 = "%s_%s_%s_%s_%s_S1_%s.bmp" % (ratio, n1, n2, exemplar, color, size)
				fname2 = "%s_%s_%s_%s_%s_S2_%s.bmp" % (ratio, n1, n2, exemplar, color, size)
				
			####
			t1 = Texture(Image.open(os.path.join(stimLib,fname1)))
			t2 = Texture(Image.open(os.path.join(stimLib,fname2)))

			if block == "sequential":
				x = screen.size[0] / 2
				y = screen.size[1] / 2

				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x, y), anchor = 'center')	

				#create viewports
				v1 = Viewport(screen=screen, stimuli=[s1])
				v2 = Viewport(screen=screen, stimuli=[s2])
				
				p1 = Presentation(go_duration=(0.5, 'seconds'), viewports=[v1])
				p = Presentation(go_duration=(0.5, 'seconds'), viewports=[v2])
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p1.go()
				p.go()
				
			else:
				x = screen.size[0] / 4
				y = screen.size[1] / 2
				
				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x * 3, y), anchor = 'center')	

				v = Viewport(screen=screen, stimuli=[s1,s2])
				p = Presentation(go_duration=(0.5, 'seconds'), viewports=[v])
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p.go()
				
		trial += 1
		sub.printData()