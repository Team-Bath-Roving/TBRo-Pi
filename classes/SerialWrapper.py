import serial
from classes.Output import Output
# Serial wrapper with exception handling
class SerialWrapper:
	s=None
	connected=False
	lines=[]
	def __init__(self,port:int,baud:int,output:Output):
		self.output=output
		self.port=port
		self.baud=baud
		self.connect()
	def connect(self):
		self.output.write("INFO",f"Connecting Serial, port {self.port}")
		try:
			self.s=serial.Serial(self.port,self.baud)
			self.output.write("INFO",f"Serial connected, port {self.port}")
			self.connected=True
		except:
			self.output.write("ERROR",f"Serial connect failed, port {self.port}")
			self.connected=False
		return self.connected
	def write(self,string,retry=True):
		if self.connected:
			try:
				self.s.write(string.encode())
				return True
			except Exception as e:
				self.output.write("ERROR",f"Serial write failed, port {self.port}")
				self.output.write("EXCEPT",e)
				if retry:
					self.connect() # try to reconnect
					return self.write(string,False) # retry write
				else:
					return False
		else:
			return False
	def receive(self,retry=False):
		if self.connected:
			try:
				if self.s.in_waiting >0:
					self.lines.append(self.s.readline().decode())
			except Exception as e:
				self.output.write("ERROR",f"Serial read failed, port {self.port}")
				self.output.write("EXCEPT",e)
				if retry:
					self.connect()
					self.receive(False)
	def available(self):
		return len(self.lines)
	def read(self):
		if self.available()>0:
			return self.lines.pop()
		else:
			self.output.write("WARN",f"Nothing to read in serial buffer, port {self.port}")
			return ""
	def close(self):
		self.output.write("INFO",f"Closing serial, port {self.port}")
		try:
			self.s.close()
		except:
			self.output.write("ERROR",f"failed to close serial, port {self.port}")
