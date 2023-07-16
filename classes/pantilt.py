import v4l2ctl
import time



class pantilt:
    def __init__(self):
        for camIndex in range(20):
            self.cam="/dev/video"+str(camIndex)
            self.settings=v4l2ctl.getCamSettings(self.cam)
            if "pan_relative" in self.settings:
                print(f"Found Orbit Sphere AF at {self.cam}")
                break
            if camIndex==20:
                print("Failed to find pantilt cam")
        self.home()
    def home(self):
        v4l2ctl.updateUVCsetting(self.cam,"pan_reset",1)
        v4l2ctl.updateUVCsetting(self.cam,"tilt_reset",-1)
        time.sleep(3)
        self.current_pan=0
        self.current_tilt=0
    def pan(self,value):
        v4l2ctl.updateUVCsetting(self.cam,"pan_relative",value)
        self.current_pan+=value
    def tilt(self,value):
        v4l2ctl.updateUVCsetting(self.cam,"tilt_relative",value)
        self.current_tilt+=value
    def panAngle(self,angle):
        self.pan(((4880*2)/180)*angle)
    def tiltAngle(self,angle):
        self.pan(((1920*2)/180)*angle)


sphereaf=pantilt()
sphereaf.home()
while True:
    for i in range(0,100):
        sphereaf.pan(100)
        time.sleep(0.05)
        sphereaf.tilt(-100)
        time.sleep(0.05)
    for i in range(0,100):
        sphereaf.pan(-100)
        time.sleep(0.05)
        sphereaf.tilt(100)
        time.sleep(0.05)



        


