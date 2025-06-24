#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import subprocess
import os
import signal
import sys

# Create log file on Raspberry Pi to track progress and errors.
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print (formatted)
    with open (LOG_FILE, "a") as f:
        f.write (formatted + "\n")

# Create folder for recordings and log
SESSION_FOLDER = "/mnt/usb/UrchinPOD"
os.makedirs(SESSION_FOLDER, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")

# Set duration of recording for a single on cycle
DURATION_MINS = 27

# Graceful exit flag and error handling.
should_exit = False

def signal_handler (sig, frame):
    global should_exit
    print ("[!] Received interrupt signal. Preparing to exit gracefully...")
    log ("[!] Received interrupt signal. Preparing to exit gracefully...")
    should_exit = True

signal.signal (signal.SIGINT, signal_handler)

# Start camera recording for given duration in seconds
def start_camera_recording(duration_secs):
    FRAME_RATE = 30
    WIDTH = 1280
    HEIGHT = 720
    BITRATE_Mbps = 3
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    h264_file = os.path.join(SESSION_FOLDER, f"video_{timestamp}.h264")

    print(f"[{timestamp}] Recording for {duration_secs} seconds → {h264_file}")
    log (f"Recording for {duration_secs} seconds → {h264_file}")
   
    command = [
        "libcamera-vid",
        "-t", str(duration_secs * 1000),
        "-o", h264_file,
        "--width", WIDTH,
        "--height", HEIGHT,
        "--framerate", FRAME_RATE,
        "--bitrate", str(BITRATE_Mbps * 1000000),
        "--inline",
        "--nopreview"
    ]

    try:
        subprocess.run(command, check=True)
        
    except subprocess.CalledProcessError as e:
        print (f"[{timestamp}] ERROR: Failed to record video.")
        print (f"[{timestamp}] Command:", e.cmd)
        print (f"[{timestamp}] Exit code:", e.returncode)
        log ("ERROR: Failed to record video.")
        log (f"Command: {e.cmd}")
        log (f"Exit code: {e.returncode}")

# Main loop
def half_hour_cycle():  
    duration_secs = DURATION_MINS * 60   
    start_camera_recording(duration_secs)
    print (f"[{datetime.now().strftime('%H:%M:%S')}] Video recorded.")
    log (f"[{datetime.now().strftime('%H:%M:%S')}] Video recorded.")
    time.sleep(10)

# Start the scheduler
half_hour_cycle ()
