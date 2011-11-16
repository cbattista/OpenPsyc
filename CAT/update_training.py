#update_training.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid, exp="pre_clean")
post = problem.Problems(DB, sid, exp="post_clean")


pre.update(update={'$set' : {'trained' :'untrained'}})
post.update(update={'$set': {'trained' :'untrained'}})

f = open("P_%s.csv" % sid)

#mark the trained problems
for line in f.readlines():
	frags = line.split(',')
	n1 = int(frags[0])
	n2 = int(frags[1])
	ns = [n1,n2].sort()
	pre.update({'n1': n1, 'n2': n2}, {'$set' : {'trained' : 'trained'}})
	post.update({'n1': n1, 'n2': n2}, {'$set' : {'trained' : 'trained'}})
	
#mark the novel problems
for pid in post.distinct('id', {'trained':'untrained'}):
	print pid
	post.update({'id': pid}, {'$set': {'trained':'novel'}})
	pre.update({'id': pid}, {'$set' : {'trained':'novel'}})

print "pre"
print pre.count({'trained':'untrained'})
print pre.count({'trained':'novel'})
print pre.count({'trained':'trained'})

print "post"
print post.count({'trained':'untrained'})
print post.count({'trained':'novel'})
print post.count({'trained':'trained'})

