import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *

from pygame.locals import *

import sys
import os
import random


#suckas need to changes this on they home computaz
sys.path.append('/home/cogdev/code/OpenPsyc')

from experiments import printWord, printText
from mongoTools import MongoAdmin
import shuffler

try:
	number = sys.argv[1]
except:
	sys.stderr("You need to specify a participant ID")


db = MongoAdmin("CAT2")
posts = db.getTable("ver_sets").posts

q = {}
q['s_id'] = number

memProblems = []
calcProblems = []
for r in posts.find(q):
	ns = [r['n1'], r['n2']]

	if r['orig_strat'] == 'calc':
		calcProblems.append(ns)
	elif r['orig_strat'] == 'mem':
		memProblems.append(ns)

verProbs = calcProblems + memProblems

print verProbs

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

distractors = [2, -2]
lOrR = ['l', 'r']

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
	key = event.key
	
	if key == K_LALT:
		if correct == "left":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')
	elif key == K_RALT:
		if correct == "right":
			ACC = 1
		else:
			ACC = 0
		print "right"
		p.parameters.go_duration=(0, 'frames')


dShuffler = shuffler.Shuffler(distractors, len(verProbs), 3)
dists = dShuffler.shuffle()

sideShuffler = shuffler.Shuffler(lOrR, len(verProbs), 3)
sides = sideShuffler.shuffle()


#generate texts
strat2 = "Please describe your strategy"
stratText, stratPort = printWord(screen, strat2, 60, (255, 255, 255), h_anchor = 2.7)
	
strategy = ""

for prob, dist, side in zip(verProbs, dists, sides):
	problem = "%s + %s = ?" % (prob[0], prob[1])
	solution = str(prob[0] + prob[1])
	distractor = str(prob[0] + prob[1] + dist)
	
	if side == "l":
		correct = "left"
		L = distractor
		R = solution
	elif side == "r":
		correct = "right"
		L = solution
		R = distractor
	
	probText, probPort = printWord(screen, problem, 60, (255, 255, 255), h_anchor = 2.9)
	lt, l = printWord(screen, L, 60, (255, 255, 255), v_anchor = 0.5, h_anchor = 2.6)
	rt, r = printWord(screen, R, 60, (255, 255, 255), v_anchor = 0.5, h_anchor = 3.3)	
	fixText, fixCross = printWord(screen, '', 60, (255, 255, 255), h_anchor = 2.5)

	#BLOCK 1 - PROBLEM
	p = Presentation(go_duration=('forever', ), viewports=[probPort, l, r])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()
	
	#BLOCK 2 - STRATEGY SELECTION
	p2 = Presentation(go_duration=('forever', ), viewports=[solPort, infoPort, stratPort])
	p2.add_controller(None, None, FunctionController(during_go_func=strategy_controller, temporal_variables = FRAMES_ABSOLUTE))
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]        
	p2.go()
	
	#BLOCK 3 - BLANK SCREEN
	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()
