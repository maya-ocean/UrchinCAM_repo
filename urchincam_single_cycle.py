#!/usr/bin/env python3
import time
from datetime import datetime
import subprocess
import os
import signal
import sys
import psutil

# Initial session folder setup (will update after mounting USB)
SESSION_FOLDER = None
LOG_FILE = None

# Logging utility
def log(message):
    global SESSION_FOLDER, LOG_FILE
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    # Only try to log if SESSION_FOLDER is set (after mount)
    if SESSION_FOLDER:
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

# Mount USB function
def mount_usb():
    usb_id_file = "/home/pi/usb_id.txt"
    mount_point = "/mnt/DATA"
    default_device = "sda1"
    user = "pi"
    group = "pi"

    # Ensure mount point exists
    os.makedirs(mount_point, exist_ok=True)

    usb_id = None
    if os.path.isfile(usb_id_file) and os.path.getsize(usb_id_file) > 0:
        with open(usb_id_file, "r") as f:
            usb_id = f.read().strip()
        if usb_id == "FULL":
            log("USBID is FULL, changing directory to mount point without mounting.")
            os.chdir(mount_point)
            return True  # Indicate mount point is usable
        else:
            device = f"/dev/{usb_id}"
    else:
        device = f"/dev/{default_device}"
        usb_id = default_device
        with open(usb_id_file, "w") as f:
            f.write(default_device)
    
    # Attempt to mount
    mount_cmd = [
        "sudo", "mount", device, mount_point, "-o", f"uid={user},gid={group}"
    ]
    try:
        subprocess.run(mount_cmd, check=True)
        log(f"Mounted {device} to {mount_point}")

        subprocess.run(["sudo", "chown", "-R", "pi:pi", mount_point], check = True)
    
    except subprocess.CalledProcessError as e:
        log(f"ERROR: Failed to mount {device} to {mount_point}: {e}")
        return False

    # Get USB name from blkid output
    try:
        blkid_out = subprocess.check_output(["sudo", "blkid"]).decode()
        for line in blkid_out.splitlines():
            if usb_id in line:
                # Try to extract something like sda1 or label
                usbname = line[18:23]
                log(f"USBNAME: {usbname}")
                break
    except Exception as e:
        log("ERROR: Could not get USBNAME from blkid: " + str(e))
    return True

# Start camera recording
def start_camera_recording(duration_secs):
    global SESSION_FOLDER
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
if __name__ == "__main__":
    # Mount USB first
    mounted = mount_usb()
    # Set session/log paths to USB only if mount succeeded
    if mounted:
        SESSION_FOLDER = "/mnt/DATA/UrchinPOD"
        LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")
    else:
        # Fallback to local storage if mount fails
        SESSION_FOLDER = "UrchinPOD"
        LOG_FILE = os.path.join(SESSION_FOLDER, "urchin_log.txt")
        log("[!] WARNING: USB not mounted, saving to local SD card.")

    half_hour_cycle()
    kill_stuck_camera_processes()
