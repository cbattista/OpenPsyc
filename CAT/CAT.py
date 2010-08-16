#! /usr/env/python

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
import serial
import Subject
import pickle
import time
import random

from pygame.locals import *

from experiments import printWord, printText
import sys

###COLLECT SUBJECT INFO
myArgs = sys.argv

print myArgs

number = "070505_" + str(myArgs[1])
try:
	trials = int(myArgs[2])
except:
	trials = 3

#create subject
subject = Subject.Subject(number, 1, 1)

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

	if f_abs == 1:
		onset = time.time()
		ser = serial.Serial(port=0, baudrate=19200)
		ser.write('\xa0\xe0')
		while ser.isOpen():
			x=chr(0)
			x = ser.read()
			if ord(x) == 16:
				offset = time.time()
				subject.inputData(trial, "stratRT", offset-onset)
				subject.inputData(trial, "strategy", "calc")
				strategy = "calc"
				ser.close()

			elif ord(x) == 1:
				offset = time.time()
				subject.inputData(trial, "stratRT", offset-onset)
				subject.inputData(trial, "strategy", "mem")
				strategy = "mem"
				ser.close()


#experimenter grading, space & escape
def key_handler(event):
	global ACC
	global falsePos
	global trueNeg
	global memLen
	global calcLen

	if event.key == K_c:
		subject.inputData(trial, "ACC", 1)
		ACC = 1
		p2.parameters.go_duration = (0, 'frames')
	elif event.key == K_i:
		subject.inputData(trial, "ACC", 0)
		ACC = 0
		p2.parameters.go_duration = (0, 'frames')
	elif event.key == K_f:
		falsePos = 1
		print "FP"
	elif event.key == K_t:
		trueNeg = 1
		print "TN"
	"""
	elif event.key == K_ESCAPE:
		p2.parameters.go_duration = (0, 'frames')
		memLen = trials
		calcLen = trials
	"""


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
#these will be the list of problems by strategy
memProblems = []
calcProblems = []

memLen = 0
calcLen = 0

#default strategy
strategy = None

print "TRIALS : %s" % trials

while memLen <= trials or calcLen <= trials:
	#generate problem based on last round
	random.shuffle(add)
	random.shuffle(subtract)
	random.shuffle(memAdd)

	badProblem = True

	if len(problemHeap):
		problem = problemHeap.pop()

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

			#format problem
			problem = "%s + %s" % (n1, n2)
			solution = str(n1 + n2)

			if problem not in memProblems and problem not in calcProblems:
				badProblem = False

	subject.inputData(trial, "problem" ,problem)
	#default values for FP and TN
	falsePos = 0
	trueNeg = 0


	#generate texts
	strat2 = "Memory (left button) or calculation (right button)?"

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

	subject.inputData(trial, "falsePos", falsePos)
	subject.inputData(trial, "trueNeg", trueNeg)

	#blank screen
	p3 = Presentation(go_duration=(1.5, 'seconds'), viewports=[fixCross])
	p3.go()

	#add problem to appropriate list based on strategy and grade
	if ACC:
		if strategy == "mem":
			memProblems.append(problem)
		elif strategy == "calc":
			calcProblems.append(problem)
	else:
		problemHeap.append(problem)
	
	trial = trial + 1

	subject.printData()

	memLen = len(memProblems)
	calcLen = len(calcProblems)

print memProblems
print calcProblems
print problemHeap	

#save problem lists
subject.inputData(0, "memProblems", memProblems)
subject.calcProblems = (0, "calcProblems", calcProblems)

#save sub
subject.printData()

subject.memProblems = memProblems
subject.calcProblems = calcProblems

subject.preserve()
