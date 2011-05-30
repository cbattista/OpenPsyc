import glob
import os
import sys
import subprocess

"""this will work with the following directory structure
root
	subject1
		Run1
		Run2
		Run3
		Run...
		RunN
	subject2
	subject3
	subject...
	subjectN


"""

rootDir = os.getcwd()
subjects = "*"
runs =  "*Run*"
anats = "*.hdr"

subjectdirs = glob.glob(os.path.join(rootDir, subjects))

brains = []

for s in subjectdirs:
	if os.path.isdir(s):
		rundirs = glob.glob(os.path.join(s, runs))
		for r in rundirs:
			anats = glob.glob(os.path.join(r, anats))
			for a in anats:
				#the name of the skull stripped file
				brain = "%s_brain" % a
				#the shell command to skull strip the brain
				command = "bet %s %s -f 0.35" % (a, brain)
				#keep a reference to the brains for later
				brains.append(os.path.join(r, brain))
				p = subprocess.Popen(command, shell=True)
