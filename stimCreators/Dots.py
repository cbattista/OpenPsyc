from DotLib import *

#SETTINGS

bgcolor = (0, 0, 0)
color = (255, 255, 255)
box = (480, 720) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
areas = [0.1]

ratios = [0.33, 0.5, 0.66]
density = [5]
seeds = range(1,4,2)
reps = 5


#info for later
boxArea = box[0] * box[1]
for rep in reps:
    for a in areas:
        for d in density:
            dotArea = int(a * boxArea)
            for n1 in seeds:
                for ratio in ratios:
                    n2 = int(round(n1 / ratio, 0))
                    print n1, n2, a, d
                    #digit check
                    if (n1 > 9) and (n2 > 9):
                        myDir = "double"
                        #compatibility check
                        compat = "compatible"
                        for i, j in zip(str(n1), str(n2)):
                            if n1 < n2:
                                if int(i) > int(j):
                                    compat = "incompatible"
                            elif n1 > n2:
                                if int(i) < int(j):
                                    compat = "incompatible"
                        myDir = os.path.join(myDir, compat)
                        #print n1, n2, compat
                        
                        
                            
                    elif (n1 > 9) or (n2 > 9):
                        myDir = "mixed"
                    else:
                        myDir = "single"
        
                    myDir = os.path.join(os.getcwd(), myDir)
                    
                    #if not os.path.exists(myDir):
                    #    os.mkdir(myDir)
                    #nomenclature SYM/NONSYM_LEFTNUM_RIGHTNUM_RATIO_AREA_DENSITY

                    
                    #n1 on the left
                    leftDir = os.path.join(myDir, "left")
                    if not os.path.exists(leftDir):
                        os.makedirs(leftDir)
                    name = "%s_%s_%s_%s_%s" % (ratio,n1, n2, a, d)
                    name = os.path.join(myDir, "left", name)
                    dots1 = dotArranger(dotArea, n1, box, d)
                    dots2 = dotArranger(dotArea, n2, box, d)
                    makeStimulus(name, dots1, box, bgcolor, color, dots2)
                    
                    name = "%s_%s_%s" % (ratio, n1, n2)
                    name = os.path.join(leftDir, name)
                    makeSymStimulus(name, dots1, box, bgcolor, color, dots2)
                    
                    #n2 on the left
                    rightDir = os.path.join(myDir, "right")
                    if not os.path.exists(rightDir):
                        os.makedirs(rightDir)
                    name = "%s_%s_%s_%s_%s" % (ratio, n2, n1, a, d)
                    name = os.path.join(rightDir, name)
                    dots1 = dotArranger(dotArea, n2, box, d)
                    dots2 = dotArranger(dotArea, n1, box, d)
                    makeStimulus(name, dots1, box, bgcolor, color, dots2)

                    name = "%s_%s_%s" % (ratio, n2, n1)
                    name = os.path.join(rightDir, name)
                    makeSymStimulus(name, dots1, box, bgcolor, color, dots2)
                    
