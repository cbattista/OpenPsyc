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

from problem import *

sys.path.append(os.path.split(os.getcwd())[0])

from experiments import printWord, printText
import subject
import shuffler
from mongoTools import MongoAdmin

###SETTINGS
DB = "CAT3"

#always verify when there are this many problems in the heap
checkHeap = 10
#always verify when one bin is full and there are this many problems in the heap
fullHeap = 5

problemTime = 1
blankTime = 2

#problem adjustment values
add = [4,5,6,7]
subtract = [1,2,3]

memAdd = [-1, -2, 1, 2]
begin = [2,3,4,5]

###COLLECT SUBJECT INFO
myArgs = sys.argv

try:
	trials = int(myArgs[2])
except:
	trials = 3

try:
	number = str(myArgs[1])
	#create subject
	subject = subject.Subject(number, 1, 1, "StratVer")
except:
	subject = adder.Adder("CAT2", "verification_pre", 20)



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

#starting operands
random.shuffle(begin)
n1 = begin[0]
n2 = begin[1]

#default strat
strat = None

###UNCHANGING STIMULI

#strat selection
fixText, fixCross = printWord(screen, '', 60, (255, 255, 255))
pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

#generate texts
strat2 = "\n\nPlease describe your strat"
stratText, stratPort = printText(screen, strat2, 60, (255, 255, 255))

print "PRESS SPACE TO START"

problems = Problems(DB, clear=False)
lastSoln = 0

mems = 0
calcs = 0

while mems < trials or calcs < trials:
	badProblem = True
	misfire = 0

	heaps = problems.count({'kind':'temp'})
	calcs = problems.count({'kind':'verified', 'strat':'calc'})
	mems = problems.count({'kind':'verified', 'strat':'mem'})
	tcalcs = problems.count({'kind':'temp', 'strat':'calc'})
	tmems = problems.count({'kind':'temp', 'strat':'mem'})

	#if the heap is at the threshold, definitely check it
	if heaps >= checkHeap:
		verify = 1
	#if the heap is getting pretty full, increase odds of checking
	elif heaps >= (checkHeap + (checkHeap/2)):
		verify = random.choice([0, 1])
	#if we have all our calc problems and there are a few in the heap
	#otherwise give it 1/4 odds of checking
	else:
		verify = random.choice([1, 0, 0, 0])

	if heaps and verify:
		#determine type of problem we are looking for and its availability
		if tcalcs <= tmems:
			look = "calc"
		elif tmems > tcalcs:
			look = "mem"
		else: 
			look = False

		#if we can get such a problem
		if look:
			ids = problems.distinct('id', {'strat': look, 'kind':'temp'})
			if ids:
				pid = random.choice(ids)
				problem = problems.get(pid)
				soln = problem.row['solution']
				#if the problem solution wasn't the same last as last time's
				if soln != lastSoln:
					badProblem = False

	if not badProblem:
		badCycles = 0
		while badProblem:
			#generate problem based on last round
			random.shuffle(add)
			random.shuffle(subtract)
			random.shuffle(memAdd)

			#if the strat was "calculation", reduce the size of the number
			if strat == "calc" and mems < trials:
				n1 = abs(n1 - subtract[0])
				n2 = abs(n2 - subtract[1])
				if n1 == 0:
					n1 = 1
				if n2 == 0:
					n2 = 1
			elif strat == "calc" and calcs >= trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]

			#if the strat was "memory", increase the size of the number
			elif strat == "mem" and calcs < trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]
			#unlesss 
			elif strat == "mem" and calcs >= trials:
				n1 = abs(n1 + memAdd[0])
				n2 = abs(n2 + memAdd[1])
				if n1 == 0:
					n1 = 1
				if n2 == 0:
					n2 = 1

			else:
				pass

			problem = Problem([n1, n2])
			ns = problem.row['ns']
			soln = problem.row['solution']

			if not problems.haveProblem(problem):
				badProblem = False

			if soln > 100:
				n1 = n1 / 2
				n2 = n2 / 2
				badProblem = True

			#don't want problems with a 10 in them, or a 1
			if (10 in ns) or (1 in ns):
				badProblem = True

			#don't want problems where both operands are the same
			if len(set(ns)) == 1:
				badProblem = True

			#don't want problem with the same solution as the last one
			if lastSoln == soln:
				badProblem = True

			badCycles += 1
			#if we are stuck in an infinite loop
			if badCycles >= 100000:
				print "Breaking loop"
				badProblem = False

	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)

	random.shuffle(ns)

	lastSoln = copy.deepcopy(soln)

	subject.inputData(trial, "problem", "%s" % problem)

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
	subject.inputData(trial, "orig_strat", strat)
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)
	subject.inputData(trial, "dist_offset", dist)
	subject.inputData(trial, "solution", soln)
	
	#CREATE STIMULLI
	probText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))

	vp, vr = printText(screen, "%s                                                 %s" % (L, R), 60, (255, 255, 255))

	fixText, fixCross = printText(screen, '', 60, (255, 255, 255))


	print "-------------------------------------"
	print "PROBLEM : %s" % problem
	print "SOLUTION : %s" % soln
	print "STATUS : %s" % problems
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
	problems.append(problem)

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
