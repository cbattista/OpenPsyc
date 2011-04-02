#GMTest.py

#testing out the guiMaster on a Shuffler object

import guiMaster

class TestObj:
	def __init__(self, items = ['1', '2', '3'], number = 1.23, wang = 1, chung=False, chong={'wee' : 'nis', 'pen' : 15}):
		self.items = items
		self.number = number
		self.wang = wang

	def testFunc(self, testarg=False):
		print self.items
		print self.number
		print self.wang

		print testarg

	def testFunc2(self, testarg=True):
		print self.chung
		print self.chong
		print testarg

gm = guiMaster.objApp(TestObj)

gm.go()
