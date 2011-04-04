#GMTest.py

#testing out the guiMaster on a Shuffler object

import guiMaster
import shuffler
class NestedObj:
	def __init__(self, a=1, b=2, c=3):
		self.a = a
		self.b = b
		self.c = c

	def __str__(self):
		return "%s %s %s" % (self.a, self.b, self.c)

class TestObj:
	def __init__(self, items = ['1', '2', '3'], number = 1.23, wang = 1, chung=False, chong={'wee' : 'nis', 'pen' : 15}, a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, testobj=NestedObj(), testobj2=NestedObj()):
		self.items = items
		self.number = number
		self.wang = wang
		self.chung = chung
		self.chong = chong
		self.testobj = testobj
		self.testobj2 = testobj2

	def testFunc(self, testarg=False):
		print self.items
		print self.number
		print self.wang
		print self.testobj2
		print testarg

	def testFunc2(self, testarg=True):
		print self.chung
		print self.chong
		print testarg
		print self.testobj

	def __privateFunc(self, privateArg = 6):
		pass



gm = guiMaster.objApp(TestObj)

gm.go()
