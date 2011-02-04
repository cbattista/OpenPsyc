import math
import random
import os
import Image, ImageDraw, ImageFilter, ImageFont
import copy
from euclid import euclid
		   
class ShapeMaster:
	def __init__(self, box, shapesize, shape= 'circle', sizemeasure='area', sizectrl = 'SC', density=5, separation=10, colors =[[255, 255, 255]], bgcolor = [0,0,0], control='', logFile = "dot_log.csv"):
		self.box = box
		self.logFile = logFile
		self.ctl_iters = 1
		self.shape = shape
		#if one item size provided
		#otherwise don't size control
		self.shapesize = []
		for d in shapesize:
			if sizemeasure == 'area':
				self.shapesize.append(box[0] * box[1] * d)
			elif sizemeasure == 'perimeter':
				self.shapesize.append((box[0] + box[1]) * d)
			
		self.sizemeasure = sizemeasure
		self.density = density
		self.separation = separation
		
		self.colors = colors
		self.bgcolor = bgcolor
		self.control = control
		self.controlValue = False

	def shapeSolver(self, n, size, MIN=.2, MAX=.8, control = ''):

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
				mySizes = self.shapeSolver(n, size)
			mySizes = mySizes[0]
		
		
		#optional step, control for another size dimension
		controlSizes = []		
				
		#determine the size of the controlled dimension
		for ms in mySizes:
			r = euclid[self.shape]['radius'](ms, self.sizemeasure)
			if control:
				cs = euclid[self.shape][control](r)
			else:
				if self.sizemeasure == 'area':
					cs = euclid[self.shape]['perimeter'](r)
				else:
					cs = euclid[self.shape]['area'](r)
			controlSizes.append(int(cs))

		#if we have a list of items and we want to control a dimension
		if mySizes and control:
			#control value has not been set
			if self.controlValue == False:	
				controlSizes = []
				iters = 100
				for i in range(iters):
					mySizes, controlSize = self.shapeSolver(n, size)
					controlSizes.append(controlSize)
				self.controlValue = sum(controlSizes) / iters
				print "CONTROL VALUE : %s" % self.controlValue
				return []
			#controlvalue has been set
			else:
				
				#% similarity of controlled value
				threshold = 85
				vals = [self.controlValue, sum(controlSizes)]
				control_ratio =  min(vals) / float(max(vals)) * 100.
				#check and see whether the control dimension is controlled enough (95% threshold)
				#print control_ratio
				print self.ctl_iters
				if control_ratio >= threshold or self.ctl_iters <= 1000:
					#it is, so we're done and we can reset the control value
					self.ctl_iters = 1
					return mySizes, sum(controlSizes)
				else:
					#it isn't
					self.ctl_iters += 1
					return []
					
		#we have a list of items and don't want to control it
		elif mySizes:
			return mySizes, sum(controlSizes)


	def generateLists(self, ns, control=''):
		#generates the area lists, depending on the ns parameters
		sizeList = []
		sepShapes = []
		if type(ns) == int:
			while not sizeList:
				sizeList = self.shapeSolver(n, self.shapesize, control=control)
				
		elif type(ns) == list:
			areaSums = []
			periSums = []

			for n, area in zip(ns, self.shapesize):
				areas = []
				while not areas:
					areas = self.shapeSolver(n, area, control=control)
				areas, controlSize = areas

				perims = map(lambda(x) : euclid[self.shape]['perimeter'](euclid[self.shape]['radius'](x, 'area')), areas)
				areaSums.append(int(sum(areas)))
				periSums.append(int(sum(perims)))
		
				sepShapes.append(areas)
				sizeList += areas

			self.areaSums = areaSums
			self.periSums = periSums
			area_r = float(areaSums[0]) / areaSums[1]
			peri_r = float(periSums[0]) / periSums[1]

			self.size_log = "%s, %s, %s, %s, %s, %s, %s" % (self.shape, areaSums[0], areaSums[1], round(area_r, 2), periSums[0], periSums[1], round(peri_r, 2))
	
		else:
			print "Just what the hell do you think you're doing"

		#print "sizelist %s, sepShapes %s" % (sizeList, sepShapes)
		self.controlValue = False
		return sizeList, sepShapes

	def shapeArranger(self, ns):
		#1 - place a dot box in a random location which does not overlap the edges
		#2 - place a dot in a random location which does not overlap the edges or any other dot boxes
		#3 - repeat until no dots are left

		goodList = 0
		breaks = 0

		ratio = float(ns[0]) / float(ns[1])

		self.ratio_log = "%s, %s, %s, %s" % (ns[0], ns[1], round(ratio, 2), round(1/ratio, 2))

		sizeList, sepShapes = self.generateLists(ns, self.control)
		
		if len(sizeList) != 1:

			while not goodList:
				shapeBoxes = []
				count = 1
				shapesizes = copy.deepcopy(sizeList)
				while len(shapesizes):
					a = shapesizes[-1]
					r = int(euclid[self.shape]['radius'](a, self.sizemeasure))
					d = int(r * 2)
					quit = 0
					reps = 1

					print a, r, d

					#if we've broken the cycle more than 10 times, we should regenerate the area list, 'cause this obviously ain't workin'
					if breaks > 9:
						sizeList, sepShapes = self.generateLists(ns)
						breaks = 0
						shapeBoxes = []
						shapesizes = copy.deepcopy(sizeList)

					while not quit:
						reps = reps + 1
						#if we've tried this too many times, restart the process...
						if reps > 100000:
							print "Arranger Reset"
							print sizeList
							#delete the list of boxes
							#put the area back into the list of areas
							shapesizes = copy.deepcopy(sizeList)
							#and break the loop
							breaks = breaks + 1
							shapeBoxes = []
							quit = 1

						x = int(random.uniform(r + self.density, self.box[0] - r - self.density))
						y = int(random.uniform(r + self.density, self.box[1] - r - self.density))
	
						shapeBox = [x, y, r, a]
	
						#if there are no dots on the screen, place the current dot on the screen and proceed to the next placement
						if count == 1:
							shapeBoxes.append(shapeBox)
							shapesizes.pop()
							quit = 1
						#otherwise check against the existing list of dots
						else:
							bad = 0
							for box in shapeBoxes:
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
								shapeBoxes.append(shapeBox)
								goodList = 1
								shapesizes.pop()
								quit = 1
					count = count + 1
		else:
			a = sizeList[0]
			r = int(circleRadius(a, self.sizemeasure))

			x = int(random.uniform(r + self.density, self.bounds[0] - r - self.density))
			y = int(random.uniform(r + self.density, self.bounds[1] - r - self.density))
			shapeBoxes = [[x, y, r, a]]

		#now, if we have multiple ns we are trying to use for an overlay, let's do that...
		if type(ns) == list and len(ns) > 1:
			newBoxes = []
	
			for d in shapeBoxes:
				a = d[3]
				for sp in sepShapes:
					if a in sp:
						index = sepShapes.index(sp)
						d.append(index)
						newBoxes.append(d)
			self.shapeBoxes = newBoxes

		#otherwise just return the dots we've got
		else:		
			self.shapeBoxes = shapeBoxes

	def drawSingle(self, name, dpi=96):
		#obtain all the possible colors
		cols = []
		for d in self.shapeBoxes:
		
			cols.append(d[4])
			
		cols = set(cols)
		cols = list(cols)

		count = 1
		for c in cols:
			image = Image.new("RGB", self.box, self.bgcolor)
					
			draw = ImageDraw.Draw(image)
			for d in self.shapeBoxes:
				if d[4] == c:
					print d
					box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
					if self.shape == 'circle':
						draw.ellipse(box1, fill = self.colors[d[4]])
					elif self.shape == 'square':
						draw.rectangle(box1, fill = self.colors[d[4]])
					elif self.shape == 'triangle':
						print box1
						draw.polygon([box1[0], box1[1], box1[0], box1[3], box1[2], box1[3]], fill = self.colors[d[4]])
						
					
			del draw
				
			fname = "%s_%s_S%s.bmp" % (self.shape, name, count)

			image.save("output/%s" % fname, "BMP", dpi=dpi)
				
			count+=1
			self.printLog(fname)

	def drawOverlay(self, name, dpi=96):
		#make a left/right dot array stimulus from two groups of bounding boxes
		image = Image.new("RGB", self.box, self.bgcolor)

		draw = ImageDraw.Draw(image)

		for d in self.shapeBoxes:
			#draw the dots on the left
			box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
			draw.ellipse(box1, fill = self.colors[d[4]])

		del draw

		fname = "%s_OL.bmp" % (name)

		image.save("output/%s" % fname, "BMP", dpi=dpi)
		self.printLog(fname)		


	def printLog(self, fname):
		if os.path.exists(self.logFile):
			f = open(self.logFile, "a")
		else:
			f = open(self.logFile, "w")
			f.write("file,n1,n2,ratio,1/ratio,shape,area_n1,area_n2,area_ratio,per_n1,per_n2,per_ratio\n")

		log = "%s, %s, %s" % (fname, self.ratio_log, self.size_log)

		f.write(log + "\n")
		f.close()
