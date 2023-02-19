
import socket
from struct import *

import pantilthat

# Prepare the UDP connection
UDP_IP = "192.168.1.99"
print ("Receiver IP: " + str(UDP_IP))
UDP_PORT = 50000
print ("Port: "+ str(UDP_PORT))
sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

data,addr=sock.recvfrom(1024)
global panstart

panstart= int(unpack_from('!f',data,36)[0])

# Continuously read from the UDP socket
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # The next line just chops a lot of floats from the received data chunk
    # Just activate and deactivate sensors in the Sensor UDP app to locate
    # the values you want
    
    pan=int(unpack_from('!f', data, 36)[0])#-panstart
    tilt=abs(int(int(unpack_from('!f', data,44)[0])))-90
    print("pan"+str(pan)+"tilt"+str(tilt))
    pan = -min(90,max(-90,pan))
    tilt= min(90,max(-90,tilt))

    pantilthat.pan(pan)
    pantilthat.tilt(tilt)
