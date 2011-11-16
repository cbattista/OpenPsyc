#strat control, mouse clicks
def mouse_handler(event):
	global strat
	global misfire

	buttons = pygame.mouse.get_pressed()
	b1 = buttons[0]
	b2 = buttons[1]
	b3 = buttons[2]
	
	if b1:
		strat = "mem"
		p2.parameters.go_duration = (0, 'frames')
	elif b3:
		strat = "calc"
		p2.parameters.go_duration = (0, 'frames')
	elif b2:
		misfire = 1
	
def key_handler(event):
	global correct 
	global ACC
	global RT
	key = event.key

	print event.key

	RT = p.time_sec_since_go
	
	if key == 308:
		if correct == "left":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')
	elif key == 313:
		if correct == "right":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')


def pause_handler(event):
	if event.key == K_SPACE:
		print "BEGINNING EXPERIMENT"
		pause.parameters.go_duration = (0, 'frames')
