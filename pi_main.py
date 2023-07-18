### IMPORT LIBS

import atexit
import time

### IMPORT PROGRAM CLASSES

import socket
import classes.Constrain
from Comms.Comms import CommsServer
from classes.SerialWrapper import SerialWrapper, scanUSB
from Streaming.StreamServer import StreamServer
# from classes.PanTilt import PanTilt,StatusNeopixel
from classes.LogiPanTilt import LogiPanTilt
from Comms.Output import Output
import subprocess
# from classes.screwtank import ScrewTank
# from classes.RadioControl import RadioControl
import sys

while True:

	def exit_handler():
		stop()
		sys.exit()
	atexit.register(exit_handler)

	WATCHDOG_TIME = 5
	MCU_KEEPALIVE = 0.4 # if MCU doesn't recieve this it turns motors off
	# Network

	# HOST_IP = socket.gethostbyname(socket.gethostname())
	HOST_IP = "0.0.0.0"
	PORTS = [5000,5001,5432]

	# Serial settings
	MCU_PORT='/dev/ttyS0'
	MCU_BAUD=115200

	MAX_PING = 2000

	### Object instantiation

	# init program output (TCP and bash)
	out=Output("LAPTOP")
	out.toggleDisplayTypes(["PING","ACK","STATUS"],False)

	# init stereo stream
	MCAST_GRP = '239.1.1.1'
	stereo=StreamServer(out,"ov5647","Stereo") # system finds the camera based upon the model number (assumes no duplicates)
	stereo.configure(1296,972)
	stereo.start(MCAST_GRP,5008,True) # using a multicast address 224.1.1.1:5008
	stereo.set_bitrate(5000000)

	# init pantilt stream

	# init TCP comms
	comms=CommsServer(HOST_IP,PORTS,out,None,WATCHDOG_TIME)
	# wait for TCP client
	comms.connect()

	scanUSB(out)

	# init motor controller serial
	mcu=SerialWrapper(MCU_PORT,MCU_BAUD,out,WATCHDOG_TIME,"MCU")
	# init pan tilt driver
	pantilt=LogiPanTilt(out)
	# init mcu driver

	# init motor driver

	### Exit handler

	def stop():
		out.write("WARN","Shutting Down",True)
		comms.close()
		mcu.close()
		stereo.stop()

	### Further setup and vars

	# create status variable
	status="STARTED"
	# store whether Arduino is powered
	powered=False

	# init comms watchdog timer
	# prevWatchdog=time.time()

	prevKeepalive=time.time()

	restart=False
	### Main Loop
	while restart==False:
		# MCU keepalive
		if time.time()-prevKeepalive>MCU_KEEPALIVE:
			mcu.write("T\n") # send test message 
			
		# Status LEDs
		prevStatus=status
		if mcu.connected:
			status="SERIAL_CONN"
			if comms.connected:
				status="SOCK_CONN"
				if powered:
					status="POWERED"
			else:
				status="STARTED"
		if status!=prevStatus:
			# led.dispHSV(*Status[status])
			pass

		# Update pan/tilt
		pantilt.run()

		# Fetch latest TCP messages
		data={}
		if comms.receive()>0:
			data=comms.read()
			for prefix,msg in data.items():
				out.write("LAPTOP",f"{prefix.ljust(6)}: {msg}",False)

		
		# Fetch latest commands from RC controller
		# rc.receive()
		# rc.process()
		# data.update(rc.commands)
		
		for prefix,msg in data.items():
			
			if 'PING' == prefix:
				out.write("ACK","Ping from laptop, forwarding to MCU")
				# screw.ping()
			if 'CAM_PAN' == prefix:
				pantilt.pan_speed(msg)
				# print(-msg)
			if 'CAM_TILT' == prefix:
				pantilt.tilt_speed(msg)
			if 'CAM_CENTRE' == prefix:
				pantilt.home()
			if 'CAM_MAST' == prefix:
				if msg>0:
					mcu.write("RAISE_MAST\n")
				elif msg<0:
					mcu.write("LOWER_MAST\n")
			if 'RESTART' == prefix:
				out.write("WARN","Restarting Rover Python Script")
				restart=True
			# if 'DRIVE' == prefix:
			# 	screw.drive(msg)
			# if 'TURN' == prefix:
			# 	screw.turn(msg)
			# if 'ROLL_R' == prefix:
			# 	screw.roll(msg)
			# if 'ROLL_L' == prefix:
			# 	screw.roll(msg)
			# if 'TURN_FORWARD' == prefix:
			# 	screw.turnForward(msg)
		
		# Fetch latest serial messages from MCU
		
		
		if mcu.receive()>0:
			line=mcu.read()
			# if len(line)>0:
			# 	out.write("MCU",line,True)
			# 	if "Motor power on" in line:
			# 		powered=True
			# 	elif "Motor power off" in line:
			# 		powered=False
	stop()
