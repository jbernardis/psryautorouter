class Train:
	def __init__(self, parent, name, loco):
		self.parent = parent
		self.name = name
		self.loco = loco
		self.blocks = []

	def AddBlock(self, block):
		if block in self.blocks:
			return

		self.blocks.append(block)
		self.parent.TrainAddBlock(self.name, block)

	def GetBlocks(self):
		return self.blocks

	def DelBlock(self, blkName):
		if blkName in self.blocks:
			self.blocks.remove(blkName)
		else:
			print("block %s not found for train %s" % (blkName, self.name))

		return len(self.blocks)
