#!/usr/bin/env python

import sys, os, time, copy, pickle
import bailey_shuffler, Subject
import wx
import experiments
from experiments import printWord

import pygame
from pygame.locals import *
import stroop_stats

	
import VisionEgg
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, ConstantController
from VisionEgg.DaqLPT import raw_lpt_module
from VisionEgg.Text import *
from VisionEgg.Textures import *

def showStimulus(screen, text, goooKey, colour):
	word, viewport = printWord(screen, text, 200, colour)
	p = Presentation(go_duration=(0.5,'seconds'),viewports=[viewport])
	p.go()
	start = time.clock()
	exit = 0
	while not exit:
		data = raw_lpt_module.inp(0x379) & 0x20		
		#print data
		if not data:
			#print "hello"
			RT = time.clock()
			p.parameters.go_duration = (0.032, 'seconds')
			dataList.append ([text, colour, start, RT])
			exit = 1
		else:
			pass


		#insStim, insView = printText(screen, insText, 30, (255, 255,255))
		#instructions = Presentation(go_duration=('forever',), viewports=[insView])

class memFrame(wx.Frame):
	def __init__(self, parent, id, title, wordList, answers):
		wx.Frame.__init__(self, parent, id, title)
		self.words = wordList
		self.dWords = copy.deepcopy(wordList)
		self.answers = answers

		self.answerList = []		

		self.sw = wx.ScrolledWindow(self)
		
		screenX = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
		screenY = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
		
		centreY = screenY / 24
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		
		self.mainSizer = wx.FlexGridSizer(3, 1, 5, 5)
		
		self.topBar = wx.Panel(self.sw, -1, size=(screenX, centreY))

		#self.topBar.SetBackgroundColour(wx.RED)

		self.titleText = wx.StaticText(self.topBar, -1, 'Do you remember seeing any of these words?  Check the box to give your answer.', style = wx.ALIGN_CENTER)

		self.mainSizer.Add(self.topBar, wx.EXPAND)
		
		wordSizer, wordSize = self.makeList()		

		#mainSizer.Add(wordSizer)
		
		self.doneButton = wx.Button(self.sw, -1, 'Next>>', size=(wordSize[0], centreY))
		
		self.topBar.SetSize((wordSize[0], centreY))

		self.titleText.SetSize((wordSize[0], centreY))

		self.mainSizer.Add(self.doneButton, wx.EXPAND)
		
		self.Bind(wx.EVT_BUTTON, self.onOK)
		
		self.sw.SetScrollbars(20,20,55,40)
		
		box.Add(self.mainSizer)

		centreX = (screenX - wordSize[0]) / 2
		
		box.PrependSpacer((centreX, screenY))
		
		self.sw.SetSizer(box)
		
		self.SetSize((screenX, screenY))


	def makeList(self):
		#make the list of words with radio buttons to go in the scroll window
		if self.dWords:		
			try:
				x = 10 - len(self.Quiz)
			except:
				x = 10
				self.Quiz = []
			if len(self.dWords) >= x:
				myWords = self.dWords[:x]
				del self.dWords[:x]
			else:
				myWords = self.dWords
				del self.dWords[:]
				self.doneButton.SetLabel('Done')

			

			#Quiz will be a list of the button groups that make up a question - which is itself a list
			#each question entry will contain a list containing the label and the radio button options
			
				
			for word in myWords:
				question = []
				wordlabel = wx.StaticText(self.sw, -1, word)
				#wordSizer.Add(wordlabel, 1)
				question.append(wordlabel)
				for a in self.answers:
					id = self.words.index(word) * len(self.answers) + a[0] - 1
					button = wx.CheckBox(self.sw, id, a[1])
					button.SetValue(0)
					#wordSizer.Add(button)
					question.append(button)
				self.Quiz.append(question)
			self.Bind(wx.EVT_CHECKBOX, self.onCheck)		
			try:
				self.mainSizer.Remove(1)
			except:
				pass			
			
			wordSizer = wx.FlexGridSizer(len(self.Quiz), len(self.answers)+1, 10, 10)

			for question in self.Quiz:
				for button in question:
					wordSizer.Add(button)	
			self.mainSizer.Insert(1, wordSizer)			
			return wordSizer, wordSizer.GetMinSize()

		else:
			myloader = Subject.SubLoader()
			sub = myloader.load()
			filename = os.path.join(sub.path, (sub.name + "_memory.pck"))
			textfile = os.path.join(sub.path, (sub.name + "_memory.txt"))
			f = open(filename, 'w')
			pickle.dump(self.answerList, f)
			f.close()
	
			f = open(textfile, 'w')
			for item in self.answerList:
				f.write(str(item) + "\n")
			f.close()
		
			self.Destroy()
			
	
	def onCheck(self, event):	
		index = event.GetId() / len(self.answers)
		answer = event.GetId() - (index * len(self.answers))
		question = self.Quiz[index]
		for i in range(1, len(self.answers)+1):
			if question[i].GetId() != event.GetId():
				question[i].SetValue(0)

	def onOK(self, event):
		#answer list is a dictionary of words and responses
		answerDict = {}
		answerDict['word']='NULL'
		answerDict['response']='NULL'
		
		answeredRange = []
		
		for question in self.Quiz:
			answered = 0
			tempDict = copy.deepcopy(answerDict)
			for i in range(1, len(question)):
				if question[i].GetValue():
					tempDict['word'] = question[0].GetLabel()
					tempDict['response'] = i
					answeredRange.append(self.Quiz.index(question))
					self.answerList.append(tempDict)
			
		while answeredRange:	
			i = answeredRange.pop()
			myq = self.Quiz.pop(i)
			for item in myq:
				item.Destroy()
		
		self.makeList()		
		self.sw.Layout()
		
					
