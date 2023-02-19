from classes.SerialWrapper import SerialWrapper
from classes.Constrain import constrain

class command:
	# Movement Commands
	L_SPEED = '[' # set left side speed (tank controls)
	R_SPEED = ']' # set right side speed (tank controls)
	OFF = '#' # any unrecognised command will power off and set targets to zero
	# Configuration
	SET_MAX_SPEED = 'S' # change max speed
	SET_MAX_ACCEL = 'A' # change accel
	SET_MICROSTEP = 'M' # change microstep value
	# Watchdog
	SET_MAX_PING = 'O' # if -1 no ping required. otherwise after this interval with no ping, turn off
	PING = 'P' # returns a PING when called. append the target time between pings to get the latency

class ScrewTank:
    l_speed=0
    r_speed=0
    l_offset=0
    r_offset=0
    forwardTurn=False
    # set invert such that +ve on both drives vehicle forward
    def __init__(self,ser,maxSpeed,maxAccel,Microstep,maxPing,invertL=False,invertR=False):
        self.ser=ser
        self.invertL=invertL
        self.invertR=invertR
        self.write(command.SET_MAX_SPEED,maxSpeed)
        self.write(command.SET_MAX_ACCEL,maxAccel)
        self.write(command.SET_MICROSTEP,Microstep)
        self.write(command.SET_MAX_PING,maxPing)
    def ping(self):
        self.write(command.PING,1000)
    def write(self,command,value):
        self.ser.write(f"{command}{value}\n")
    def off(self):
        self.l_speed=0
        self.r_speed=0
        self.l_offset=0
        self.r_offset=0
        self.write(command.OFF,0)
    def setL(self):
        speed=self.l_speed+self.l_offset
        if self.invertL:
            speed=-speed
        constrain(speed,-255,255)
        self.write(command.L_SPEED,speed)
    def setR(self):
        speed=self.r_speed+self.r_offset
        if self.invertR:
            speed=-speed
        constrain(speed,-255,255)
        self.write(command.R_SPEED,speed)
    def drive(self,speed:int):
        self.l_speed=speed
        self.r_speed=speed
        self.setL()
        self.setR()
    def roll(self,speed:int):
        self.l_speed=speed
        self.r_speed=-speed
        self.setL()
        self.setR()
    def turnForward(self,mode:bool):
        self.forwardTurn=mode
    def turn(self,speed:int):
        if speed>0: # turn right
            if self.forwardTurn: # increase left speed
                self.l_offset=speed
                self.r_offset=0
            else:                # decrease right speed
                self.r_offset=speed
                self.l_offset=0
        if speed<0: # turn left
            if self.forwardTurn: # increase right speed
                self.l_offset=0
                self.r_offset=-speed
            else:                # decrease left speed
                self.r_offset=0
                self.l_offset=speed

