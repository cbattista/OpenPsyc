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

def put_problem(t_abs):
	global phase
	global start
	global pText #problem text
	global dText #distractor text

	if not phase:
		start = t_abs
		phase = "problem"

	t = t_abs - start

	if t >= problem_duration and phase == "problem":
		p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
		p.parameters.viewports = [pText, dText]
		phase = "distractors"

	elif t >= (problem_duration + distractor_duration) and phase == "distractors":
		p.parameters.viewports = []
		phase = "pause"

	elif t >= (dot_duration  + distractor_duration + pause_duration)
		p.parameters.go_duration = [0, 'frames']

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
problem_duration = 2 #how long the program stays on the screen
distractor_duration = 2
pause_duration = 1
probs_per_block = 20
RUN_FIX = 5 #how long the fixation at the start of the run appears for
DTI_FIX = 25 #how long the DTI acquisition has to last for

j = jitterTool(events=probs_per_block, offsets=probs_per_block/2)
isis = jitterTools(events=probs_per_block, offsets=5, TR=4)

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

#math problem
p = Presentation(go_duration=('forever', ))

start = makeText(screen, 'Press the SPACEBAR to start')
start.go()

runFix = makeText(screen, '+', duration=RUN_FIX, quittable=False)

dtiFix = makeText(screen, '|', duration=DTI_FIX, quittable=False)

###DB STUFF
db = "mri_test"
pre = Problems(db, sid, "addition")

###do problem shuffling stuff here
#for blocks of problems
pBlocks = [[], [], [], []]

for r in ['func','func','dti','func','func']:
	runFix.go()
	if r == 'dti':
		dtiFix.go()
	else:
		problems = pBlocks.pop()
		#get the order of jitters and isis for this block
		jitters = j.shuffle()
		isis = isi.shuffle()


	for p in problems:


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
	pText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))
	print L, R
	dText, vr = printText(screen, "\n\n\n\n\n\n\n\n\n%s                                               %s" % (L, R), 60, (255, 255, 255))
	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS

	p.parameters.viewports=[probPort]
	p.go()

	#p3 = Presentation(go_duration=(blankTime, 'seconds'), viewports=[fixCross])
	#p3.go()


	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)

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
