class Turnout:
	def __init__(self, parent, name, state):
		self.parent = parent
		self.name = name
		self.state = state
		self.locked = False

	def Lock(self, flag=True):
		if self.locked == flag:
			return
		self.locked = flag
		self.parent.TurnoutLockChange(self.name, self.locked)

	def IsLocked(self):
		return self.locked

	def SetState(self, state):
		if self.state == state:
			return
		self.state = state
		self.parent.TurnoutStateChange(self.name, self.state)

	def GetState(self):
		return self.state

	def GetName(self):
		return self.name
