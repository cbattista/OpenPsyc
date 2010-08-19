#! /usr/env/python

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

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

#suckas need to changes this on they home computaz
sys.path.append('/home/cogdev/code/OpenPsyc')

from experiments import printWord, printText
import subject


###COLLECT SUBJECT INFO
myArgs = sys.argv

print myArgs

number = "070505_" + str(myArgs[1])
try:
	trials = int(myArgs[2])
except:
	trials = 3

#create subject
subject = subject.Subject(number, 1, 1)

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

framerate = 60

#helper functions
def frame_to_time(f):
    t = float(f) / float(framerate)
    return t

def time_to_frame(t):
    f = t * framerate
    return f

#problem control, SRBox voice trigger
def problem_controller(f_abs):
	if f_abs == 1:
		onset = time.time()
		ser = serial.Serial(port=0, baudrate=19200)
		ser.write('\xa0\xe0')
		x=chr(0)

		while ser.isOpen():
			x = ser.read()
			if ord(x) == 32:
				offset = time.time()
				#end signal
				RT = offset - onset
				subject.inputData(trial, "RT", RT)
				p.parameters.go_duration = (0, 'frames')
				ser.close()

#strategy control, SRBox buttons
def strategy_controller(f_abs):
	global strategy
	global ACC
	global misfire

	if f_abs == 1:
		onset = time.time()
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

			elif ord(x) == 4:
				ACC = 1
				
			elif ord(x) == 8:
				ACC = 0

			elif ord(x) == 16:
				misfire = 1
				
			


#experimenter grading, space & escape
def key_handler(event):
	if event.key == K_ESCAPE:
		print "NEED A REGRADING FUNCTION HERE WOO"

	elif event.key == K_q:
		print "QUIT PROGRAM WOOO"
		p2.parameters.go_duration = (0, 'frames')
		memLen = trials
		calcLen = trials


#problem adjustment values
add = [4,5,6,7]
subtract = [1,2,3]

memAdd = [-1, -2, 1, 2]

begin = [2,3,4]

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

memLen = 0
calcLen = 0

#default strategy
strategy = None

while memLen <= trials or calcLen <= trials:
	#generate problem based on last round
	random.shuffle(add)
	random.shuffle(subtract)
	random.shuffle(memAdd)

	badProblem = True

	#if either of the bins is full, definitely check
	if len(memTemp) >= trials or len(calcTemp) >= trials:
		verify = 1
	#if they are getting pretty full, increase the odds of checking
	elif len(memTemp) >= (trials/2) or len(calcTemp) >= (trials/2):
		verify = random.choice([0, 1])
	#otherwise give it 1/3 odds of checking
	else:
		verify = random.choice([1, 0, 0, 0])

	if len(problemHeap) and verify:
		ns = problemHeap.pop(0)

	else:

		while badProblem:
			#if the strategy was "calculation", reduce the size of the number
			if strategy == "calc" and memLen <= trials:
				n1 = abs(n1 - subtract[0])
				n2 = abs(n2 - subtract[1])
				if n1 == 0:
					n1 = 1
				if n2 == 0:
					n2 = 1
			elif strategy == "calc" and memLen > trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]

			#if the strategy was "memory", increase the size of the number
			elif strategy == "mem" and calcLen <= trials:
				n1 = n1 + add[0]
				n2 = n2 + add[1]
			elif strategy == "mem" and calcLen > trials:
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

			previousProblems = memProblems + calcProblems + incorrects

			if ns not in previousProblems:
				badProblem = False

	subject.inputData(trial, "n1", ns[0])
	subject.inputData(trial, "n2", ns[1])
	solution = str(ns[0] + ns[1])

	random.shuffle(ns)
	problem = "%s + %s" % (ns[0], ns[1])
	subject.inputData(trial, "problem", problem)

	#default values for misfiring voice key
	misfire = 0
	ACC = 1

	#generate texts
	strat2 = "Please describe your strategy"

	viewtext, viewport = printWord(screen, problem, 60, (255, 255, 255), h_anchor = 2.75)
	solText, solPort = printWord(screen, solution, 60, (255, 255, 255), v_anchor = 0.5)
	stratText, stratPort = printWord(screen, strat2, 60, (255, 255, 255), h_anchor = 2.25)
	expText, expPort = printWord(screen, problem, 60, (255, 255, 255), v_anchor = 1.5)
	fixText, fixCross = printWord(screen, '', 60, (255, 255, 255), h_anchor = 2.5)

	#BLOCK 1 - Problem & RESPONSE

	p = Presentation(go_duration=('forever', ), viewports=[viewport, solPort, expPort])
	p.add_controller(None, None, FunctionController(during_go_func=problem_controller, temporal_variables = FRAMES_ABSOLUTE))
	p.go()

	#BLOCK 2 - STRATEGY SELECTION & GRADING
	p2 = Presentation(go_duration=('forever', ), viewports=[solPort, stratPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()

	subject.inputData(trial, "misfire", misfire)

	#blank screen
	p3 = Presentation(go_duration=(1.5, 'seconds'), viewports=[fixCross])
	p3.go()

	#add problem to appropriate list based on strategy and grade
	subject.inputData(trial, "ACC", ACC)
	subject.inputData(trial, "strategy", strategy)

	ns.sort()

	if ACC:
		if strategy == "mem" and ns in memTemp:
			memProblems.append(ns)
			memTemp.remove(ns)
			subject.inputData(trial, "verified", 1)
		elif strategy == "mem":
			memTemp.append(ns)
			problemHeap.append(ns)
			subject.inputData(trial, "verified", 0)
		elif strategy == "calc" and ns in calcTemp:
			calcProblems.append(ns)
			calcTemp.remove(ns)
			subject.inputData(trial, "verified", 1)
		elif strategy == "calc":
			calcTemp.append(ns)
			problemHeap.append(ns)
			subject.inputData(trial, "verified", 0)
		
	else:
		incorrects.append(problem)
	
	trial = trial + 1

	subject.printData()

	memLen = len(memProblems)
	calcLen = len(calcProblems)

#save sub
subject.printData()

subject.memProblems = memProblems
subject.calcProblems = calcProblems

subject.preserve()
