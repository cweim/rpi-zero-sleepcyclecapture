import os
import time
from datetime import datetime
import subprocess
import sys

# Function to check available sleep states
def check_sleep_states():
    try:
        with open('/sys/power/state', 'r') as f:
            states = f.read().strip().split()
        print(f"Available sleep states: {states}")
        return states
    except Exception as e:
        print(f"Error reading sleep states: {e}")
        return []

# Function to test a specific sleep state
def test_sleep_state(state, duration=10):
    print(f"\nTesting '{state}' sleep state for {duration} seconds...")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Entering {state} state...")

    try:
        # Execute rtcwake with the specified state
        subprocess.run(["sudo", "rtcwake", "-m", state, "-s", str(duration)], check=True)

        # If we get here, the sleep and wake worked
        wake_time = datetime.now().strftime('%H:%M:%S')
        print(f"Successfully woke up at {wake_time}")
        print(f"✓ {state} sleep state works!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to use {state} sleep state: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error with {state} sleep state: {e}")
        return False

# Main test function
def main():
    print("=== Raspberry Pi Low-Power State Tester ===")

    # Check available states
    available_states = check_sleep_states()

    if not available_states:
        print("ERROR: No sleep states found. Your system may not support any low-power modes.")
        sys.exit(1)

    # States to test in order of preference (most power saving first)
    test_states = ['mem', 'standby', 'freeze', 'disk']

    # Filter to only test available states
    states_to_test = [state for state in test_states if state in available_states]

    if not states_to_test:
        print("ERROR: None of the known low-power states are available on this system.")
        print("Available states are:", available_states)
        print("But these are not recognized as standard low-power states.")
        sys.exit(1)

    # Test each available state
    working_states = []

    for state in states_to_test:
        if test_sleep_state(state):
            working_states.append(state)

    # Summary
    print("\n=== Sleep State Test Results ===")
    if working_states:
        print(f"Working sleep states: {', '.join(working_states)}")
        print(f"Recommended state to use: {working_states[0]} (most power efficient)")

        # Test the recommended state with a longer duration
        print("\nFinal test of recommended state...")
        test_sleep_state(working_states[0], 30)
    else:
        print("No working sleep states found.")
        print("Your system may not support proper low-power modes.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
