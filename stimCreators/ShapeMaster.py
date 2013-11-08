import math
import random
import os
import Image, ImageDraw, ImageFilter, ImageFont
import copy
from euclid import euclid
import datetime
		   
class ShapeMaster:
	def __init__(self, box=[640, 640], shapesize = [0.3, 0.3], shape= 'circle', sizemeasure='area', density=5, separation=25, colors =[[255, 255, 255]], overlay = False, bgcolor = [0,0,0], outline = [255, 255, 255], control='', drawOutline=False, MIN=.2, MAX=.8, texture=None, sameSize = False):

		#make an output directory
		if not os.path.exists("stimuli"):
			os.mkdir("stimuli")

		self.texture = texture

		self.box = box
		self.logFile = "dot_log_%s.csv" % datetime.datetime.now()
		self.ctl_iters = 1
		self.shape = shape
		#if one item size provided
		#otherwise don't size control
		self.sizemeasure = sizemeasure

		self._setSize(shapesize)
		
		self.MIN = MIN
		self.MAX = MAX
		
		self.sameSize = sameSize

		self.overlay = overlay
		self.density = density
		self.separation = separation
		
		self.colors = colors
		self.bgcolor = bgcolor
		self.outline = outline
		self.control = control
		self.controlValue = False
		self.drawOutline = drawOutline

	def _setSize(self, shapesize):
		self.shapeSize = []
		for s in shapesize:
			if self.sizemeasure == 'area':
				self.shapeSize.append(self.box[0] * self.box[1] * s)
			elif self.sizemeasure == 'perimeter':
				self.shapeSize.append((self.box[0] + self.box[1]) * s)


	def _shapeSolver(self, n=1, size=100, control = ''):
		#input - number of dots
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

		if n > 1:
			if self.sameSize:
				mySizes = [avg] * n
			else:
				#make a guess on the average sizes of the n-1 of the items
				for i in range(n-1):
					num = random.uniform(self.MIN, self.MAX)
					operation = random.choice(operations)
					mySizes.append(avg + (operation * num * avg))

				#determine the appropriate size of the nth item
				total = sum(mySizes)
				diff = size - total
		
				if diff > 0 and diff >= (avg*self.MIN) and diff <= (avg*self.MAX):
					mySizes.append(diff)
				else:
					mySizes = []
					while not mySizes:
						mySizes = self._shapeSolver(n, size)
					mySizes = mySizes[0]

		else:
			mySizes = [size]
		
		
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
					mySizes, controlSize = self._shapeSolver(n, size)
					controlSizes.append(controlSize)
				self.controlValue = sum(controlSizes) / iters
				print "CONTROL VALUE : %s" % self.controlValue
				return []
			#controlvalue has been set
			else:
				#% similarity of controlled value
				threshold = 95
				#print self.controlValue, controlSizes
				vals = [self.controlValue, sum(controlSizes)]
				control_ratio =  min(vals) / float(max(vals)) * 100.
				#check and see whether the control dimension is controlled enough (95% threshold)
				#print control_ratio
				#print self.ctl_iters
				#if control_ratio >= threshold or self.ctl_iters <= 1000:
				if control_ratio >= threshold or self.ctl_iters >= 10000:
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


	def _generateLists(self, ns=[1, 2], control=''):
		#generates the area lists, depending on the ns parameters
		sizeList = []
		sepShapes = []
		if type(ns) == int:
			while not sizeList:
				sizeList = self._shapeSolver(n, self.shapeSize, control=control)
				
		elif type(ns) == list:
			areaSums = []
			periSums = []
			for n, size in zip(ns, self.shapeSize):
				sizes = []
				while not sizes:
					sizes, controlSize = self._shapeSolver(n, size, control=control)

				if self.sizemeasure == 'area':
					areaSums.append(int(sum(sizes)))
					perims = map(lambda(x) : euclid[self.shape]['perimeter'](euclid[self.shape]['radius'](x, 'area')), sizes)
					periSums.append(int(sum(perims)))
				elif self.sizemeasure == 'perimeter':
					periSums.append(int(sum(sizes)))
					areas = map(lambda(x) : euclid[self.shape]['area'](euclid[self.shape]['radius'](x, 'perimeter')), sizes) 
					areaSums.append(int(sum(areas)))
	
				sepShapes.append(sizes)
				sizeList += sizes


			self.areaSums = areaSums
			self.periSums = periSums
			area_r = float(areaSums[0]) / areaSums[1]
			peri_r = float(periSums[0]) / periSums[1]


			self.size_log = "%s, %s, %s, %s, %s, %s" % (areaSums[0], areaSums[1], round(area_r, 2), periSums[0], periSums[1], round(peri_r, 2))
	
		else:
			print "Just what the hell do you think you're doing"

		self.controlValue = False
		return sizeList, sepShapes

	def shapeArranger(self, ns=[1,2]):
		#1 - place a dot box in a random location which does not overlap the edges
		#2 - place a dot in a random location which does not overlap the edges or any other dot boxes
		#3 - repeat until no dots are left

		goodList = 0
		breaks = 0
		
		ratio = float(ns[0]) / float(ns[1])

		self.ratio_log = "%s, %s, %s, %s" % (ns[0], ns[1], round(ratio, 2), round(1/ratio, 2))

		self.ns = ns


		sizeList, sepShapes = self._generateLists(ns, self.control)
		
		if len(sizeList) > 1:

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

					#if we've broken the cycle more than 10 times, we should regenerate the area list, 'cause this obviously ain't workin'
					if breaks > 9:
						sizeList, sepShapes = self._generateLists(ns)
						breaks = 0
						shapeBoxes = []
						shapesizes = copy.deepcopy(sizeList)

					while not quit:
						reps = reps + 1
						#if we've tried this too many times, restart the process...
						if reps > 100000:
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

	def drawSingle(self, name="", dpi=96):
		#obtain all the possible colors
		cols = []
		for d in self.shapeBoxes:
		
			cols.append(d[4])
			
		cols = set(cols)
		cols = list(cols)

		count = 1

		for c in cols:
			image = Image.new("RGB", self.box, self.bgcolor)
	
			print self.box

			draw = ImageDraw.Draw(image)
			for d in self.shapeBoxes:
				if d[4] == c:
					box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
					if not self.texture:
						if self.shape == 'circle':
							draw.ellipse(box1, fill = self.colors[c])
						elif self.shape == 'square':
							draw.rectangle(box1, fill = self.colors[c])
						elif self.shape == 'triangle':
							draw.polygon([box1[0], box1[1], box1[0], box1[3], box1[2], box1[3]], fill = self.colors[c])
					else:
						#open the bitmap
						mybit = Image.open(self.texture)
						size = box1[2] - box1[0]
						print size
						print box1
						#scale the it
						newsize = mybit.resize([size, size], Image.ANTIALIAS)
						x,y = newsize.size
						print x, y
						#get the new pixel data
						pixels = newsize.getdata()
						#paste the image at the appropriate location
						image.paste(newsize, box1)

					
			del draw
			
			if self.texture:
				texName = self.texture.split('.')[0]
			else:
				texName = ""

			fname = "%s_%s_%s_S%s.bmp" % (self.shape, texName, name, count)

			image.save("stimuli/%s" % fname, "BMP", dpi=dpi)
				
			count+=1
			self._printLog(fname)

	def drawDual(self, name="shapes", dpi=96):
		#obtain all the possible colors
		cols = []
		for d in self.shapeBoxes:
		
			cols.append(d[4])
			
		cols = set(cols)
		cols = list(cols)

		#self.shapeBoxes = [self.shapeBoxes[0], self.shapeBoxes[2]]

		count = 0

		image = Image.new("RGB", [self.box[0] *2, self.box[1]], self.bgcolor)
				
		draw = ImageDraw.Draw(image)

		if self.drawOutline:
			draw.rectangle([0, 0, self.box[0] * 2, self.box[1]], fill = self.outline)
			draw.rectangle([4, 4, (self.box[0] * 2) - 4, self.box[1] - 4], fill = self.bgcolor)

		draw.rectangle([self.box[0] - 4, 0, self.box[0] + 4, self.box[1]], fill = self.outline)

		cols = list(set(cols))
		print cols

		for c in cols:
			print "Color:", c
			for d in self.shapeBoxes:
				print d
				if d[4] == c:
					print "Match!"
					box1 = [d[0] - d[2] + (count * self.box[0]), d[1] - d[2], d[0] + d[2] + (count * self.box[0]), d[1] + d[2]]
					if self.shape == 'circle':
						draw.ellipse(box1, fill = self.colors[c])
					elif self.shape == 'square':
						draw.rectangle(box1, fill = self.colors[c])
					elif self.shape == 'triangle':
						draw.polygon([box1[0], box1[1], box1[0], box1[3], box1[2], box1[3]], fill = self.colors[c])

			count+=1
					
		del draw
			
		fname = "%s_%s_D.bmp" % (self.shape, name)

		image.save("stimuli/%s" % fname, "BMP", dpi=dpi)
				
		self._printLog(fname)

	def drawOverlay(self, name="shapes", dpi=96):
		#make a left/right dot array stimulus from two groups of bounding boxes

		if self.overlay:

			image = Image.new("RGB", self.box, self.bgcolor)

			draw = ImageDraw.Draw(image)

			for d in self.shapeBoxes:
				#draw the dots on the left
				box1 = [d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2]]
				draw.ellipse(box1, fill = self.colors[d[4]])

			del draw

			fname = "%s_OL.bmp" % (name)

			image.save("stimuli/%s" % fname, "BMP", dpi=dpi)
			self._printLog(fname)		

		else:
			raise Exception("You told me you didn't want an overlay, sucka!  You need to pass in overlay=True in the arguments or I will not be able to draw things right!")


	def _printLog(self, fname="shapes"):
		if os.path.exists(self.logFile):
			f = open(self.logFile, "a")
		else:
			f = open(self.logFile, "w")
			f.write("file,shape,n1,n2,ratio,1/ratio,area_n1,area_n2,area_ratio,per_n1,per_n2,per_ratio\n")

		log = "%s, %s, %s, %s" % (fname, self.shape, self.ratio_log, self.size_log)

		f.write(log + "\n")
		f.close()

	def drawDualSym(self, name="shapes", n1=1, n2=2, dpi = (96,96)):
		#now let us make the image with the number in it
		image = Image.new("RGB", [self.box[0] * 2, self.box[1]], self.bgcolor)

		draw = ImageDraw.Draw(image)

		font = ImageFont.truetype("arial.ttf", 200)

		if self.drawOutline:
			draw.rectangle([0, 0, self.box[0] * 2, self.box[1]], fill = self.outline)
			draw.rectangle([4, 4, (self.box[0] * 2) - 4, self.box[1] - 4], fill = self.bgcolor)

		draw.rectangle([self.box[0] - 4, 0, self.box[0] + 4, self.box[1]], fill = self.outline)

		#left text
		text = str(n1)
		fontsize = font.getsize(text)
		draw.text((self.box[0]/2 - fontsize[0]/2 , self.box[1] /2 - fontsize[1]/2), text, fill = self.outline, font = font)    
		#right text
		text = str(n2)
		draw.text((self.box[0]/2 - fontsize[0]/2 + self.box[0], self.box[1]/2 - fontsize[1]/2), text, fill = self.outline, font = font)

		del draw
		image.save("stimuli/%s_D_SYM.bmp" % name, "BMP", dpi=dpi)


	def drawDualMixed(self, name="mixed", number="L", dpi=96):
		#obtain all the possible colors
		
		font = ImageFont.truetype("arial.ttf", 200)
		
		cols = []
		for d in self.shapeBoxes:
		
			cols.append(d[4])
			
		cols = set(cols)
		cols = list(cols)


		if number == "L":
			count = 0
			text = str(self.ns[1])
			fontsize = font.getsize(text)
			text_coords = (self.box[0]/2 - fontsize[0]/2 + self.box[0], self.box[1]/2 - fontsize[1]/2)
		elif number == "R":
			count = 1
			text = str(self.ns[0])
			fontsize = font.getsize(text)
			text_coords = (self.box[0]/2 - fontsize[0]/2 , self.box[1] /2 - fontsize[1]/2)
		else:
			raise Exception("drawDualMixed, number arg takes either L or R")


		image = Image.new("RGB", [self.box[0] *2, self.box[1]], self.bgcolor)
				
		draw = ImageDraw.Draw(image)



		if self.drawOutline:
			draw.rectangle([0, 0, self.box[0] * 2, self.box[1]], fill = self.outline)
			draw.rectangle([4, 4, (self.box[0] * 2) - 4, self.box[1] - 4], fill = self.bgcolor)

		draw.rectangle([self.box[0] - 4, 0, self.box[0] + 4, self.box[1]], fill = self.outline)

		draw.text(text_coords, text, fill = self.outline, font = font)    


		cols = list(set(cols))
		print cols

		c = cols[count]

		for d in self.shapeBoxes:
			print d
			if d[4] == c:
				print "Match!"
				box1 = [d[0] - d[2] + (count * self.box[0]), d[1] - d[2], d[0] + d[2] + (count * self.box[0]), d[1] + d[2]]
				if self.shape == 'circle':
					draw.ellipse(box1, fill = self.colors[c])
				elif self.shape == 'square':
					draw.rectangle(box1, fill = self.colors[c])
				elif self.shape == 'triangle':
					draw.polygon([box1[0], box1[1], box1[0], box1[3], box1[2], box1[3]], fill = self.colors[c])
	
		del draw
			
		fname = "%s_%s_M%s.bmp" % (self.shape, name, number)

		image.save("stimuli/%s" % fname, "BMP", dpi=dpi)
				
		self._printLog(fname)


