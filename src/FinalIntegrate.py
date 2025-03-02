# motors/sensors
from rover import motor
from rover.drivetrain import Drivetrain
from rover.battery import Battery
from rover.sonar import Sonar
from rover.motor import Motor
# opencv
import cv2
from rover.sonar_led import SonarLEDS

# extra
from rover import constants
import gpiozero
import time
import signal
import albertFunctions
from rover.servo import Servo
from rover import constants
import numpy as np
#import human_navigate

#!/usr/bin/env python3
import time
import math
import signal
import sys

#tensor model
import tflite_runtime.interpreter as tflite

#Initializing the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 5)  # Manual exposure mode
cap.set(cv2.CAP_PROP_EXPOSURE, -1)         # Adjust exposure (-1 to -13 for some cameras)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)       # Adjust brightness (0-100)
cap.set(cv2.CAP_PROP_CONTRAST, 20)         # Adjust contrast (0-100)
cap.set(cv2.CAP_PROP_SHARPNESS, 20)       # Increase sharpness (if supported)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Adjust to 30 or 60 if supported

# Loading facial recogenition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")




# Tensor
#load labels
with open("Models/labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Load the TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="Models/model.tflite")
interpreter.allocate_tensors()
# Get model input details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
# Get input shape
input_shape = input_details[0]['shape'][1:3]  # Expected input size (e.g., 224x224)




#Loading compoenents, 
drivetrain = Drivetrain()
sonar = Sonar()
buzzer = gpiozero.Buzzer(constants.BUZZER_PIN)
# battery = Battery()
pan_servo = Servo(constants.CAMERA_SERVOS['pan'])
tilt_servo = Servo(constants.CAMERA_SERVOS['tilt'])
sonar_leds = SonarLEDS()
sonar_leds.setRGBMode(0)
sonar_leds.left.setPixelColor(0x000000)
sonar_leds.right.setPixelColor(0x000000)


# Calibration constants (tweak these as needed)
ACTUAL_SPEED       = 0.296    # m/s at speed setting 100
FORWARD_SPEED      = 100      # Speed setting for forward motion
STRAFE_SPEED       = 100      # Speed setting for strafing
ACTUAL_STRAFE_SPEED = 0.267
OBSTACLE_THRESHOLD = 0.20      # m; trigger obstacle avoidance if an object is closer than this
CLEAR_THRESHOLD    = 0.25     # m; consider path clear if sensor reads at least this distance
FORWARD_STEP       = 0.01     # m; distance to move forward each step
TARGET_THRESHOLD   = 0.3      # m; target is reached if within this distance
TURN_CALIBRATION   = 1        # Time in seconds for a 90° turn (adjust based on testing)

#Human_Navigate







def signal_handler(sig, frame):
    drivetrain.set_motion(speed=0, angular_speed=0)
    buzzer.off()
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

def turn(angle):
    global x_position, y_position, current_angle_relative_to_x_axis
    if abs(angle) < 1:  # Ignore very small turns
        return
    if angle > 0:
        drivetrain.set_motion(angular_speed=100)
    else:
        drivetrain.set_motion(angular_speed=-100)
    # Duration is proportional to the absolute angle (90° -> TURN_CALIBRATION sec)
    duration = abs(angle) / 90 * TURN_CALIBRATION
    time.sleep(duration)
    drivetrain.set_motion(speed=0)
    current_angle_relative_to_x_axis = (current_angle_relative_to_x_axis + angle) % 360

def strafe_right(num_meters):
    global x_position, y_position, current_angle_relative_to_x_axis
    drivetrain.set_motion(speed=STRAFE_SPEED, heading=0)
    time.sleep(num_meters / ACTUAL_STRAFE_SPEED)
    drivetrain.set_motion(speed=0)
    rad = math.radians(current_angle_relative_to_x_axis)
    x_position += math.sin(rad) * num_meters
    y_position -= math.cos(rad) * num_meters

def strafe_left(num_meters):
    global x_position, y_position, current_angle_relative_to_x_axis
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
        return distance
    except Exception as e:
        return 2.0








# Global position and orientation variables
global x_position, y_position, current_angle_relative_to_x_axis
x_position = 0.0
y_position = 0.0
# Robot's "current_angle_relative_to_x_axis" is in degrees.
# Assuming the robot's front is initially aligned with 90° (i.e. positive y-axis)
current_angle_relative_to_x_axis = 90.0

drivetrain = Drivetrain()
sonar = Sonar()

#Looping
albertFunctions.setDefault(pan_servo, tilt_servo)
tilt = 45
pan = 90
panTilt = True
follow = True
haventSeen = 0
tweaking = False
tweakingCountn = 0

# Set target coordinates (one target)
target_x = 0.0
target_y = 3.0

humanBuzz = True
hydrantBuzz = True
carBuzz = True

while get_distance_to_target(target_x, target_y) > TARGET_THRESHOLD:
    print(f"x_position: {x_position} y_position: {y_position}")
    ret, frame = cap.read()
    if not ret:
        print("camera broken")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    oldpan = pan
    oldtilt = tilt
    if(panTilt and not tweaking):
        pan, tilt, haventSeen = albertFunctions.panAndTilt(pan_servo, tilt_servo, faces, pan, tilt, haventSeen)
        tweaking = True
    
    if(tweaking):
        tweakingCountn += 1
    if(tweakingCountn > 25):
        tweaking = False

    # Preprocess frame for model
    img = cv2.resize(frame, tuple(input_shape))  # Resize to model input size
    img = np.expand_dims(img, axis=0).astype(np.uint8)  # Normalize

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    # Get the highest probability label
    label_id = np.argmax(predictions)
    confidence = predictions[label_id] / 255
    detected_label = labels[label_id] if confidence > 0.5 else "Unknown"
    print(detected_label)
    
    # Buzzing
    if (humanBuzz and len(faces) > 0):
        if detected_label == "Humans":
            sonar_leds.left.setPixelColor(0x00FF00)
            sonar_leds.right.setPixelColor(0x00FF00)

            for i in range(3):
                buzzer.on()
                time.sleep(0.1)
                buzzer.off()
                time.sleep(0.1)
            humanBuzz = False
            sonar_leds.left.setPixelColor(0x000000)
            sonar_leds.right.setPixelColor(0x000000)

    if (carBuzz and (read_ultrasonic() < OBSTACLE_THRESHOLD)):

        if detected_label == "Cars":
            sonar_leds.left.setPixelColor(0xFF00FF)
            sonar_leds.right.setPixelColor(0xFF00FF)

            for i in range(2):
                buzzer.on()
                time.sleep(0.1)
                buzzer.off()
                time.sleep(0.1)
            carBuzz = False
            sonar_leds.left.setPixelColor(0x000000)
            sonar_leds.right.setPixelColor(0x000000)

    if (hydrantBuzz and (read_ultrasonic() < OBSTACLE_THRESHOLD)):
        if detected_label == "Fire Hydrant":
            sonar_leds.left.setPixelColor(0x0000FF)
            sonar_leds.right.setPixelColor(0x0000FF)

            for i in range(1):
                buzzer.on()
                time.sleep(0.1)
                buzzer.off()
                time.sleep(0.1)
            hydrantBuzz = False
            sonar_leds.left.setPixelColor(0x000000)
            sonar_leds.right.setPixelColor(0x000000)

    # Display the label on the frame
    cv2.putText(frame, f"Detected: {detected_label} ({confidence:.2f})", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)

    cv2.imshow("Face Detection.jpg", frame)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

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
        
        if read_ultrasonic() < OBSTACLE_THRESHOLD:
            total_angle = 0
            angle = 20
            while total_angle <= 360 and read_ultrasonic() < OBSTACLE_THRESHOLD * 2:
                turn(angle)
            
    
    go_straight(FORWARD_STEP)

cap.release()
cv2.destroyAllWindows()
drivetrain.set_motion(speed=0)
print("Target reached!")
sys.exit(0)
