#! /usr/env/python

#assessment.py

import VisionEgg
#VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
import pickle
import time
import random

from pygame.locals import *

import sys
import os
import copy
import adder

from newproblem import *
import shuffler

ns = range(1, 11)

combos = []

for n1 in ns:
	for n2 in ns:
		prob = [n1, n2]
		prob.sort()
		if prob not in combos:
			combos.append(prob)

print len(combos)

db = "jump_kids"
sid = "Tyler"

problems = Problems(db, sid, "addition")

#1st lets assess the kid, show them each problem twice

s = shuffler.ListAdder(combos, size= 2)

stimList = s.shuffle()

for s in stimList:
	problem = Problem(s)

	ns = problem.row['ns']
	n1 = ns[0]
	n2 = ns[1]
	soln = problem.row['solution']	

	#record some problem info
	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", "%s" % problem)
	subject.inputData(trial, "solution", soln)

	random.shuffle(ns)

	lastSoln = copy.deepcopy(soln)


	problem_string = "%s + %s = ?" % (ns[0], ns[1])

	#DISTRACTOR CONFIG
	dist = random.choice(problem.row['distractors'])
	op = random.choice(["+", "-"])

	distractor = eval("%s %s %s" % (soln, op, dist))

	side = random.choice(['l', 'r'])

	if side == "l":
		correct = "left"
		L = str(soln)
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = str(soln)

	
	#SAVE DISTRACTOR INFO
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)
	subject.inputData(trial, "dist_offset", dist)
