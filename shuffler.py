#usr/bin/env/python

"""
C. Battista Psychometric Experiment Module - Built in the Peters Lab
Copyright (C) 2007 Christian Joseph Battista

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

import os, pickle, random, glob, copy

"""
Condition Class
Condition objects are used to carry lists of items for an IV, as well as the name of that IV and the max allowable
repetitions that will be tolerated during the creation of pseudorandom lists.  Here is where you would be specifying
the random rules.
Args are your IV item list, the IV name and allowable repeats
"""
class Condition:
	def __init__(self, items, name="", repeats=2):
		self.items = items
		self.name = name
		self.repeats = repeats
		self.num = len(items)
		#leave this slot blank as it will be filled in by the MultiShuffler
		self.instances = 0

	def __str__(self):
		string = "Condition %s: %s items, %s repeats, items: %s\n" % (self.name, self.num, str(self.repeats), str(self.items))
		return string

"""
Stimulus Macro Class
This class is a macro that creates a stimulus object from scratch.  Because the stimulus could theoretically have
many conditions and randomization rules, it is easier to just write the stimClass.py to suit the Condition objects
we are using.  
Args are a list of condition objects
"""
class StimulusMacro:
	def __init__(self, conditions):
		self.conditions = conditions

	"""Create the Custom Stimulus Object According to our Conditions"""
	def createObject(self):
		#__init__ string
		self.slotString = "\tdef __init__(self"
		#__str__ string
		self.returnString = "\t\tstring = \""
		s1 = ""
		s2 = " % ("
		#__eq__ string	
		self.eqString = ""


		#run through our conditions to build the __init__, __str__ and __eq__ methods
		for c in self.conditions:
			#for __init__
			self.slotString = self.slotString + (", %s=0" % c.name)
			#for __str__
			s1 = s1 + c.name + ":%s" + " | "
			s2 = s2 + "str(self." + c.name + "),"
			#for __eq__
			self.eqString = self.eqString + ("\t\tif self.%s == other.%s:\n" % (c.name, c.name))
			self.eqString = self.eqString + "\t\t\tl.append(1)\n\t\telse:\n\t\t\tl.append(0)\n"


		self.slotString = self.slotString + ",number=0):\n"
		s1 = s1.rstrip('| ')
		s2 = s2.rstrip(',')
		self.returnString = self.returnString + s1 + "\"" + s2 +")\n"

		#open and write the stimClass
		f = open("stimClass.py", 'w')
		f.write("class Stimulus:\n")
		f.write(self.slotString)
		for c in self.conditions:
			f.write("\t\tself.%s = %s\n" % (c.name, c.name))
		f.write("\t\tself.number = number")
		f.write("\n")
		f.write("\n")
		f.write("\tdef __str__(self):\n")
		f.write(self.returnString)
		f.write("\t\treturn string\n")
		f.write("\n")
		f.write("\tdef __eq__(self, other):\n")
		f.write("\t\tl=[]\n")
		f.write(self.eqString)
		f.write("\t\treturn l")
		f.close()

	"""
	Write the Function that will create a list of Stimulus Objects for shuffling

	Arg is how many times to iteratate the first list so we get the correct # of stimuli
	"""
	
	def writeListFunction(self, x):
		l = []
		#get list of condition items
		for c in self.conditions:
			l.append(c.items)

		#create string to make up the for loop
		forString = "\tstimList = []\n"
		#start counting tab stops for nested loops
		tabStop = "\t"
		#start counting list #s for variable declaration
		listInt = 1
		#the first list variable
		listString = "list1"

		#now put it all together
		forString = forString + tabStop + ("for list%s in (%s * %s):\n" % (str(listInt), str(l[0]), str(x)))
		for list in l[1:len(l)]:
			tabStop = tabStop + "\t"
			listInt = listInt + 1
			forString = forString + tabStop + ("for list%s in %s:\n" % (str(listInt), str(list)))
			listString = listString + (",list%s" % listInt)

		forString = forString + tabStop + ("\tstimList.append(Stimulus(%s))\n" % listString)
		
		#write it out
		f = open("listMaker.py", "w")
	
		f.write("def listMaker(s):\n")
	
		f.write("\tStimulus = s\n")

		f.write(forString)
	
		f.write("\treturn stimList")
	
		f.close()

"""
MultiShuffler Class.  Used to shuffle a list according to multiple conditions and random rules.  
Args are your list of conditions and how many trials you want to create.  
Note:  Random Rules are specified in the Condition objects, not here.
"""
class MultiShuffler:
	def __init__(self, conditions, trials):
		print "i'm alive"
		self.conditions = conditions
		self.trials = trials
		y = 1
		self.cList = []
		for c in self.conditions:
			#set how many instances of each item should be present
			self.cList.append(c.items)
			c.instances = trials / c.num
			#how many items we'd have if we made a list using nested for loops
			y = y * c.num

		#al-jebr to figure out how many loops through the first condition list we need to get desired # of trials
		x = self.trials / y

		#create stimulus macro
		sm = StimulusMacro(self.conditions)
		#write stimClass.py with stimulus objects
		sm.createObject()
		sm.writeListFunction(x)
		#import the stimulus object
		from stimClass import Stimulus
		#create list of stimuli
		from listMaker import listMaker
		self.stimList = listMaker(Stimulus)
		
		
	#Okay so the idea was to go through the list of stimuli and look at them with the 
	def shuffle(self):
		count = 0
		while count < self.trials:
			random.shuffle(self.stimList)
			repeats = []
			repeatTally = [0] * len(self.conditions)
			for c in self.conditions:
				repeats.append(c.repeats)

			#go through list and check for repeats
			badshuffle = 0
			count = 1
			while not badshuffle:
				if count == self.trials:
					break				
				comp = self.stimList[count-1] == self.stimList[count]

				for i in range(0, len(comp)):
					if comp[i] == 0:
						repeatTally[i] = 0
					else:
						repeatTally[i] = repeatTally[i] + comp[i]

				for i, j in zip(repeatTally, repeats):
					if i < j:
						pass
					else:
						print count
						badshuffle = 1
						print "bad shuffle"

				count = count + 1

		return self.stimList
			
	
#BEHOLD THE MIGHTY SHUFFLER CLASS - needs cleanup but is damn useful
class Shuffler:
	"""args are list of items, number of trials, allowable repeats and ratio of items (an n-tuple with index corresponding to item)"""
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
					
			multi = self.trials / len(self.itemList)
			
			self.itemList = self.itemList * multi
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
		

			

