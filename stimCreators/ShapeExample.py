from ShapeMaster import *

bgcolor = (255, 255, 255)
colors = ((255, 0, 0), (0,255,0))
box = (300, 378) #region of screen occupied by dots

shape = 'circle'

n1s = [2,3,4,5]
n2s = [4,5,6,7]

#match the areas
area = 0.045

shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)

for n1, n2 in zip(n1s, n2s):
	shapeMaster.shapeArranger([n1, n2])
	name = "%s_%s_area" % (n1, n2)
	shapeMaster.drawSingle(name)

#match the perimeters
perimeter = 0.8

shapeMaster = ShapeMaster(box, [perimeter, perimeter], shape=shape, sizemeasure = 'perimeter', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)

for n1, n2 in zip(n1s, n2s):
	shapeMaster.shapeArranger([n1, n2])
	name = "%s_%s_perimeter" % (n1, n2)
	shapeMaster.drawSingle(name)
	

#different densities and separations (with area matching)
area = 0.045

shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)

for n1, n2 in zip(n1s, n2s):
	#increase the density
	shapeMaster.density = 50
	shapeMaster.shapeArranger([n1, n2])
	name = "%s_%s_area_dens" % (n1, n2)
	shapeMaster.drawSingle(name)

	#decrease the minimum separation
	shapeMaster.density = 5
	shapeMaster.separation = 10
	shapeMaster.shapeArranger([n1, n2])
	name = "%s_%s_area_sep" % (n1, n2)
	shapeMaster.drawSingle(name)


