#usr/bin/env/python

#here is the standard subject info GUI you use at the start of most experiments
#we ask for the subject #, the session #, the subject's sex and their handedness

import os, cPickle, random
import Tkinter
from Tkinter import *

try:
	import pygame
	import VisionEgg
	from VisionEgg.GUI import *
	from VisionEgg.Core import *
	from VisionEgg.FlowControl import Presentation
	from VisionEgg.Text import *
except:
	pass

class Point:
	def __init__(self,x=0,y=0):
		self.x = x
		self.y = y

"""function to print a paragraph or so of text"""
def printText (screen, theText, fontSize, theColor):
	instructions = []
	textColor = theColor
	screensize = screen.size
	spacebuff = Point()
	spacebuff.x = screensize[0]/12
	spacebuff.y = screensize[1] - screensize[1]/12
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

"""function to print a single word"""
def printWord (screen, theText, fontSize, theColor):
	instructions = []
	textColor = theColor
	screensize = screen.size
	spacebuff = Point()
	myFont = pygame.font.Font(None, fontSize)
	fontX = myFont.size(theText)[0]
	fontY = myFont.size(theText)[1]

	spacebuff.x = (screensize[0] / 2) - (fontX / 2)
	spacebuff.y = (screensize[1] / 2) - (fontY / 2)


	print fontX, fontY


	instructions.append(Text ( text = theText, position = (spacebuff.x, spacebuff.y), color = theColor, font_size = fontSize))
	
	viewport = Viewport( screen=screen, stimuli=instructions)
	return instructions, viewport
	

#BEHOLD THE MIGHTY SHUFFLER CLASS - needs cleanup but is damn useful
class Shuffler:
	def __init__(self, items=[], trials=0):
		self.items = items
		self.trials = trials
		self.itemList = []
		self.instances = trials  / len(items)

	def shuffleIt(self):
		listgood = 0
		while listgood != 1:
			trialCounter = 1
			while trialCounter <= self.trials:
				#assign random item from list of items
				myChoice = random.choice(self.items)
				#for first two trials no pattern can exist, so add values w/o a check
				if trialCounter < 3:
					self.itemList.append(myChoice)
					trialCounter = trialCounter + 1
				#after that we must check for 3 in a rows
				else:
					#don't add anything to list the 2 preceding values are the same
					if myChoice == self.itemList[trialCounter-2] and myChoice == self.itemList[trialCounter-3]:
						pass
					#if 2 preceding are not same as current, add it to itemList and go to next trial
					else:
						self.itemList.append(myChoice)
						trialCounter = trialCounter + 1	
			#if we have equal amounts of each instance then we're OK.
			print self.itemList
			if self.checkEquality():
				print self.itemList
				return self.itemList
				#tell the listgood while we can exit
				listgood = 1
			#otherwise we need to regenerate the list - empty list and go back to top of listgood while
			else:
				self.itemList = []
	

	def checkEquality(self):
		checkList = []
		for items in self.items:
			if self.itemList.count(items) == self.instances:
				checkList.append(1)
			else:
				checkList.append(0)
		if 0 in checkList:
			return 0
		else:
			return 1

	#shuffle a list with some parameters
	#use this function when you have 2 lists to shuffle, for instance x =  [0,1] and y = [1,2,3,4,5] where each item 
	#of y should be assigned each item of x once
	#first you would use shuffleIt to make a long list of 'parameters', that is, enough x items to fill up the desired
	#number of trials.  then use shuffleIt2 to assign items in y to the parameter list
	#returns list of [item y, item x], one for each trial
	def shuffleIt2(self, params):
		i = 1
		itemList = []
		myList = []

		while i <= self.instances:
			for item in self.items:
				myList.append(item)
			random.shuffle(myList)
			itemList.append(myList)
			myList = []
			i = i + 1

		for par in params:
			self.itemList.append([itemList[par][0], par])
			itemList[par].pop(0)
				

		return self.itemList

			
	def shuffleItWithParams(self, list1, list2):
		#shuffle the list using its current itemList as parameters
		params = self.itemList
		self.itemList = []
		trialCounter = 1
		while trialCounter <= self.trials:
			if params[trialCounter-1] == 1:
				random.shuffle(list1)
				self.itemList.append(list1[0])
				list1.pop(0)
				trialCounter = trialCounter + 1
			#otherwise do the same with the nomatch list
			else:
				random.shuffle(list2)
				self.itemList.append(list2[0])
				list2.pop(0)
				trialCounter = trialCounter + 1
		return self.itemList

	def shuffleItwithinTrials(self, lastItems):
		#now we've got to add the angles to each pair
		#for each pair (e.g. 1,2 or 19,19 or whatever), each item in angles must be represented once
		#we can make 12 distinct random angle lists (1 for each pair) and then add them 
		#as we step through the face pair list
		#let's make the 12 shuffled angle lists
		trialCounter = 1
		while trialCounter < self.trials:
			myList = []
			blocks = 1
			while blocks <= 12:
				weeList = self.items[:]
				random.shuffle(weeList)
				#before we can be sure the shuffled list is OK, we must make sure no angles are repeated next
				#to each other
				if blocks < 2:
					myList.append(weeList)
					blocks = blocks + 1
				else:
					if myList[blocks-2][-1] == weeList[0]:
						pass
					else:
						myList.append(weeList)
						blocks = blocks + 1
			#now we have to add all the angles
			#we musn't repeat two angles in a row, so let's store the previous x value
			#initialize to an angle we're not using, in this case 1
			newList = myList[:]
			lastx = 1
			#print myList
			#print newList
			for items in lastItems:
				myIndex = faces.index(items)
				x = newList[myIndex][0]
				#for the first entry we don't need to check anything
				if len(self.itemList) < 2:
					self.itemList.append([items[0], items[1], x])
					newList[myIndex].pop(0)
					lastx = x
					trialCounter = trialCounter + 1
				#for the rest
				else:
					#check if the last angle we put in is the same as the current one
					#by this method we can run into problems if there is a single item list
					#with a wrong value - there won't be [1] to put in
					#so if that happens we have to restart the loop and try again
					if x == lastx and len(newList[myIndex]) > 1:
						#it is the same we will put in the next angle in the list instead
						x = newList[myIndex][1]
						self.itemList.append([items[0], items[1], x])
						newList[myIndex].pop(1)
						lastx = x
						trialCounter = trialCounter + 1
					elif x == lastx and len(newList[myIndex]) == 1:
						self.itemList = []
						trialCounter = 1
						break
					else:
						#otherwise continue as usual
						self.itemList.append([items[0], items[1], x])
						newList[myIndex].pop(0)
						lastx = x
						trialCounter = trialCounter + 1
		return self.itemList


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
		colorShuffler = Shuffler(myColors, trials)
		print 'made shuffler'
		colorList = colorShuffler.shuffleIt()
		print colorList
	
		if self.useWords:
			wordList = self.createWordList(colorList)
			return colorList, wordList			
		else:
			return colorList

def loadAnswers(answerFile):
	answerList = []
	f = open(os.path.join('data', answerFile), 'r')
	for line in f.readlines():
		temp = line.strip()
		answerList.append([int(temp.split('_')[0]), temp.split('_')[1]])
	f.close()
	return answerList	
