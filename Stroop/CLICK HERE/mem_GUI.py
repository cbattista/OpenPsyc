#!/usr/bin/env/python

import wx
import experiments

class memFrame(wx.Frame):
	def __init__(self, parent, id, title, wordList, answers):
		wx.Frame.__init__(self, parent, id, title)
		pass

class memApp(wx.App):
    def OnInit(self, wordList):
		answer = experiments.loadAnswers('possibleAnswers.txt')
		

		frame = memFrame(None, -1, 'Memory Test', wordList, answers)
		frame.Show(True)
		return True