#! /usr/env/python

import VisionEgg
#VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
import serial
import pickle
import time
import random

from pygame.locals import *

import sys
import os
import copy

from problem import Problem

#suckas need to changes this on they home computaz
sys.path.append('/home/cogdev/code/OpenPsyc')

from experiments import printWord, printText
import subject
import shuffler
from mongoTools import MongoAdmin

###SETTINGS

#always verify when there are this many problems in the heap
checkHeap = 10
#always verify when one bin is full and there is this many problems in the heap
fullHeap = 5

problemTime = 1
blankTime = 2

#problem adjustment values
add = [4,5,6,7]
subtract = [1,2,3]

memAdd = [-1, -2, 1, 2]
begin = [2,3,4,5]

framerate = 60


###COLLECT SUBJECT INFO
myArgs = sys.argv

number = str(myArgs[1])

try:
	trials = int(myArgs[2])
except:
	trials = 3

#create subject
subject = subject.Subject(number, 1, 1, "StratVer")

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()


#strategy control, SRBox buttons
def strategy_controller(f_abs):
	global strategy

	if f_abs == 1:
		ser = serial.Serial(port=0, baudrate=19200)
		ser.write('\xa0\xe0')
		while ser.isOpen():
			x=chr(0)
			x = ser.read()
			if ord(x) == 1:
				strategy = "mem"
				ser.close()
				p2.parameters.go_duration = (0, 'frames')

			elif ord(x) == 2:
				strategy = "calc"
				ser.close()
				p2.parameters.go_duration = (0, 'frames')


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

#this will be the problems we want the person to repeat
problemHeap = []

#list of incorrect problems
incorrects = []

#these will be the list of UNCONFIRMED problems by strategy

memTemp = []
calcTemp = []

#these will be the list of CONFIRMED problems by strategy
memProblems = []
calcProblems = []

#default strategy
strategy = None

#default empty problem
ns = []
lastns = []
lastlastns = []
lastSoln = 0

###UNCHANGING STIMULI

#strategy selection
fixText, fixCross = printWord(screen, '', 60, (255, 255, 255))
pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

#generate texts
strat2 = "\n\nPlease describe your strategy"
stratText, stratPort = printText(screen, strat2, 60, (255, 255, 255))

print "PRESS SPACE TO START"


