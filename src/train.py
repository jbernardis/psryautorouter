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

	def DelBlock(self, block):
		if block in self.blocks:
			self.blocks.remove(block)
			self.parent.TrainRemoveBlock(self.name, block, self.blocks)
		else:
			print("block %s not found for train %s" % (block, self.name))
			
		if len(self.blocks) > 0:
			self.parent.TrainTailInBlock(self.name, self.blocks[0])

		return len(self.blocks)
