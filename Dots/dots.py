#dots.py

import sys
import os
import pickle

sys.path.append("c:\code\OpenPsyc")

import experiments
import subject
import shuffler
import CBalance

blocks = ["sequential", "paired", "overlapping"]

if os.path.exists("cb.pck"):
	f = open("cb.pck")
	cb = pickle.load(f)
	f.close()
else:
	cb = CBalance.Counterbalance(blocks)

blockOrder = cb.advance()

for block in blockOrder:

	ratios = shuffler.Condition([.3, .4, .5, .6, .7, .8], "ratio", 6)
	seeds = shuffler.Condition([4, 5, 6, 7, 8], "seed", 6)
	size = shuffler.Condition(["control", "noncontrol"], "size", 5)

	order = ["large", "small"]
	trials = 240

	myShuffler = shuffler.MultiShuffler([ratios, seeds, size], trials)
	sideShuffler = shuffler.Shuffler(order, trials, 3)

	stimList = myShuffler.shuffle()
	sideList = sideShuffler.shuffle()

	for stim, order in zip(stimList, sideList):
		ratio = getattr(stim, "ratio")
		n1 = getattr(stim, "seed")
		n2 = int(n1 * 1/ratio)
		size = getattr(stim, "size")
		
		exemplar = 1
		
		if block == "overlay":
			fname = "%s_%s_%s_OL_NS_%s.bmp" % (ratio, n1, n2, exemplar)
			
			t = Texture(Image.open(fname))
			x = screen.size[0] / 2
			y = screen.size[1] / 2
			s = TextureStimulus(texture = t, position = (x, y), anchor = 'center')
			v = Viewport(screen=screen, stimuli=[s])
			p = Presentation(go_duration = (0, 'seconds'), viewports=[v])
			p.go()
		
		else:
			if order == "large":
				fname1 = "%s_%s_%s_S2_%s.bmp" % (ratio, n1, n2, exemplar)
				fname2 = "%s_%s_%s_S1_%s.bmp" % (ratio, n1, n2, exemplar)
			else:
				fname1 = "%s_%s_%s_S1_%s.bmp" % (ratio, n1, n2, exemplar)
				fname2 = "%s_%s_%s_S2_%s.bmp" % (ratio, n1, n2, exemplar)
				
			####
			t1 = Texture(Image.open(fname1))
			t2 = Texture(Image.open(fname2))

			if block == "sequential":
				x = screen.size[0] / 2
				y = screen.size[1] / 2

				s1 = TextureStimulus(texture = t1, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = t2, position = (x, y), anchor = 'center')	

				#create viewports
				v1 = Viewport(screen=screen, stimuli=[s1])
				v2 = Viewport(screen=screen, stimuli=[s2])
				
				p1 = Presentation(go_duration=(0.5, 'seconds'), viewports=[v1])
				p2 = Presentation(go_duration=(0.5, 'seconds'), viewports=[v2])
				p1.go()
				p2.go()
				
			else:
				x = screen.size[0] / 4
				y = screen.size[1] / 2
				
				s1 = TextureStimulus(texture = tex, position = (x, y), anchor = 'center')
				s2 = TextureStimulus(texture = tex2, position = (x * 3, y), anchor = 'center')	

				v = viewport(screen=screen, stimuli=[s1,s2]
				p = Presentation(go_duration=(0.5, 'seconds'), viewports=[v])
				p.go()