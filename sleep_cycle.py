import os
import time
from datetime import datetime
import subprocess
import shutil

if shutil.which("libcamera-still"):
    CAMERA_CMD = "libcamera-still"
elif shutil.which("raspistill"):
    CAMERA_CMD = "raspistill"
else:
    print("ERROR: No camera command found. Please install raspberrypi-ui-mods package.")
    exit(1)

print(f"Starting camera capture script using {CAMERA_CMD}...")
print("Images will be saved in date-based folders")

try:
    with open('/sys/power/state', 'r') as f:
        SLEEP_STATES = f.read().strip().split()

    if 'mem' in SLEEP_STATES:
        SLEEP_STATE = 'mem'
    elif 'suspend' in SLEEP_STATES:
        SLEEP_STATE = 'suspend'
    else:
        print(f"Warning: No suitable sleep state found. Available states: {SLEEP_STATES}")
        SLEEP_STATE = None

    print(f"Using sleep state: {SLEEP_STATE if SLEEP_STATE else 'None - will use time.sleep() instead'}")
except:
    print("Warning: Could not determine available sleep states. Will use time.sleep() instead.")
    SLEEP_STATE = None

cycle_count = 0

try:
    while True:
        cycle_count += 1
        print(f"\n--- Cycle #{cycle_count} ---")

        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        daily_dir = f"./images/{date_str}"
        if not os.path.exists(daily_dir):
            print(f"Creating new directory for today: {daily_dir}")
            os.makedirs(daily_dir)

        image_path = f"{daily_dir}/image_{timestamp}.jpg"
        print(f"Capturing image to: {image_path}")

        if CAMERA_CMD == "libcamera-still":
            capture_cmd = f"{CAMERA_CMD} -n -o {image_path}"
        else:  # raspistill
            capture_cmd = f"{CAMERA_CMD} -n -o {image_path}"

        result = os.system(capture_cmd)

        if result == 0:
            print("✓ Image captured successfully")
        else:
            print(f"✗ Error capturing image, command returned: {result}")

        print("Syncing filesystem...")
        os.system("sync")

        print(f"Waiting for 60 seconds starting at {datetime.now().strftime('%H:%M:%S')}...")

        # Sleep using appropriate method
        if SLEEP_STATE:
            try:
                print(f"Entering {SLEEP_STATE} sleep state...")
                subprocess.run(["sudo", "rtcwake", "-m", SLEEP_STATE, "-s", "60"])
                print(f"Woke up at {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"Sleep error: {e}")
                print("Falling back to regular time.sleep()")
                time.sleep(60)
        else:
            # If no suitable sleep state, just use regular time.sleep
            time.sleep(60)

        # Buffer time
        print("Waiting for 2 seconds buffer time...")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nScript stopped by user")
except Exception as e:
    print(f"Error: {e}")
    raise
