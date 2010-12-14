import math
import random
import os
import Image, ImageDraw, ImageFilter, ImageFont
import copy

#HELPER FUNCS
def circleArea(radius):
	return math.pi * (radius ** 2)

def circleRadius(size, sizemeasure):
	if sizemeasure == 'area':
		return (size / math.pi) ** 0.5
	elif sizemeasure == 'perimeter':
		return size / (math.pi * 2) 

def fromRadius(r, measure):
	if measure == 'area':
		return math.pi * r **2
	elif measure == 'perimeter':
		return 2 * math.pi * r
	else:
		return None
		
#make a left/right dot array stimulus from two groups of bounding boxes
def makeStimulus(name, dots1, size, bgcolor, color, dots2=[], dpi=(96, 96)):
	if dots2:
		image = Image.new("RGB", [size[0] * 2, size[1]], bgcolor)    
	else:
		image = Image.new("RGB", size, bgcolor)

	draw = ImageDraw.Draw(image)

	for d1 in dots1:
		#draw the dots on the left
		box1 = [d1[0] - d1[2], d1[1] - d1[2], d1[0] + d1[2], d1[1] + d1[2]]
		draw.ellipse(box1, fill = color)

	if dots2:
		for d2 in dots2:
			#draw the dots on the right
			box2 = [d2[0] - d2[2] + size[0], d2[1] - d2[2], d2[0] + d2[2] + size[0], d2[1] + d2[2]]
			draw.ellipse(box2, fill = color)

		draw.line([size[0], 0, size[0], size[1]], fill = color, width = 2)
	del draw
	#image = image.filter(ImageFilter.BLUR)

	image.save("%s_NONSYM.bmp" % name, "BMP", dpi=dpi)

def makeSymStimulus(name, n1, size, bgcolor, color,  n2=[], dpi = (96,96)):
	#now let us make the image with the number in it
	if n2:
		image = Image.new("RGB", [size[0] * 2, size[1]], bgcolor)
	else:
		image = Image.new("RGB", size, bgcolor)
	draw = ImageDraw.Draw(image)

	font = ImageFont.truetype("arial.ttf", 128)


	#left text
	text = str(len(n1))
	fontsize = font.getsize(text)
	draw.text((size[0]/2 - fontsize[0]/2 , size[1] /2 - fontsize[1]/2), text, fill = color, font = font)    
	#right text
	if n2:
		text = str(len(n2))
		fontsize = font.getsize(text)
		draw.text((size[0]/2 - fontsize[0]/2 + size[0], size[1]/2 - fontsize[1]/2), text, fill = color, font = font)

		draw.line([size[0], 0, size[0], size[1]], fill = color, width = 2)
	del draw
	image.save("%s_SYM.bmp" % name, "BMP", dpi=dpi)
   
