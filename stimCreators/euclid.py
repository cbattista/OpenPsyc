#euclid.py
import math

#some handy functions for getting the sizes (like area, radius, and perimeter) of a variety of shapes

#HELPER FUNCS
def circleRadius(size, sizemeasure):
	if sizemeasure == 'area':
		return (size / math.pi) ** 0.5
	elif sizemeasure == 'perimeter':
		return size / (math.pi * 2) 

def circleFromRadius(r, measure):
	if measure == 'area':
		return math.pi * r **2
	elif measure == 'perimeter':
		return 2 * math.pi * r
	else:
		return None

def squareRadius(size, sizemeasure):
	if sizemeasure == 'area':
		return (size ** 0.5) / 2 
	elif sizemeasure == 'perimeter':
		return size / 8

def squareFromRadius(r, measure):
	if measure == 'area':
		return (r * 2) ** 2

	elif measure == 'perimeter':
		return r * 8

def triangleRadius(size, sizemeasure):
	if sizemeasure == 'area':
		return ((size * 2) ** 0.5) / 2
	elif sizemeasure == 'perimeter':
		return size / (8 ** 0.5 * 4)

euclid = {'square':{}, 'circle':{}, 'triangle':{}}
euclid['square']['area'] = lambda r: (r*2) ** 2
euclid['square']['perimeter'] = lambda r: r * 8
euclid['square']['radius'] = squareRadius

euclid['circle']['area'] = lambda r:  math.pi * r ** 2
euclid['circle']['perimeter'] = lambda r: 2 * math.pi * r
euclid['circle']['radius'] = circleRadius

euclid['triangle']['area'] = lambda r : ((r * 2) ** 2) / 2
euclid['triangle']['perimeter'] = lambda r : 4 * r + (8 * r **2) ** 0.5
euclid['triangle']['radius'] = triangleRadius




