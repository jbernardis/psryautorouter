class RouteRequest:
	def __init__(self, train, route, entryblk):
		self.train = train
		self.route = route
		self.entryblk = entryblk

	def GetName(self):
		return self.route.GetName()

	def GetOS(self):
		return self.route.GetOS()

	def GetTrain(self):
		return self.train

	def GetEntryBlock(self):
		return self.entryblk
