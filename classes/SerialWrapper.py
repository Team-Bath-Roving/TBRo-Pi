import serial
import time
from tbroLib.Output import Output
import threading

# Serial wrapper with exception handling

TIMEOUT=1

class SerialWrapper:
	s=None
	connected=False
	lines=[]
	def __init__(self,port:int,baud:int,output:Output,watchdog_time,name):
		self.output=output
		self.port=port
		self.baud=baud
		self.name=name
		self.connect()
		self.watchdog_thread=threading.Thread(target=self.watchdog,args=(watchdog_time,),daemon=True)
		self.watchdog_thread.start()
	def watchdog(self,ping_delay):
		while(True):
			time.sleep(ping_delay)
			self.write("P\n")
			if not self.connected:
				self.output.write("WARN",f"Serial connection to {self.name} lost, reconnecting",True)
				self.connect()
	def connect(self):
		self.output.write("INFO",f"Connecting Serial, port {self.port}")
		try:
			self.s=serial.Serial(self.port,self.baud,timeout=TIMEOUT)
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
				if self.s.in_waiting >10:
					t=time.time()
					line=self.s.readline()
					if time.time()-t < TIMEOUT-0.1:
						line=line.decode()
						line=line.rstrip()
						self.lines.append(line)
						return self.available()
					else:
						self.output.write("WARN",f"Serial timeout, port {self.port}")
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
