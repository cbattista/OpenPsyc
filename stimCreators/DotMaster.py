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
	def __init__(box, area, density=5, separation=150):
		self.box = box
		self.area = area
		self.density = density
		self.separation = separation
		self.dotArea = box[0] * box[1] * area


	def dotSolver(self, n, MIN=.25, MAX=.75):
		#input - area, number of dots
		#output - radius of each dot
		#solver algo
		#1 - calculate average area
		#2 - generate a random value which is a portion of that area
		#3 - randomly determine to add or subtract that
		#4 - perform that operation on the dot
		#5 - repeat until only 1 dot is left
		#6 - make the last dot the necessary size so the area works out

		avg = self.area / n
		operations = [-1, 1]
		myAreas = []
		for i in range(n-1):
		    num = random.uniform(MIN, MAX)
		    operation = random.choice(operations)
		    myAreas.append(avg + (operation * num * avg))
		    
		total = sum(myAreas)
		diff = abs(area - total + avg)
		myAreas.append(avg + diff)
		return myAreas

	def dotArranger(self, n):
		#1 - place a dot box in a random location which does not overlap the edges
		#2 - place a dot in a random location which does not overlap the edges or any other dot boxes
		#3 - repeat until no dots are left

		goodList = 0
		breaks = 0

		areaList = dotSolver(dotArea, n)

		if n != 1:

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
		                areaList = dotSolver(dotArea, n1)
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
		                
		                dotBox = (x, y, r)
		                
		                #if there are no dots on the screen, place the current dot on the screen and proceed to the next placement
		                if count == 1:
		                    dotBoxes.append(dotBox)
		                    dotAreas.pop()
		                    quit = 1
		                #otherwise check against the existing list of dots
		                else:
		                    bad = 0
		                    #print "Checking through dot list: %s" % dotBoxes
		                    for box in dotBoxes:
		                        minRadius = r + self.box[2] + 5 + separation
		                        x2 = self.box[0]
		                        y2 = self.box[1]        
		                        
		                        a = abs(x - x2)
		                        b = abs(y - y2)
		                        
		                        cSquare = a**2 + b**2
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
		    dotBoxes = [(x, y, r, a)]
        
    
    return dotBoxes


	def MultiArranger(self, ns):
		dotAreas = []
		areaList = []
		for n in ns:
			areas = dotSolver(dotArea, n)
			dotAreas.append(areas)
			areaList += areas

		dotboxes = dotArranger(areaList)

		for d in dotBoxes:
			a = d[3]
			for area in areas:
				if 

	def drawSingle(self, dotBoxes):
		pass

	def drawDouble(self, dotBoxes1, dotBoxes2):
		pass

	def drawOverlay(self, dotBoxes):
		pass




