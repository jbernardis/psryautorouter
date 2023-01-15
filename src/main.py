import wx

import os, inspect, sys
cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import logging
logging.basicConfig(filename=os.path.join("logs", "autorouter.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from mainframe import MainFrame 


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()