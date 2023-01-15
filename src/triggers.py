import json
import os
import pprint

TriggerPointFront = 'F'  # front of train
TriggerPointRear = 'R'  # rear of train


class Triggers:
	def __init__(self):
		with open(os.path.join(os.getcwd(), "data", "arscripts.json"), "r") as jfp:
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
			return TriggerPointFront

		if block not in self.triggerTable[train]:
			return TriggerPointFront

		return self.triggerTable[train][block]["trigger"]
