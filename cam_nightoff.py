import time
from datetime import datetime
from picamera2 import Picamera2

TOTAL_HOURS = 72
SEGMENT_MINS = 10
DAWN = 6
DUSK = 19
thismany = int((TOTAL_HOURS * 60) / SEGMENT_MINS)

cam = Picamera2()

cam.video_configuration.controls.FrameRate = 30.0

try:
    for i in range(thismany):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        hour = now.hour

        # Record video segments during daylight hours
        if DAWN <= hour <= DUSK:
            cam.start_and_record_video(f"{timestamp}.mp4", duration=SEGMENT_MINS*60)
        # Sleep for duration and then try again during nighttime
        else:
            time.sleep (SEGMENT_MINS*60)

except KeyboardInterrupt:
    break

# Stop recording after TOTAL_HOURS
finally:
    cam.stop_recording()
