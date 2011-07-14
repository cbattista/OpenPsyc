#update_training.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid)
post = problem.Problems(DB, sid, exp="post")

print pre.count({'trained': 'novel'})

pre.update(update={'$set' : {'trained' :'novel'}})
post.update(update={'$set': {'trained' :'novel'}})



print post.count({})
print post.count({'trained':'novel'})

f = open("P_%s.csv" % sid)

for line in f.readlines():
	frags = line.split(',')
	n1 = int(frags[0])
	n2 = int(frags[1])
	ns = [n1,n2].sort()
	pre.update({'n1': n1, 'n2': n2}, {'$set' : {'trained' : 'trained'}})
	post.update({'n1': n1, 'n2': n2}, {'$set' : {'trained' : 'trained'}})
	

print pre.count({'trained':'novel'})

