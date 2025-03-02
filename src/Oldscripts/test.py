import cv2
from rover.drivetrain import Drivetrain
from rover.sonar import Sonar
from rover.motor import Motor
import time
import signal

# Load Haar cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 5)  # Manual exposure mode
cap.set(cv2.CAP_PROP_EXPOSURE, -1)         # Adjust exposure (-1 to -13 for some cameras)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)       # Adjust brightness (0-100)
cap.set(cv2.CAP_PROP_CONTRAST, 20)         # Adjust contrast (0-100)
cap.set(cv2.CAP_PROP_SHARPNESS, 20)       # Increase sharpness (if supported)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Adjust to 30 or 60 if supported
drivetrain = Drivetrain()
sonar = Sonar()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if(len(faces) >= 1):
        if (sonar.get_distance() > 300):
            drivetrain.set_motion(speed=100, heading=90)
    
    if(len(faces) == 0):
        drivetrain.set_motion(speed=0, heading=90)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow("Face Detection.jpg", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
