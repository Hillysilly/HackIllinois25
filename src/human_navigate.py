#!/usr/bin/env python3
import time
import math
import signal
import sys

from rover.drivetrain import Drivetrain
from rover.sonar import Sonar

# Calibration constants (tweak these as needed)
ACTUAL_SPEED       = 0.335    # m/s at speed setting 100
FORWARD_SPEED      = 100      # Speed setting for forward motion
STRAFE_SPEED       = 100      # Speed setting for strafing
ACTUAL_STRAFE_SPEED = 0.305
OBSTACLE_THRESHOLD = 0.20      # m; trigger obstacle avoidance if an object is closer than this
CLEAR_THRESHOLD    = 0.25     # m; consider path clear if sensor reads at least this distance
FORWARD_STEP       = 0.01     # m; distance to move forward each step
TARGET_THRESHOLD   = 0.3      # m; target is reached if within this distance
TURN_CALIBRATION   = 1        # Time in seconds for a 90° turn (adjust based on testing)

# Global position and orientation variables
global x_position, y_position, current_angle_relative_to_x_axis
x_position = 0.0
y_position = 0.0
# Robot's "current_angle_relative_to_x_axis" is in degrees.
# Assuming the robot's front is initially aligned with 90° (i.e. positive y-axis)
current_angle_relative_to_x_axis = 90.0

drivetrain = Drivetrain()
sonar = Sonar()

def signal_handler(sig, frame):
    print("\nShutting down...")
    drivetrain.set_motion(speed=0, angular_speed=0)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def go_straight(num_meters):
    global x_position, y_position, current_angle_relative_to_x_axis
    # Command the robot to move with its current heading.
    drivetrain.set_motion(speed=FORWARD_SPEED, heading=90)
    time.sleep(num_meters / ACTUAL_SPEED)
    drivetrain.set_motion(speed=0)
    # Update the position assuming perfect motion
    rad = math.radians(current_angle_relative_to_x_axis)
    x_position += math.cos(rad) * num_meters
    y_position += math.sin(rad) * num_meters
    print("New position: ({:.2f}, {:.2f})".format(x_position, y_position))

def turn(angle):
    global x_position, y_position, current_angle_relative_to_x_axis
    if abs(angle) < 1:  # Ignore very small turns
        return
    print("Turning {:.2f} degrees".format(angle))
    if angle > 0:
        drivetrain.set_motion(angular_speed=100)
    else:
        drivetrain.set_motion(angular_speed=-100)
    # Duration is proportional to the absolute angle (90° -> TURN_CALIBRATION sec)
    duration = abs(angle) / 90 * TURN_CALIBRATION
    time.sleep(duration)
    drivetrain.set_motion(speed=0)
    current_angle_relative_to_x_axis = (current_angle_relative_to_x_axis + angle) % 360
    print("New orientation: {:.2f} degrees".format(current_angle_relative_to_x_axis))

def strafe_right(num_meters):
    global x_position, y_position, current_angle_relative_to_x_axis
    print("Strafing right for {:.2f} m".format(num_meters))
    drivetrain.set_motion(speed=STRAFE_SPEED, heading=0)
    time.sleep(num_meters / ACTUAL_STRAFE_SPEED)
    drivetrain.set_motion(speed=0)
    rad = math.radians(current_angle_relative_to_x_axis)
    x_position += math.sin(rad) * num_meters
    y_position -= math.cos(rad) * num_meters

def strafe_left(num_meters):
    global x_position, y_position, current_angle_relative_to_x_axis
    print("Strafing right for {:.2f} m".format(num_meters))
    drivetrain.set_motion(speed=STRAFE_SPEED, heading=180)
    time.sleep(num_meters / ACTUAL_STRAFE_SPEED)
    drivetrain.set_motion(speed=0)
    rad = math.radians(current_angle_relative_to_x_axis)
    x_position -= math.sin(rad) * num_meters
    y_position += math.cos(rad) * num_meters

def get_distance_to_target(target_x, target_y):
    global x_position, y_position, current_angle_relative_to_x_axis
    return math.hypot(target_x - x_position, target_y - y_position)

def read_ultrasonic():
    global x_position, y_position, current_angle_relative_to_x_axis
    try:
        distance = sonar.get_distance() * 0.001
        print("Ultrasonic reading: {:.2f} m".format(distance))
        return distance
    except Exception as e:
        print("Ultrasonic sensor error:", e)
        return 2.0

# Set target coordinates (one target)
target_x = 0.0
target_y = 3.0

# Main navigation loop: continue until the target is reached.
while get_distance_to_target(target_x, target_y) > TARGET_THRESHOLD:
    # Calculate desired angle (in degrees) from current position to target.
    delta_x = target_x - x_position
    delta_y = target_y - y_position
    desired_angle = math.degrees(math.atan2(delta_y, delta_x))
    # Compute the minimal turning angle (normalize to [-180,180])
    turn_angle = (desired_angle - current_angle_relative_to_x_axis + 180) % 360 - 180
    if turn_angle > 10:
        turn(turn_angle)
    
    # Check for obstacles using the ultrasonic sensor.
    if read_ultrasonic() < OBSTACLE_THRESHOLD:
        print("Obstacle detected!")
        # Strafe right in small increments until the path is clear.
        total_strafe_distance_right = 0
        while read_ultrasonic() < CLEAR_THRESHOLD:
            strafe_right(0.01)
            total_strafe_distance_right += 0.05
            if (read_ultrasonic() > CLEAR_THRESHOLD):
                strafe_right(0.1)
            if (total_strafe_distance_right >= 0.75):
                break
        if read_ultrasonic() < OBSTACLE_THRESHOLD:
            strafe_left(0.05)
            total_strafe_distance_left = 0
            while read_ultrasonic() < CLEAR_THRESHOLD:
                strafe_left(0.01)
                total_strafe_distance_left += 0.05
                if (read_ultrasonic() > CLEAR_THRESHOLD):
                    strafe_left(0.1)
                if (total_strafe_distance_left >= 1.5):
                    break
        
        if read_ultrasonic() < OBJECT_THRESHOLD:
            total_angle = 0
            angle = 20
            while total_angle <= 360 and read_ultrasonic() < OBSTACLE_THRESHOLD * 2:
                turn(angle)
            
    
    go_straight(FORWARD_STEP)


drivetrain.set_motion(speed=0)
print("Target reached!")
sys.exit(0)
