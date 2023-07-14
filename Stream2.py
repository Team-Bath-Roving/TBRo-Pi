
import socket
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

from signal import signal, SIGINT
running=True
picam2 = Picamera2()
video_config = picam2.create_video_configuration({
    "size": (1296, 972)},)
picam2.configure(video_config)
encoder = H264Encoder(bitrate=1000000,repeat=True,iperiod=5)

def handler(signal_received,frame):
    picam2.stop_recording()
    running=False

signal(SIGINT, handler)


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.connect(("192.168.68.103", 8081))
    stream = sock.makefile("wb")
    picam2.start_recording(encoder, FileOutput(stream))
    while(running):
        time.sleep(1)
        # for i in range(0,320):
        #     time.sleep(1)
        #     picam2.set_controls({"Contrast":i/10})
