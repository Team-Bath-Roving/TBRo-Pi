from classes.v4l2ctl import getCamSettings, updateUVCsetting
import time
import os
import subprocess
from Comms.Output import Output

# Determines usb ID for device with the given name
def find_usb_id(name="Orbit"):
        out = subprocess.Popen(['lsusb'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        out = stdout.decode('UTF-8').splitlines()
        for line in out:
            if name in line:
                ID=line[line.find("ID")+3:]
                ID=ID[:ID.find(" ")]
                return ID
        return None
# Finds the /dev/video path of a usb webcam given the usb id
def find_dev_path(usb_id):
    out = subprocess.Popen(['v4l2-ctl','--list-devices'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    out = stdout.decode('UTF-8').splitlines()
    for idx,line in enumerate(out):
        if usb_id in line:
            return out[idx+1].strip()
    return None

# A class to control a Logitech Sphere/Orbit AF
class LogiPanTilt:
    def __init__(self,output:Output):
        self.current_pan=0
        self.current_tilt=0
        self.output=output
        self.panspeed=0
        self.tiltspeed=0
        self.panInterval=0
        self.tiltInterval=0
        self.init=False
        self.usb_id=find_usb_id("Orbit")
        if not self.usb_id is None:
            self.path=find_dev_path(self.usb_id)
            if not self.path is None:
                
                output.write("INFO",f"Found Logitech Orbit/Sphere at {self.path} {self.usb_id}",True)
                self.settings=getCamSettings(self.path)
                if not "pan_relative" in self.settings:
                    output.write("INFO","Running Guvcview to add pan/tilt settings",True)
                    p=subprocess.Popen(['guvcview','-d',self.path],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                    time.sleep(5)
                    p.kill()
                    self.settings=getCamSettings(self.path)
                    if not "pan_relative" in self.settings:
                        output.write("ERROR","Failed to add pan/tilt settings, is guvcview installed?",True)
                    else:
                        self.init=True
                else:
                    self.init=True
                # self.home()
            else:
                output.write("ERROR","Failed to find Logitech Orbit/Sphere UVC /dev/video path",True)
        else:
            output.write("ERROR","Failed to find Logitech Orbit/Sphere USB ID",True)
    
    def send_command(self,command,value):
        if self.init:
            updateUVCsetting(self.path,command,value)
    def home(self):
        self.send_command("pan_reset",1)
        time.sleep(2)
        self.send_command("tilt_reset",0)
        time.sleep(2)
        self.current_pan=0
        self.current_tilt=0
    def pan(self,value):
        self.send_command("pan_relative",value)
        self.current_pan+=value
    def tilt(self,value):
        self.send_command("tilt_relative",value)
        self.current_tilt+=value
    def pan_angle(self,angle):
        self.pan(((4880*2)/180)*angle)
    def tilt_angle(self,angle):
        self.pan(((1920*2)/180)*angle)
    def pan_speed(self,speed):
        self.panspeed=speed
    def tilt_speed(self,speed):
        self.tiltspeed=speed
    def run(self):
        if self.panspeed!=0 and time.time()-self.panInterval>abs(1/self.panspeed):
            if self.panspeed>0:
                self.pan(100)
            if self.panspeed<0:
                self.pan(-100)
            self.panInterval=time.time()
        if self.tiltspeed!=0 and time.time()-self.tiltInterval>abs(1/self.tiltspeed):
            if self.tiltspeed>0:
                self.tilt(100)
            if self.tiltspeed<0:
                self.tilt(-100)
            self.tiltInterval=time.time()

# sphereaf=LogiPanTilt(Output())
# sphereaf.tilt(-1000)
# while True:
#     for i in range(0,1000):
#         sphereaf.pan(100)
#         time.sleep(i/1000.0)
#         # sphereaf.tilt(-100)
#         # time.sleep(0.05)0
#     for i in range(0,1000):
#         sphereaf.pan(-100)
#         time.sleep(i/1000.0)
#         # sphereaf.tilt(100)
#         # time.sleep(0.05)



        


