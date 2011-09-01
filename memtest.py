#memory test outline
import random
import shuffler
import os
import time

def clear(dur=0):
	os.system("clear")
	if dur:
		time.sleep(dur)

def write(msg, dur=2, c=False):
	if c:
		clear()
	print msg
	time.sleep(dur)

def ask(msg, dur=2, c=False):
	if c:
		clear()
	answer = raw_input("%s:  " % msg)
	return answer

sense = ["The cat purred", "That dog was yappy", "I didn't like that dog", "I really prefered the cute kitty", "The dog was too annoying and barky", "I guess deep down I'm a cat person"]
nonsense = ['Outpost the green', 'Make pursuit table locker', 'Guys into crimson request fetch', 'd', 'e', 'f']

trials = len(sense) * 2

nORs = shuffler.Condition([0, 1], "sense", 3)
sizes = shuffler.Condition(range(len(sense)), "size", 3)

ms = shuffler.MultiShuffler([nORs, sizes], trials)
stimList = ms.shuffle()

instructions = "Remember the last word from each sentence while answering whether the sentences make sense or not."

question1 = "Did that make sense? (y/n)"

question2 = "What were those words?"

wordList = []

clear()

write(instructions)
clear(1)

for s in stimList:

	if s.sense:
		sentence = sense[s.size]
	else:
		sentence = nonsense[s.size]

	write(sentence)
	clear(1)
	

	wordList.append(sentence.split(' ')[-1])

	answer = ask(question1)
	if (answer == "y" and s.sense) or (answer == "n" and not s.sense):
		correct = "correct!"
	else:
		correct = "incorrect!"	

	write(correct, 1, True)

	clear(1)
	write(question2)
	clear(1)

print wordList




