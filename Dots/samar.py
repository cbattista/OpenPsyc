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


basePath = '/home/samar/OpenPsyc'

sys.path.append(basePath)

basePath = os.path.join(basePath, 'Dots')

import experiments
import subject
import shuffler
import CBalance
import dotGUI

f = open("controls.pck")
controls = pickle.load(f)
f.close()

#response format
response = controls['response']

sub = subject.Subject(controls['subject id'], experiment = "dots", session=response)


###BEGIN SETTINGS

#total trials
trials = controls['trials']


#of the total trials, how many do you want to run (good for testing), put -1 for all
subtrials = controls['subtrials']

volumeThresh = -30

#instruction text
f = open(os.path.join(basePath, "instructions.txt"))
text = f.read()
f.close()
instructionText = unicode(text, "utf-8")

#the text presented when a break is given
f = open(os.path.join(basePath, "breakmessage.txt"))
text = f.read()
f.close()
breakText = unicode(text, "utf-8")

#take a break after this many trials
break_trial = controls['break trial']

#total duration of each dot array, in seconds
dot_duration = controls['dot duration'] / 1000.

#total duration of each mask
mask_dur = controls['mask duration'] / 1000.
mask_img = Image.open(os.path.join(basePath, "mask.BMP"))

#size of fixation cross
crossSize = 80
crossChar = '+'
#duration of fixation cross
cross_duration = controls['ISI'] / 1000.
 
###END SETTINGS

stimLib = os.path.join(basePath, "stimuli")
	
screen = get_default_screen()

screen.parameters.bgcolor = (.52, .51, .52)

pygame.init()

trial = 1


###INITIALIZE SOUND
import pygst
pygst.require('0.10')
import gst, gobject
gobject.threads_init()
pipeline = gst.parse_launch(
	'pulsesrc ! audioconvert ! '
	'audio/x-raw-int,channels=1,rate=44100,endianness=1234,'
	'width=32,depth=32,signed=(bool)True !'
	'level name=level interval=10000000 !'
	'fakesink')
 
level = pipeline.get_by_name('level')
bus = pipeline.get_bus()
bus.add_signal_watch()

if response == "voice":   
	# start the pipeline
	pipeline.set_state(gst.STATE_PLAYING)
 
###END INITIALIZE SOUND


def put_image_dual(t_abs):
	global phase
	global start
	global bus
	global talked
	global fixCross

	if not phase:
		start = t_abs
		phase = "dots"
		talked = False
		fixText, fixCross = experiments.printWord(screen, '+', crossSize, (0, 0, 0))

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


	if response == "voice":
		message = bus.poll('GST_MESSAGE_ANY', 1)
		# read peak
		if message:
			if message.src is level:
				if message.structure.has_key('peak'):
					peak = message.structure['peak'][0]
					print peak
					if peak > volumeThresh  and peak < 0 and not talked:
						sub.inputData(trial, "RT", t)
						print t
						talked = True
						fixText, fixCross = experiments.printWord(screen, '&', crossSize, (0, 0, 0))

def mouseGrade(event):
	global side
	global misfire
	buttons = pygame.mouse.get_pressed()
	b1 = buttons[0]
	b2 = buttons[1]
	b3 = buttons[2]
	if b1:
		user_side = "left"
		if side=="large":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)
		sub.inputData(trial, "user_side", user_side)

	elif b3:
		user_side = "right"
		if side=="small":
			sub.inputData(trial, "ACC", 1)
		else:
			sub.inputData(trial, "ACC", 0)
		sub.inputData(trial, "user_side", user_side)

	elif b2:
		misfire = 1

def quitHandler(event):
	global trialList
	if event.key == pygame.locals.K_q:
		print "might quit"
		if 64 == pygame.key.get_mods():
			trialList = zip([], [])
			print "definitely quitting"
		


def mouseFunc(event):
	global side
	global pressed

	RT = p.time_sec_since_go * 1000

	sub.inputData(trial, "RT", RT)

	halfway = screen.size[0] / 2

	if event.pos[0] < halfway:
		user_side = "left"
	elif event.pos[0] > halfway:
		user_side = "right"
	else:
		user_side = "middle"

	sub.inputData(trial, "user_side", user_side)

	if not pressed:
		if user_side == "right":
			if side=="small":
				sub.inputData(trial, "ACC", 1)
			else:
				sub.inputData(trial, "ACC", 0)
		elif user_side == "left":
			if side=="large":
				sub.inputData(trial, "ACC", 1)
			else:
				sub.inputData(trial, "ACC", 0)
		else:
			sub.inputData(trial, "ACC", 0)
	else:
		sub.inputData(trial, "ACC", 2)


	pressed = True

