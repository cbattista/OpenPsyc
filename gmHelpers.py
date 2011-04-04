import wx

class FloatCtrl(wx.TextCtrl):
	"""extension of TextCtrl object to process floating point numbers"""
	def __init__(self, parent, *args, **kwargs):
		wx.TextCtrl.__init__(self, parent, *args, **kwargs)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue())

class CodeBox(wx.BoxSizer):
	def __init__(self, parent, arg, orient=wx.VERTICAL, *args, **kwargs):
		wx.BoxSizer.__init__(self, *args, **kwargs)
		self.text = wx.TextCtrl(parent, -1)		
		self.btn = wx.Button(parent, -1, 'Eval')
		self.btn.Disable()
		self.SetOrientation(orient)
		self.arg=arg

		self.Add(self.text)
		self.Add(self.btn)
		
	def Eval(self):
		if self.text.GetValue():
			return eval(self.text.GetValue())
		else:
			return None	

	def GetId(self):
		return self.btn.GetId()

	def GetTextId(self):
		return self.text.GetId()
	


class ClassBox(wx.BoxSizer):
	def __init__(self, parent, value, arg, orient=wx.VERTICAL, *args, **kwargs):
		wx.BoxSizer.__init__(self, *args, **kwargs)

		self.parent = parent

		self.SetOrientation(orient)

		btn = wx.Button(self.parent, -1, 'Edit')

		#if we have a instance of a class		
		if str(type(value)) == "<type 'instance'>":
			#it can be initialized
			btn.the_class = value.__class__
			btn.the_instance = value
		else:
			btn.the_class = value
			btn.the_instance = None

		if arg:
			btn.arg = arg


		self.Add(wx.StaticText(self.parent, -1, str(btn.the_class)))
		self.Add(wx.StaticText(self.parent, -1, str(btn.the_instance)))
		self.Add(btn)	

		self.btn = btn

	def GetValue(self):
		if self.btn.the_instance:
			return self.btn.the_instance
		else:
			return self.btn.the_class

def unpackSizer(w, parent):
	if len(w.GetChildren()) > 1:
		value = []
		for b in w.GetChildren():
			value.append(parent.read(b))
	else:
		value = parent.read(w.GetItem(0))

	return value

def unpackItem(w, parent):
	if w.IsWindow():
		value = parent.read(w.GetWindow())
	else:
		value = parent.read(w.GetSizer())

	return value
