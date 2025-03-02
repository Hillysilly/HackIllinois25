import cv2
import time

# Open the camera


cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)  # Manual exposure mode
cap.set(cv2.CAP_PROP_EXPOSURE, -1)         # Adjust exposure (-1 to -13 for some cameras)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 40)       # Adjust brightness (0-100)
cap.set(cv2.CAP_PROP_CONTRAST, 20)         # Adjust contrast (0-100)
cap.set(cv2.CAP_PROP_SHARPNESS, 20)       # Increase sharpness (if supported)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Adjust to 30 or 60 if supported

time.sleep(2)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Process the frame (example: convert to grayscale)
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Save the processed frame as an image
    cv2.imwrite('output_image.jpg', frame)

    # Display the processed frame
    # cv2.imshow('Processed Frame', rgb)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()