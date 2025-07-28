#!/bin/bash

# Set USB thumb drive name.
MOUNT_NAME="URCHIN2"

# Log output
exec > /home/pi/Urchin_log.txt 2>&1

# Runs video recording in a loop 5 times.
for (( i=0; i<5; i++ )); do
echo "$i"
# Record 5 minute video segment. 
libcamera-vid -t 300000 -o "/media/pi/$MOUNT_NAME/video_$(date +%Y%m%d_%H%M%S).h264" --width 1280 --height 720 --bitrate 3000000 --inline --nopreview
sleep 10
done

# After loop has completed, unmount the USB drive. 
lsblk
sync
sudo umount /media/pi/$MOUNT_NAME

# To run this script, navigate to its folder. 
# sudo chmod +x UrchinCAM_lib.sh
# sudo ./UrchinCAM_lib.sh




