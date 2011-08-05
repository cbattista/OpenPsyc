import wx
import pickle

class FloatCtrl(wx.TextCtrl):
	"""extension of TextCtrl object to process floating point numbers"""
	def __init__(self, parent, value, *args, **kwargs):
		wx.TextCtrl.__init__(self, parent, *args, **kwargs)
		self.SetFloat(value)

	def SetFloat(self, value):
		self.SetValue(str(value))

	def GetFloat(self):
		return float(self.GetValue())

class dotConfig(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)

		sizer = wx.BoxSizer(wx.VERTICAL)

		controls = {}
		controls['subject id'] = 666
		controls['trials'] = 240
		controls['dot duration'] = 750
		controls['mask duration'] = 500
		controls['ISI'] = 750
		controls['break trial'] = 60

		self.controls = controls

		self.ctrls = []

		for k in self.controls.keys():
			control = wx.SpinCtrl(self, -1, max=10000, initial=controls[k], size=(60, 80))
			control.label = k
			self.ctrls.append(control)
			sizer.Add(wx.StaticText(self, -1, k))
			sizer.Add(control)

		sizer.Add(wx.Button(self, -1, 'Proceed to Experiment'))

		self.Bind(wx.EVT_BUTTON, self.onButton)

		self.SetSizerAndFit(sizer)

	def onButton(self, event):
		for c in self.ctrls:
			self.controls[c.label] = int(c.GetValue())

		f = open("controls.pck", "w")
		pickle.dump(self.controls, f)
		f.close()

		self.Destroy()

app = wx.App()
dc = dotConfig(None, title="Samar's Dot Task", size=(640,480))
dc.Show()
app.MainLoop()
