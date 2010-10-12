class goFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		self.Continue = wx.Button(self, 2, 'Continue > >') 
		self.GoBack = wx.Button(self, 3, '< < Repeat')
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.GoBack)		
		sizer.Add(self.Continue)
		
		self.Bind(wx.EVT_BUTTON, self.go, id=2)
		self.Bind(wx.EVT_BUTTON, self.back, id=3)

		self.SetSizer(sizer)

		self.Layout()

	def go(self, event):
		self.Destroy()
		print 'going'
		go_ahead = 1


	def back(self, event):
		self.Destroy()
		go_ahead = 0
	

class goAhead(wx.App):
	def OnInit(self):
		frame = goFrame(None, -1, 'Continue?')
		frame.Centre()
		frame.Show(True)
		return True
