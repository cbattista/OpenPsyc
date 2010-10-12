from DotLib import *

bgcolor = (0, 0, 0)
color = (255, 255, 255)
box = (960, 720) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
areas = [0.1]

density = [5]

numbers = [2,3,4,5,6,7,8,9]

boxArea = box[0] * box[1]

#This time we need arrays of 1-9 dots (5 each). for a total of 45 items

#For this matching task I need four displays of 2,3,4,5,6,7,8 and 9 dots. 

for a in areas:
    for d in density:
        dotArea = int(a * boxArea)
        for n in numbers:
            for i in range(1, 5):
                name = "%s_%s_%s_%s" % (n, i, a, d)
                print name
                dots = dotArranger(dotArea, n, box, d)
                makeStimulus(name, dots, box, bgcolor, color) 
                #name = str(n)
                #makeSymStimulus(name, dots, box, bgcolor, color)