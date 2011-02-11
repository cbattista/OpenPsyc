from ShapeMaster import *

bgcolor = (0, 0, 0)
colors = [(255, 255, 255), (255, 255, 255)]
box = (600, 680) #region of screen occupied by dots

ratios = [.9, .75, .66, .5, .33]
seeds = [6, 7, 8, 9,10, 11]
reps = [1,2,3,4,5,6]

area = 0.03

for shape in ['square', 'triangle']:
	for r in ratios:

		shapeMaster = ShapeMaster(box, [area/r, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, control='perimeter')
			
		for s in seeds:
			for rep in reps:
				n1 = s
				n2 = int(round((s * 1/r), 0))
				shapeMaster.shapeArranger([n1, n2])

				name = "%s_%s_%s_%s_incon" % (r, n1, n2, rep)		
				shapeMaster.drawSingle(name)

for shape in ['square', 'triangle']:
	for r in ratios:

		shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor)
			
		for s in seeds:
			for rep in reps:
				n1 = s
				n2 = int(round((s * 1/r), 0))
				shapeMaster.shapeArranger([n1, n2])

				name = "%s_%s_%s_%s_con" % (r, n1, n2, rep)		
				shapeMaster.drawSingle(name)