class memApp(wx.App):
    def OnInit(self):
		answers = experiments.loadAnswers('possibleAnswers.txt')
		frame = memFrame(None, -1, 'Memory Test', memoryList, answers)
		frame.Centre()
		frame.Show(True)
		return True

class subFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)

		mainSizer = wx.FlexGridSizer(4,2,10,10)

		self.number = wx.TextCtrl(self, -1, '')

		mainSizer.Add(wx.StaticText(self, -1, 'Participant Number: '))

		mainSizer.Add(self.number)

		self.male = wx.RadioButton(self, -1, 'Female', style=wx.RB_GROUP)
		self.female = wx.RadioButton(self, -1, 'Male')

		self.left = wx.RadioButton(self, -1, 'Left', style=wx.RB_GROUP)
		self.right = wx.RadioButton(self, -1, 'Right')


		handbox = wx.BoxSizer(wx.HORIZONTAL)
		sexbox = wx.BoxSizer(wx.HORIZONTAL)
	
		handbox.Add(self.left)
		handbox.Add(self.right)

		sexbox.Add(self.female)
		sexbox.Add(self.male)

		mainSizer.Add(wx.StaticText(self, -1, 'Sex: '))

		mainSizer.Add(sexbox)

		mainSizer.Add(wx.StaticText(self, -1, 'Hand: '))

		mainSizer.Add(handbox)

		mainSizer.Add(wx.Button(self, -1, 'OK'))
	
		self.Bind(wx.EVT_BUTTON, self.onOK)

		self.SetSizer(mainSizer)

		self.Layout()

	def onOK(self, event):
		if self.male.GetValue():
			sex = 2
		else:
			sex = 1
		if self.left.GetValue():
			hand = 1		
		else:
			hand = 2
		
		sub = Subject.Subject(self.number.GetValue(), sex, hand)

		sub.save()

		self.Destroy()

class subInfo(wx.App):
	def OnInit(self):
		frame = subFrame(None, -1, 'Enter Participant Info')
		frame.Centre()
		frame.Show(True)
		return True	


def main():


	subjectApp = subInfo(0)
	subjectApp.MainLoop()

	pygame.init()
	screen = get_default_screen()
	screen.parameters.bgcolor = (0.0,0.0,0.0,0.0)
	pygame.display.set_caption("Welcome to the Experiment")

	global dataList

	dataList = []
	
	myList, justWords, followWords = bailey_shuffler.makeStroopList()

	print len(myList)
	print len(justWords)
	print len(followWords)

	for item in myList:
		showStimulus(screen, item[0][1], item[1])

	#now we need to make a list of the words with some distractors
	global memoryList

	memoryList = bailey_shuffler.makeDistractorList(justWords, followWords)
	
	#now we launch our wx App
	memoryApp = memApp(0)
	memoryApp.MainLoop()

	myloader = Subject.SubLoader()

	sub = myloader.load()

	filename = os.path.join(sub.path, (sub.name + "_stroop_data.pck"))

	textfile = os.path.join(sub.path, (sub.name + "_stroop_data.txt"))

	f = open(filename, 'w')

	pickle.dump(dataList, f)

	f.close()

	f = open(textfile, 'w')
	
	for line in dataList:
		f.write(str(line)+ "\n")

	f.close()

	stroop_stats.addSubData(sub)

	#stroop_stats.writeAllSubjects()

	stroop_stats.addSubMemoryData(sub)

	#stroop_stats.writeAllMemory()

	#stroop_stats.printMemoryWords()

	#stroop_stats.printStroopWordResults()

	#print dataList

if __name__ == '__main__': main()
