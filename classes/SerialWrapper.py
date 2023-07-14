import serial
import time
from tbroLib.Output import Output
import threading
import serial.tools.list_ports

# Serial wrapper with exception handling


TIMEOUT=1

def scanUSB(out):
	out.write("INFO","Scanning USB ports...",True)
	ports = serial.tools.list_ports.comports()
	for port in sorted(ports):
		out.write("INFO",f"Found USB Device: {port.device} Desc: {port.description} Prod: {port.product}  VID:PID={port.vid}:{port.pid}  MF:{port.manufacturer}",True)

class SerialWrapper:
	s=None
	connected=False
	prev_connected=True
	scanUSB=False
	lines=[]
	def __init__(self,port,baud:int,output:Output,watchdog_time,name,prod_code=None):
		self.output=output
		self.port=port
		self.baud=baud
		self.name=name # the name used in terminal output
		self.prod_code=prod_code # device product code
		if not prod_code is None: # if product code defined, 
			self.scanUSB=True
		self.connect()
		self.watchdog_thread=threading.Thread(target=self.watchdog,args=(watchdog_time,),daemon=True)
		self.watchdog_thread.start()
	def watchdog(self,ping_delay):
		while(True):
			time.sleep(ping_delay)
			self.write("P\n")
			if not self.connected:
				if self.prev_connected:
					self.output.write("WARN",f"{self.name} serial connection lost, reconnecting",True)
					self.prev_connected=False
				self.connect()
			else:
				self.prev_connected=True
	def getUSBport(self):
		ports = serial.tools.list_ports.comports()
		for port in ports:
			if port.product==self.prod_code:
				if port.device!=self.port:
					self.output.write(f"INFO",f"Found {self.name} at port {port.device}",True)
				return port.device
		if self.prev_connected:
			self.port=None
			self.output.write(f"WARN",f"Could not find {self.name} device: \"{self.prod_code}\"")
		return None
	def connect(self):
		if self.scanUSB:
			self.port=self.getUSBport()
		if not self.port is None:
			self.output.write("INFO",f"Connecting {self.name} serial, port {self.port}")
			try:
				self.s=serial.Serial(self.port,self.baud,timeout=TIMEOUT)
				self.output.write("INFO",f"{self.name} serial connected",True)
				self.connected=True
			except:
				self.output.write("ERROR",f"{self.name} serial connect failed")
				self.connected=False
		return self.connected
	def write(self,string,retry=False):
		if self.connected:
			try:
				self.s.write(string.encode())
				return True
			except Exception as e:
				self.connected=False
				self.output.write("ERROR",f"{self.name} serial write failed")
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
					else:
						self.output.write("WARN",f"{self.name} serial timeout",True)
			except Exception as e:
				self.connected=False
				self.output.write("ERROR",f"{self.name} serial read failed")
				self.output.write("EXCEPT",e)
				if retry:
					self.connect()
					self.receive(False)
		return self.available()
	def available(self):
		return len(self.lines)
	def read(self):
		if self.available()>0:
			return self.lines.pop()
		else:
			self.output.write("WARN",f"Nothing to read in {self.name} serial buffer")
			return ""
	def close(self):
		self.output.write("INFO",f"Closing {self.name} serial")
		try:
			self.s.close()
		except:
			self.output.write("ERROR",f"failed to close {self.name} serial")
