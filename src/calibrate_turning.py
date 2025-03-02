#!/usr/bin/env python3
"""
Calibration script for determining the TURN_CALIBRATION parameter.
This measures how long it takes for the robot to turn 90 degrees.
"""
import time
import signal
import sys
from rover.drivetrain import Drivetrain

# Default test parameters
TEST_ANGLE = 360       # Degrees to rotate for calibration
ANGULAR_SPEED = 100    # Angular speed setting (0-100)

def signal_handler(sig, frame, drivetrain):
    """Handles clean shutdown on Ctrl+C"""
    print("\nShutting down...")
    drivetrain.set_motion(angular_speed=0)
    sys.exit(0)

def calibrate_turning():
    """
    Run a calibration test to measure how long it takes for the robot
    to turn the specified angle at the given angular speed.
    """
    print("=== TURNING CALIBRATION TEST ===")
    print(f"This test will rotate the robot {TEST_ANGLE} degrees")
    print("You need a reference point to determine when the turn is complete")
    print("1. Place the robot on the floor with clear space around it")
    print("2. Mark or note the direction the front of the robot is facing")
    print(f"3. Calculate what {TEST_ANGLE}° looks like for reference")
    
    input("Press Enter when ready to start the test...")
    
    drivetrain = Drivetrain()
    
    # Set up signal handler for clean exit with Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drivetrain))
    
    # Ask for turning duration estimate
    initial_duration = float(input(f"Enter your initial guess for {TEST_ANGLE}° turn duration (seconds): "))
    
    while True:
        print("\nStarting turn test with duration:", initial_duration)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("Turning...")
        
        # Start turning
        drivetrain.set_motion(angular_speed=ANGULAR_SPEED)
        time.sleep(initial_duration)
        drivetrain.set_motion(angular_speed=0)
        
        # Get feedback
        result = input(f"\nDid the robot turn exactly {TEST_ANGLE} degrees? (y/n): ").lower()
        
        if result == 'y':
            # Calculate the turn calibration value (time for 90 degrees)
            if TEST_ANGLE == 90:
                turn_calibration = initial_duration
            else:
                turn_calibration = initial_duration * (90 / TEST_ANGLE)
                
            print("\n=== RESULTS ===")
            print(f"Turn duration for {TEST_ANGLE}°: {initial_duration:.3f} seconds")
            print(f"Calculated 90° turn duration: {turn_calibration:.3f} seconds")
            print("\nIn your navigate.py file, set:")
            print(f"TURN_CALIBRATION = {turn_calibration:.3f}    # Time in seconds for a 90° turn")
            break
        else:
            # Adjust the duration based on feedback
            feedback = input("Did it turn too far (f) or not far enough (n)? (f/n): ").lower()
            adjustment = float(input("By what factor should we adjust the time? (e.g., 0.8 for less, 1.2 for more): "))
            
            if feedback == 'f':
                initial_duration = initial_duration / adjustment
            else:
                initial_duration = initial_duration * adjustment
                
            print(f"Adjusted duration: {initial_duration:.3f} seconds")
    
    # Ask to run again
    run_again = input("\nRun another test? (y/n): ").lower()
    if run_again == 'y':
        calibrate_turning()

if __name__ == "__main__":
    try:
        # Allow custom angle parameter from command line
        if len(sys.argv) > 1:
            TEST_ANGLE = float(sys.argv[1])
        
        calibrate_turning()
    except KeyboardInterrupt:
        print("\nTest interrupted!")
    except Exception as e:
        print(f"Error: {e}")