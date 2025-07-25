#!/bin/bash
mount /dev/... /mnt/path
ffmpeg -f v4l2 -frame 30 -video_size 1280x720 -i /dev/video0 -t 300 /mnt/path/output.mp4
shutdown -P now

