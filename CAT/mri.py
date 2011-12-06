#! /usr/env/python

#assessment.py
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

sys.path.append(os.path.split(os.getcwd())[0])

from problem import *
import shuffler
import subject
from experiments import *
from mongoTools import MongoAdmin

"""
phase 1 - 20 problems
phase 2 - 20 problems
phase 3- dti run
phase 4 - 20 problems
phase 5 - 20 problems

"""

#FUNCTIONS
#strat control, mouse clicks
def diff_handler(event):
	global strat
	global pausePort
	global paused
	global diffTime

	key = event.key	
	
	if key == pygame.locals.K_SPACE:
		strat = 'mem'
		p2.parameters.go_duration = (0, 'frames')
	elif key == pygame.locals.K_p:
		#pause the screen
		if not paused:
			paused = True
			p2.parameters.viewports.append(pausePort)
			p2.parameters.go_duration = ('forever', '')
		else:
			paused = False
			p2.parameters.viewports.pop(-1)
			p2.parameters.go_duration = (diffTime, 'seconds')
	
def key_handler(event):
	global correct 
	global ACC
	global RT
	key = event.key

	RT = p.time_sec_since_go
	
	if key == 308:
		if correct == "left":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')
	elif key == 307 or key == 313:
		if correct == "right":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')

###COLLECT EXPERIMENT INFO
myArgs = sys.argv

try:
	sid = str(myArgs[1])
except:
	sid = 666

#create subject
subject = subject.Subject(sid, 1, 1, "Assessment")

try:
	low = int(myArgs[2])
	high = int(myArgs[3])
except:
	n1 = 2
	n2 = 3

try:
	operation = str(myArgs[4])
except:
	operation = '+'

###VARIABLES

#settings variables
problemTime = 1 #how long the program stays on the screen
blankTime = 0.1 #blank between problem and solutions
diffTime = 2.5 #how long the strategy response appears for

#state variables
done = False
trial = 0 #trial number
phase = 1 #phase of the experiment
direction = "up" #direction of operands
maxOp = 35 #maximum operand size
memCount = 20
calcCount = 40

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

###UNCHANGING STIMULI

#the math problem
p4 = Presentation(go_duration=(problemTime, 'seconds'))
#math problem with distractors
p = Presentation(go_duration=('forever', ))

#strat selection
p2 = makeText(screen, "\n\nDescribe your strategy", duration=diffTime)
p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, diff_handler)]        

#fixation
p3 = makeText(screen, '', duration=0.5, quittable=False)

start = makeText(screen, 'Press the SPACEBAR to start')
start.go()

###DB STUFF
db = "mri_test"
problems = Problems(db, sid, "addition_post")

for old in problems.find():
	trial += 1
	strat = 'calc'
	paused = False

	problem = Problem([old['n1'], old['n2']])

	print phase, trial, problem

	#get problem info and data
	ns = problem.row['ns']
	n1 = ns[0]
	n2 = ns[1]
	soln = problem.row['solution']	
	lastSoln = copy.deepcopy(soln)

	#record problem operands, solution, and id
	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", "%s" % problem)
	subject.inputData(trial, "solution", soln)

	#prep the problem for display
	random.shuffle(ns)
	problem_string = "%s %s %s = ?" % (ns[0], operation, ns[1])

	#select the distractor
	distractor = problem.getDistractor()
	side = random.choice(['l', 'r'])
	if side == "l":
		correct = "left"
		L = str(soln)
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = str(soln)

	#record distractor info
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)

	#vision egg display stuff
	probText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))
	print L, R
	vp, vr = printText(screen, "\n\n\n\n\n\n\n\n\n%s                                               %s" % (L, R), 60, (255, 255, 255))
	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS

	p4.parameters.viewports=[probPort]
	p4.go()

	#p3 = Presentation(go_duration=(blankTime, 'seconds'), viewports=[fixCross])
	#p3.go()

	p.parameters.viewports=[probPort, vr]
	p.parameters.go_duration=('forever', '')
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)

	if diffTime > 1.5:
		diffTime -= .1

	#BLOCK 2 - strat SELECTION
	p2.parameters.go_duration=(diffTime, 'seconds')
	p2.go()

	#BLOCK 3 - BLANK SCREEN
	p3.go()

	subject.inputData(trial, 'strat', strat)

	response = {'trial': trial, 'RT' : RT, 'ACC' : ACC, 'strat' : strat}

	problem.addResponse(response)
	problems.append(problem)

	subject.printData()

#save sub
subject.printData()

subject.preserve()
