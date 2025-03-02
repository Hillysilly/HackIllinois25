#!/usr/bin/env python3
"""
Calibration script for determining the ACTUAL_SPEED parameter.
This measures how fast the robot moves (in m/s) when set to speed 100.
"""
import time
import signal
import sys
from rover.drivetrain import Drivetrain

# Default test parameters
TEST_DISTANCE = 1.78  # meters to travel for test
TEST_SPEED = 100     # speed setting to use (0-100)

def signal_handler(sig, frame, drivetrain):
    """Handles clean shutdown on Ctrl+C"""
    print("\nShutting down...")
    drivetrain.set_motion(speed=0, heading=90)
    sys.exit(0)

def calibrate_speed():
    """
    Run a calibration test to measure the robot's actual speed when
    set to a specific speed setting.
    """
    print("=== SPEED CALIBRATION TEST ===")
    print(f"This test will run the robot forward at speed {TEST_SPEED}")
    print(f"Place the robot at the start of a {TEST_DISTANCE}m measured course")
    print("The test will measure how long it takes to travel this distance")
    
    input("Press Enter when ready to start the test...")
    
    drivetrain = Drivetrain()
    
    # Set up signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drivetrain))
    
    # Record start time and begin moving
    start_time = time.time()
    drivetrain.set_motion(speed=TEST_SPEED, heading=90)  # Forward movement
    
    input("Press Enter IMMEDIATELY when robot reaches the end marker...")
    drivetrain.set_motion(speed=0)  # Stop the robot
    
    # Calculate elapsed time and speed
    elapsed_time = time.time() - start_time
    actual_speed = TEST_DISTANCE / elapsed_time
    
    print("\n=== RESULTS ===")
    print(f"Distance: {TEST_DISTANCE} meters")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Calculated speed: {actual_speed:.3f} m/s")
    print("\nIn your navigate.py file, set:")
    print(f"ACTUAL_SPEED = {actual_speed:.3f}    # m/s at speed setting {TEST_SPEED}")
    
    # Run multiple tests for consistency
    run_again = input("\nRun another test? (y/n): ").lower()
    if run_again == 'y':
        calibrate_speed()

if __name__ == "__main__":
    try:
        # Allow custom distance parameter from command line
        if len(sys.argv) > 1:
            TEST_DISTANCE = float(sys.argv[1])
        
        calibrate_speed()
    except KeyboardInterrupt:
        print("\nTest interrupted!")
    except Exception as e:
        print(f"Error: {e}")