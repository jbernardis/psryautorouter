class Fifo:
	def __init__(self):
		self.data = {}
		self.nextin = 0
		self.nextout = 0

	def Append(self, data):
		self.data[self.nextin] = data
		self.nextin += 1

	def Pop(self):
		if self.nextin == self.nextout:
			return None

		result = self.data[self.nextout]
		del self.data[self.nextout]
		self.nextout += 1
		return result

	def Peek(self):
		if self.nextin == self.nextout:
			return None

		return self.data[self.nextout]

	def IsEmpty(self):
		return self.nextin == self.nextout
