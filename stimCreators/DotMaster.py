import math
import random
import os
import Image, ImageDraw, ImageFilter, ImageFont
import copy

#HELPER FUNCS
def circleArea(radius):
	return math.pi * (radius ** 2)

def circleRadius(area):
	return (area / math.pi) ** 0.5

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
	def __init__(self, box, area, density=5, separation=10, colors =[[255, 255, 255]], bgcolor = [0,0,0]):
		self.box = box
		self.area = area
		if type(area) != list:
			self.sizectrl = "SC"
			self.dotArea = box[0] * box[1] * area
		else:
			self.sizectrl = "NSC"
			self.dotArea = []
			for a in area:
				self.dotArea.append(box[0] * box[1] * a)
		self.density = density
		self.separation = separation
		
		self.colors = colors
		self.bgcolor = bgcolor


	def dotSolver(self, n, area, MIN=.25, MAX=.75):
		#input - area, number of dots
		#output - radius of each dot
		#solver algo
		#1 - calculate average area
		#2 - generate a random value which is a portion of that area
		#3 - randomly determine to add or subtract that
		#4 - perform that operation on the dot
		#5 - repeat until only 1 dot is left
		#6 - make the last dot the necessary size so the area works out

		avg = area / float(n)
		operations = [-1, 1]
		myAreas = []
		for i in range(n-1):
			num = random.uniform(MIN, MAX)
			operation = random.choice(operations)
			myAreas.append(avg + (operation * num * avg))

		total = sum(myAreas)
		diff = area - total
		if diff > 0 and diff >= (avg*MIN) and diff <= (avg*MAX):
			myAreas.append(diff)
			print "area: %s" % sum(myAreas)
			return myAreas
		else:
			return []

	def generateLists(self, ns):
		#generates the area lists, depending on the ns parameters
		print "##generating lists"
		areaList = []
		sepDots = []
		if type(ns) == int:
			while not areaList:
			
				areaList = self.dotSolver(n, self.dotArea)

		elif type(ns) == list and self.sizectrl == "SC":
			for n in ns:
				areas = []
				while not areas:
					areas = self.dotSolver(n, self.dotArea)
				sepDots.append(areas)
				areaList += areas
				
		elif type(ns) == list and self.sizectrl == "NSC":
			for n, area in zip(ns, self.dotArea):
				areas = []
				while not areas:
					areas = self.dotSolver(n, area)
				sepDots.append(areas)
				areaList += areas
		
		else:
			print "Just what the hell do you think you're doing"

		return areaList, sepDots

	def dotArranger(self, ns):
		#1 - place a dot box in a random location which does not overlap the edges
		#2 - place a dot in a random location which does not overlap the edges or any other dot boxes
		#3 - repeat until no dots are left

		goodList = 0
		breaks = 0

		areaList, sepDots = self.generateLists(ns)

		if len(areaList) != 1:

			while not goodList:
				dotBoxes = []
				count = 1
				dotAreas = copy.deepcopy(areaList)
				while len(dotAreas):
					a = dotAreas[-1]
					r = int(circleRadius(a))
					d = int(r * 2)
					quit = 0
					reps = 1

					#if we've broken the cycle more than 10 times, we should regenerate the area list, 'cause this obviously ain't workin'
					if breaks > 9:
						areaList, sepDots = self.generateLists(ns)
						#print "regenning area list"
						breaks = 0
						dotBoxes = []
						dotAreas = copy.deepcopy(areaList)

					while not quit:
						reps = reps + 1
						#print reps
						#if we've tried this too many times, restart the process...
						if reps > 100000:
							#delete the list of boxes
							#put the area back into the list of areas
							dotAreas = copy.deepcopy(areaList)
							#and break the loop
							#print "(%s)break, n = %s" % (breaks, len(dotBoxes))
							breaks = breaks + 1
							dotBoxes = []
							quit = 1

						x = int(random.uniform(r + self.density, self.box[0] - r - self.density))
						y = int(random.uniform(r + self.density, self.box[1] - r - self.density))
	
						dotBox = [x, y, r, a]
	
						#if there are no dots on the screen, place the current dot on the screen and proceed to the next placement
						if count == 1:
							dotBoxes.append(dotBox)
							dotAreas.pop()
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
								dotAreas.pop()
								quit = 1
					count = count + 1
				#print "SUCCESS: %s" % dotBoxes
			#print len(dotBoxes), dotBoxes
		else:
			a = areaList[0]
			r = int(circleRadius(a))

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
		
