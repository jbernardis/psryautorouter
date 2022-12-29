class Block:
	def __init__(self, parent, name, state, direction, clear):
		self.parent = parent
		self.name = name
		self.state = state
		self.direction = direction
		self.clear = clear
		self.train = None
		self.loco = None

	def SetState(self, state):
		if state == self.state:
			return

		self.state = state
		self.parent.BlockStateChange(self.name, self.state)

	def SetDirection(self, direction):
		if direction == self.direction:
			return

		self.direction = direction
		self.parent.BlockDirectionChange(self.name, self.direction)

	def SetClear(self, clear):
		if clear == self.clear:
			return

		self.clear = clear
		self.parent.BlockClearChange(self.name, self.clear)

	def SetTrain(self, train, loco):
		if train == self.train and loco == self.loco:
			return

		oldTrain = self.train
		oldLoco = self.loco
		self.train = train
		self.loco = loco
		self.parent.BlockTrainChange(self.name, oldTrain, oldLoco, self.train, self.loco)

	def GetName(self):
		return self.name

	def GetDirection(self):
		return self.direction

	def GetState(self):
		return self.state

	def GetClear(self):
		return self.clear