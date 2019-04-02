import cv2
import numpy as np
from cv2 import aruco

cap = cv2.VideoCapture(0)


def detect_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    return frame_markers


while True:
    ret, frame = cap.read()
    
    if ret:
        frame_mirror = cv2.flip(frame, 1)
        
        frame_markers = detect_image(frame)
        frame_markers_mirror = detect_image(frame_mirror)
 
        cv2.imshow('frame', frame_markers)
        cv2.imshow('mirror', frame_markers_mirror)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

