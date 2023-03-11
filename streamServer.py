from picamera2 import Picamera2
from picamera2.encoders import H264Encoder,Encoder,JpegEncoder,MJPEGEncoder
from picamera2.outputs import FfmpegOutput,FileOutput


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


picamYUV = Picamera2(0)
picamMJPEG = Picamera2(1)

video_configYUV = picamYUV.create_video_configuration()
picamYUV.configure(video_configYUV)
video_configMJPEG = picamMJPEG.create_video_configuration({"format": "MJPEG"})
picamMJPEG.configure(video_configMJPEG)

encoderh264 = H264Encoder(repeat=True, iperiod=15)
# encoderNull= Encoder()

outputH264 = FfmpegOutput("-f mpegts tcp://0.0.0.0:8081")
outputMJPEG = FfmpegOutput("-f mjpeg tcp://0.0.0.0:8082")

encoderh264.output=outputH264
# encoderNull.output=outputMJPEG

# picamYUV.start_recording(encoderh264,outputH264)
picamMJPEG.start_recording(MJPEGEncoder(),outputMJPEG)
# outputMJPEG.start()


while input():
    print("s")

