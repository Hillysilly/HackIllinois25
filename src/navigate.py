#!/usr/bin/env python3
import time
import math
import signal
import sys

from rover.drivetrain import Drivetrain
from rover.sonar import Sonar

# Calibration constants (tweak these as needed)
ACTUAL_SPEED       = 0.172    # m/s at speed setting 100
FORWARD_SPEED      = 100     # Speed setting for forward motion
STRAFE_SPEED       = 100     # Speed setting for strafing
OBSTACLE_THRESHOLD = 0.2     # m; trigger obstacle avoidance if an object is closer than this
CLEAR_THRESHOLD    = 0.3     # m; consider path clear if sensor reads at least this distance
FORWARD_STEP       = 0.2     # m; distance to move forward each step
TARGET_THRESHOLD   = 0.1     # m; target is reached if within this distance
MAX_STRAFE_ATTEMPTS = 10     # Maximum number of strafe attempts before trying a different strategy
TURN_CALIBRATION   = 1     # Time in seconds for a 90° turn (adjust based on testing)
# turn speed = 4 seconds for 360 degrees

def read_ultrasonic(sonar, attempts=3):
    """
    Reads the ultrasonic sensor with error handling.
    Takes multiple readings and returns their average to reduce noise.
    """
    distances = []
    for _ in range(attempts):
        try:
            distance = sonar.get_distance()
            if 0.01 < distance < 4.0:  # Reasonable range check
                distances.append(distance)
            time.sleep(0.01)  # Short delay between readings
        except Exception as e:
            print(f"Sensor reading error: {e}")
    
    if not distances:
        print("Warning: No valid sensor readings obtained, assuming path is clear")
        return 2.0  # Default safe value
    
    avg_distance = sum(distances) / len(distances)
    print(f"Ultrasonic reading: {avg_distance:.2f} m")
    return avg_distance

def turn(drivetrain, angle_deg, current_heading):
    """
    Turns the robot by a specified angle (in degrees) using a fixed turning rate.
    Includes a small pause after turning to stabilize.
    Returns the new heading.
    """
    if abs(angle_deg) < 3:  # Ignore very small turns
        return current_heading
    
    angular_speed = 100  # Slightly reduced for better accuracy
    direction = 1 if angle_deg > 0 else -1
    duration = abs(angle_deg) / 90 * TURN_CALIBRATION
    
    print(f"Turning {angle_deg:.2f}° from heading {current_heading:.2f}°")
    drivetrain.set_motion(angular_speed=angular_speed * direction)
    time.sleep(duration)
    drivetrain.set_motion(angular_speed=0)
    time.sleep(0.1)  # Short pause to stabilize
    
    new_heading = (current_heading + angle_deg) % 360
    print(f"New heading: {new_heading:.2f}°")
    return new_heading

def move_forward(drivetrain, distance, speed, heading):
    """
    Moves forward a fixed distance along the given heading.
    Returns the (dx, dy) displacement.
    """
    if distance < 0.01:  # Don't move for very small distances
        return 0, 0
        
    travel_time = distance / ACTUAL_SPEED
    print(f"Moving forward {distance:.2f} m along heading {heading:.2f}°")
    drivetrain.set_motion(speed=speed, heading=heading)
    time.sleep(travel_time)
    drivetrain.set_motion(speed=0)
    time.sleep(0.1)  # Short pause to stabilize
    
    # Calculate displacement using heading
    dx = distance * math.cos(math.radians(heading))
    dy = distance * math.sin(math.radians(heading))
    return dx, dy

def handle_obstacle(drivetrain, sonar, current_x, current_y, current_heading):
    """
    More robust obstacle avoidance strategy.
    First tries strafing left, but if that fails, tries right or backing up.
    """
    print("Obstacle detected! Attempting to navigate around...")
    
    # First try strafing left
    strafe_heading = (current_heading + 90) % 360
    strafe_attempts = 0
    
    while read_ultrasonic(sonar) < CLEAR_THRESHOLD and strafe_attempts < MAX_STRAFE_ATTEMPTS:
        print("Strafing left...")
        dx_strafe, dy_strafe = move_forward(drivetrain, 0.1, STRAFE_SPEED, strafe_heading)
        current_x += dx_strafe
        current_y += dy_strafe
        strafe_attempts += 1
    
    # If left strafing didn't work, try right
    if strafe_attempts >= MAX_STRAFE_ATTEMPTS:
        print("Left strafing failed to clear obstacle. Trying right...")
        strafe_heading = (current_heading - 90) % 360
        strafe_attempts = 0
        
        while read_ultrasonic(sonar) < CLEAR_THRESHOLD and strafe_attempts < MAX_STRAFE_ATTEMPTS:
            print("Strafing right...")
            dx_strafe, dy_strafe = move_forward(drivetrain, 0.1, STRAFE_SPEED, strafe_heading)
            current_x += dx_strafe
            current_y += dy_strafe
            strafe_attempts += 1
    
    # If right strafing also failed, back up and try a different angle
    if strafe_attempts >= MAX_STRAFE_ATTEMPTS:
        print("Strafing failed. Backing up and trying a different approach...")
        backup_heading = (current_heading + 180) % 360
        dx_backup, dy_backup = move_forward(drivetrain, 0.3, FORWARD_SPEED, backup_heading)
        current_x += dx_backup
        current_y += dy_backup
        
        # Turn 45 degrees and try again
        current_heading = turn(drivetrain, 45, current_heading)
    
    # After avoiding obstacle, move forward a bit
    if read_ultrasonic(sonar) >= CLEAR_THRESHOLD:
        dx_fwd, dy_fwd = move_forward(drivetrain, FORWARD_STEP, FORWARD_SPEED, current_heading)
        current_x += dx_fwd
        current_y += dy_fwd
    
    return current_x, current_y, current_heading

