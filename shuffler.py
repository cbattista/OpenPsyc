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
		output = "class Stimulus:\n" + self.slotString
		
		for c in self.conditions:
			output += "\t\tself.%s = %s\n" % (c.name, c.name)
		
		output += "\t\tself.number = number\n\n\tdef __str__(self):\n"
		output += self.returnString
		output += "\t\treturn string\n\n\tdef __eq__(self, other):\n\t\tl=[]\n"
		output += self.eqString
		output += "\t\treturn l"
			
		return output
		
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
	
		output = "def listMaker(s):\n"
		output += "\tStimulus = s\n"
		output += forString	
		output += "\treturn stimList"
	
		return output
		
"""
MultiShuffler Class.  Used to shuffle a list according to multiple conditions and random rules.  
Args are your list of conditions and how many trials you want to create.  
Note:  Random Rules are specified in the Condition objects, not here.
"""
class MultiShuffler:
	def __init__(self, conditions, trials):
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
		exec(sm.createObject())		
		exec(sm.writeListFunction(x))

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
						badshuffle = 1

				count = count + 1

		return self.stimList
			
	
#BEHOLD THE MIGHTY SHUFFLER CLASS - needs cleanup but is damn useful
class Shuffler:
	"""args are list of items, number of trials, allowable repeats and ratio of items (an n-tuple with index corresponding to item)"""
	def __init__(self, items=[1,2,3,4], trials=16, repeats=2, ratio=[]):
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
						
	def shuffle(self):
				
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

#a class to make a relatively balanced stimulus list from a set of items, which forbids repeats of item i within r items
class ListShuffler():
	def __init__(self, items=[1,2,3,4], length=24, repeats=3):
		if length % len(items):
			raise Exception("hey meathead I can't make a list of %s things out of %s items" % (length, len(items)))			
		else:
			self.items = items
			self.length = length
			self.iters = length / len(items)
			self.repeats = repeats
	
	def shuffle(self):
		self.finalList = []
		for i in range(self.iters):
			items = copy.deepcopy(self.items)
			random.shuffle(items)
			if not i:
				self.finalList+=items
			else:
				quit = False
				while not quit:
					bad = False				
					for r in range(1, self.repeats):
						my_slice = self.finalList[-r:] + items[:self.repeats-r]
						if len(set(my_slice)) != self.repeats:
							bad = True
					if not bad:
						self.finalList+= items
						quit = True
					else:
						items = copy.deepcopy(self.items)
						random.shuffle(items)

		return self.finalList


	def printList(self):
		print self.finalList
class GoNoGo:
	def __init__(self, gosignal=1, nogosignal=0, minBlock=6, maxBlock=8, blockRepeat=3):
		self.blockRange = range(minBlock, maxBlock+1)
		self.blockSize = random.choice(self.blockRange)
		self.makeSignals()
		self.repeats = 0
		self.blockRepeat= blockRepeat
		self.gosignal = gosignal
		self.nogosignal = nogosignal	

	def getSignal(self):
		if self.signals:
			signal = self.signals.pop()
		else:
			self.nextBlock()
			self.makeSignals()
			signal = self.signals.pop()

		if signal == 'go':
			output = self.gosignal
		else:
			output = self.nogosignal

		return output

	def nextBlock(self):
		newBlock = random.choice(self.blockRange)
		if self.blockSize == newBlock:
			self.repeats += 1
		else:
			self.repeats = 0

		if self.repeats >= self.blockRepeat:
			self.repeats =- 1
			self.next()	
		else:
			self.blockSize = newBlock

	def makeSignals(self):
		self.signals = ['nogo'] * self.blockSize
		self.signals += ['go']
		

class ListAdder:
	def __init__(self, items=[1,2,3,4], size=2):
		self.lists = []
		self.items = items
		self.size = size

	def shuffle(self):
		badshuffle = True

		while badshuffle:
			lists = []
			for i in range(self.size):
				new_items = copy.deepcopy(self.items)
				random.shuffle(new_items)
				lists.append(new_items)

			checkFail = False
			for l in lists:
				index = lists.index(l)
				if index != len(lists)-1:
					if lists[index][-1] == lists[index+1][0]:
						checkFail = True

			if not checkFail:
				badshuffle = False

		newList = []
		for l in lists:
			newList += l

		self.finalList = newList
		return newList



