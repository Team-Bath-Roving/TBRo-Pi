from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
# from classes.jsock import *
import json
import errno
from classes.Output import Output
import os 

SIZE = 1024
# TCP json communications module
class Comms:
	msg_in=[] # store json messages received
	connected=False
	client_sock=None
	def __init__(self,host_IP:str,host_port:int,output:Output,key):
		self.output=output
		self.host_IP=host_IP
		self.host_port=host_port
		self.key=key
		# self.create_socket()
	def receive(self):
		if self.connected:
			try:
				data=self.client_sock.receive()
				if not data is None:
					self.msg_in.insert(0,data)
			except Exception as e:
				if e!="unpack requires a buffer of 5 bytes":
					self.connected=False
					self.output.write(Output.EXCEPT,e,False)
	def available(self):
		return len(self.msg_in)
	def read(self):
		if self.available():
			return self.msg_in.pop()
		else:
			raise Exception("Nothing to read")
	def send(self,msg,retry=True):
		if self.connected:
			try:
				self.client_sock.send(msg)
				return True
			except Exception as e:
				self.output.write(Output.EXCEPT,e,False)
				# print(retry)
				if retry:
					self.output.write(Output.WARN, "TCP write fail, retry",False)
					return self.send(msg,False)
				else:
					self.output.write(Output.ERROR, "TCP write fail, reconnecting",False)
					self.connect()
					return False
		else:
			self.output.write(Output.ERROR, "TCP write fail: Socket closed",False)
			return False

class CommsServer(Comms):
	server_sock=None
	def create_socket(self):
		self.server_sock=ServerSocket(self.key)
	def connect(self):
		self.close()
		self.output.write(Output.INFO,f"TCP server awaiting connections at {self.host_IP}:{self.host_port}",False)
		try:
			self.create_socket()
			# self.server_sock._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			self.server_sock.bind(self.host_IP,self.host_port)
			# while self.client_sock is None:
			# 	self.client_sock=self.server_sock.accept()
			self.connected=True
			print(self.client_sock.poll())
			self.output.write(Output.INFO,f"TCP client connected from {self.client_sock.remote_address}",False)
		except Exception as e:
			self.output.write(Output.EXCEPT,e,False)
			self.connected=False
			self.output.write(Output.ERROR,"No TCP client connected",False)
		return self.connected
	def close(self):
		self.output.write(Output.INFO,"Closing sockets",False)
		try:
			if not self.server_sock is None:
				self.server_sock._socket.shutdown(SHUT_RDWR)
				self.server_sock.close()
			if not self.client_sock is None:
				self.client_sock._socket.shutdown(SHUT_RDWR)
				self.client_sock.close()
			self.client_sock=None
			self.server_sock=None
			self.connected=False
			self.output.write(Output.INFO,"Sockets Closed",False)
		except Exception as e:
			self.output.write(Output.ERROR,"Failed to close sockets",False)
			self.output.write(Output.EXCEPT,e,False)

class CommsClient(Comms):
	def create_socket(self):
		self.client_sock=ClientSocket(self.key)
	def connect(self):
		self.close()
		self.output.write(Output.INFO,"Connecting to TCP server",False)
		while not self.connected:
			try:
				self.create_socket()
				self.client_sock.connect(self.host_IP,self.host_port)
				self.connected=True
				print(self.client_sock.poll())
				self.output.write(Output.INFO,f"Connected to TCP server at {self.host_IP}:{self.host_port} from {self.client_sock.local_address}",False)
			except Exception as e:
				if not "[WinError 10061]" in str(e):
					self.output.write(Output.EXCEPT,e,False)
					self.output.write(Output.ERROR,"TCP connection failed",False)
				self.connected=False
		return self.connected
	def close(self):
		self.output.write(Output.INFO,"Closing sockets",False)
		try:
			if not self.client_sock is None:
				self.client_sock._socket.shutdown(SHUT_RDWR)
				self.client_sock.close()
			self.client_sock=None
			self.connected=False
			self.output.write(Output.INFO,"Sockets Closed",False)
		except Exception as e:
			self.output.write(Output.ERROR,"Failed to close sockets",False)
			self.output.write(Output.EXCEPT,e,False)
	