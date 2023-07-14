# find available resolutions and framerates with libcamera-vid --list-cameras
# libcamera-vid -t 0 --inline --width 1296 --height 972 -o - | nc -k -l 8081

# Alternatively, using gst (could change sink to RTSP or RTC, however these seem quite slow)
libcamera-vid -t 0 --inline --width 1296 --height 972 -o - | gst-launch-1.0 fdsrc ! tcpserversink host=0.0.0.0 port=8081

# UDP requires recieving IP to be set manually unless multicast used (which requires firewall config)
# libcamera-vid -t 0 --inline --width 1296 --height 972 -o - | gst-launch-1.0 fdsrc ! udpsink host=RECEIVER_IP port=8081