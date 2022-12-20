import wx
import wx.lib.newevent

import json

from settings import Settings

from signal import Signal
from block import Block

from listener import Listener
from rrserver import RRServer

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent()
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.sessionid = None
		self.subscribed = False
		self.settings = Settings()
		self.scripts = {}
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.listener = None
		self.rrServer = None

		self.title = "PSRY Auto Router"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh")
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		vsz.AddSpacer(20)

		hsz.AddSpacer(20)
		hsz.Add(self.bSubscribe)
		hsz.AddSpacer(20)
		hsz.Add(self.bRefresh)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def Initialize(self):
		self.listener = None
		self.ShowTitle()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		print("finished initialize")

	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				print("Unable to establish connection with server")
				self.listener = None
				return

			self.listener.start()
			self.subscribed = True
			self.bSubscribe.SetLabel("Disconnect")
			self.bRefresh.Enable(True)

		self.ShowTitle()

	def OnRefresh(self, _):
		if self.sessionid is not None:
			self.rrServer.SendRequest({"refresh": {"SID": self.sessionid}})
			self.requestRoutes()

	def requestRoutes(self):
		if self.sessionid is not None:
			self.rrServer.SendRequest({"refresh": {"SID": self.sessionid, "type": "routes"}})

	def raiseDeliveryEvent(self, data):  # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			print("Unable to parse (%s)" % data)
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					self.turnouts[turnout] = state

			elif cmd == "block":
				print("%s: %s" % (cmd, parms))
				for p in parms:
					block = p["name"]
					state = p["state"]
					direction = p["dir"]
					clear = p["clear"]
					if block not in self.blocks:
						self.blocks[block] = Block(self, block, state, direction, clear != 0)
					else:
						b = self.blocks[block]
						b.SetState(state)
						b.SetDirection(direction)
						b.SetClear(clear)

			elif cmd == "signal":
				for p in parms:
					sigName = p["name"]
					aspect = int(p["aspect"])
					if sigName not in self.signals:
						self.signals[sigName] = Signal(self, sigName, aspect)
					else:
						self.signals[sigName].SetAspect(aspect)

			elif cmd == "signallock":
				for p in parms:
					sigName = p["name"]
					lock = int(p["state"])
					if sigName in self.signals:
						self.signals[sigName].Lock(lock != 0)
					else:
						print("Don't know signal '%s'" % sigName)

			elif cmd == "routedef":
				name = parms["name"]
				os = parms["os"]
				ends = parms["ends"]
				signals = parms["signals"]
				turnouts = parms["turnouts"]
				print("%10.10s  %10.10s       %10.10s  %10.10s" % (ends[0], ends[1], signals[0], signals[1]))

			elif cmd == "setroute":
				for p in parms:
					blknm = p["block"]
					rte = p["route"]
					try:
						ends = p["ends"]
					except KeyError:
						ends = None
					self.routes[blknm] = [rte, ends]

			elif cmd == "settrain":
				for p in parms:
					block = p["block"]
					name = p["name"]
					loco = p["loco"]

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				self.requestRoutes()

			else:
				if cmd not in ["control", "relay", "handswitch", "siglever", "breaker"]:
					print("************************ Unprocessed Message: %s: %s" % (cmd, parms))

	def SignalAspectChange(self, sigName, nLock):
		print("signal %s lock has changed %s" % (sigName, str(nLock)))

	def SignalLockChange(self, sigName, nAspect):
		print("signal %s aspect has changed %d" % (sigName, nAspect))

	def BlockDirectionChange(self, blkName, nDirection):
		print("block %s has changed direction: %s" % (blkName, nDirection))

	def BlockStateChange(self, blkName, nState):
		print("block %s has changed state: %d" % (blkName, nState))

	def BlockClearChange(self, blkName, nClear):
		print("block %s has changed clear: %s" % (blkName, str(nClear)))

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def Request(self, req):
		if self.subscribed:
			print("Outgoing request: %s" % json.dumps(req))
			self.rrServer.SendRequest(req)

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.sessionid = None
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		self.ShowTitle()

	def OnClose(self, _):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		self.Destroy()

