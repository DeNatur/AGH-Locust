# Load libraries
import cv2
import numpy as np
from generate_results import GenerateFinalDetections
 
# Instantiate a new detector
finalDetector = GenerateFinalDetections()

def readFromCamera():
    cap = cv2.VideoCapture(0)
    
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        frame = finalDetector.predict(frame)
        # Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cap.release()
        cv2.destroyAllWindows()

def readFromImage():
    frame = cv2.imread('test.jpg')
    frame = finalDetector.predict(frame)
    # Display the resulting frame
    cv2.imshow('frame',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

readFromImage()
