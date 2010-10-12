from DotLib import *

#SETTINGS

bgcolor = (0, 0, 0)
color = (255, 255, 255)
box = (480, 720) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
areas = [0.1]

ratios = [0.66]
density = [5]
seeds = [3, 2]
reps = range(6)


#info for later
boxArea = box[0] * box[1]
for id in reps:
    for a in areas:
        for d in density:
            dotArea = int(a * boxArea)
            for n1 in seeds:
                for ratio in ratios:
                    n2 = int(round(n1 / ratio, 0))
                    print n1, n2, a, d
                    #digit check
                    myDir = os.getcwd()
                    
                    #if not os.path.exists(myDir):
                    #    os.mkdir(myDir)
                    #nomenclature SYM/NONSYM_LEFTNUM_RIGHTNUM_RATIO_AREA_DENSITY

                    #n1 on the left
                    name = "%s_%s_%s_%s_%s_%s" % (ratio,n1, n2, a, d, id)
                    dots1 = dotArranger(dotArea, n1, box, d)
                    dots2 = dotArranger(dotArea, n2, box, d)
                    makeStimulus(name, dots1, box, bgcolor, color, dots2)
                    
                    #n2 on the left
                    name = "%s_%s_%s_%s_%s_%s" % (ratio, n2, n1, a, d, id)
                    dots1 = dotArranger(dotArea, n2, box, d)
                    dots2 = dotArranger(dotArea, n1, box, d)
                    makeStimulus(name, dots1, box, bgcolor, color, dots2)
