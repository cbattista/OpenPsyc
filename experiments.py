#usr/bin/env/python

"""
C. Battista PsychoMetric Experiments Module
Copyright (C) 2007 Christian Joseph Battista/Jobe Microsystems

email - battista.christian@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program, 'LICENSE.TXT'; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""


#here is the standard subject info GUI you use at the start of most experiments
#we ask for the subject #, the session #, the subject's sex and their handedness

import pygame
import VisionEgg
from VisionEgg.GUI import *
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import *




class Point:
	pass

def printWord (screen, theText, fontSize, theColor, h_anchor = 1, v_anchor = 1):
	x = (screen.get_size()[0] / 4) * h_anchor
	y = screen.get_size()[1] / 2 * v_anchor
	myFont = pygame.font.Font(None, fontSize)
	x = x - (myFont.size(theText)[1])
	word = Text(text = theText, position = (x,y), color = theColor, font_size = fontSize)
	viewport = Viewport (screen = screen, stimuli = [word])
	return word, viewport

def printText (screen, theText, fontSize, theColor, h_anchor = 1, v_anchor = 1):
	instructions = []
	textColor = theColor
	screensize = screen.get_size()
	spacebuff = Point()
	spacebuff.x = screensize[0]/12 * h_anchor
	spacebuff.y = screensize[1] - (screensize[1]/12 * v_anchor)
	myFont = pygame.font.Font(None, fontSize)
	for line in theText:
		if line == "\n":
			spacebuff.y = spacebuff.y - myFont.size('A')[1]*2
		else:
			myLine = line.replace("\n", "")
			myWords = myLine.split(' ')
			rangeCount = 1
			doesItFit = ""
			n = len(myWords)
			while n >= 0:
				itFits = doesItFit
				doesItFit = doesItFit + myWords[rangeCount-1] + (" ")
				fitVal = screensize[0] - spacebuff.x * 2
				if myFont.size(doesItFit)[0] < fitVal:
					if n == rangeCount:
						spacebuff.y = spacebuff.y - myFont.size('A')[1]
						instructions.append(Text ( text = doesItFit, position = (spacebuff.x, spacebuff.y), color = theColor, font_size = fontSize))
						n = 0
						doesItFit = ""
						break
					else:
						rangeCount = rangeCount + 1
						itFits = doesItFit
						
				else:
					spacebuff.y = spacebuff.y - myFont.size('A')[1]
					instructions.append(Text ( text = itFits, position = (spacebuff.x, spacebuff.y), color = theColor, font_size = fontSize))
					doesItFit = ""
					n = n -rangeCount + 1
					del myWords[0:rangeCount-1]
					rangeCount = 1
	viewport = Viewport( screen=screen, stimuli=instructions)
	return instructions, viewport

	f = open(script, 'r')
	
	trialLines = []
	
	for line in f.readlines():
		trialLines.append(line)
	
	return trialLines
		
#this function blits some parsed text on the screen
#it takes the screen to blit to as an argument and also the file which holds the text
#since it just shows text and then quits once SPACEBAR is pressed, it is good for showing experiment instructions, hence the name
def showInstructions(screen,  textfile, textSize=30, textcolor=(0, 0, 0)):
	#create our instruction screen
	#load up the instruction text
	f = open(textfile, 'r')
	insText = f.readlines()
	f.close()

	if len(insText) > 1:
		insStim, insView = printText(screen, insText, textSize, textcolor)
	else:
		insSim, insView = printWord(screen, insText, textSize, textcolor)

	instructions = Presentation(go_duration=('forever',), viewports=[insView])

	#add a quit function and a handler to go with it
	def quitKey(event):
		if event.key == pygame.locals.K_SPACE:
			quit()

	def quit(dummy_arg=None):
		instructions.parameters.go_duration = (0,'frames')

	instructions.parameters.handle_event_callbacks=[(pygame.locals.QUIT, quit),(pygame.locals.KEYDOWN, quitKey)]

	#show instructions
	instructions.go()

