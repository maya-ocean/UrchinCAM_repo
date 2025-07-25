#!/bin/bash
sudo mount /dev/sda1 /media/pi/URCHIN2
libcamera-vid -t 300000 -o "/media/pi/URCHIN2/video_$(date +%Y%m%d_%H%M%S).mp4" --width 1280 --height 720 --bitrate 3000000 --inline --nopreview
