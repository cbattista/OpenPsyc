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
	number = int(raw_input("Enter a participant number, beeyatch:").strip())

sub = subject.Subject(number, experiment = "shapecon")


###BEGIN SETTINGS

#total trials
trials = 720

#of the total trials, how many do you want to run (good for testing), put -1 for all
subtrials = -1

#the text presented when a break is given
breakText = "Time for a break.\nPRESS SPACE TO CONTINUE."
#take a break after this many trials
break_trial = 60

#total duration of each dot array, in seconds
dot_duration = .750

#total duration of each mask
mask_dur = 0.5
mask_img = Image.open("mask.BMP")

#size of fixation cross
crossSize = 80
#duration of fixation cross
cross_duration = .750

bgcolor = (0, 0, 0)
color = (1, 1, 1)
 
###END SETTINGS

stimLib = "stimuli"
	
screen = get_default_screen()

screen.parameters.bgcolor = bgcolor

pygame.init()

fixText, fixCross = experiments.printWord(screen, '+', crossSize, color)

trial = 1

#HANDLERS

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

	correct = cDict[color]
	
	sub.inputData(trial, "RT", RT)
	if event.key == pygame.locals.K_LCTRL:
		sub.inputData(trial, "key", "L_CTRL")
	elif event.key == pygame.locals.K_RCTRL:
		sub.inputData(trial, "key", "R_CTRL")	
	else:
		sub.inputData(trial, "key", "NA")

	if not pressed:

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
		sub.inputData(trial, "ACC", 2)

	pressed = True


#fixation pause
#add response handlers

fixText, fixCross = experiments.printWord(screen, '+', crossSize, color)

instructionText = "In this experiment you will see 2 groups of dots.\nPress LEFT CTRL when there are more dots on the left.\nPress RIGHT CTRL when there are more dots on the right.\n\nPRESS SPACE TO CONTINUE."	 

ratios = shuffler.Condition([.9, .75, .66, .5, .33 ], "ratio", 6)
seeds = shuffler.Condition([6, 7, 8, 9, 10, 11], "seed", 6)
size = shuffler.Condition(["con", "incon"], "size", 6)
exemplars = shuffler.Condition([1, 2, 3, 4, 5, 6], "exemplar", 20)
shapes = shuffler.Condition(['square', 'triangle'], "shape", 7)

order = ["large", "small"]

print "loading ratio/seed/size/exemplar order..."
myShuffler = shuffler.MultiShuffler([ratios, seeds, size, exemplars, shapes], trials)

stimList = myShuffler.shuffle()

sides = shuffler.Condition(order, "sides", 5)

print "loading sides order..."
csShuffler = shuffler.Shuffler(order, trials, 3)
csList = csShuffler.shuffle()

x = screen.size[0] / 4
y = screen.size[1] / 2

print "Beginning block now..."
experiments.showInstructions(screen, instructionText, textcolor=color)

if subtrials == -1:
	stimList = stimList
	csList = csList
else:
	stimList = stimList[0:subtrials]
	csList = csList[0:subtrials]

line = TextureStimulus(anchor='center', color = [255, 255, 255], position = [screen.size[0]/2, screen.size[1]/2], size= [4, 680])

for stim, cs in zip(stimList, csList):
	pressed = False

	ratio = getattr(stim, "ratio")
	n1 = getattr(stim, "seed")
	n2 = int(round(n1 * 1/ratio, 0))
	size = getattr(stim, "size")
	exemplar = getattr(stim, "exemplar")
	shape = getattr(stim, "shape")
	
	side = cs
	
	sub.inputData(trial, "ACC", "NA")
	sub.inputData(trial, "RT", "NA")
	sub.inputData(trial, "ratio", ratio)
	sub.inputData(trial, "n1", n1)
	sub.inputData(trial, "n2", n2)
	sub.inputData(trial, "sizectrl", size)
	sub.inputData(trial, "exemplar", exemplar)
	sub.inputData(trial, "order", side)
	sub.inputData(trial, "shape", shape)
	
	if side == "large":
		fname1 = "%s_%s_%s_%s_%s_%s_S2.bmp" % (shape, ratio, n1, n2, exemplar, size)
		fname2 = "%s_%s_%s_%s_%s_%s_S1.bmp" % (shape, ratio, n1, n2, exemplar, size)
	else:
		fname1 = "%s_%s_%s_%s_%s_%s_S1.bmp" % (shape, ratio, n1, n2, exemplar, size)
		fname2 = "%s_%s_%s_%s_%s_%s_S2.bmp" % (shape, ratio, n1, n2, exemplar, size)
		
	####
	t1 = Texture(Image.open(os.path.join(stimLib,fname1)))
	t2 = Texture(Image.open(os.path.join(stimLib,fname2)))
	
	phase = ""
	s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
	s2 = TextureStimulus(texture = t2, position = (x * 3, y), anchor = 'center')	

	texture_object1 = s1.parameters.texture.get_texture_object()
	texture_object2 = s2.parameters.texture.get_texture_object()

	v = Viewport(screen=screen, stimuli=[s1,s2, line])
	p = Presentation(go_duration=('forever', ), viewports=[v])
	p.add_controller(None, None, FunctionController(during_go_func=put_image_dual, temporal_variables = TIME_SEC_ABSOLUTE))
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, keyFunc)]
	p.go()

	if trial % break_trial == 0 and trial != trials:
		print trial, "BREAK TIME"
		experiments.showInstructions(screen, breakText, textcolor = [0, 0, 0])

	trial += 1
	sub.printData()


