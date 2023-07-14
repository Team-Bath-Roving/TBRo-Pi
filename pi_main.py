### IMPORT LIBS

import atexit
import time

### IMPORT PROGRAM CLASSES

import socket
import classes.Constrain
from tbroLib.Comms import CommsServer
from classes.SerialWrapper import SerialWrapper, scanUSB
from classes.PanTilt import PanTilt,StatusNeopixel
from tbroLib.Output import Output
from classes.screwtank import ScrewTank
from classes.RadioControl import RadioControl
import sys
import serial.tools.list_ports

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
MCU_KEEPALIVE = 0.4 # if MCU doesn't recieve this it turns motors off
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
out=Output("LAPTOP")
out.toggleDisplayTypes(["PING","ACK","STATUS"],False)
# init TCP comms
comms=CommsServer(HOST_IP,PORTS,out,None,WATCHDOG_TIME)
# wait for TCP client
comms.connect()

scanUSB(out)

# init motor controller serial
mcu=SerialWrapper(None,MCU_BAUD,out,WATCHDOG_TIME,"MCU","USB Serial")
# init RC reciever serial
rcSer=SerialWrapper(None,RC_BAUD,out,WATCHDOG_TIME,"RC","HKT6A-V2 RX")
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

# init comms watchdog timer
# prevWatchdog=time.time()

prevKeepalive=time.time()




### Main Loop
while True:
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
		led.dispHSV(*Status[status])

	# Update pan/tilt
	pantilt.run()

	# Fetch latest TCP messages
	data={}
	if comms.receive()>0:
		data=comms.read()
		for prefix,msg in data.items():
			out.write("LAPTOP",f"{prefix.ljust(6)}: {msg}",False)

	
	# Fetch latest commands from RC controller
	rc.receive()
	rc.process()
	data.update(rc.commands)
	
	for prefix,msg in data.items():
		
		if 'PING' == prefix:
			out.write("ACK","Ping from laptop, forwarding to MCU")
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
	
	
	if mcu.receive()>0:
		line=mcu.read()
		if len(line)>0:
			out.write("MCU",line,True)
			if "Motor power on" in line:
				powered=True
			elif "Motor power off" in line:
				powered=False
