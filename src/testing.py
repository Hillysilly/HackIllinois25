import cv2
import numpy as np
import time
from math import atan2, degrees, sqrt
import RPi.GPIO as GPIO
from rover.drivetrain import Drivetrain
from rover.camera import Camera
from rover.servo import Servo

# --- Hardware Setup ---
GPIO.setmode(GPIO.BCM)
ULTRASONIC_TRIGGER_PIN = 17  # Adjust as needed
ULTRASONIC_ECHO_PIN = 27     # Adjust as needed
LED_PIN = 18                 # Adjust as needed
GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

drivetrain = Drivetrain()
camera = Camera()
camera_servo = Servo(servo_id=1)


def turn(angle_deg):
    """Turn the robot by a specified angle in degrees."""
    speed = 75
    duration = abs(angle_deg) / 90 * 1.3 # Calibrate: seconds for 90° turn
    print(f"Turning {angle_deg}° for {duration}s")
    if angle_deg > 0:  # Turn right
        drivetrain.front_left_motor.forward(speed)
        drivetrain.rear_left_motor.forward(speed)
        drivetrain.front_right_motor.reverse(speed)
        drivetrain.rear_right_motor.reverse(speed)
    else:  # Turn left
        drivetrain.front_left_motor.reverse(speed)
        drivetrain.rear_left_motor.reverse(speed)
        drivetrain.front_right_motor.forward(speed)
        drivetrain.rear_right_motor.forward(speed)
    time.sleep(duration)
    stop_motors()

def stop_motors():
    """Stop all motors."""
    drivetrain.front_left_motor.stop()
    drivetrain.front_right_motor.stop()
    drivetrain.rear_left_motor.stop()
    drivetrain.rear_right_motor.stop()



if __name__ == "__main__":
    try:
        turn(360)

        exit()
    except KeyboardInterrupt:
        stop_motors()
    finally:
        GPIO.cleanup()
