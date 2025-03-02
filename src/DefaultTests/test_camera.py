from rover.camera import Camera
from rover import constants
import picamera
import time
import signal
import cv2
import numpy as np
import matplotlib.pyplot as plt

camera = Camera()
if __name__ == '__main__':

        print(camera.capture())
        Image = camera.image_array
        ImageNP = np.array(Image)
        print(ImageNP.shape)
        cv2.imwrite("image.png", Image)
        # for row in Image:
        #         for col in row:
        #                 print(len(col))
        #                 print("(" + str(col[0]) + "," + str(col[1]) + ")")