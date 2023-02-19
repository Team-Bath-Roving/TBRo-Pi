while true
do
libcamera-vid -t 0 --inline --listen --shutter 16666 --width 1920 --height 1080 --framerate 30 --bitrate 1000000  -o tcp://0.0.0.0:8080
done
