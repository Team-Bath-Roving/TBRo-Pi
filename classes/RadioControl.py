from classes.SerialWrapper import SerialWrapper
from classes.Output import Output
from classes.Constrain import constrain
import json

# map channel to command, centre, deadzone, range
mapping = {
    # "LeftX":("ROLL_R",90,5,255),
    # "LeftY":("DRIVE",90,5,255),
    "RightX":("CAM_PAN",90,5,15),
    "RightY":("CAM_TILT",90,5,15),
    # "LeftDial":("TURN",0,5,255),
}


class RadioControl:
    channels={}
    commands={}
    mode=1 # 0 is inactive, 1 is drive + cam, 2 is payload control
    def __init__(self,ser,output:Output):
        self.output=output
        self.ser=ser
    def receive(self):
        self.channels={}
        self.ser.receive()
        while self.ser.available()>0:
            line=self.ser.read()
            # self.output.write("RC",line,false)
            # print(line)
            self.channels.update(json.loads(line.rstrip()))
            # print(self.channels)
    def process(self):
        self.commands={}
        if "RightDial" in self.channels:
            if self.channels["RightDial"] > 90:
                self.mode=1
            else:
                self.mode=0
        if self.mode==1:
            for channel,rawvalue in self.channels.items():
                if channel in mapping:
                    command=mapping[channel][0]
                    centre=mapping[channel][1]
                    deadzone=mapping[channel][2]
                    multiplier=mapping[channel][3]
                    value=rawvalue-centre
                    if value < 0-deadzone/2 or value > 0+deadzone/2:
                        value=value/90
                        value=value*multiplier
                        constrain(value,-multiplier,multiplier)
                    else:
                        value=0
                    self.commands.update({command:value})
                    self.output.write("RC",f"{command.ljust(6)}: {value}",False)

                