#!/usr/bin/env python
#dots.py


import sys
import os
import pickle
import time
import random

from VisionEgg.Textures import *
from VisionEgg.Core import *
from VisionEgg.FlowControl import TIME_INDEPENDENT
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE


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


###BEGIN SETTINGS

#total trials
trials = 240

#of the total trials, how many do you want to run (good for testing), put -1 for all
subtrials = -1

#blocks to be displyaed
blocks = ["sequential", "paired", "overlapping"]

#the text presented when a break is given
breakText = "Time for a break.\nPRESS SPACE TO CONTINUE."
#take a break after this many trials
break_trial = 60

#total duration of each dot array, in seconds
dot_duration = 0.75

#total duration of each mask
mask_dur = 0.5
mask_img = Image.open("mask.BMP")

#size of fixation cross
crossSize = 80
#duration of fixation cross
cross_duration = .750
 
###END SETTINGS

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

fixText, fixCross = experiments.printWord(screen, '+', crossSize, (0, 0, 0))

trial = 1

#HANDLERS

def put_image_sequential(t_abs):
	global phase
	global start

	if not phase:
		start = t_abs
		phase = "dots1"

	t = t_abs - start


	if t >= dot_duration and phase == "dots1":
		texture_object.put_sub_image(Image.open(os.path.join(stimLib,fname2)))
		phase = "dots2"

	elif t >= (dot_duration * 2) and phase == "dots2":
		texture_object.put_sub_image(mask_img)
		phase = "mask"
	elif t >= (dot_duration * 2 + mask_dur) and phase == "mask":
		p.parameters.viewports = [fixCross]
		phase = "cross"
	elif t >= (dot_duration * 2 + mask_dur + cross_duration):
		p.parameters.go_duration = [0, 'frames']

def put_image_dual(t_abs):
	global phase
	global start

	if not phase:
		start = t_abs
		phase = "dots"

	t = t_abs - start

	if t >= dot_duration and phase == "dots":
		texture_object1.put_sub_image(mask_img)
		texture_object2.put_sub_image(mask_img)
		phase = "mask"
	elif t >= (dot_duration + mask_dur) and phase == "mask":
		p.parameters.viewports = [fixCross]
		phase = "cross"
	elif t >= (dot_duration + mask_dur + cross_duration):
		p.parameters.go_duration = (0, 'frames')

def put_image_overlapping(t_abs):
	global phase
	global start
	
	if not phase:
		start = t_abs
		phase = "dots"

	t = t_abs - start

	if t >= dot_duration and phase == "dots":
		texture_object.put_sub_image(mask_img)
		phase = "mask"
	elif t >= (dot_duration + mask_dur) and phase == "mask":
		p.parameters.viewports = [fixCross]
		phase = "cross"
	elif t >= (dot_duration + mask_dur + cross_duration):
		p.parameters.go_duration = (0, 'frames')

def keyFunc(event):
	global color
	global cDict
	global yellowB
	global blueB
	global trial
	global block
	global side	
	global pressed

	RT = p.time_sec_since_go * 1000

	if block == "sequential":
		RT-= (dot_duration * 1000)

	correct = cDict[color]
	
	sub.inputData(trial, "RT", RT)
	
	if not pressed:

		if block == "paired":

			if event.key == pygame.locals.K_LCTRL:
				if side == "large":
					sub.inputData(trial, "ACC", 1)
				else:
					sub.inputData(trial, "ACC", 0)
			elif event.key == pygame.locals.K_RCTRL:
				if side == "large":
					sub.inputData(trial, "ACC", 0)
				else:
					sub.inputData(trial, "ACC", 1)

		else:

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

		if RT <= 0:
			sub.inputData(trial, "ACC", 3)


	else:
		sub.inputData(trial, "ACC", 2)

	pressed = True


#fixation pause
#add response handlers

