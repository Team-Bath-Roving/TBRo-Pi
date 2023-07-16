import pantilthat
import colorsys
import time
from classes.Constrain import constrain

class PanTiltHat:
	pan=0 # current pos
	tilt=0
	target_pan=0 # target pos
	target_tilt=0
	pan_rate=50 # speed to move to target pos
	tilt_rate=50
	interval=0.05 
	pan_continuous=False
	tilt_continuous=False
	pan_velocity=0
	tilt_velocity=0
	accel=0.01
	pan_velocity_current=0
	tilt_velocity_current=0
	# init sets update interval in seconds
	def __init__(self,interval):
		self.interval=interval
		self.prevInterval=time.time()
		self.enabled(True)
		self.run()
	def enabled(self,state=True):
		pantilthat.servo_enable(1,state)
		pantilthat.servo_enable(2,state)
	# move to set angles. call as fast as possible
	def pan_accelerate(self,target):
		if self.pan_velocity_current<target:
			if target > 0:
				self.pan_velocity_current+=self.accel
				self.pan_velocity_current=constrain(self.pan_velocity_current,-180,target)
			else:
				self.pan_velocity_current=0
		elif self.pan_velocity_current>target:
			if target < 0:
				self.pan_velocity_current-=self.accel
				self.pan_velocity_current=constrain(self.pan_velocity_current,target,180)
			else:
				self.pan_velocity_current=0
	def tilt_accelerate(self,target):
		if self.tilt_velocity_current<target:
			if target > 0:
				self.tilt_velocity_current+=self.accel
				self.tilt_velocity_current=constrain(self.tilt_velocity_current,-180,target)
			else:
				self.tilt_velocity_current=0
		elif self.tilt_velocity_current>target:
			if target < 0:
				self.tilt_velocity_current-=self.accel
				self.tilt_velocity_current=constrain(self.tilt_velocity_current,target,180)
			else:
				self.tilt_velocity_current=0
	def run(self):
		if time.time()-self.prevInterval>self.interval:
			self.prevInterval=time.time()
			if self.pan_continuous:
				self.pan_accelerate(self.pan_velocity)
			elif self.pan!=self.target_pan:
				if self.pan < self.target_pan:
					self.pan_accelerate(self.pan_rate)
				elif self.pan > self.target_pan:
					self.pan_accelerate(-self.pan_rate)
				else:
					self.pan_accelerate(0)
			if self.tilt_continuous:
				self.tilt_accelerate(self.tilt_velocity)
			elif self.tilt!=self.target_tilt:
				if self.tilt < self.target_tilt:
					self.tilt_accelerate(self.tilt_rate)
				elif self.tilt > self.target_tilt:
					self.tilt_accelerate(-self.tilt_rate)
				else:
					self.tilt_accelerate(0)
			self.pan+=self.pan_velocity_current
			self.pan=constrain(self.pan,-90,90)
			self.tilt+=self.tilt_velocity_current
			self.tilt=constrain(self.tilt,-90,90)
			pantilthat.pan(self.pan)
			pantilthat.tilt(self.tilt)
	# move instantly to an angle at next interval
	def set_pan(self,angle):
		self.pan_continuous=False
		angle=constrain(angle,-90,90)
		self.pan=angle
		self.target_pan=angle
	def set_tilt(self,angle):
		self.tilt_continuous=False
		angle=constrain(angle,-90,90)
		self.tilt=angle
		self.target_tilt=angle
	# move at a set rate to an angle
	def pan_toward(self,angle,rate=-1):
		self.pan_continuous=False
		angle=constrain(angle,-90,90)
		self.target_pan=angle
		if rate!=-1:
			self.set_pan_rate(rate)
	def tilt_toward(self,angle,rate=-1):
		self.tilt_continuous=False
		angle=constrain(angle,-90,90)
		self.target_tilt=angle
		if rate!=-1:
			self.set_tilt_rate(rate)
	# set rate of change
	def set_pan_rate(self,rate):
		self.pan_rate=constrain(rate,0,90)
	def set_tilt_rate(self,rate):
		self.tilt_rate=constrain(rate,0,90)
	def set_accel(self,accel):
		self.accel=accel
	# instantly change angle by an amount at next interval
	def pan(self,angle):
		self.pan_continuous=False
		self.set_pan(self.pan+angle)
	def tilt(self,angle):
		self.tilt_continuous=False
		self.set_tilt(self.tilt+angle)
	def pan_speed(self,angle):
		self.pan_velocity=angle
		self.pan_continuous=True
	def tilt_speed(self,angle):
		self.tilt_continuous=True
		self.tilt_velocity=angle

# wrapper class for neopixel functions
class StatusNeopixel:
	H=0
	S=0
	V=0
	def __init__(self,max_val=0.2):
		self.max_val=constrain(max_val,0,1)
		pantilthat.light_mode(1)
		pantilthat.light_type(0)
	def dispHSV(self,h,s=1,v=1):
		if h!=self.H and s!=self.S and v!=self.V:
			h=constrain(h,0,360)
			s=constrain(s,0,1)
			v=constrain(v,0,1)*self.max_val
			self.h,self.s,self.v=h,s,v
			R,G,B = [int(x*255) for x in  colorsys.hsv_to_rgb((h) / 360.0, s, v)]
			pantilthat.set_all(R,G,B)
			pantilthat.show()
	def off(self):
		self.dispHSV(0,0,0)
