from ShapeMaster import *

bgcolor = (0, 0, 0)
colors = (255, 255, 255)
box = (600, 680) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
area = 0.045
perimeter = 1.6

ratios = [.9, .75, .66, .5, .33]
seeds = [6, 7, 8, 9,10, 11]
reps = [1,2,3,4,5,6]


for shape in ['square', 'triangle']:
	for sm, smm in zip(['area', 'perimeter'], [area, perimeter]):
		###DO THE AREA CONTROLLED STIMULI
		shapeMaster = ShapeMaster(box, [smm], shape=shape, sizemeasure = sm, colors = colors, bgcolor = bgcolor)
		for r in ratios:
			for s in seeds:
				print r, s
				for rep in reps:
					n1 = s
					n2 = int(round(s * 1./r, 0))
					shapeMaster.shapeArranger([n1], n1, n2, r)

					name = "%s_%s_%s_con_%s" % (sm, r, n1, rep)
		
					shapeMaster.drawSingle(name)

					shapeMaster.shapeArranger([n2], n1, n2, r)

					name = "%s_%s_%s_con_%s" % (sm, r, n2, rep)

					shapeMaster.drawSingle(name)



		###DO THE AREA UNCONTROLLED STIMULI
		for r in ratios:
			if sm == 'area':
				control = 'perimeter'
			else:
				control = 'area'
			shapeMaster = ShapeMaster(box, [smm/r], shape=shape, sizemeasure = sm, colors = colors, bgcolor = bgcolor, control=control) 
			for s in seeds:
				print r, s
				for rep in reps:
					n1 = s
					n2 = int(s * 1/r)
					shapeMaster.shapeArranger([n1], n1, n2, r)

					name = "%s_%s_%s_incon_%s" % (sm, r, n1, rep)		

					shapeMaster.drawSingle(name)

			shapeMaster = ShapeMaster(box, [smm], shape=shape, sizemeasure = sm, colors = colors, bgcolor = bgcolor, control=control) 
			for s in seeds:
				print r, s
				for rep in reps:
					n1 = s
					n2 = int(s * 1/r)
					shapeMaster.shapeArranger([n2], n1, n2, r)

					name = "%s_%s_%s_incon_%s" % (sm, r, n2, rep)		

					shapeMaster.drawSingle(name)


