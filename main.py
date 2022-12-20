import wx

from mainframe import MainFrame 


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()