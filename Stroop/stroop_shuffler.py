#!usr/bin/env/python

import experiments
from experiments import *
import experiments_beta
import random
import os

def makePracticeList(trials=20):
	words = ['one','two','three','four','five']
	#print 'making list'
	pracStroop = experiments.Stroop(useWords=1, words=words)
	#print 'made shuffler'
	pracColors, pracWords = pracStroop.createList(trials)
	finalList = []
	for i in range(0, trials):
		finalList.append([pracWords[i], pracColors[i]])

	return finalList

def makeClassicStroop():
	print 'making classic stroop list'

	stroop = Stroop(useWords=1)

	colorList, wordList = stroop.createList(32)

	followWords = []
	finalList = []
	justWords = []

	for i in range(0, len(wordList)):
		finalList.append([wordList[i], colorList[i]])
		justWords.append(wordList[i])

	return finalList, justWords, followWords
