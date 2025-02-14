from rover.drivetrain import Drivetrain
import time
import signal


if __name__ == '__main__':

    drivetrain = Drivetrain()

    def signal_handler(sig, frame):
        drivetrain.front_left_motor.stop()
        drivetrain.front_right_motor.stop()
        drivetrain.rear_left_motor.stop()
        drivetrain.rear_right_motor.stop()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print('front left motor forward')
    drivetrain.front_left_motor.forward(50)
    time.sleep(1)
    print('front left motor reverse')
    drivetrain.front_left_motor.reverse(50)
    time.sleep(1)
    drivetrain.front_left_motor.stop()

    print('front right motor forward')
    drivetrain.front_right_motor.forward(50)
    time.sleep(1)
    print('front right motor reverse')
    drivetrain.front_right_motor.reverse(50)
    time.sleep(1)
    drivetrain.front_right_motor.stop()

    print('rear left motor forward')
    drivetrain.rear_left_motor.forward(50)
    time.sleep(1)
    print('rear left motor reverse')
    drivetrain.rear_left_motor.reverse(50)
    time.sleep(1)
    drivetrain.rear_left_motor.stop()

    print('rear right motor forward')
    drivetrain.rear_right_motor.forward(50)
    time.sleep(1)
    print('rear right motor reverse')
    drivetrain.rear_right_motor.reverse(50)
    time.sleep(1)
    drivetrain.rear_right_motor.stop()
