import experiments_beta
from experiments_beta import *


def randomize():
	items = [0, 30, 60, 90, 120, 150, 180]

	trials = 112

	repeats = 2

	ratio = [20, 40, 20, 8, 8, 8, 8]
	shuffler = Shuffler (items, trials, repeats, ratio)

	myList = shuffler.shuffleIt()

	print myList

	sum = 0
	for item in myList:
		sum = sum + item
	
	average = sum / len(myList)

	print average

def computeSimpleRatios():
	items = [0, 60, 90, 120, 150, 180]
	trials = 112
	for num in range(16, trials + 1):
		sum = 0
		sum = 30 * num
		for item in items:
			others = (trials - num) / 6
			sum = sum + (others * item)
		avg = sum / trials
		if avg == 60:
			print "Weight: %i, Others: %i Avg: %i" % (num, others, avg)
		
def computeComplexRatios():
	f = open('weights.txt', 'w')
	items = [0, 30, 60, 90]
	trials = 112
	neighbours = range(8, 21)
	neighbours.reverse()
	target = range(8, 80)
	for t in target:
		for n in neighbours:
			sum = 0
			sum = 150 * t
			sum = sum + (120 * n) + (180 * n)
			others = (trials - t - (n*2)) / len(items)
			for item in items:
				sum = sum + (others * item)
			avg = sum / trials
			if avg == 120:
				f.write("# of 30s: %i | # of 0s and 60s: %i | # of 90s, 120s, 150s, 180s: %i | Average: %i\n" % (t, n, others, avg))
	f.close()
computeComplexRatios()
#randomize()