import time
from datetime import datetime
from picamera2 import Picamera2

TOTAL_HOURS = 1
SEGMENT_MINS = 10
thismany = (TOTAL_HOURS * 60) / SEGMENT_MINS

cam = Picamera2()

cam.video_configuration.controls.FrameRate = 30.0

for i in range(thismany):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        cam.start_and_record_video(f"{timestamp}.mp4", duration=6*60)

    except KeyboardInterrupt:
        break
    
    finally:
        cam.stop_recording()
