#!usr/bin/env/python

import random
import os
import shuffler

class Stroop:
	def __init__(self, colors=[], useWords=0, words=[]):
		self.useWords = useWords
		if colors == []:
			red=[255,0,0]
			blue=[0,0,255]
			green=[0,255,0]
			white=[255,255,255]
			self.colors = [red,blue,green,white]
		else:
			self.colors = colors
		if words == []:
			self.words = ["red", "blue", "green", "white"]
		else:
			self.words = words
		#print self.colors

	def createWordList(self, colorList):
		wordList = []
		for colors in colorList:
			myWords = []
			for j in self.words:
				myWords.append(j)
			i = self.colors.index(colors)
			myWords.pop(i)
			good = 0
			while not good:
				word = random.choice(myWords)
				if wordList == []:
					wordList.append(word)
					prevWord = word
					good = 1
				else:
					if prevWord == word:
						good = 0
					else:
						wordList.append(word)
						prevWord = word
						good = 1
		print wordList
		return wordList

	def createList(self, trials=100):
		myColors = self.colors
		print myColors
		colorShuffler = shuffler.Shuffler(myColors, trials)
		print 'made shuffler'
		colorList = colorShuffler.shuffle()
		print colorList
	
		if self.useWords:
			wordList = self.createWordList(colorList)
			return colorList, wordList			
		else:
			return colorList

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
