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


sys.path.append('/home/cogdev/code/OpenPsyc/')

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
subject = subject.Subject(number, 1, 1, "training")

#connect to db
db = MongoAdmin("magnitude")

#retrieve problems
posts = db.getTable("post_sets").posts

q= {}
q['s_id'] = number
q['trained'] = 1

problems = []

for r in posts.find(q):
	ns = [r['n1'], r['n2']]
	trained = r['trained']
	orig_strat = r['orig_strat']

	problems.append([ns, trained, orig_strat])


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




add_problems = problems * 10

bad = False
quit = 0

#make production list
while not quit:
	random.shuffle(add_problems)
	last_five = []
	for p in add_problems:
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

bad = False
quit = 0

mag_problems = problems * 10

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

def pause_handler(event):
	if event.key == K_SPACE:
		print "BEGINNING EXPERIMENT"
		pause.parameters.go_duration = (0, 'frames')

#default strategy
strategy = None

trial = 1

fixText, fixCross = printWord(screen, '', 60, (255, 255, 255), h_anchor = 2.5)

print "PRESS SPACE TO START"

pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

for stim in stimList:
		
	if stim == "mag":
		p = mag_problems.pop(0)
		symbol = "|"
		solution = str(max([n1, n2]))
	elif stim == "add":
		p = add_problems.pop(0)
		symbol = "+"
		solution = str(n1 + n2)

	n1 = p[0][0]
	n2 = p[0][1]

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
	subject.inputData(trail, "type", stim)

	#format problem
	print "----------------------"
	print "PROBLEM: %s" % problem
	print "SOLUTION: %s " % solution
	print "----------------------"

	ns = [n1, n2]

	#default values for misfiring voice key
	misfire = 0
	ACC = 1


	expText, expPort = printWord(screen, problem, 60, (255, 255, 255), h_anchor = 2)

	#BLOCK 1 - Problem & RESPONSE

	p = Presentation(go_duration=('forever', ), viewports=[expPort])
	p.add_controller(None, None, FunctionController(during_go_func=problem_controller, temporal_variables = FRAMES_ABSOLUTE))
	p.go()

	#BLOCK 2 - STRATEGY SELECTION & GRADING
	p2 = Presentation(go_duration=('forever', ), viewports=[expPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()

	subject.inputData(trial, "misfire", misfire)
	subject.inputData(trial, "ACC", ACC)

	#blank screen
	p3 = Presentation(go_duration=(1.5, 'seconds'), viewports=[fixCross])
	p3.go()

	trial = trial + 1

	subject.printData()

#save sub
subject.printData()

fileName = subject.fname
dbName = "magnitude"
tableName = "training"

reader = ReadTable(fileName = fileName, dbName=dbName, tableName = tableName, clear=False)


