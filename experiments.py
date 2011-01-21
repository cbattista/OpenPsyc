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
import Image
import VisionEgg
from VisionEgg.GUI import *
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import *
from VisionEgg.Textures import *




class Point:
	pass

def printWord (screen, theText, fontSize, theColor):
	x = (screen.get_size()[0] / 2)
	y = screen.get_size()[1] / 2
	myFont = pygame.font.Font(None, fontSize)
	x = x - (myFont.size(theText)[0] / 2)
	y = y - (myFont.size(theText)[1] / 2)
	word = Text(text = theText, position = (x,y), color = theColor, font_size = fontSize)
	viewport = Viewport (screen = screen, stimuli = [word])
	return word, viewport

def printText (screen, theText, fontSize, theColor):
	instructions = []
	textColor = theColor
	screensize = screen.get_size()
	spacebuff = Point()
	spacebuff.x = screensize[0]/12
	spacebuff.y = screensize[1] - (screensize[1]/12)
	myFont = pygame.font.Font(None, fontSize)
	fittedText = []
	theText = theText.split('\n')
	for line in theText:
		myWords = line.split(' ')
		doesItFit = ""
		while len(myWords):
			word = myWords.pop(0)
			itFits = doesItFit
			doesItFit += word + (" ")
			fitVal = screensize[0] - spacebuff.x * 2
			if myFont.size(doesItFit)[0] < fitVal:
				itFits = doesItFit
					
			else:
				fittedText.append(doesItFit)
				doesItFit = ""
		fittedText.append(itFits)

	xpos = screen.size[0] / 2
	ypos = screen.size[1] / 2 + len(fittedText) / 2 * myFont.size(fittedText[0])[1]


	for line in fittedText:
		
		instructions.append(Text 
							(text = line, 
							anchor = 'center', 
							position = (xpos, ypos - fittedText.index(line) * myFont.size(line)[1]), 
							color = theColor, 
							font_size = fontSize)
							)



	viewport = Viewport( screen=screen, stimuli=instructions)
	return instructions, viewport

		
#this function blits some parsed text on the screen
#it takes the screen to blit to as an argument and also the file which holds the text
#since it just shows text and then quits once SPACEBAR is pressed, it is good for showing experiment instructions, hence the name
def showInstructions(screen,  text, textSize=60, textcolor=(255, 255, 255)):
	#create our instruction screen
	#load up the instruction text
	insText = text.split("\n")

	if len(insText) > 1:
		insStim, insView = printText(screen, insText, textSize, textcolor)
	else:
		insSim, insView = printWord(screen, insText[0], textSize, textcolor)

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

def showImage(screen, img, duration=1):
	img = Image.open(img)

	#create textures
	tex = Texture(img)

	x = screen.size[0] / 2
	y = screen.size[1] / 2

	stimulus = TextureStimulus(texture = tex, position = (x, y), anchor = 'center')

	#create viewports
	viewport = Viewport(screen=screen, stimuli=[stimulus])

	image = Presentation(go_duration=(duration, 'seconds'), viewports=[viewport])
	image.go()


