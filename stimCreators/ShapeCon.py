from ShapeMaster import *

bgcolor = (0, 0, 0)
colors = (255, 255, 255)
box = (600, 680) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
area = 0.045

ratios = [.9, .75, .66, .5, .33, .25]
seeds = [6, 7, 8, 9, 10]
reps = [1,2,3,4]

shape = 'square'

###DO THE AREA CONTROLLED STIMULI
shapeMaster = ShapeMaster(box, [area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor)
for r in ratios:
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(round(s * 1./r, 0))
			shapeMaster.shapeArranger([n1], n1, n2, r)

			name = "%s_%s_con_%s" % (r, n1, rep)
		
			shapeMaster.drawSingle(name)

			shapeMaster.shapeArranger([n2], n1, n2, r)

			name = "%s_%s_con_%s" % (r, n2, rep)

			shapeMaster.drawSingle(name)


###DO THE AREA UNCONTROLLED STIMULI
for r in ratios:
	myArea = [area/r, area]
	print myArea
	shapeMaster = ShapeMaster(box, [area/r], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, control='perimeter') 
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(s * 1/r)
			shapeMaster.shapeArranger([n1], n1, n2, r)

			name = "%s_%s_incon_%s" % (r, n1, rep)		

			shapeMaster.drawSingle(name)

	shapeMaster = ShapeMaster(box, [area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, control='perimeter') 
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(s * 1/r)
			shapeMaster.shapeArranger([n2], n1, n2, r)

			name = "%s_%s_incon_%s" % (r, n2, rep)		

			shapeMaster.drawSingle(name)
