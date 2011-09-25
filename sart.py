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

sub = subject.Subject(666, experiment='sart')

digits = range(0, 10)

ls = shuffler.ListShuffler(digits, 30)
stimList = ls.shuffle()
target = 3

sub = subject.Subject(666, experiment="sart")

def key_handler(event):
	global s
	global target
	global acc
	global RT

	if event.key == pygame.locals.K_SPACE:
		if s == target:
			acc = 1
			pressed = 1
		else:
			acc = 0
			pressed = 1

		RT = p.time_sec_since_go

trial = 0

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

pygame.mixer.init()

sound = pygame.mixer.Sound("beep.wav")

sound.play()

for s in stimList:
	trial += 1
	print s
	RT = 0
	acc = 0

	w, v = printWord(screen, str(s), 48, [255, 255, 255])
	p = Presentation(go_duration=[0.675, 'seconds'], viewports=[v])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	sub.inputData(trial, "RT", RT)
	sub.inputData(trial, "acc", acc)
	sub.inputData(trial, "s", s)
	sub.inputData(trial, "target", target)

	sub.printData()

sub.printData()
