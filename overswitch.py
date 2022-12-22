class OverSwitch:
	def __init__(self, name):
		self.name = name
		self.routes = {}
		self.activeRoute = None
		self.pendingActiveRoute = None

	def AddRoute(self, rte):
		name = rte.GetName()
		self.routes[name] = rte
		if self.pendingActiveRoute is not None:
			if self.pendingActiveRoute == name:
				self.activeRoute = rte
				self.pendingActiveRoute = None

	def SetActiveRoute(self, rtName):
		if rtName is None or rtName == "None":
			self.activeRoute = None
			return

		if rtName not in self.routes:
			self.pendingActiveRoute = rtName
			return

		self.activeRoute = self.routes[rtName]

	def GetActiveRoute(self):
		return self.activeRoute