def navigate_to_target(target_x, target_y, current_x, current_y, current_heading, drivetrain, sonar):
    """
    Navigate toward the target (target_x, target_y) while avoiding obstacles.
    Updates and returns the robot's current position and heading.
    """
    approach_attempts = 0
    max_approach_attempts = 20  # Prevent infinite loops
    
    while math.hypot(target_x - current_x, target_y - current_y) > TARGET_THRESHOLD:
        if approach_attempts >= max_approach_attempts:
            print("Warning: Unable to reach target after multiple attempts")
            break
            
        approach_attempts += 1
        
        # Calculate desired heading toward target
        dx = target_x - current_x
        dy = target_y - current_y
        desired_heading = math.degrees(math.atan2(dy, dx)) +90)
        
        # Calculate minimal turn (in the range -180 to 180)
        turn_angle = (desired_heading - current_heading + 180) % 360 - 180
        
        if abs(turn_angle) > 5:  # Only turn if angle difference is significant
            current_heading = turn(drivetrain, turn_angle, current_heading)
        
        # Check for obstacles ahead
        front_distance = read_ultrasonic(sonar)
        
        if front_distance < OBSTACLE_THRESHOLD:
            # Use the obstacle handling function
            current_x, current_y, current_heading = handle_obstacle(
                drivetrain, sonar, current_x, current_y, current_heading
            )
        else:
            # No obstacle: move forward a small step (or less if close to target)
            distance_to_target = math.hypot(dx, dy)
            step = min(FORWARD_STEP, distance_to_target * 0.8)  # Slow down as we get closer
            
            dx_fwd, dy_fwd = move_forward(drivetrain, step, FORWARD_SPEED, current_heading)
            current_x += dx_fwd
            current_y += dy_fwd
        
        print(f"Current position: ({current_x:.2f}, {current_y:.2f}), Heading: {current_heading:.2f}°")
        print(f"Distance to target: {math.hypot(target_x - current_x, target_y - current_y):.2f} m")
        
        # Short pause between iterations to avoid overwhelming the system
        time.sleep(0.1)
    
    print(f"Reached target ({target_x:.2f}, {target_y:.2f})")
    return current_x, current_y, current_heading

def signal_handler(sig, frame, drivetrain):
    """Handles clean shutdown on Ctrl+C"""
    print("\nShutting down...")
    drivetrain.set_motion(speed=0, angular_speed=0)
    sys.exit(0)

def navigate(target_x, target_y):
    """
    Main navigation function that can be called externally.
    Navigates to a target point (x, y) in meters from the starting position.
    """
    # Create hardware objects
    drivetrain = Drivetrain()
    sonar = Sonar()
    
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drivetrain))
    
    # Starting position and heading (in meters and degrees)
    current_x, current_y = 0.0, 0.0
    current_heading = 0.0  # Assuming 0 is to the right (positive x-axis)
    
    print(f"\nNavigating to target: ({target_x:.2f}, {target_y:.2f})")
    
    try:
        # Navigate to the target
        current_x, current_y, current_heading = navigate_to_target(
            target_x, target_y, current_x, current_y, current_heading, drivetrain, sonar
        )
        
        # Stop the robot at the end
        drivetrain.set_motion(speed=0)
        print("Navigation complete.")
        
        return True
    except Exception as e:
        print(f"Navigation error: {e}")
        drivetrain.set_motion(speed=0)  # Safety stop
        return False

if __name__ == '__main__':
    # If run directly, navigate to a single point
    x, y = 0, 1
    navigate(x, y)