fixText, fixCross = experiments.printWord(screen, '+', crossSize, (0, 0, 0))

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

	
	if block == "paired":
		instructionText = "In this stage you will see 2 groups of dots.\n%s\n  Press LEFT CTRL when there are more dots on the left side of the screen.\n  Press RIGHT CTRL when there are more dots on the right side of the screen.\n\nPRESS SPACE TO CONTINUE." % (blockIns[block])
	else:
		instructionText = "In this stage you will see 2 groups of dots.\n%s\n  Each group will be either yellow or blue.  Your job is to choose which group has more dots in it.\n\nPress %s for yellow.\nPress %s for blue.\n\nPRESS SPACE TO CONTINUE." % (blockIns[block], yellowB, blueB)	 


	print "entering block %s" % block
	ratios = shuffler.Condition([.9, .75, .66, .5, .33, .25], "ratio", 6)
	seeds = shuffler.Condition([6, 7, 8, 9, 10], "seed", 6)
	size = shuffler.Condition(["con", "incon"], "size", 5)
	exemplars = shuffler.Condition([1, 2, 3, 4], "exemplar", 20)
		
	order = ["large", "small"]
	color = ["C1", "C2"]

	cDict = {}
	cDict["C1"] = "blue"
	cDict["C2"] = "yellow"
	print "loading ratio/seed/size/exemplar order..."
	myShuffler = shuffler.MultiShuffler([ratios, seeds, size, exemplars], trials)
	stimList = myShuffler.shuffle()

	sides = shuffler.Condition(order, "sides", 5)
	colors = shuffler.Condition(color, "colors", 6)

	print "loading sides/colors order..."
	csShuffler = shuffler.MultiShuffler([sides, colors], trials)
	csList = csShuffler.shuffle()
	
	print "configuring stimulus displays windows..."
	if block == "overlapping" or block == "sequential":
		x = screen.size[0] / 2
		y = screen.size[1] / 2

	else:

		x = screen.size[0] / 4
		y = screen.size[1] / 2

	print "Beginning block now..."
	experiments.showInstructions(screen, instructionText, textcolor=(0, 0, 0))

	if subtrials == -1:
		stimList = stimList
		csList = csList
	else:
		stimList = stimList[0:subtrials]
		csList = csList[0:subtrials]


	for stim, cs in zip(stimList, csList):
		pressed = False

		ratio = getattr(stim, "ratio")
		n1 = getattr(stim, "seed")
		n2 = int(round(n1 * 1/ratio, 0))
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

		if block == "overlapping":
			phase = ""
			fname = "%s_%s_%s_%s_%s_OL.bmp" % (ratio, n1, color, size, exemplar)
						
			t = Texture(Image.open(os.path.join(stimLib, fname)))
			s = TextureStimulus(texture = t, position = (x, y), anchor = 'center')
			texture_object = s.parameters.texture.get_texture_object()
			v = Viewport(screen=screen, stimuli=[s])
			p = Presentation(go_duration = ('forever', ), viewports=[v])
			p.add_controller(None, None, FunctionController(during_go_func=put_image_overlapping, temporal_variables = TIME_SEC_ABSOLUTE))
			p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
			p.go()
					
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
				phase = ""
				s = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				texture_object = s.parameters.texture.get_texture_object()				

				v = Viewport(screen=screen, stimuli=[s])
				
				p = Presentation(go_duration=('forever', ), viewports=[v])
				p.add_controller(None, None, FunctionController(during_go_func=put_image_sequential, temporal_variables = TIME_SEC_ABSOLUTE))
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p.go()

			else:
				phase = ""
				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x * 3, y), anchor = 'center')	

				texture_object1 = s1.parameters.texture.get_texture_object()
				texture_object2 = s2.parameters.texture.get_texture_object()

				v = Viewport(screen=screen, stimuli=[s1,s2])
				p = Presentation(go_duration=('forever', ), viewports=[v])
				p.add_controller(None, None, FunctionController(during_go_func=put_image_dual, temporal_variables = TIME_SEC_ABSOLUTE))
				p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
				p.go()


		if trial % break_trial == 0 and trial != trials:
			print trial, "BREAK TIME"
			experiments.showInstructions(screen, breakText, textcolor = [0, 0, 0])

		trial += 1
		sub.printData()


