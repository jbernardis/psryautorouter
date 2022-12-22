import wx
import wx.lib.newevent

import json

from fifo import Fifo

from settings import Settings

from triggers import Triggers
from routerequest import RouteRequest
from turnout import Turnout
from signal import Signal
from block import Block
from overswitch import OverSwitch
from train import Train
from route import Route

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

		self.triggers = Triggers()

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.osList = {}
		self.trains = {}
		self.OSQueue = {}
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
			#  print("receipt: %s: %s" % (cmd, parms))
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					if turnout not in self.turnouts:
						self.turnouts[turnout] = Turnout(self, turnout, state)
					else:
						self.turnouts[turnout].SetState(state)

			elif cmd == "turnoutlock":
				for p in parms:
					toName = p["name"]
					lock = int(p["state"])
					if toName in self.turnouts:
						self.turnouts[toName].Lock(lock != 0)

			elif cmd == "block":
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

			elif cmd == "routedef":
				name = parms["name"]
				os = parms["os"]
				ends = parms["ends"]
				signals = parms["signals"]
				turnouts = parms["turnouts"]
				if os not in self.osList:
					self.osList[os] = OverSwitch(os)

				rte = Route(self, name, os, ends, signals, turnouts)
				self.routes[name] = rte
				self.osList[os].AddRoute(rte)

			elif cmd == "setroute":
				print("setroute: %s: %s" % (cmd, parms))
				for p in parms:
					blknm = p["block"]
					rtnm = p["route"]
					if blknm not in self.osList:
						self.osList[blknm] = OverSwitch(blknm)

					self.osList[blknm].SetActiveRoute(rtnm)

			elif cmd == "settrain":
				for p in parms:
					block = p["block"]
					name = p["name"]
					loco = p["loco"]

					if name is None:
						self.blocks[block].SetTrain(None, None)
					else:
						if name not in self.trains:
							self.trains[name] = Train(self, name, loco)

						self.trains[name].AddBlock(block)

						self.blocks[block].SetTrain(name, loco)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				self.requestRoutes()

			else:
				if cmd not in ["control", "relay", "handswitch", "siglever", "breaker"]:
					print("************************ Unprocessed Message: %s: %s" % (cmd, parms))

	def SignalLockChange(self, sigName, nLock):
		print("signal %s lock has changed %s" % (sigName, str(nLock)))
		self.EvaluateQueuedRequests()

	def SignalAspectChange(self, sigName, nAspect):
		print("signal %s aspect has changed %d" % (sigName, nAspect))
		self.EvaluateQueuedRequests()

	def TurnoutLockChange(self, toName, nLock):
		print("turnout %s lock has changed %s" % (toName, str(nLock)))
		self.EvaluateQueuedRequests()

	def TurnoutStateChange(self, toName, nState):
		print("turnout %s state has changed %s" % (toName, nState))
		self.EvaluateQueuedRequests()

	def BlockDirectionChange(self, blkName, nDirection):
		print("block %s has changed direction: %s" % (blkName, nDirection))
		self.EvaluateQueuedRequests()

	def BlockStateChange(self, blkName, nState):
		print("block %s has changed state: %d" % (blkName, nState))
		self.EvaluateQueuedRequests()

	def BlockClearChange(self, blkName, nClear):
		print("block %s has changed clear: %s" % (blkName, str(nClear)))
		self.EvaluateQueuedRequests()

	def BlockTrainChange(self, blkName, oldTrain, oldLoco, newTrain, newLoco):
		if oldTrain is not None:
			try:
				if self.trains[oldTrain].DelBlock(blkName) == 0:
					del(self.trains[oldTrain])
			except KeyError:
				pass

	def TrainAddBlock(self, train, block):
		print("train %s had moved into block %s" % (train, block))
		routeRequest = self.CheckTrainInBlock(train, block)
		if routeRequest is None:
			print("we have nothing for this train in this block")
			return

		if self.EvaluateRouteRequest(routeRequest):
			self.SetupRoute(routeRequest)
		else:
			self.EnqueueRouteRequest(routeRequest)

	def CheckTrainInBlock(self, train, block):
		rtName = self.triggers.GetRoute(train, block)
		if rtName is None:
			return None

		return RouteRequest(train, self.routes[rtName], block)

	def EvaluateRouteRequest(self, rteRq):
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		print("evaluate route %s" % rname)
		rte = self.routes[rname]
		os = self.osList[rte.GetOS()]
		activeRte = os.GetActiveRoute()
		tolock = []
		siglock = []
		if activeRte is None or activeRte.GetName() != rname:
			for t in rte.GetTurnouts():
				toname, state = t.split(":")
				if self.turnouts[toname].IsLocked() and self.turnouts[toname].GetState() != state:
					#  turnout is locked AND we need to change it
					tolock.append(toname)
		#  else we are already on this route - no turnout evauation needed

		sigNm = rte.GetSignalForEnd(blkName)
		if sigNm is not None:
			if self.signals[sigNm].IsLocked():
				siglock.append(sigNm)

		if len(tolock) + len(siglock) == 0:
			print("eval true")
			return True  # OK to proceed with this route
		else:
			#  TODO - do something with the tolock and siglock arrays
			print("Eval false %s %s" % (str(tolock), str(siglock)))
			return False  # this route is unavailable right now

	def SetupRoute(self, rteRq):
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		print("set up route %s" % rname)
		rte = self.routes[rname]
		for t in rte.GetTurnouts():
			toname, state = t.split(":")
			self.Request({"turnout": {"name": toname, "status": state}})

		sigNm = rte.GetSignalForEnd(blkName)
		if sigNm is not None:
			self.Request({"signal": {"name": sigNm, "aspect": -1}})

	def EnqueueRouteRequest(self, rteRq):
		osNm = rteRq.GetOS()
		if osNm not in self.OSQueue:
			self.OSQueue[osNm] = Fifo()

		self.OSQueue[osNm].Append(rteRq)

	def EvaluateQueuedRequests(self):
		print("evaluating queued requests")
		for osNm in self.OSQueue:
			print("OS: %s" % osNm)
			req = self.OSQueue[osNm].Peek()
			if req is not None:
				print("Request for block %s" % req.GetName())
				if self.EvaluateRouteRequest(req):
					print("OK to proceed")
					self.OSQueue[osNm].Pop()
					self.SetupRoute(req)

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

