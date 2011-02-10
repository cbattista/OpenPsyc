from ShapeMaster import *

bgcolor = (0, 0, 0)
colors = [(255, 255, 255), (255, 255, 255)]
box = (600, 680) #region of screen occupied by dots

ratios = [.9, .75, .66, .5, .33]
seeds = [6, 7, 8, 9,10, 11]
reps = [1,2,3,4,5,6]


for shape in ['square', 'triangle']:
	if shape == 'square':
		perimeter = 0.8
		area = 0.045
	elif shape == 'triangle':
		perimeter = 1.6
		area = 0.045
	for sm, smm in zip(['area', 'perimeter'], [area, perimeter]):
		for r in ratios:

			if sm == 'area':
				control = 'perimeter'
			else:
				control = 'area'

			shapeMaster = ShapeMaster(box, [smm/r, smm], shape=shape, sizemeasure = sm, colors = colors, bgcolor = bgcolor, control=control)

			for s in seeds:
				print r, s
				for rep in reps:
					n1 = s
					n2 = int(round((s * 1/r), 0))
					shapeMaster.shapeArranger([n1, n2])

					name = "%s_%s_%s_%s_%s" % (sm, r, n1, n2, rep)		
					shapeMaster.drawSingle(name)


