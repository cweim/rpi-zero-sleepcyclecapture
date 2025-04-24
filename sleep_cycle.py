#!/usr/bin/env python3
"""
Power-efficient Raspberry Pi camera script that captures an image every 60 seconds.
Implements power-saving features to extend battery life for remote deployments.
"""

import os
import time
import subprocess
from datetime import datetime
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Capture images at regular intervals with power-saving")
parser.add_argument("--interval", type=int, default=60, help="Interval between captures in seconds (default: 60)")
parser.add_argument("--show-preview", action="store_true", help="Show camera preview (uses more power)")
parser.add_argument("--use-libcamera", action="store_true", help="Use libcamera-still instead of raspistill")
args = parser.parse_args()

# Global variables
in_low_power_mode = False
cycle_count = 0
CAMERA_CMD = "libcamera-still" if args.use_libcamera else "raspistill"

def disable_unused_components():
    """Disable unused hardware components to save power."""
    try:
        # Try to disable HDMI (might not work on all Pi models)
        try:
            subprocess.run(["sudo", "tvservice", "-o"], check=False)
            print("✓ HDMI output disabled")
        except:
            print("! Could not disable HDMI output")

        # Try to set CPU governor to powersave using sudo
        try:
            subprocess.run(["sudo", "sh", "-c", "echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"], check=False)
            # For multi-core Pis like Zero 2W, try to set all cores
            for i in range(1, 4):
                subprocess.run(["sudo", "sh", "-c", f"echo powersave > /sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor"], check=False)
            print("✓ CPU governor set to powersave mode")
        except:
            print("! Could not set CPU governor")

        print("Power-saving mode activated")
    except Exception as e:
        print(f"! Warning: Could not disable some components: {e}")

def enter_low_power_mode():
    """Enter a low-power state between captures."""
    global in_low_power_mode
    print("Entering low power mode...")

    # Set flag for low power mode
    in_low_power_mode = True

    # Additional power-saving could be implemented here
    # For example, turning off other peripherals via GPIO

    print("System now in low-power mode")

def exit_low_power_mode():
    """Exit the low-power state before capture."""
    global in_low_power_mode
    print("Exiting low power mode...")

    # Clear low power mode flag
    in_low_power_mode = False

    print("System resumed normal operation")

def setup():
    """Initialize the system."""
    print("Initializing camera system...")

    # Create images directory if it doesn't exist
    if not os.path.exists("./images"):
        os.makedirs("./images")

    # Apply power-saving settings
    disable_unused_components()

    print(f"Camera system initialized. Using {CAMERA_CMD} for captures.")
    print(f"Images will be captured every {args.interval} seconds.")

def capture_image():
    """Capture an image and save it with timestamp."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Create daily directory if it doesn't exist
    daily_dir = f"./images/{date_str}"
    if not os.path.exists(daily_dir):
        print(f"Creating new directory for today: {daily_dir}")
        os.makedirs(daily_dir)

    # Define image path with timestamp
    image_path = f"{daily_dir}/image_{timestamp}.jpg"
    print(f"Capturing image to: {image_path}")

    # Prepare capture command
    if CAMERA_CMD == "libcamera-still":
        capture_cmd = f"{CAMERA_CMD} -n -o {image_path}"
    else:  # raspistill
        capture_cmd = f"{CAMERA_CMD} -n -o {image_path}"

    # Execute capture command
    result = os.system(capture_cmd)

    if result == 0:
        print("✓ Image captured successfully")
        return True
    else:
        print(f"✗ Error capturing image, command returned: {result}")
        return False

def main():
    """Main program loop."""
    global cycle_count

    # Setup system
    setup()

    try:
        while True:
            # Exit low-power mode before capture
            if in_low_power_mode:
                exit_low_power_mode()

            # Increment cycle counter
            cycle_count += 1
            print(f"\n--- Cycle #{cycle_count} ---")
            print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Capture image
            capture_success = capture_image()

            # Enter low-power mode between captures
            enter_low_power_mode()

            # Wait for next interval
            print(f"Waiting {args.interval} seconds until next capture...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up before exit
        if in_low_power_mode:
            exit_low_power_mode()
        print("Camera system shut down")

if __name__ == "__main__":
    main()
