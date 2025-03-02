
# motors/sensors
from rover import motor
from rover.drivetrain import Drivetrain
from rover.battery import Battery
from rover.sonar import Sonar
from rover.motor import Motor
# opencv
import cv2
# extra
from rover import constants
import gpiozero
import time
import signal
import tflite_runtime.interpreter as tflite
import numpy as np

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

#load labels
with open("Models/labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Load the TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="Models/model.tflite")
interpreter.allocate_tensors()
# Get model input details
input_details = interpreter.get_input_details()
print(input_details)
output_details = interpreter.get_output_details()
print(output_details)
# Get input shape
input_shape = input_details[0]['shape'][1:3]  # Expected input size (e.g., 224x224)

# Loading facial recogenition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

#Loading components, 
drivetrain = Drivetrain()
sonar = Sonar()
battery = Battery()

#Functions

#Looping
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect faces
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # if(len(faces) >= 1):
    #     if (sonar.get_distance() > 500):
    #         drivetrain.set_motion(speed=100, heading=90)
    
    # if(len(faces) == 0):
    #     drivetrain.set_motion(speed=0, heading=90)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

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
    print(confidence)
    detected_label = labels[label_id] if confidence > 0.5 else "Unknown"

    # Display the label on the frame
    cv2.putText(frame, f"Detected: {detected_label} ({confidence:.2f})", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)

    cv2.imshow("Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
