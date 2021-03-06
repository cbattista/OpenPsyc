#!usr/bin/env/python
"""
#List Shuffler for Bailey Stroop Program

#By Mr. Xian

#So...what are we up to here?

#We have some lists...they are lists of words.  There are 2 types, Target and Neutral (T & N). There are 21 T words and 73 N words.  94 words total, 1 for each trial, making 94 trials.

#Target has three sub-categories -  these are abuse, positive and neutral.   There are 7 abuse, 7 positive and 7 neutral words.

#Ordering

#1.  Each T word presented once pseudorandomly across trials.  Subcategories selected pseudorandomly using no 3 in a row rule.

#2.  Each T word followed by 3 or 4 N words.  Number of N words selected  pseudorandomly using no 3 in a row rule.  

  
"""

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

def makeStroopList():
	print 'making stroop list'

	abuse=[]
	neutral=[]
	positive=[]
	Ns=[]

	abuseF = open(os.path.join('data', 'abuse.txt'), 'r')
	for lines in abuseF.readlines():
		abuse.append(lines.strip())
	abuseF.close()

	neutralF = open(os.path.join('data', 'neutral.txt'), 'r')
	for lines in neutralF.readlines():
		neutral.append(lines.strip())
	neutralF.close()

	positiveF = open(os.path.join('data', 'positive.txt'), 'r')
	for lines in positiveF.readlines():
		positive.append(lines.strip())	
	positiveF.close()

	NsF = open(os.path.join('data', 'Ns.txt'), 'r')
	for lines in NsF.readlines():
		Ns.append(lines.strip())
	NsF.close()

	stroop = Stroop()

	print 'hello'

	colorList = stroop.createList(96)

	print colorList

	#indeces for subcategories of T
	Ts = [1,2,3]

	#to select how many N words follow T words
	threeOrfour = [3,4] 

	#make shufflers
	t_or_f = Shuffler(threeOrfour, 22)
	Tshuffler = Shuffler(Ts, 21)

	#shuffle Lists
	t_or_fList = t_or_f.shuffleIt()
	TList = Tshuffler.shuffleIt()

	wordList = []
	
	followWords = []

	for items in TList:
		#select T word from appropriate category
		if items == 1:
			random.shuffle(abuse)
			word = ['Target - abuse', abuse.pop()]
		elif items == 2:
			random.shuffle(neutral)
			word = ['Target - neutral', neutral.pop()]
		else:
			random.shuffle(positive)
			word = ['Target - positive', positive.pop()]
		
		#append T word
		wordList.append(word)
	
		#select how many N words to follow
		howmany = t_or_fList.pop()
		#append N words
		for i in range(0, howmany):
			random.shuffle(Ns)
			print word			
			word = Ns.pop()
			wordList.append(['Neutral', word])			
			if i == 0:
				followWords.append(word)
			else:
				pass
			
	finalList = []
	justWords = []

	start1 = ['Neutral', 'soap']
	start2 = ['Neutral', 'four']
	
	finalList.append([start1, [0, 255, 0]])
	finalList.append([start2, [255, 0, 0]])


	for i in range(0, len(wordList)):
		finalList.append([wordList[i], colorList[i]])
		justWords.append(wordList[i])

	return finalList, justWords, followWords


def makeDistractorList(words, followWords):
	
	categoryList = []
	pList = []
	aList = []
	nList = []
	NList = []
	
	
	for w in words:
		if w[0] not in categoryList:
			categoryList.append(w[0])
			
	categoryList.sort()
	
	for w in words:
		if w[0] == categoryList[0]:
			NList.append(w[1])
		elif w[0] == categoryList[1]:
			aList.append(w[1])
		elif w[0] == categoryList[2]:
			nList.append(w[1])
		else:
			pList.append(w[1])
	
		
	Fa = []
	
	FaF = open(os.path.join("data", "fakeabuse.txt"), 'r')
	for lines in FaF.readlines():
		Fa.append(lines.strip())
	FaF.close()
	
	Fp = []
	
	FpF = open(os.path.join("data", "fakepositive.txt"), 'r')
	for lines in FpF.readlines():
		Fp.append(lines.strip())
	FpF.close()
	
	Fn = []
	
	FnF = open(os.path.join("data", "fakeneutral.txt"), 'r')
	for lines in FnF.readlines():
		Fn.append(lines.strip())
	FnF.close()
	
	FNs = []
	
	FNsF = open(os.path.join("data", "fakeNs.txt"), 'r')
	for lines in FNsF.readlines():
		FNs.append(lines.strip())
	FNsF.close()
	
	random.shuffle(Fa)
	random.shuffle(Fp)
	random.shuffle(Fn)
	random.shuffle(FNs)
	random.shuffle(followWords)
	

	distractorList = Fa[:5] + Fp[:5] + Fn[:5] + FNs[:15]
	
	wordList = aList[:5] + nList[:5] + pList[:5] + followWords[:15]
	
	shuffler = Shuffler([0,1], 60)
	
	shuffler.shuffleIt()
	
	memoryList = shuffler.shuffleItWithParams(distractorList, wordList)
	
	return memoryList



"""
def main():
	for i in range(1,10):
		myList = makeList()
		filename = "StroopList_" + str(i) + ".txt"
		f = open(filename, 'w')
		for items in myList:
			f.write("Word: " + str(items[0]) + " Color: " + str(items[1]))
			f.write("\n")
		f.close()

if __name__ == '__main__': main()
"""