#fixation pause
#add response handlers



ratios = shuffler.Condition([.9, .75, .66, .5, .33, .25], "ratio", 6)
seeds = shuffler.Condition([6, 7, 8, 9, 10], "seed", 6)
size = shuffler.Condition(["con", "incon"], "size", 5)
exemplars = shuffler.Condition([1, 2, 3, 4], "exemplar", 20)
	
order = ["large", "small"]
color = ["C1", "C2"]

print "loading ratio/seed/size/exemplar order..."
myShuffler = shuffler.MultiShuffler([ratios, seeds, size, exemplars], trials)
stimList = myShuffler.shuffle()

sides = shuffler.Condition(order, "sides", 5)
colors = shuffler.Condition(color, "colors", 6)

print "loading sides/colors order..."
csShuffler = shuffler.MultiShuffler([sides, colors], trials)
csList = csShuffler.shuffle()

x = screen.size[0] / 4
y = screen.size[1] / 2

print "Beginning block now..."
experiments.showInstructions(screen, instructionText, textcolor=(0, 0, 0))

if subtrials == 0:
	stimList = stimList
	csList = csList
else:
	stimList = stimList[0:subtrials]
	csList = csList[0:subtrials]

trialList = zip(stimList, csList)

while trialList:
	stim, cs = trialList.pop(0)
	crossChar = '+'
	pressed = False
	misfire = 0
	
	ratio = getattr(stim, "ratio")
	n1 = getattr(stim, "seed")
	n2 = int(round(n1 * 1/ratio, 0))
	size = getattr(stim, "size")
	exemplar = getattr(stim, "exemplar")
	
	side = getattr(cs, "sides")
	color = getattr(cs, "colors")
	
	sub.inputData(trial, "ACC", "NA")
	sub.inputData(trial, "RT", "NA")
	sub.inputData(trial, "user_side", "NA")
	sub.inputData(trial, "ratio", ratio)
	sub.inputData(trial, "n1", n1)
	sub.inputData(trial, "n2", n2)
	sub.inputData(trial, "sizectrl", size)
	sub.inputData(trial, "exemplar", exemplar)
	sub.inputData(trial, "order", side)
	sub.inputData(trial, "largecolor", color)
	
	if side == "large":
		fname1 = "%s_%s_%s_%s_%s_S2.bmp" % (ratio, n1, color, size, exemplar)
		fname2 = "%s_%s_%s_%s_%s_S1.bmp" % (ratio, n1, color, size, exemplar)
	else:
		fname1 = "%s_%s_%s_%s_%s_S1.bmp" % (ratio, n1, color, size, exemplar)
		fname2 = "%s_%s_%s_%s_%s_S2.bmp" % (ratio, n1, color, size, exemplar)
		
	####
	t1 = Texture(Image.open(os.path.join(stimLib,fname1)))
	t2 = Texture(Image.open(os.path.join(stimLib,fname2)))
	
	phase = ""
	s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
	s2 = TextureStimulus(texture = t2, position = (x * 3, y), anchor = 'center')	

	texture_object1 = s1.parameters.texture.get_texture_object()
	texture_object2 = s2.parameters.texture.get_texture_object()

	v = Viewport(screen=screen, stimuli=[s1,s2])
	p = Presentation(go_duration=('forever', ), viewports=[v])
	p.add_controller(None, None, FunctionController(during_go_func=put_image_dual, temporal_variables = TIME_SEC_ABSOLUTE))

	if response == "voice":
		p.parameters.handle_event_callbacks=[(pygame.locals.MOUSEBUTTONDOWN, mouseGrade), (pygame.locals.KEYDOWN, quitHandler)]
	else:
		p.parameters.handle_event_callbacks=[(pygame.locals.MOUSEBUTTONDOWN, mouseFunc), (pygame.locals.KEYDOWN, quitHandler)]

	p.go()
	
	if response == "voice":
		sub.inputData(trial, "misfire", misfire)


	if trial % break_trial == 0 and trial != trials:
		print trial, "BREAK TIME"
		experiments.showInstructions(screen, breakText, textcolor = [0, 0, 0])

	trial += 1
	sub.printData()

