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

#should be either "r" or "m", where r is rotation comparison, and m is magnitude comparison
comparison = str(myArgs[2])


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


fontsize = 80


#determine all ratios
allnums = []

for p in problems:
	n1 = p[0][0]
	n2 = p[0][1]
	allnums.append(n1)
	allnums.append(n2)

trials = 400

#make magnitudes and whatnot
ls = shuffler.ListShuffler(range(len(problems)), trials/2, 5)
add_problems = ls.shuffle()
mag_problems = ls.shuffle()

mag_angles = [15, 30, 345, 330]
mag_sides = ["left", "right"] 


angle_shuffler = shuffler.Shuffler(mag_angles, trials/2, 5)
angles = angle_shuffler.shuffle()

side_shuffler = shuffler.Shuffler(mag_sides, trials/2, 4)
sides = side_shuffler.shuffle()

items = ["add", "mag"]

#STIMULUS TYPE AND SIDE SHUFFLER
stim_shuffler = shuffler.Shuffler(items, trials, 5)
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
				time.sleep(0.75)
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

while len(stimList):

	if problemQ:
		stim = problemQ[2]
		n1 = problemQ[0]
		n2 = problemQ[1]
	else:
		stim = stimList.pop(0)
		if stim == "mag":
			p = problems[mag_problems.pop(0)]
			n1 = p[0][0]
			n2 = p[0][1]
			solution = str(max([n1, n2]))
		elif stim == "add":
			p = problems[add_problems.pop(0)]
			n1 = p[0][0]
			n2 = p[0][1]
			solution = str(n1 + n2)



	numbers = [n1, n2]
	random.shuffle(numbers)

	if stim == "mag":
		problemString = "%s | %s" % (numbers[0], numbers[1])
		
		a = angles.pop(0)
		s = sides.pop(0)
		x = screen.size[0] / 7
		y = screen.size[1] / 2

		if s == "left":

			ns1 = Text(text = str(n1), angle = a, anchor = 'center', position = [x * 3, y], color = [255,255,255], font_size = fontsize)
			ns2 = Text(text = str(n2), angle = 0, anchor = 'center', position = [x * 4, y], color = [255,255,255], font_size = fontsize)

		else:

			ns1 = Text(text = str(n1), angle = 0, anchor = 'center', position = [x * 3, y], color = [255,255,255], font_size = fontsize)
			ns2 = Text(text = str(n2), angle = a, anchor = 'center', position = [x * 4, y], color = [255,255,255], font_size = fontsize)


		expPort = Viewport(screen=screen, stimuli=[ns1, ns2])


	else:
		ns1 = str(numbers[0])
		ns2 = str(numbers[1])

		if len(ns1) == 1:
			ns1 = " %s" % ns1
		if len(ns2) == 1:
			ns2 = " %s" % ns2	

		problem = "   %s\n+ %s" % (ns1, ns2)
		problemString = "%s + %s" % (numbers[0], numbers[1])


		expText, expPort = printText(screen, problem, fontsize, (255, 255, 255))

	subject.inputData(trial, "comparison", comparison)
	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", problemString)
	subject.inputData(trial, "type", stim)

	#format problem
	print "----------------------"
	print "PROBLEM: %s" % problemString
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
tableName = "training"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=False)


