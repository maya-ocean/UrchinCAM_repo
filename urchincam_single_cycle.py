#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import subprocess
import os
import signal
import sys

# USB mount point
MOUNT_POINT = "/mnt/usb"
SESSION_FOLDER = os.path.join(MOUNT_POINT, "UrchinPOD")
LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")
    
# Create log file on Raspberry Pi to track progress and errors.
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted = f"[{timestamp}] {message}"
    print (formatted)
    with open (LOG_FILE, "a") as f:
        f.write (formatted + "\n")

# Check if USB is mounted.
def is_mounted():
    return os.path.ismount(MOUNT_POINT)

# Exit if USB is not mounted
if not is_mounted():
    log ("USB is not mounted. Exiting.")
    exit(1)
         
# Create folder for recordings and log
os.makedirs(SESSION_FOLDER, exist_ok=True)

# Set duration of recording for a single on cycle
DURATION_MINS = 27

# Graceful exit flag and error handling.
should_exit = False

def signal_handler (sig, frame):
    global should_exit
    log ("[!] Received interrupt signal. Preparing to exit gracefully...")
    should_exit = True

signal.signal (signal.SIGINT, signal_handler)

# Start camera recording for given duration in seconds
def start_camera_recording(duration_secs):
    FRAME_RATE = 30
    WIDTH = 1280
    HEIGHT = 720
    BITRATE_Mbps = 3
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    h264_file = os.path.join(SESSION_FOLDER, f"video_{timestamp}.h264")

    log (f"Recording for {duration_secs} seconds → {h264_file}")
   
    command = [
        "libcamera-vid",
        "-t", str(duration_secs * 1000),
        "-o", h264_file,
        "--width", str(WIDTH),
        "--height", str(HEIGHT),
        "--framerate", str(FRAME_RATE),
        "--bitrate", str(BITRATE_Mbps * 1000000),
        "--inline",
        "--nopreview"
    ]

    try:
        subprocess.run(command, check=True)
        
    except subprocess.CalledProcessError as e:
        log ("ERROR: Failed to record video.")
        log (f"Command: {e.cmd}")
        log (f"Exit code: {e.returncode}")

# Main loop
def half_hour_cycle():  
    duration_secs = DURATION_MINS * 60   
    start_camera_recording(duration_secs)
    log (f"[{datetime.now().strftime('%H-%M-%S')}] Video recorded.")
    time.sleep(10)

# Start the scheduler
half_hour_cycle ()
