
import socket
from struct import *
import math
import pantilthat

# Prepare the UDP connection
UDP_IP = "192.168.68.100"
print ("Receiver IP: " + str(UDP_IP))
UDP_PORT = 50000
print ("Port: "+ str(UDP_PORT))
sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

data,addr=sock.recvfrom(1024)
panstart=0
print(type(data))
#panstart= int(unpack_from('!f',data,36)[0])

# Continuously read from the UDP socket
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # The next line just chops a lot of floats from the received data chunk
    # Just activate and deactivate sensors in the Sensor UDP app to locate
    # the values you want
    

    
    data=str(data).replace("'","").replace("b","").replace(" ","").split(",")
    data=[float(i) for i in data]
    #print(data)
    gravity=0
    if len(data)>=18:
        gravity=data[20]
    if len(data)>=18:
        #print(data)
        yaw=data[14]
        pitch=data[16]
        if panstart==0:
            panstart=yaw
        print(f"yaw {yaw} pitch {pitch}")
        pan=(yaw)-panstart
        tilt=pitch-90
        if gravity<0:
            tilt=90-pitch
        tilt-=0
        print(f"pan {pan} tilt {tilt}")
        #print("pan"+str(pan)+"tilt"+str(tilt))
        if pan > 180:
            pan = pan-360
        pan = -min(90,max(-90,pan))
        tilt= min(90,max(-90,tilt))
        #print(data[20])
        pantilthat.pan(pan)
        pantilthat.tilt(tilt)
