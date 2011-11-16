from ShapeMaster import *

bgcolor = (255, 255, 255)
colors = ((255, 0, 0), (0,255,0))
box = (300, 378) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
area = 0.045

shape = 'circle'

shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)

n1s = [2,3,4,5]
n2s = [4,5,6,7]

for n1, n2 in zip(n1s, n2s):
	shapeMaster.shapeArranger([n1, n2])
	name = "%s_%s" % (n1, n2)
	shapeMaster.drawSingle(name)


