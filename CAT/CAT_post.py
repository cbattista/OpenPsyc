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

print myArgs

number = str(myArgs[1])

#create subject
subject = subject.Subject(number, 1, 1, "post_pro")

#connect to db
db = MongoAdmin("CAT2")

#retrieve problems
posts = db.getTable("post_sets").posts

q= {}
q['s_id'] = number

problems = []

for r in posts.find(q):
	ns = [r['n1'], r['n2']]
	trained = r['trained']
	orig_strat = r['orig_strat']

	problems.append([ns, trained, orig_strat])

problems = problems * 2

random.shuffle(problems)

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

fixText, fixCross = printText(screen, '', 60, (255, 255, 255))

print "PRESS SPACE TO START"

pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

for p in problems:
		
	n1 = p[0][0]
	n2 = p[0][1]
	problem = "%s + %s" % (n1, n2)


	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "trained", p[1])
	subject.inputData(trial, "orig_strat", p[2])
	subject.inputData(trial, "problem", problem)

	#format problem
	solution = str(n1 + n2)
	print "----------------------"
	print "PROBLEM: %s" % problem
	print "SOLUTION: %s " % solution
	print "----------------------"

	ns = [n1, n2]

	#default values for misfiring voice key
	misfire = 0
	ACC = 1

	#generate texts
	strat2 = "\n\nPlease describe your strategy"

	stratText, stratPort = printText(screen, strat2, 60, (255, 255, 255))
	expText, expPort = printText(screen, problem, 60, (255, 255, 255))

	#BLOCK 1 - Problem & RESPONSE

	p = Presentation(go_duration=('forever', ), viewports=[expPort])
	p.add_controller(None, None, FunctionController(during_go_func=problem_controller, temporal_variables = FRAMES_ABSOLUTE))
	p.go()

	#BLOCK 2 - STRATEGY SELECTION & GRADING
	p2 = Presentation(go_duration=('forever', ), viewports=[expPort, stratPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()


	subject.inputData(trial, "misfire", misfire)
	subject.inputData(trial, "ACC", ACC)
	subject.inputData(trial, "strategy", strategy)

	#blank screen
	p3 = Presentation(go_duration=(1.5, 'seconds'), viewports=[fixCross])
	p3.go()

	trial = trial + 1

	subject.printData()

#save sub
subject.printData()


