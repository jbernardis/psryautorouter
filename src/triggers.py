import json
import pprint


class Triggers:
	def __init__(self):
		with open("triggers.json", "r") as jfp:
			self.triggerTable = json.load(jfp)			
		pprint.pprint(self.triggerTable)

	def GetRoute(self, train, block):
		if train not in self.triggerTable:
			return None

		if block not in self.triggerTable[train]:
			return None

		return self.triggerTable[train][block]["route"]

	def GetTriggerPoint(self, train, block):
		if train not in self.triggerTable:
			return None

		if block not in self.triggerTable[train]:
			return None

		return self.triggerTable[train][block]["trigger"]
