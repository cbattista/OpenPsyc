from DotMaster import *

bgcolor = (132, 130, 132)
colors = [(255, 255, 16), (0, 4, 214)]
box = (480, 720) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
area = [0.075, 0.15]

ratios = [.3, .4, .5, .6, .7, .8]
seeds = [4, 5, 6, 7, 8]
reps = [1]



dotMaster = DotMaster(box, area, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, control='perimeter')

for r in ratios:
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(s * 1/r)
			dotMaster.dotArranger([n1, n2])

			
			name = "%s_%s_C1" % (r, n1)
		
			#dotMaster.drawOverlay(name)
			dotMaster.drawSingle(name)

			#name = "%s_%s_%s_%s_C2" % (r, n1, n2, rep)
		
			#dotMaster.colors.reverse()
		
			#dotMaster.drawOverlay(name)
			#dotMaster.drawSingle(name)

