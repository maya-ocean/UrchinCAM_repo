#!/bin/bash

# Log output
exec > /home/pi/Urchin_log.txt 2>&1

# Check if drive exists
if [ ! -e /dev/sda1 ]; then
    echo "/dev/sda1 not found. Exiting."
    exit 1
fi

# Check if drive is mounted. 
if ! mount | grep -q "/media/pi/URCHIN2"; then
    # Mount drive if not mounted.
    sudo mkdir -p /media/pi/URCHIN2
    # The below line will only work if the drive is read by the pi as sda1. Make sure to only have one drive in the pi at a time.
    sudo mount /dev/sda1 /media/pi/URCHIN2
fi

# Runs video recording in a loop 5 times.
for (( i=0; i<5; i++ )); do
echo "$i"
# Record 5 minute video segment. 
libcamera-vid -t 300000 -o "/media/pi/URCHIN2/video_$(date +%Y%m%d_%H%M%S).h264" --width 1280 --height 720 --bitrate 3000000 --inline --nopreview
sleep 10
done

# After loop has completed, unmount the USB drive. 
lsblk
sync
sudo umount /media/pi/URCHIN2

# To run this script, navigate to its folder. 
# sudo chmod +x UrchinCAM_lib.sh
# sudo ./UrchinCAM_lib.sh




