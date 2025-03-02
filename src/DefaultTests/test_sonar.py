import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rover.servo import Servo
from rover import constants
import time
import signal

from rover.sonar import Sonar
import time

sonar = Sonar()
while True:
    print(sonar.get_distance() * 0.001)
    time.sleep(1)