class DotMaster:
	def __init__(self, box, dotsize, sizemeasure='area', sizectrl = 'SC', density=5, separation=10, colors =[[255, 255, 255]], bgcolor = [0,0,0], control=''):
		self.box = box

		#if one item size provided
		if type(dotsize) != list:
			#control the sizes of both groups of items
			self.sizectrl = "SC"
			if sizemeasure == 'area':
				self.dotSize = box[0] * box[1] * dotsize
			elif sizemeasure == 'perimeter':
				self.dotSize = (box[0] + box[1]) * dotsize
		else:
			#otherwise don't size control
			self.sizectrl = "NSC"
			self.dotSize = []
			for d in dotsize:
				if sizemeasure == 'area':
					self.dotSize.append(box[0] * box[1] * d)
				elif sizemeasure == 'perimeter':
					self.dotSize.append((box[0] + box[1]) * d)
			
		self.sizemeasure = sizemeasure
		self.density = density
		self.separation = separation
		
		self.colors = colors
		self.bgcolor = bgcolor
		self.control = control
		self.controlValue = False

	def dotSolver(self, n, size, MIN=.3, MAX=.7, control = ''):

		#input - size, number of dots
		#output - radius of each dot
		#solver algo
		#1 - calculate average size
		#2 - generate a random value which is a portion of that size
		#3 - randomly determine to add or subtract that
		#4 - perform that operation on the dot
		#5 - repeat until only 1 dot is left
		#6 - make the last dot the necessary size so the size works out

		avg = size / float(n)
		operations = [-1, 1]
		mySizes = []
		
		#make a guess on the average sizes of the n-1 of the items
		for i in range(n-1):
			num = random.uniform(MIN, MAX)
			operation = random.choice(operations)
			mySizes.append(avg + (operation * num * avg))

		#determine the appropriate size of the nth item
		total = sum(mySizes)
		diff = size - total
		
		if diff > 0 and diff >= (avg*MIN) and diff <= (avg*MAX):
			mySizes.append(diff)
		else:
			mySizes = []
			while not mySizes:
				mySizes = self.dotSolver(n, size)
			mySizes = mySizes[0]
		
		
		#optional step, control for another size dimension
		controlSizes = []		
				
		#determine the size of the controlled dimension
		for ms in mySizes:
			r = circleRadius(ms, self.sizemeasure)
			if control:
				cs = fromRadius(r, control)
			else:
				if self.sizemeasure == 'area':
					cs = fromRadius(r, 'perimeter')
				else:
					cs = fromRadius(r, 'area')
			controlSizes.append(int(cs))

		#if we have a list of items and we want to control a dimension
		if mySizes and control:
			#control value has not been set
			if self.controlValue == False:	
				controlSizes = []
				for i in range(20):	
					mySizes, controlSize = self.dotSolver(n, size)
					controlSizes.append(controlSize)
				self.controlValue = sum(controlSizes) / 20
				return []
			#controlvalue has been set
			else:
				#check and see whether the control dimension is controlled enough :p
				if abs(sum(controlSizes) - self.controlValue) <= 20:
					#it is
					return mySizes, sum(controlSizes)
				else:
					#it isn't
					return []
					
		#we have a list of items and don't want to control it
		elif mySizes:
			return mySizes, sum(controlSizes)


	def generateLists(self, ns, control=''):
		#generates the area lists, depending on the ns parameters
		sizeList = []
		sepDots = []
		if type(ns) == int:
			while not sizeList:
				sizeList = self.dotSolver(n, self.dotSize, control=control)

		elif type(ns) == list and self.sizectrl == "SC":
			print "SC"
			for n in ns:

				areas = []
				while not areas:
					areas = self.dotSolver(n, self.dotSize, control=control)
				sepDots.append(areas)
				sizeList += areas
				
		elif type(ns) == list and self.sizectrl == "NSC":
			print "NSC"
			for n, area in zip(ns, self.dotSize):
				areas = []
				while not areas:
					print n, area
					areas = self.dotSolver(n, area, control=control)
				areas, controlSize = areas

				sepDots.append(areas)
				sizeList += areas
		
		else:
			print "Just what the hell do you think you're doing"

		print "sizelist %s, sepdots %s" % (sizeList, sepDots)
			
		return sizeList, sepDots

	def dotArranger(self, ns):
		#1 - place a dot box in a random location which does not overlap the edges
		#2 - place a dot in a random location which does not overlap the edges or any other dot boxes
		#3 - repeat until no dots are left

		goodList = 0
		breaks = 0

		sizeList, sepDots = self.generateLists(ns, self.control)
		
		if len(sizeList) != 1:

			while not goodList:
				dotBoxes = []
				count = 1
				dotSizes = copy.deepcopy(sizeList)
				while len(dotSizes):
					a = dotSizes[-1]
					r = int(circleRadius(a, self.sizemeasure))
					d = int(r * 2)
					quit = 0
					reps = 1

					#if we've broken the cycle more than 10 times, we should regenerate the area list, 'cause this obviously ain't workin'
					if breaks > 9:
						sizeList, sepDots = self.generateLists(ns)
						breaks = 0
						dotBoxes = []
						dotSizes = copy.deepcopy(sizeList)

					while not quit:
						reps = reps + 1
						#if we've tried this too many times, restart the process...
						if reps > 100000:
							#delete the list of boxes
							#put the area back into the list of areas
							dotSizes = copy.deepcopy(sizeList)
							#and break the loop
							breaks = breaks + 1
							dotBoxes = []
							quit = 1

						x = int(random.uniform(r + self.density, self.box[0] - r - self.density))
						y = int(random.uniform(r + self.density, self.box[1] - r - self.density))
	
						dotBox = [x, y, r, a]
	
						#if there are no dots on the screen, place the current dot on the screen and proceed to the next placement
						if count == 1:
							dotBoxes.append(dotBox)
							dotSizes.pop()
							quit = 1
						#otherwise check against the existing list of dots
						else:
							bad = 0
							for box in dotBoxes:
								minRadius = r + box[2] + 5 + self.separation
								x2 = box[0]
								y2 = box[1]        
					
								ax = abs(x - x2)
								by = abs(y - y2)
					
								cSquare = ax**2 + by**2
								c = (cSquare ** 0.5)
					
								if c < minRadius:
									bad = 1
											    
							if not bad:
								dotBoxes.append(dotBox)
								goodList = 1
								dotSizes.pop()
								quit = 1
					count = count + 1
		else:
			a = sizeList[0]
			r = int(circleRadius(a, self.sizemeasure))

			x = int(random.uniform(r + self.density, self.bounds[0] - r - self.density))
			y = int(random.uniform(r + self.density, self.bounds[1] - r - self.density))
			dotBoxes = [[x, y, r, a]]

		#now, if we have multiple ns we are trying to use for an overlay, let's do that...
		if type(ns) == list and len(ns) > 1:
			newBoxes = []
	
			for d in dotBoxes:
				a = d[3]
				for sp in sepDots:
					if a in sp:
						index = sepDots.index(sp)
						d.append(index)
						newBoxes.append(d)
			self.dotBoxes = newBoxes

		#otherwise just return the dots we've got
		else:		
			self.dotBoxes = dotBoxes

	def drawSingle(self, name, dpi=96):
		#obtain all the possible colors
		cols = []
		for d in self.dotBoxes:
		
			cols.append(d[4])
			
		cols = set(cols)
		cols = list(cols)

		count = 1
		for c in cols:
			image = Image.new("RGB", self.box, self.bgcolor)
					
			draw = ImageDraw.Draw(image)
			for d in self.dotBoxes:
				if d[4] == c:
					box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
					draw.ellipse(box1, fill = self.colors[d[4]])
					
			del draw
				
			image.save("%s_S%s_%s.bmp" % (name, count, self.sizectrl), "BMP", dpi=dpi)
				
			count+=1

	def drawOverlay(self, name, dpi=96):
		#make a left/right dot array stimulus from two groups of bounding boxes
		image = Image.new("RGB", self.box, self.bgcolor)

		draw = ImageDraw.Draw(image)

		for d in self.dotBoxes:
			#draw the dots on the left
			box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
			draw.ellipse(box1, fill = self.colors[d[4]])

		del draw

		image.save("%s_OL_%s.bmp" % (name, self.sizectrl), "BMP", dpi=dpi)
		
