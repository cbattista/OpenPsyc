#guiMaster.py
import wx
import inspect
import gm_cfg
import array

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


class objSizer(wx.GridBagSizer):
	def __init__(self, parent, target, recurse=True, color=[100, 100, 200], *args, **kwargs):

		#fun with python - get the attributes of an Object, see what the default values to ascertain what type of gui component it should be
		wx.GridBagSizer.__init__(self, *args, **kwargs)
		
		#get the args from the right places
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

		self.items = {}
		self.items['args'] = []
		self.items['init'] = None
		self.items['methods'] = []


		#get the arguments, create GUI components out of them, store them for later
		for arg in self.argnames:
			i = self.argnames.index(arg)
			if len(self.defaults) > i:
				value = self.defaults[i]
			else:
				value = None

			p = wx.Panel(self.parent, -1)
			widget = objWidget(p, arg, value, self)
			p.SetSizer(widget)
			self.widgets.append(widget)
			self.items['args'].append(p)
		

		#create the 'init' function button - this one is special because its args are already listed
		b_id = 1

		if inspect.isclass(self.target):
			init = wx.Button(self.parent, b_id, 'Initialize')
			self.items['init'] = init

		self.functions = []
		self.buttons = []

		if self.recurse:
			for f in inspect.getmembers(self.target):
				#if this is a user defined, public function, create a frame for its arguments
				if inspect.isbuiltin(f[0]) or f[0].startswith('__'):
					pass
				else:
					b_id += 1
					self.functions.append(f[1])
					button = wx.Button(self.parent, b_id, f[0])
					button.Disable()
					self.buttons.append(button)
					functionFrame = objSizer(self.parent, f[1], recurse=False)
					self.items['methods'].append(functionFrame)

		self.parent.Bind(wx.EVT_BUTTON, self.onButton)
		self.layout()


	def layout(self):
		args = self.items['args']
		init = self.items['init']
		methods = self.items['methods']

		numitems = len(args)

		#if we're assembling the top level args
		if self.recurse:
			#we want a grid of args
			if numitems % 2:
				rows = numitems/2
				cols = numitems/2 + 1
			else:
				rows = numitems/2
				cols = numitems/2
		#otherwise we just want a line of args
		else:
			cols = numitems
			rows = 1

		self.SetRows(rows)
		self.SetCols(cols)

		index = 0
		colours = [wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION), wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION)]

		for r in range(0, rows):
			for c in range(0, cols):
				if len(args) > index:
					a = args[index]
					a.SetBackgroundColour(colours[0])
					self.Add(a, [r, c], flag = wx.ALL | wx.EXPAND, border = 5)
					colours.reverse()

				index += 1

		if init:
			cols += 1
			self.SetCols(cols)
			self.Add(init, [0, cols-1], span=[rows, 1], flag = wx.EXPAND)

		count = rows + 1
		if len(methods):
			rows += len(methods) + 1
			self.SetRows(rows + 1)
			self.Add(wx.StaticLine(self.parent), pos=[count, 0], span=[1, cols], flag=wx.EXPAND)
			count += 1

		for b, m in zip(self.buttons, methods):
			#we want to place these at the start of each new row
			self.Add(m, [count, 0], span=[1, cols - 1], flag=wx.EXPAND)	
			self.Add(b, [count, cols-1], flag=wx.EXPAND)
		
			count += 1

	def onButton(self, event):
		if event.GetId() == 1:
			values = self.deconstruct()
			#now create an object from the values
			self.obj = self.target()
			for a, v in zip(self.argnames, values):
				setattr(self.obj, a, v)

			for b in self.buttons:
				b.Enable()

		else:
			function = self.functions[event.GetId() - 2]
			ff = self.items['methods'][event.GetId() - 2]
			values = ff.deconstruct()
			argString = ""
			for a, v in zip(ff.argnames, values):
				if type(v) == str:
					v = "\"%s\"" % v
				argString += ", %s=%s" % (a, v)
			exec("function(self.obj%s)" % argString)

	def deconstruct(self):
		#get the values for each of the fields
		values = []
		for w in self.widgets:
			value = w.read()
			value = value[1]

			#check if it's a string that wants to be a dict
			if type(value) == list:
				isDict = False
				v = value[0]
				if type(v) == list:
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

class objWidget(wx.BoxSizer):
	def __init__(self, parent, arg, value, orient = wx.VERTICAL, *args, **kwargs):
		wx.BoxSizer.__init__(self, *args, **kwargs)
		self.parent = parent

		if type(value) == str:
			widget = wx.TextCtrl(self.parent, -1, value)
		elif type(value) == int:
			widget = wx.SpinCtrl(self.parent, -1, str(value))
		elif type(value) == float:
			widget = FloatCtrl(self.parent, -1)
			widget.SetFloat(value)
		elif type(value) == list:
			widget = wx.BoxSizer(wx.VERTICAL)
			for v in value:
				item = objWidget(self.parent, None, v)
				widget.Add(item)
		elif type(value) == bool:
			widget = wx.CheckBox(self.parent, -1)
			widget.SetValue(value)
			orient = wx.HORIZONTAL
		elif type(value) == dict:
			widget = wx.BoxSizer(wx.VERTICAL)

			for k in value.keys():
				item = objWidget(self.parent, k, value[k], wx.HORIZONTAL)
				widget.Add(item)

		else:
			widget = wx.TextCtrl(self.parent, -1, str(value))

		if arg:
			self.Add(wx.StaticText(self.parent, -1, arg), flag=wx.ALIGN_CENTER)
		
		self.Add(widget)
				

	def read(self, w=None):
		if w==None:
			w = self
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
		elif wt == 'BoxSizer' or wt == 'objWidget':
			if len(w.GetChildren()) > 1:
				value = []
				for b in w.GetChildren():
					value.append(self.read(b))
			else:
				value = self.read(w.GetItem(0))
		elif wt == 'SizerItem':
			if w.IsWindow():
				value = self.read(w.GetWindow())
			else:
				value = self.read(w.GetSizer())
		elif wt == 'StaticText':
			value = "{" + w.GetLabel()

		return value


