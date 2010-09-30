import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *

from pygame.locals import *

import sys
import os
import random
import serial

#suckas need to changes this on they home computaz
sys.path.append('/home/cogdev/code/OpenPsyc')

from experiments import printWord, printText
from mongoTools import MongoAdmin
import shuffler
import subject

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")


subject = subject.Subject(number, "VER_PRE")

db = MongoAdmin("CAT2")
posts = db.getTable("ver_sets").posts

q = {}
q['s_id'] = number

calcProblems = []
memProblems = []

for r in posts.find(q):
	ns = [r['n1'], r['n2']]
	trained = r['trained']

	if r['orig_strat'] == 'calc':
		calcProblems.append([ns, trained])
	elif r['orig_strat'] == 'mem':
		memProblems.append([ns, trained])

verProbs = calcProblems + memProblems

print calcProblems
print memProblems

#mix these guys up so it's not all trained and untrained in separate blocks
random.shuffle(calcProblems)
random.shuffle(memProblems)

##SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

distractors = [2, -2]
lOrR = ['l', 'r']
strats = ['mem', 'calc']


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

dShuffler = shuffler.Shuffler(distractors, len(verProbs), 3)
dists = dShuffler.shuffle()

sideShuffler = shuffler.Shuffler(lOrR, len(verProbs), 3)
sides = sideShuffler.shuffle()

sShuffler = shuffler.Shuffler(strats, len(verProbs), 3)
strategies = sShuffler.shuffle()


#generate texts
strat2 = "Please describe your strategy"
stratText, stratPort = printWord(screen, strat2, 60, (255, 255, 255), h_anchor = 1)
	
strategy = ""
RT = 0
ACC = 0

fixText, fixCross = printWord(screen, '', 60, (255, 255, 255), h_anchor = 2.5)

print "PRESS SPACE TO START"

pause = Presentation(go_duration=('forever', ), viewports=[fixCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()


trial = 1

for dist, side, strategy in zip(dists, sides, strategies):

	if strategy == "mem":
		prob = memProblems.pop()
		trained = prob[1]
		prob = prob[0]
	elif strategy == "calc":
		prob = calcProblems.pop()
		trained = prob[1]
		prob = prob[0]

	problem = "%s + %s = ?" % (prob[0], prob[1])
	solution = str(prob[0] + prob[1])
	distractor = str(prob[0] + prob[1] + dist)
	
	subject.inputData(trial, "n1", prob[0])
	subject.inputData(trial, "n2", prob[1])
	subject.inputData(trial, "orig_strat", strategy)
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)
	subject.inputData(trial, "dist_offset", dist)
	subject.inputData(trial, "trained", trained)
	
	if side == "l":
		correct = "left"
		L = solution
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = solution
	
	probText, probPort = printWord(screen, problem, 60, (255, 255, 255), h_anchor = 1.5)
	lt, l = printWord(screen, L, 60, (255, 255, 255), h_anchor = 0.5)
	rt, r = printWord(screen, R, 60, (255, 255, 255), h_anchor = 3)	
	fixText, fixCross = printWord(screen, '', 60, (255, 255, 255), h_anchor = 1.5)

	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS
	problem = Presentation(go_duration=(2, 'seconds'), viewports=[probPort])
	problem.go()

	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()

	p = Presentation(go_duration=('forever', ), viewports=[l, r])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	
	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)
	
	#BLOCK 2 - STRATEGY SELECTION
	p2 = Presentation(go_duration=('forever', ), viewports=[stratPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()
	
	subject.inputData(trial, "cur_strat", strategy)
	
	#BLOCK 3 - BLANK SCREEN
	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()
	
	trial = trial + 1
	
	subject.printData()
	
subject.preserve()
