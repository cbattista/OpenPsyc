import wx

class FloatCtrl(wx.TextCtrl):
	"""extension of TextCtrl object to process floating point numbers"""
	def __init__(self, parent, *args, **kwargs):
		wx.TextCtrl.__init__(self, parent, *args, **kwargs)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue())

