import Image
from numpy import *
from numpy.random import normal

def makeNoise(x, y, name=""):
	#stuff for red/green mask
	npts = x * y
		
	random.seed()
	rednoise=normal(0,255,npts)  #mean, std dev, num pts
	red = rednoise.reshape(x, y)

	greennoise=normal(0,255,npts)
	green = greennoise.reshape(x, y)

	blue = zeros(npts)
	blue = blue.reshape(x, y)

	#print rednoise
	#print greennoise

	pixels = array([red, green, blue])

	#print pixels
	pixels = pixels.T

	arr = pixels.__array_interface__
	shape = arr['shape']
	ndim = len(shape)	
	print ndim
	

	img = Image.fromarray(pixels, mode="RGB")
	if name:
		img.save("%s.BMP" % name)
	else:
		img.save("mask.BMP")

for i in range(0, 10):
	makeNoise(480, 720, i)