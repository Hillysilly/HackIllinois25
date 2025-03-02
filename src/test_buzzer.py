from rover import constants
from rover.drivetrain import Drivetrain
import time
import gpiozero
import threading

# Initialize components
buzzer = gpiozero.Buzzer(constants.BUZZER_PIN)
drivetrain = Drivetrain()

# Function to run the buzzer for a certain time
def run_buzzer(duration):
    buzzer.on()
    time.sleep(duration)
    buzzer.off()

# Function to move the drivetrain for a certain time
def run_drivetrain(duration, speed=100, heading=90):
    drivetrain.set_motion(speed=speed, heading=heading)
    time.sleep(duration)
    drivetrain.set_motion(speed=0, heading=heading)  # Stop after time

if __name__ == '__main__':
    duration = 1  # Run both for 3 seconds

    buzzer_thread = threading.Thread(target=run_buzzer, args=(duration,))
    drivetrain_thread = threading.Thread(target=run_drivetrain, args=(duration,))

    buzzer_thread.start()
    drivetrain_thread.start()

    buzzer_thread.join()
    drivetrain_thread.join()

    print("Both buzzer and drivetrain have stopped.")
