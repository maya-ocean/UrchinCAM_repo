#!/bin/bash

# Check if drive is mounted. 
if ! mount | grep -q "/media/pi/URCHIN2"; then
    # Mount drive if not mounted.
    sudo mkdir -p /media/pi/URCHIN2
    sudo mount /dev/sda1 /media/pi/URCHIN2
fi

# Runs video recording in a loop 5 times.
for (( i=0; i<5; i++ )); do
echo "$i"
# Record 5 minute video segment. 
libcamera-vid -t 300000 -o "/media/pi/URCHIN2/video_$(date +%Y%m%d_%H%M%S).h264" --width 1280 --height 720 --bitrate 3000000 --inline --nopreview
sleep 10
done

# To run this script, navigate to its folder. 
# sudo chmod +x UrchinCAM_lib.sh
# sudo ./UrchinCAM_lib.sh




