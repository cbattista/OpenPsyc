from DotMaster import *

bgcolor = (132, 130, 132)
colors = [(255, 255, 16), (0, 4, 214)]
box = (600, 680) #region of screen occupied by dots
#areas = [0.05, 0.1, 0.15, 0.2, 0.25] #area of box taken up by dots
area = 0.045

ratios = [.9, .75, .66, .5, .33, .25]
seeds = [6, 7, 8, 9, 10]
reps = [1,2,3,4]

###DO THE AREA CONTROLLED STIMULI
dotMaster = DotMaster(box, [area, area], sizemeasure = 'area', colors = colors, bgcolor = bgcolor)
for r in ratios:
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(round(s * 1./r, 0))
			dotMaster.dotArranger([n1, n2])

			
			name = "%s_%s_C1_con_%s" % (r, n1, rep)
		
			dotMaster.drawOverlay(name)
			dotMaster.drawSingle(name)

			name = "%s_%s_C2_con_%s" % (r, n1, rep)
		
			dotMaster.colors.reverse()
		
			dotMaster.drawOverlay(name)
			dotMaster.drawSingle(name)


###DO THE AREA UNCONTROLLED STIMULI
for r in ratios:
	myArea = [area/r, area]
	print myArea
	dotMaster = DotMaster(box, myArea, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, control='perimeter') 
	for s in seeds:
		print r, s
		for rep in reps:
			n1 = s
			n2 = int(s * 1/r)
			dotMaster.dotArranger([n1, n2])
			name = "%s_%s_C1_incon_%s" % (r, n1, rep)		
			dotMaster.drawOverlay(name)
			dotMaster.drawSingle(name)

			name = "%s_%s_C2_incon_%s" % (r, n1, rep)
		
			dotMaster.colors.reverse()
		
			dotMaster.drawOverlay(name)
			dotMaster.drawSingle(name)

