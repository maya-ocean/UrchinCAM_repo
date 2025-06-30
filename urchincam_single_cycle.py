#!/usr/bin/env python3
import time
from datetime import datetime
import subprocess
import os
import signal
import sys
import psutil

# Session folder setup
SESSION_FOLDER = "UrchinPOD"
LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")

# Logging utility
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    os.makedirs(SESSION_FOLDER, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(formatted + "\n")

# Graceful exit
should_exit = False
def signal_handler(sig, frame):
    global should_exit
    log("[!] Received interrupt signal. Preparing to exit gracefully...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

# Start camera recording
def start_camera_recording(duration_secs):
    FRAME_RATE = 30
    WIDTH = 1280
    HEIGHT = 720
    BITRATE_Mbps = 3
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    h264_file = os.path.join(SESSION_FOLDER, f"video_{timestamp}.h264")

    log(f"Recording for {duration_secs} seconds → {h264_file}")
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
        log("ERROR: Failed to record video.")
        log(f"Command: {e.cmd}")
        log(f"Exit code: {e.returncode}")

# Kill stuck libcamera processes
def kill_stuck_camera_processes():
    camera_processes = ["libcamera-vid"]
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(
                cam_proc in (proc.info['name'] or '') or
                any(cam_proc in (cmd or '') for cmd in (proc.info['cmdline'] or []))
                for cam_proc in camera_processes):
                if proc.pid != os.getpid():
                    proc.terminate()
                    log(f"Killed stuck process: {proc.info['name']} (PID {proc.pid})")
                    killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not killed:
        log("No stuck camera processes found.")

# Run the recording cycle
def half_hour_cycle():
    DURATION_MINS = 27
    duration_secs = DURATION_MINS * 60
    start_camera_recording(duration_secs)
    log("Video recorded.")
    time.sleep(10)

# -------- Main Execution --------
half_hour_cycle()
kill_stuck_camera_processes()

