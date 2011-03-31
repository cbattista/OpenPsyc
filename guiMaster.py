#guiMaster.py
import wx
import inspect

class FloatCtrl(wx.TextCtrl):
	#extension of TextCtrl object to process floating point numbers
	def __init__(self, parent, *args, **kwargs):
		wx.TextCtrl.__init__(self, parent, *args, **kwargs)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue())

class objApp:
	def __init__(self, targetClass):
		self.app = wx.App(False)
		objMaker(None, targetClass)

	def go(self):
		self.app.MainLoop()

class objMaker:
	def __init__(self, parent, target, recurse=True, *args, **kwargs):
		if inspect.isclass(target) or inspect.isfunction(target):
			frame = wx.Frame(None)
			self.frame = frame
			sizer = objSizer(frame, target)
			self.sizer = sizer
			self.frame.SetSizerAndFit(sizer)
			self.frame.Show()
		elif inspect.ismethod(target):
			self.frame = None
			self.sizer = objSizer(parent, target)


class objSizer(wx.BoxSizer):
	def __init__(self, parent, target, recurse=True, *args, **kwargs):

		#fun with python - get the attributes of an Object, see what the default values to ascertain what type of gui component it should be
		wx.BoxSizer.__init__(self, *args, **kwargs)

		self.SetOrientation(wx.VERTICAL)

		if inspect.isclass(target):
			self.args = inspect.getargspec(target.__init__)
		elif inspect.isfunction(target) or inspect.ismethod(target):
			self.args = inspect.getargspec(target)
		else:
			raise Exception("I only work with functions, classes and methods, dick.")

		self.title = inspect.getfile(target)
	
		self.target = target

		self.recurse = recurse

		self.parent = parent

		#get the arguments and the default values
		self.argnames = self.args[0]
		self.argnames.remove('self')
		self.defaults = self.args[3]
		
		#make the thing
		self.construct()

	def construct(self):
		self.widgets = []

		#get the arguments, create GUI components out of them
		for arg in self.argnames:
			i = self.argnames.index(arg)
			if len(self.defaults) > i:
				value = self.defaults[i]
			else:
				value = None

			sizer = self.makeWidget(arg, value)

			self.Add(sizer)

		
		#create the 'init' function button - this one is special because its args are already listed
		b_id = 1

		if inspect.isclass(self.target):
			init = wx.Button(self.parent, b_id, 'Initialize')
			self.Add(init)

		self.functions = []
		self.functionFrames = []
		
		if self.recurse:
			for f in inspect.getmembers(self.target):
				#if this is a user defined function, create a frame for its arguments
				if inspect.isbuiltin(f[0]) or f[0].startswith('__'):
					pass
				else:
					b_id += 1
					self.functions.append(f[1])
					button = wx.Button(self.parent, b_id, f[0])
					self.Add(button)
					functionFrame = objSizer(self.parent, f[1], recurse=False)
					self.functionFrames.append(functionFrame)
					self.Add(functionFrame)

		self.parent.Bind(wx.EVT_BUTTON, self.onButton)

	def onButton(self, event):
		if event.GetId() == 1:
			values = self.deconstruct()
			#now create an object from the values
			self.obj = self.target()
			for a, v in zip(self.argnames, values):
				setattr(self.obj, a, v)

		else:
			function = self.functions[event.GetId() - 2]
			ff = self.functionFrames[event.GetId() - 2]
			values = ff.deconstruct()
			argString = ""
			for a, v in zip(ff.argnames, values):
				argString += ", %s=%s" % (a, v)
			exec("function(self.obj%s)" % argString)

	def deconstruct(self):
		#get the values for each of the fields
		values = []
		for w in self.widgets:
			value = self.readWidget(w)
			#check if it's a string that wants to be a dict
			if type(value) == list:
				isDict = False
				v = value[0]
				if len(v) == 2:
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

		return values

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
			widget = wx.TextCtrl(self.parent, -1, value)
		elif type(value) == int:
			widget = wx.SpinCtrl(self.parent, -1, str(value))
		elif type(value) == float:
			widget = FloatCtrl(self.parent, -1)
			widget.SetFloat(value)
		elif type(value) == list:
			if len(value) <= 4:
				widget = wx.BoxSizer(wx.HORIZONTAL)
			else:
				widget = wx.BoxSizer(wx.VERTICAL)

			for v in value:
				item = self.makeWidget(None, v, root=False)
				widget.Add(item)
		elif type(value) == bool:
			widget = wx.CheckBox(self.parent, -1)
			widget.SetValue(value)
			orient = wx.HORIZONTAL
		elif type(value) == dict:
			widget = wx.BoxSizer(wx.VERTICAL)

			for k in value.keys():
				item = self.makeWidget(k, value[k], wx.HORIZONTAL, root=False)
				widget.Add(item)

		else:
			widget = wx.TextCtrl(self.parent, -1, str(value))

		if root:
			self.widgets.append(widget)

		sizer = wx.BoxSizer(orient)
		if arg:
			sizer.Add(wx.StaticText(self.parent, -1, arg))
		sizer.Add(widget)

		return sizer

