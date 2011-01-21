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
import copy

from pygame.locals import *
import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])


import subject
from experiments import printWord, printText
from mongoTools import MongoAdmin
import shuffler


###COLLECT SUBJECT INFO
myArgs = sys.argv

number = str(myArgs[1])

#should be either "b" or "m", where b is brightness comparison, and m is magnitude comparison
condition = str(myArgs[2])


#create subject
subject = subject.Subject(number, experiment = "training")

#connect to db
db = MongoAdmin("magnitude")

#retrieve problems
posts = db.getTable("training_sets").posts

q= {}
q['s_id'] = str(number)

problems = []

for r in posts.find(q):
	ns = [r['n1'], r['n2']]
	orig_strat = r['strategy']

	problems.append([ns, orig_strat])


def normalize(u):
    low  = min(u)
    high = max(u)
    norm = max(abs(low), high)
    for i in range(len(u)):
        u[i] = u[i]*(1.0/norm)
    return u


#determine all ratios
allnums = []

for p in problems:
	n1 = p[0][0]
	n2 = p[0][1]
	allnums.append(n1)
	allnums.append(n2)

brightness = normalize(allnums)

#make magnitudes whatnot
add_problems = problems * 10
random.shuffle(add_problems)

mag_problems = problems * 10
random.shuffle(mag_problems)

#make mag/brightness list
while not quit:
	random.shuffle(mag_problems)
	last_five = []
	for p in mag_problems:
		if p in last_five:
			bad = True
			break

		if len(last_five) < 5:
			last_five.append(p)
		else:
			last_five.pop(0)
			last_five.append(p)

	if not bad:
		quit = True

items = ["add", "mag"]


stim_shuffler = shuffler.Shuffler(items, 400, 5)
stimList = stim_shuffler.shuffle()


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

#experimenter grading, space & escape
def key_handler(event):
	global ACC
	global misfire

	if event.key == K_SPACE:
		ACC = 0
	elif event.key == K_m:
		misfire = 1
	elif event.key == K_ESCAPE:
		print "NEED A REGRADING FUNCTION HERE WOO"
	elif event.key == K_q:
		print "QUIT PROGRAM WOOO"
		p2.parameters.go_duration = (0, 'frames')

def pause_handler(event):
	if event.key == K_SPACE:
		print "BEGINNING EXPERIMENT"
		pause.parameters.go_duration = (0, 'frames')

#default strategy
strategy = None

trial = 1

fixText, fixCross = printWord(screen, '*', 120, (255, 255, 255))
errorText, errorPort = printWord(screen, 'X', 120, (1., .1, .1))


print "PRESS SPACE TO START"

pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

problemQ = []

while len(stimList):

	if problemQ:
		stim = problemQ[2]
		n1 = problemQ[0]
		n2 = problemQ[1]
	else:
		stim = stimList.pop(0)
		if stim == "mag":
			p = mag_problems.pop(0)
			n1 = p[0][0]
			n2 = p[0][1]
			symbol = "  OR  "
			solution = str(max([n1, n2]))
		elif stim == "add":
			p = add_problems.pop(0)
			n1 = p[0][0]
			n2 = p[0][1]
			symbol = "  +  "
			solution = str(n1 + n2)

	if condition == "b":
		i1 = problems.index(n1)
		i2 = problems.index(n2)
		b1 = brightness[i1]
		b2 = brightness[i2]
		problem = "%s %s %s" % (b1, symbol, b2)

	else:
		problem = "%s %s %s" % (n1, symbol, n2)


	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", problem)
	subject.inputData(trial, "type", stim)

	#format problem
	print "----------------------"
	print "PROBLEM: %s" % problem
	print "SOLUTION: %s " % solution
	print "----------------------"

	ns = [n1, n2]

	#default values for misfiring voice key
	misfire = 0
	ACC = 1


	expText, expPort = printWord(screen, problem, 80, (255, 255, 255))

	#BLOCK 1 - Problem & RESPONSE

	p = Presentation(go_duration=('forever', ), viewports=[expPort])
	p.add_controller(None, None, FunctionController(during_go_func=problem_controller, temporal_variables = FRAMES_ABSOLUTE))
	p.go()

	#BLOCK 2 - STRATEGY SELECTION & GRADING
	p2 = Presentation(go_duration=(1.5, 'seconds'), viewports=[fixCross])
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()

	if ACC == 0:
		problemQ = [n1, n2, stim]
		error = Presentation(go_duration=(1, 'seconds'), viewports=[errorPort])
		error.go()
	else:
		problemQ = []

	subject.inputData(trial, "misfire", misfire)
	subject.inputData(trial, "ACC", ACC)

	trial = trial + 1

	subject.printData()

#save sub
subject.printData()

fileName = subject.fname
dbName = "magnitude"
tableName = "training"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=False)


