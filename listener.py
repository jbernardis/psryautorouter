
import threading
import socket
import logging


class Listener(threading.Thread):
	def __init__(self, parent, ip, port):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.parent = parent
		self.isRunning = False
		self.endOfLife = False
		self.skt = None
		self.connected = False

	def connect(self):
		try:
			self.skt = socket.create_connection((self.ip, self.port))
		except:
			self.skt = None
			return False

		self.skt.settimeout(0.5)
		self.connected = True
		return True
		
	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife

	def run(self):
		if not self.connected:
			logging.error("Unable to start thread: socket listener does not exist")
			self.endOfLife = True
			return

		self.isRunning = True
		while self.isRunning:
			totalRead = 0
			szBuf = b''
					
			while totalRead < 2 and self.isRunning:
				try:
					b = self.skt.recv(2-totalRead)
					if len(b) == 0:
						self.skt.close()
						self.isRunning = False
						self.parent.raiseDisconnectEvent()

				except ConnectionResetError:
					self.skt.close()
					self.isRunning = False
					self.parent.raiseDisconnectEvent()
					
				except socket.timeout:
					pass
				else:
					szBuf += b
					totalRead += len(b)

			if not self.isRunning:
				break

			try:
				msgSize = int.from_bytes(szBuf, "little")
			except:
				print("Unable to determine message length: (", szBuf, ")")
				msgSize = None

			if msgSize:		
				totalRead = 0
				msgBuf = b''
		
				while totalRead < msgSize and self.isRunning:		
					try:
						b = self.skt.recv(msgSize - totalRead)
						if len(b) == 0:
							self.skt.close()
							self.parent.raiseDisconnectEvent()
							self.isRunning = False

					except ConnectionResetError:
						self.skt.close()
						self.isRunning = False
						self.parent.raiseDisconnectEvent()
							
					except socket.timeout:
						pass
					else:
						msgBuf += b
						totalRead += len(b)
			
				if self.isRunning:
					if totalRead == msgSize:
						self.parent.raiseDeliveryEvent(msgBuf)
	
		self.endOfLife = True
		
