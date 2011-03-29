#guiMaster.py
import wx
import inspect

class FloatCtrl(wx.TextCtrl):
	def __init__(self, parent, *args, **kwargs):
		wx.TextCtrl.__init__(self, parent, *args, **kwargs)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue())

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
		self.widgets = []

		mainBox = wx.BoxSizer(wx.VERTICAL)

		for arg in self.argnames:
			i = self.argnames.index(arg)
			if len(self.defaults) > i:
				value = self.defaults[i]
			else:
				value = None

			sizer = self.makeWidget(arg, value)

			mainBox.Add(sizer)

		#make a an 'init' button
		mainBox.Add(wx.Button(self.frame, -1, 'GO!'))

		self.frame.Bind(wx.EVT_BUTTON, self.deconstruct)

		self.frame.SetSizerAndFit(mainBox)

		self.frame.Show()


	def deconstruct(self, event):
		values = []
		for w in self.widgets:
			value = self.readWidget(w)
			#check if it's a string that wants to be a dict
			if type(value) == list:
				isDict = False
				v = value[0]
				if len(v) == 2:
					print v[0]
					if v[0].startswith('{'):
						isDict = True

				if isDict:
					d = {}
					for v in value:
						key = v[0].lstrip('{')
						val = v[1]
						d[key] = val
					value = d 

			values.append(value)

		print values

	def readWidget(self, w):
		wt = str(type(w))
		wt = wt.split('.')[-1]
		wt = wt.strip("'>")

		value = wt

		if wt == 'TextCtrl':
			value = w.GetValue()
		elif wt == 'SpinCtrl':
			value = int(w.GetValue())
		elif wt == 'FloatCtrl':
			value = w.GetFloat()
		elif wt == 'CheckBox':
			value = w.GetValue()
		elif wt == 'BoxSizer':
			if len(w.GetChildren()) > 1:
				value = []
				for b in w.GetChildren():
					value.append(self.readWidget(b))
			else:
				value = self.readWidget(w.GetItem(0))
		elif wt == 'SizerItem':
			if w.IsWindow():
				value = self.readWidget(w.GetWindow())
			else:
				value = self.readWidget(w.GetSizer())
		elif wt == 'StaticText':
			value = "{" + w.GetLabel()

		return value

	def makeWidget(self, arg, value, orient=wx.VERTICAL, root = True):
		if type(value) == str:
			widget = wx.TextCtrl(self.frame, -1, value)
		elif type(value) == int:
			widget = wx.SpinCtrl(self.frame, -1, str(value))
		elif type(value) == float:
			widget = FloatCtrl(self.frame, -1)
			widget.SetFloat(value)
		elif type(value) == list:
			widget = wx.BoxSizer(wx.VERTICAL)

			for v in value:
				item = self.makeWidget(None, v, root=False)
				widget.Add(item)
		elif type(value) == bool:
			widget = wx.CheckBox(self.frame, -1)
			widget.SetValue(value)
			orient = wx.HORIZONTAL
		elif type(value) == dict:
			widget = wx.BoxSizer(wx.VERTICAL)

			for k in value.keys():
				item = self.makeWidget(k, value[k], wx.HORIZONTAL, root=False)
				widget.Add(item)

		else:
			widget = wx.TextCtrl(self.frame, -1, str(value))

		if root:
			self.widgets.append(widget)

		sizer = wx.BoxSizer(orient)
		if arg:
			sizer.Add(wx.StaticText(self.frame, -1, arg))
		sizer.Add(widget)

		return sizer

	def go(self):
		self.app.MainLoop()


