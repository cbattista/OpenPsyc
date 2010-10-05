#usr/bin/env/python

"""
C. Battista Psychometric Experiment Module - Built in the Peters Lab
Copyright (C) 2007 Christian Joseph Battista

email - battista.christian@gmail.com
snailmail - Peters Research Lab, Department of Psychology, University of Guelph, Guelph, Ontario, Canada, N1G 2W1

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

import os, pickle, random, glob, copy

#the Subject Class - for storing individual subject study results
#takes subject # as int, sex and handedness as bools and whatever other experiment-depending data goes in a list 
#initialize like this - mySubject = Subject(1, 1, 1, trialData)
#methods are mySubject.saveData() which outputs a data file Subject 1.txt and Subject 1.pck
#and mySubject.loadInfo() which loads the subjectInfo from the subInfo GUI
class SubLoader():
	def __init__(self):
		self.path = "settings/subjectInfo.pck"
		
	def load(self):
		f = open(self.path)
		sub = pickle.load(f)
		f.close()
		return sub

class Subject:
	#initialize current subject, taking sub info from the picked subkectInfo file generated
	#by subjectInfoGUI
	#IMPORTANT - must run GUI before creating instance of Subject class for this to work
	def __init__ (self, number=0, sex=1, hand=1):
		self.number = number
		self.sex = sex
		self.hand = hand

	def save(self):
		f = open("settings/subjectInfo.pck", "w")
		pickle.dump(self, f)
		f.close()
	
#BEHOLD THE MIGHTY SHUFFLER CLASS - needs cleanup but is damn useful
class Shuffler:
	"""args are list of items, number of trials, allowable repeats and ratio of items (an n-tuple with index corresponing to item)"""
	def __init__(self, items, trials, repeats=2, ratio=[]):
		self.items = items
		self.trials = trials
		self.itemList = []
		
		self.ratio = ratio
		
		#check to see if we've specified a ratio
		if not self.ratio:
			self.instances = trials  / len(self.items)
			tolerance = abs((self.instances * len(self.items)) - self.trials)
			self.tolerance = range(-tolerance, tolerance+1)
			#make sure repeats is positive non-zero value
			if repeats <= 1:
				self.repeats = 1
			else:
				self.repeats = repeats
		else:
			self.tolerance = [0]
			
			#now we have to calculate allowable repeats for this ratio
			if len(self.items) == 2:
				allowableRepeats = self.trials / min(ratio)
				if repeats > allowableRepeats:
					self.repeats = repeats
				else:
					self.repeats = allowableRepeats
			else:
				self.repeats = repeats
			
				
		print self.repeats
		
		
				
	def shuffleIt(self):
		
		if not self.ratio:
			listgood = 0
			while listgood != 1:
				#if there are more elements in the list than we have trials
				if len(self.items) > self.trials:
					self.itemList = random.sample(self.items, self.trials)
					return self.itemList
					listgood = 1
			
				#if there are equal amounts of elements and trials
				if len(self.items) == self.trials:
					list = self.items
					random.shuffle(self.items)
					self.itemList = list
					return self.itemList
					listgood = 1
			
				#otherwise...
				while len(self.itemList) < self.trials:
					#assign random item from list of items
					myChoice = random.choice(self.items)
					#for first trials no pattern can exist, so add values w/o a check
					if len(self.itemList) < self.repeats:
						self.itemList.append(myChoice)
					#after that we must check for repeats
					else:
						#begin counting number of repeats, starting at last item in list
						repeats = 0
						for j in range(1, self.repeats+1):
							if myChoice == self.itemList[len(self.itemList)-1]:
								repeats = repeats + 1
						if repeats >= self.repeats:
							pass
						#if 2 preceding are not same as current, add it to itemList and go to next trial
						else:
							self.itemList.append(myChoice)

			
				#we still have a problem, and that is that we need a set amount of instances of each
				#so we get the distinct elements from the list
			
				#so let's check through, adding one to variable 'check' when we are satisfied
				check = 0
						
				#they should be even if we haven't set a ratio
				for item in self.items:
					for t in self.tolerance:
						if self.itemList.count(item) == (self.instances + t):
							check = check + 1
							break
			
				if check == len(self.items):
					return(self.itemList)
					listgood = 1
				else:
					self.itemList = []
	
		else:
			#if we are using a ratio system the logic is a bit different than the brute force method above
			#first we create our complete list of elements in the desired amounts
			for i in range(0, len(self.items)):
				for j in range(1, self.ratio[i]+1):
					self.itemList.append(self.items[i])
			#now we will shuffle them and see if this satisfies our repeat condition in a similar fashion to above
			listgood = 0
			while not listgood:
				random.shuffle(self.itemList)
				repeats = 0
				badList = 0
				for i in range(1, len(self.itemList)):
					if self.itemList[i] == self.itemList[i-1]:
						repeats = repeats + 1
						if repeats >= self.repeats:
							badList = 1
					else:
						repeats = 0
				if not badList:
					return self.itemList
					listgood = 1
				else:
					pass
			
			
	

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

			
	def shuffleItwithParams(self, params):
		#now we have some parameters - params holds whether we are going to use same faces or diff faces
		#let's make a separate list that we can shuffle - we need 4 instances of each face to spread the 19
		#over 84 trials
		trialCounter = 1
		matchList = []
		nomatchList = []
		while trialCounter <= self.trials:
			#print trialCounter
			#make sure our lists are non-empty
			if matchList == [] and nomatchList == []:
				matchList = self.items[6:13]
				random.shuffle(matchList)
				nomatchList = self.items[0:6]
				random.shuffle(nomatchList)
			elif matchList == []:
				matchList = self.items[6:13]
				random.shuffle(matchList)
			elif nomatchList == []:
				nomatchList = self.items[0:6]
				random.shuffle(nomatchList)
			#if this is a matching pair add first item from shuffled list and remove
			if params[trialCounter-1] == 1:
				self.itemList.append(matchList[0])
				matchList.pop(0)
				trialCounter = trialCounter + 1
			#otherwise do the same with the nomatch list
			else:
				self.itemList.append(nomatchList[0])
				nomatchList.pop(0)
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
		

			

