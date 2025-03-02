from rover.servo import Servo
from rover import constants
import time
import signal

pan_servo = Servo(constants.CAMERA_SERVOS['pan'])

tilt_servo = Servo(constants.CAMERA_SERVOS['tilt'])

if __name__ == '__main__':
    pan_servo.set_angle(45)
    tilt_servo.set_angle(90)
    exit()