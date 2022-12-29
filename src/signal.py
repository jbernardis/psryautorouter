class Signal:
	def __init__(self, parent, name, aspect):
		self.parent = parent
		self.name = name
		self.aspect = aspect
		self.locked = False

	def Lock(self, flag=True):
		if self.locked == flag:
			return
		self.locked = flag
		self.parent.SignalLockChange(self.name, self.locked)

	def IsLocked(self):
		return self.locked

	def SetAspect(self, aspect):
		if self.aspect == aspect:
			return
		self.aspect = aspect
		self.parent.SignalAspectChange(self.name, self.aspect)

	def GetAspect(self):
		return self.aspect

	def GetName(self):
		return self.name
