from ShapeMaster import *

bgcolor = (0, 0, 0)
colors = [(255, 255, 255)]
box = (600, 680) #region of screen occupied by dots

ratios = [.9, .75, .66, .5, .33]
seeds = [6, 7, 8, 9,10, 11]
reps = [1,2,3,4,5,6]

area = 0.03

shapeMaster = ShapeMaster(box, [area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor)
			
			
	shapeMaster.shapeArranger([n1])

				name = "%s_%s_%s_%s_con" % (r, n1, n2, rep)		
				shapeMaster.drawSingle(name)

