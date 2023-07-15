import socket
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput


# class stream:
#     process=None
#     def __init__(self,port,format,width,height):
#         self.port=port
#         self.format=format
#         self.width=width
#         self.height=height
#     def start(self):
#         command = ['gst-launch-1.0',
#             '-v',
#             'fdsrc', 'fd=0',
#             '!','tcpserversink',
#             'host=0.0.0.0',
#             f'port={port}']
#         try:
#             self.process.kill()
#         except:
#             pass
#         self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#     def stop(self):
#         self.process.stdin.close()  # Closing stdout terminates  sub-process.
#         self.process.wait()  # Wait for sub-process to finish
#     def running(self):
#         if not self.process.poll() is None:
#             return False
#         else:
#             return True
#     def framerate(self): #! TODO: make this return the output framerate somehow, so we can restart if it is too low
#         return 1
#     def write(self,data):
#         self.process.stdin.write(data)




# # num_cams=len(camera_list)

# class camera:
#     cam=None
#     usb=False
#     def __init__(self,model):
#         # List available devices
#         cam_list=Picamera2.global_camera_info()
#         for idx,camera in enumerate(cam_list):
#             # Find camera with corresponding model name
#             if model in camera["Model"]:
#                 # Determine if CSI or USB (YUV or MJPEG)
#                 if "usb" in camera["Id"]:
#                     usb=True
#                 # Initialise camera
#                 cam=Picamera2(idx)


from signal import signal, SIGINT
running=True
stereo = Picamera2(0)
stereo_config = stereo.create_video_configuration({
    "size": (1296, 972)},)
stereo.configure(stereo_config)
# pantilt = Picamera2(0)
# pantilt_config = pantilt.create_video_configuration({
#     "size": (640,480)},
#     "format":"YUYV"
#     )
# pantilt.configure(pantilt_config)
encoder = H264Encoder(bitrate=1000000,repeat=True,iperiod=5)

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007


stereo_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
stereo_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
# pantilt_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stereo_sock.connect((MCAST_GRP, MCAST_PORT))
stream = stereo_sock.makefile("wb")
stereo.start_recording(encoder, FileOutput(stream))
# pantilt_sock.connect(("192.168.68.103", 8082))
# stream = pantilt_sock.makefile("wb")
# pantilt_sock.start_recording(encoder, FileOutput(stream))

while(running):
    time.sleep(1)


def handler(signal_received,frame):
    # stereo.stop_recording()
    pantilt.stop_recording()
    stereo_sock.close()
    
    running=False

signal(SIGINT, handler)