#! /usr/env/python

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
from VisionEgg.Text import *
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

#create subject
subject = subject.Subject(number, experiment = "box_mag")

#connect to db
db = MongoAdmin("magnitude")

#retrieve problems
posts = db.getTable("training_sets").posts

fontsize = 80
boxsize = 160

numbers = range(1, 41)
random.shuffle(numbers)
n1s = numbers[:20]
n2s = numbers[20:]

mag_problems=[]

for n1, n2 in zip(n1s, n2s):
	mag_problems.append([n1,n2])


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

#STIMULI

#Fixation Cross
fixText, fixCross = printWord(screen, '*', 120, (255, 255, 255))
errorText, errorPort = printWord(screen, 'X', 120, (1., .1, .1))

print "PRESS SPACE TO START"

pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

problemQ = []

while len(mag_problems):

	if problemQ:
		stim = problemQ[2]
		n1 = problemQ[0]
		n2 = problemQ[1]
	else:
		p = mag_problems.pop(0)
		n1 = p[0]
		n2 = p[1]
		symbol = "  OR  "
		solution = str(max([n1, n2]))

	#Make Rectangles and numbers
	x = screen.size[0] / 4
	y = screen.size[1] / 2

	numbers = [n1, n2]
	random.shuffle(numbers)

	problem = "%s   OR   %s" % (numbers[0], numbers[1])
	expText, expPort = printText(screen, problem, 80, (255, 255, 255))

	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", problem)

	#format problem
	print "----------------------"
	print "PROBLEM: %s" % problem
	print "SOLUTION: %s " % solution
	print "----------------------"

	ns = [n1, n2]

	#default values for misfiring voice key
	misfire = 0
	ACC = 1

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
tableName = "box_pre"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=False)


