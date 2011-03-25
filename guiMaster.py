#guiMaster.py
import wx
import inspect

class FloatCtrl(wx.TextCtrl):
	def __init__(self, parent, *args, **kwargs):
		wx.TextCtrl__init__(self, parent, *args, **kwargs)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue)

class guiMaster:
	def __init__(self, targetClass):
		#fun with python - get the attributes of an Object, see what the default values to ascertain what type of gui component it should be
		if inspect.isclass(targetClass):
			self.targetClass = targetClass
		else:
			raise Exception("You need to provide me with a target class, sucka!")		
	
		self.args = inspect.getargspec(self.targetClass.__init__)

		#get the arguments and the default values
		self.argnames = self.args[0]
		self.argnames.remove('self')
		self.defaults = self.args[3]
		self.app = wx.App(False)
		self.frame = wx.Frame(None, title=inspect.getfile(self.targetClass))
		
		#make the thing
		self.construct()

	def construct(self):
		self.sizers = []

		mainBox = wx.BoxSizer(wx.VERTICAL)

		for arg in self.argnames:
			i = self.argnames.index(arg)
			if len(self.defaults) > i:
				value = self.defaults[i]
			else:
				value = None

			sizer = self.makeWidget(arg, value)

			mainBox.Add(sizer)

		self.frame.SetSizerAndFit(mainBox)

		self.frame.Show()


	def makeWidget(self, arg, value, orient=wx.VERTICAL):
		self.widgets = []

		sizer = wx.BoxSizer(orient)

		sizer.Add(wx.StaticText(self.frame, -1, arg))

		if type(value) == str:
			widget = wx.TextCtrl(self.frame, -1, value)
		elif type(value) == int:
			widget = wx.SpinCtrl(self.frame, -1, str(value))
		elif type(value) == float:
			widget = wx.FloatCtrl(self.frame, -1)
			widget.SetFloat(value)
		elif type(value) == 'NoneType':
			widget = wx.TextCtrl(self.frame, -1)
		else:
			widget = wx.TextCtrl(self.frame, -1, str(value))
	
		self.widgets.append(widget)

		sizer.Add(widget)

		return sizer

	def go(self):
		self.app.MainLoop()


