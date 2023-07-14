
import socket
import time
import threading
import sys
import subprocess
from signal import signal, SIGINT

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder,H264Encoder,Encoder
from picamera2.outputs import FileOutput

IP="192.168.68.103"
global running
running=True

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    global running
    running=False

signal(SIGINT, handler)


cam_info=Picamera2.global_camera_info()


print(cam_info)
class Cam:
    c=None
    def __init__(self,idx,ip,port,width,height):
        self.idx=idx
        self.ip=ip
        self.port=port
        self.width=width
        self.height=height

cams=[
    Cam(0,"0.0.0.0",8081,1296,972),
    # Cam(1,IP,8082,640,480),
]


frameLimits=None
for cam in cams:
    if len(cam_info)>cam.idx:
        cam.c=Picamera2(cam.idx)
        config= cam.c.create_video_configuration({
            "size": (cam.width, cam.height),
            "format":"YUV420"
            })
        cam.c.configure(config)


def stream(cam):
    cam.c.start()
    # ffmpeg -i /dev/video1 -vcodec h264_v4l2m2m -f mpegts tcp://0.0.0.0:8082\?listen
    # gst-launch-1.0 -v fdsrc fd=0 ! udpsink host=192.168.68.103 port=8081
    command=['ffmpeg',
        '-hide_banner',
        '-f','rawvideo',
        '-video_size',f'{cam.width}x{cam.height}',
        '-pixel_format','yuv420p',
        '-i', '-',
        '-vcodec','h264_v4l2m2m',
        '-f', 'mpegts',      # Get rawvideo output format.
        f'tcp://{cam.ip}:{cam.port}\?listen']
    # command=['gst-launch-1.0',
    #          '-v','fdsrc','fd=0','!',
    #          'tcpserversink','host=0.0.0.0','port=8081']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    while(running):
        # print(process.stdout.readlines())
        frame=cam.c.capture_buffer()
        # print(len(frame))
        if len(frame)>0:
            try:
                process.stdin.write(frame)
            except:
                pass
        

threads=[]
for cam in cams:
    thread=threading.Thread(target=stream,args=(cam,),daemon=True)
    thread.start()
    threads.append(thread)

while running:
    time.sleep(1)
time.sleep(1)
sys.exit()