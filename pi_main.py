### IMPORT LIBS

import atexit
import time

### IMPORT PROGRAM CLASSES

import socket
import classes.Constrain
from classes.Comms import CommsServer
from classes.SerialWrapper import SerialWrapper
from classes.PanTilt import PanTilt,StatusNeopixel
from classes.Output import Output
from classes.screwtank import ScrewTank
from classes.RadioControl import RadioControl
import sys

### CONSTANTS
# Status colours     
Status = {
	"STARTED"     : (300 ,1,0.5),
	"SERIAL_CONN" : (200 ,1,0.5),
	"SOCK_CONN"   : (100 ,1,0.5),
	"POWERED"     : (0   ,0,1),
	"ERROR"       : (0   ,1,0.5),                                                                   
}

WATCHDOG_TIME = 5
# Network

# HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_IP = "0.0.0.0"
PORTS = [5000,5001,5432]

# Serial settings
MCU_PORT='/dev/ttyUSB0'
MCU_BAUD=9600
RC_PORT='/dev/ttyACM0'
RC_BAUD=115200

# Rover movement settings
MAX_SPEED = 2000
MAX_ACCEL = 1000
MICROSTEP = 4
MAX_PING = 2000
# Motor controller startup commands
INIT_COMMANDS=[	f"\nS{MAX_SPEED}\n",
				f"\nA{MAX_ACCEL}\n",
				f"\nM{MICROSTEP}\n"]

### Object instantiation

# init program output (TCP and bash)
out=Output()
# init TCP comms
comms=CommsServer(HOST_IP,PORTS,out,None)
# init motor controller serial
mcu=SerialWrapper(MCU_PORT,MCU_BAUD,out)
# init RC reciever serial
rcSer=SerialWrapper(RC_PORT,RC_BAUD,out)
# init RC reciever module
rc=RadioControl(rcSer,out)
# init pan tilt
pantilt=PanTilt(0.005) # update at 30Hz
# init status light
led=StatusNeopixel(0.05) # max brightness 20%
# init screwtank driver
screw=ScrewTank(mcu,MAX_SPEED,MAX_ACCEL,MICROSTEP,MAX_PING)

### Exit handler

def exit_handler():
		out.write("INFO","Shutting Down",False)
		pantilt.enabled(False)
		comms.close()
		mcu.close()
		led.off()
		sys.exit()
atexit.register(exit_handler)

### Further setup and vars

# create status variable
status="STARTED"
# store whether Arduino is powered
powered=False
# provide comms to output module
out.assignTCP(comms)
# wait for TCP client
comms.connect()
# init comms watchdog timer
prevWatchdog=time.time()

### Main Loop
while True:
	# Status
	if mcu.connected:
		status="SERIAL_CONN"
		if comms.connected:
			status="SOCK_CONN"
			if powered:
				status="POWERED"
	else:
		status="STARTED"
	led.dispHSV(*Status[status])
	
	# Connection watchdog
	if time.time()-prevWatchdog>WATCHDOG_TIME:
		prevWatchdog=time.time()
		comms.send({"PING":0})
		mcu.write("T\n")
		# rcSer.write("PING\n")
		# if input("Stop?")=='y':
		# 	comms.close()
		if not comms.connected:
			comms.connect()
		if not mcu.connected:
			mcu.connect()
		if not rcSer.connected:
			rcSer.connect()

	# Update pan/tilt
	pantilt.run()

	# Fetch latest TCP messages
	data={}
	comms.receive()
	if comms.available()>0:
		data=comms.read()
		for prefix,msg in data.items():
			out.write("LAPTOP",f"{prefix.ljust(6)}: {msg}",False)
			
	# Fetch latest commands from RC controller
	rc.receive()
	rc.process()
	data.update(rc.commands)
	
	for prefix,msg in data.items():
		
		if 'PING' == prefix:
			comms.send({"ACK":"Pi"})
			screw.ping()
		if 'CAM_PAN' == prefix:
			pantilt.pan_speed(-msg)
			# print(-msg)
		if 'CAM_TILT' == prefix:
			pantilt.tilt_speed(-msg)
		if 'CAM_CENTRE' == prefix:
			pantilt.pan_toward(0)
			pantilt.tilt_toward(0)
		if 'DRIVE' == prefix:
			screw.drive(msg)
		if 'TURN' == prefix:
			screw.turn(msg)
		if 'ROLL_R' == prefix:
			screw.roll(msg)
		if 'ROLL_L' == prefix:
			screw.roll(msg)
		if 'TURN_FORWARD' == prefix:
			screw.turnForward(msg)

	# Fetch latest serial messages from MCU
	mcu.receive()
	if mcu.available()>0:
		line=mcu.read()
		out.write("MCU",line)
		if "Motor power on" in line:
			powered=True
		elif "Motor power off" in line:
			powered=False