while len(memProblems) < trials or len(calcProblems) < trials:
	#generate problem based on last round
	random.shuffle(add)
	random.shuffle(subtract)
	random.shuffle(memAdd)

	badProblem = True

	#if the heap is at the threshold, definitely check it
	if len(problemHeap) >= (checkHeap):
		verify = 1
	#if we have all our calc problems and there are a few in the heap
	elif len(calcProblems) >= trials and len(problemHeap) > fullHeap:
		verify = 1
	#if we have all our memory problems and there are a few in the heap 
	elif len(memProblems) >= trials and len(problemHeap) > fullHeap:
		verify = 1

	#if we have enough temps to make a full set of calcs
	elif (len(calcProblems) + len(calcTemp)) >= trials:
		verify = 1
	#if we have enough temps to make a full set of mems
	elif (len(calcProblems) + len(calcTemp)) >= trials:
		verify = 1

	#if the heap is getting pretty full, increase odds of checking
	elif len(problemHeap) >= (checkHeap + (checkHeap/2)):
		verify = random.choice([0, 1])
	#if we have all our calc problems and there are a few in the heap
	#otherwise give it 1/4 odds of checking
	else:
		verify = random.choice([1, 0, 0, 0])

	#we don't want repeats, though, need a pad of 5
	if (ns in problemHeap[:5] or (lastns in problemHeap[:5]) or (lastlastns in problemHeap[:5])) and verify:
		verify = 0

	if len(problemHeap) and verify and (sum(problemHeap[0]) != lastSoln):
		ns = problemHeap.pop(0)

	else:
		badCycles = 0
		while badProblem:
			#if the strategy was "calculation", reduce the size of the number
			if strategy == "calc" and len(memProblems) < trials:
				n1 = abs(n1 - subtract[0])
				n2 = abs(n2 - subtract[1])
				if n1 == 0:
					n1 = 1
				if n2 == 0:
					n2 = 1
			elif strategy == "calc" and len(memProblems) >= trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]

			#if the strategy was "memory", increase the size of the number
			elif strategy == "mem" and len(calcProblems) < trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]
			#unlesss 
			elif strategy == "mem" and len(calcProblems) >= trials:
				n1 = abs(n1 + memAdd[0])
				n2 = abs(n2 + memAdd[1])
				if n1 == 0:
					n1 = 1
				if n2 == 0:
					n2 = 1

			else:
				pass

			ns = [n1, n2]
			ns.sort()

			print ns			

			previousProblems = memProblems + calcProblems + incorrects

			if ns not in previousProblems:
				badProblem = False

			#don't want problems that add to over 100
			if sum(ns) > 100:
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
			if lastSoln == (n1 + n2):
				badProblem = True

			badCycles += 1
			#if we are stuck in an infinite loop
			if badCycles >= 100000:
				print "Breaking loop"
				badProblem = False

	subject.inputData(trial, "n1", ns[0])
	subject.inputData(trial, "n2", ns[1])

	random.shuffle(ns)

	problem = Problem(ns)

	lastSoln = problem.solution

	subject.inputData(trial, "problem", "%s" % problem)

	problem_string = "%s + %s = ?" % (ns[0], ns[1])


	#DISTRACTOR CONFIG
	dist = random.choice(problem.distractors)
	op = random.choice(["+", "-"])

	distractor = eval("%s %s %s" % (problem.solution, op, dist))

	side = random.choice(['l', 'r'])

	if side == "l":
		correct = "left"
		L = str(problem.solution)
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = str(problem.solution)

	
	#SAVE DISTRACTOR INFO
	subject.inputData(trial, "orig_strat", strategy)
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)
	subject.inputData(trial, "dist_offset", dist)
	subject.inputData(trial, "solution", problem.solution)
	
	#CREATE STIMULLI
	probText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))

	vp, vr = printText(screen, "%s                                                 %s" % (L, R), 60, (255, 255, 255))

	fixText, fixCross = printText(screen, '', 60, (255, 255, 255))

	#EXPERIMENTER INFO
	info = "mems: %s/%s, tmems: %s, calcs: %s/%s, tcalcs: %s, heap: %s" % (len(memProblems), trials, len(memTemp), len(calcProblems), trials, len(calcTemp), len(problemHeap))

	print "-------------------------------------"
	print "PROBLEM : %s" % problem
	print "SOLUTION : %s" % problem.solution
	print "STATUS : %s" % info
	print "-------------------------------------"

	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS
	problem = Presentation(go_duration=(problemTime, 'seconds'), viewports=[probPort])
	problem.go()

	p3 = Presentation(go_duration=(blankTime, 'seconds'), viewports=[fixCross])
	p3.go()

	p = Presentation(go_duration=('forever', ), viewports=[vr])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	
	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)
	
	#BLOCK 2 - STRATEGY SELECTION
	p2 = Presentation(go_duration=('forever', ), viewports=[stratPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()
	
	#BLOCK 3 - BLANK SCREEN
	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()
	

	subject.inputData(trial, "ACC", ACC)
	subject.inputData(trial, "strategy", strategy)

	ns.sort()
	lastns = copy.deepcopy(ns)
	lastlastns = copy.deepcopy(lastns)

	if ACC:
		if strategy == "mem" and ns in memTemp:
			memProblems.append(ns)
			memTemp.remove(ns)
			subject.inputData(trial, "verified", 1)
		elif strategy == "mem" and len(memProblems) < trials:
			memTemp.append(ns)
			problemHeap.append(ns)
			subject.inputData(trial, "verified", 0)
		elif strategy == "mem":
			subject.inputData(trial, "verified", 0)
			memTemp.append(ns)
			#don't add to heap
			
		elif strategy == "calc" and ns in calcTemp:
			calcProblems.append(ns)
			calcTemp.remove(ns)
			subject.inputData(trial, "verified", 1)
		elif strategy == "calc" and len(calcProblems) < trials:
			calcTemp.append(ns)
			problemHeap.append(ns)
			subject.inputData(trial, "verified", 0)
		elif strategy == "calc":
			subject.inputData(trial, "verified", 0)
			calcTemp.append(ns)
			
		#if we have enough memory or calcs, take those suckas out of the heap
		if len(memProblems) >= trials:
			problemHeap = calcTemp
		elif len(calcProblems) >= trials:
			problemHeap = memTemp
		
	else:
		incorrects.append(problem)
		subject.inputData(trial, "verified", "NA")
	
	trial = trial + 1

	subject.printData()

#save sub
subject.printData()

subject.memProblems = memProblems
subject.calcProblems = calcProblems

subject.preserve()

print "Experiment Complete!"
print "Now move the ppt data file to the 'pre' directory and run uploadData"
