#!/usr/bin/env python3
import time
from datetime import datetime
import subprocess
import os
import signal
import sys
import psutil

# USB and session folder setup
MOUNT_POINT = "/mnt/usb"
SESSION_FOLDER = os.path.join(MOUNT_POINT, "UrchinPOD")
LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")
USERNAME = "pi"

# Logging utility
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    os.makedirs(SESSION_FOLDER, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(formatted + "\n")

# Detect unmounted removable USB devices
def get_usb_devices():
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,MOUNTPOINT,RM,TYPE", "-nr"],
            stdout=subprocess.PIPE,
            check=True,
            text=True
        )
        devices = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 4:
                name, mountpoint, rm, dtype = parts[:4]
                if rm == "1" and dtype == "part" and not mountpoint:
                    devices.append(f"/dev/{name}")
        return devices
    except subprocess.CalledProcessError as e:
        print(f"Error detecting USB: {e}")
        return []

# Attempt to mount USB
def mount_usb(device, mount_point, user):
    try:
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)
        subprocess.run(
            ["sudo", "mount", device, mount_point, "-o", f"uid={user},gid={user}"],
            check=True
        )
        log(f"Mounted {device} to {mount_point}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error mounting USB: {e}")
        return False

# Check and auto-mount USB if needed
def ensure_usb_mounted():
    if os.path.ismount(MOUNT_POINT):
        log("USB already mounted.")
        return True

    log("USB not mounted. Searching for removable devices...")
    usb_devices = get_usb_devices()
    if not usb_devices:
        log("No USB devices found.")
        return False

    device = usb_devices[0]
    log(f"Attempting to mount {device} to {MOUNT_POINT}")
    if mount_usb(device, MOUNT_POINT, USERNAME):
        log("USB mounted successfully.")
        return True
    else:
        log("Failed to mount USB.")
        return False

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
if ensure_usb_mounted():
    half_hour_cycle()
    kill_stuck_camera_processes()
else:
    log("USB mount failed. Exiting.")
    sys.exit(1)
