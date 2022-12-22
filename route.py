class Route:
	def __init__(self, parent, name, os, ends, signals, turnouts):
		self.parent = parent
		self.os = os
		self.name = name
		self.ends = ends
		self.signals = signals
		self.turnouts = turnouts

	def GetName(self):
		return self.name

	def GetOS(self):
		return self.os

	def GetTurnouts(self):
		return self.turnouts

	def GetEnds(self):
		return self.ends

	def GetSignals(self):
		return self.signals

	def GetSignalForEnd(self, end):
		if end == self.ends[0]:
			return self.signals[0]
		elif end == self.ends[1]:
			return self.signals[1]
		else:
			return 0
