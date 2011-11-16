from experiments import printWord, showInstructions
import subject
import shuffler
import pygame
import random
from CBalance import Counterbalance as cb

import VisionEgg
from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *

sub = subject.Subject(666, experiment='gonogo')

words = {}
words['positive'] = range(0, 30)
words['negative'] = range(30, 60)
words['neutral'] = range(60, 90)

maxACC = 5

blockorder = cb(['positive', 'negative'], "gonogo.pck").advance()

gng = shuffler.GoNoGo()

def key_handler(event):
	global signal
	global ACC
	global acc
	global pressed
	global RT

	if event.key == pygame.locals.K_SPACE:
		if signal:
			ACC += 1
			acc = 1
			pressed = 1
		else:
			acc = 0
			pressed = 1
			ACC = 0

		RT = p.time_sec_since_go

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

c, cv = printWord(screen, 'O', 48, [0, 255, 0])
ic, icv = printWord(screen, '+', 48, [255, 0, 0])
f, fv = printWord(screen, '', 48, [0, 0, 0])

cp = Presentation(go_duration=[0.1, 'seconds'], viewports=[cv])
icp = Presentation(go_duration=[0.1, 'seconds'], viewports=[icv])
fix = Presentation(go_duration=[0.05, 'seconds'], viewports=[fv])

trial = 0

for block in blockorder:
	for gowords in ([block, 'neutral'], ['neutral', block]):
		ACC = 0
		while ACC <= maxACC:
			trial+=1
			RT = 0
			pressed = 0
			signal = gng.getSignal()

			print signal
			if signal:
				acc = 0
				word = random.choice(words[gowords[0]])
			else:
				acc = 1
				word = random.choice(words[gowords[1]])

			print word

			w, v = printWord(screen, str(word), 48, [255, 255, 255])
			p = Presentation(go_duration=[0.675, 'seconds'], viewports=[v])
			p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
			p.go()

			sub.inputData(trial, "word", word)
			sub.inputData(trial, "block", block)
			sub.inputData(trial, "RT", RT)
			sub.inputData(trial, "acc", acc)
			sub.inputData(trial, "accTally", ACC)

			#feedback
			if acc:
				cp.go()
			else:
				icp.go()

			fix.go()

		ACC = 0

	showInstructions(screen, "Time for a break.  Press space to continue.")
