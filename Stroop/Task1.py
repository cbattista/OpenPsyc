#Task1.py

import os
import sys

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, ConstantController
from VisionEgg.DaqLPT import raw_lpt_module
from VisionEgg.Text import *
from VisionEgg.Textures import *

#get the openpsych path
sys.path.append('/OpenPsyc')

from experiments import *
import subject
import stroop


def showStimulus(screen, text, colour, useLPT=True):
	word, viewport = printWord(screen, text, 200, colour)
	p = Presentation(go_duration=(stroopDuration,'seconds'),viewports=[viewport])
	
	if useLPT:
		p.go()
		start = time.clock()
		exit = 0
		while not exit:
			data = raw_lpt_module.inp(0x379) & 0x20		
			#print data
			if not data:
				#print "hello"
				RT = time.clock()
				p.parameters.go_duration = (blank, 'seconds')
				subject.inputData(trial, "text", text)
				subject.inputData(trial, "colour", colour)
				subject.inputData(trial, "RT", RT)
				exit = 1
			else:
				pass

def pause_handler(event):
	if event.key == K_SPACE:
		enoughPractice = True
		pause.parameters.go_duration = (0, 'frames')
	elif event.key == K_r or event.key = K_R:
		pause.parameters.go_duration = (0, 'frames')

			
#CONFIG STUFF
global blankFollow
global stroopDuration
			
stroopDuration = 0.5
blankFollow = 0.032
			

"""
GET PPT INFO
"""

Subject = subject.Subject(1)


#SET SCREEN

pygame.init()
screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0)
pygame.display.set_caption("Welcome to the Experiment")

"""
RUN STROOP NUMBER WORDS, REPEAT UNTIL ACC > 80%
1. run numbers
2. prompt: continue?  y/n

"""
global enoughPractice
global trial
global experiment

trial = 1
experiment = "numbers"

enoughPractice = False

while not enoughPractice:
	pracList = stroop.makePracticeList()
	for item in pracList:
		showStimulus(screen, item[0], item[1])
		trial += 1
		
	#experimenter prompt
	pracText, pracView = printWord(screen, 'Press SPACE TO CONTINUE, R TO REDO', 60, (255, 255, 255))

	pause = Presentation(go_duration=('forever', ), viewports=[pracView])
	pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, practice_handler)]  
	pause.go()



"""
TRADITIONAL STROOP
1.  run trad stroop, 32 trials, 8 colour words
"""

trials = 32
colourWords = ["red", "blue", "green", "white", "yellow", "pink", "orange", "grey"]
colours = [[255, 0, 0], [0, 0, 255], [0, 255, 0], [255, 255, 255], [255, 255, 0], [255, 0, 255], [255, 153, 51], [100, 100, 100]]

Stroop = stroop.Stroop(colourWords, True, colours)
colorList, wordList = stroop.createList(32)

trial = 1 
experiment = "classic"

for colour, word in zip(colorList, wordList):
	showStimulus(screen, word, colour)
	trial += 1


#BEGIN EMOTIONAL STROOP
	
trial = 1
experiment = "emotional_stroop"

highNum = "4758354"
lowNum = "2"

trialList = []
f = open("P_%s.csv") % s_id
for lines in f.readlines():
	lines = lines.strip()
	lines = lines.strip('"')
	trialList.append(lines.split(','))
f.close()

for t in trialList:
	memLoad = t[0]
	block = t[1]
	if block = "low":
		text = "Remember the number %s.\nPress SPACE to continue." % lowNum
	elif block = "high"
		text = "Remember the number %s.\nPress SPACE to continue." % highNum
	else:
		text = "Press SPACE to continue."
	
	showInstructions(text)