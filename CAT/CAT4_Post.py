#! /usr/env/python

import VisionEgg
#VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
import pickle
import time
import random

from pygame.locals import *

import sys
import os
import copy
import adder

from problem import *

sys.path.append(os.path.split(os.getcwd())[0])

from experiments import printWord, printText
import subject
import shuffler
from mongoTools import MongoAdmin

###SETTINGS
DB = "CAT3"

problemTime = 1
blankTime = 2

###COLLECT SUBJECT INFO
myArgs = sys.argv

try:
	sid = str(myArgs[1])
	#create subject
	subject = subject.Subject(sid, 1, 1, "StratVerPost")
except:
	subject = adder.Adder("CAT2", "verification_post", 20)
	sid = 666

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()


#strat control, mouse clicks
def mouse_handler(event):
	global strat
	global misfire

	buttons = pygame.mouse.get_pressed()
	b1 = buttons[0]
	b2 = buttons[1]
	b3 = buttons[2]
	
	if b1:
		strat = "mem"
		p2.parameters.go_duration = (0, 'frames')
	elif b3:
		strat = "calc"
		p2.parameters.go_duration = (0, 'frames')
	elif b2:
		misfire = 1
	
def key_handler(event):
	global correct 
	global ACC
	global RT
	key = event.key

	print event.key

	RT = p.time_sec_since_go
	
	if key == 308:
		if correct == "left":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')
	elif key == 313:
		if correct == "right":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')


def pause_handler(event):
	if event.key == K_SPACE:
		print "BEGINNING EXPERIMENT"
		pause.parameters.go_duration = (0, 'frames')

#initial variables
trial = 1

#default strat
strat = None

###UNCHANGING STIMULI

#strat selection
fixText, fixCross = printWord(screen, '', 60, (255, 255, 255))
pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

#generate texts
strat2 = "\n\nPlease describe your strategy"
stratText, stratPort = printText(screen, strat2, 60, (255, 255, 255))

print "PRESS SPACE TO START"

pre_problems = Problems(DB, sid, clear=False)
post_problems = Problems(DB, sid, exp="post", clear=False)

query = {'kind' : 'verified'}

ver_pre = pre_problems.query(query)

ns_list = []

for row in ver_pre:
	ns_list.append(row['ns'])

ns_list = ns_list * 2

random.shuffle(ns_list)

print len(ns_list)
print ns_list

lastSoln = 0

mems = 0
calcs = 0

for ns in ns_list:
	#reset state vars
	misfire = 0
	verify = 0
	problem = None
	soln = None


	problem = Problem(ns)

	ns = problem.row['ns']
	n1 = ns[0]
	n2 = ns[1]
	soln = problem.row['solution']

	#record some problem info
	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", "%s" % problem)
	subject.inputData(trial, "solution", soln)

	random.shuffle(ns)

	lastSoln = copy.deepcopy(soln)


	problem_string = "%s + %s = ?" % (ns[0], ns[1])

	#DISTRACTOR CONFIG
	dist = random.choice(problem.row['distractors'])
	op = random.choice(["+", "-"])

	distractor = eval("%s %s %s" % (soln, op, dist))

	side = random.choice(['l', 'r'])

	if side == "l":
		correct = "left"
		L = str(soln)
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = str(soln)

	
	#SAVE DISTRACTOR INFO
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)
	subject.inputData(trial, "dist_offset", dist)
	
	#CREATE STIMULLI
	probText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))

	vp, vr = printText(screen, "%s                                                 %s" % (L, R), 60, (255, 255, 255))

	fixText, fixCross = printText(screen, '', 60, (255, 255, 255))


	print "-------------------------------------"
	print "PROBLEM : %s" % problem
	print "SOLUTION : %s" % soln
	print "-------------------------------------"

	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS
	p4 = Presentation(go_duration=(problemTime, 'seconds'), viewports=[probPort])
	p4.go()

	p3 = Presentation(go_duration=(blankTime, 'seconds'), viewports=[fixCross])
	p3.go()

	p = Presentation(go_duration=('forever', ), viewports=[vr])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	
	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)
	
	#BLOCK 2 - strat SELECTION
	p2 = Presentation(go_duration=('forever', ), viewports=[stratPort])
	p2.parameters.handle_event_callbacks=[(pygame.MOUSEBUTTONDOWN, mouse_handler)]        
	p2.go()
	
	#BLOCK 3 - BLANK SCREEN
	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()

	subject.inputData(trial, "strat", strat)
	
	response = {'trial': trial, 'RT' : RT, 'ACC' : ACC, 'misfire' : misfire, 'strat' : strat}

	problem.addResponse(response)
	post_problems.append(problem)

	ns.sort()
	lastns = copy.deepcopy(ns)
	lastlastns = copy.deepcopy(lastns)
	
	trial = trial + 1

	subject.printData()

#save sub
subject.printData()

subject.preserve()

print "Experiment Complete!"
print "Now move the ppt data file to the 'pre' directory and run uploadData"
