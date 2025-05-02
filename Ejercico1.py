import cv2
import numpy as np

cap = cv2.VideoCapture('/home/belen/Embebidos2/Lab 9/recursos lab 9/bouncing.mp4.mp4')
fgbg = cv2.createBackgroundSubtractorMOG2()
subtractor = cv2.createBackgroundSubtractorKNN()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    fgmask = fgbg.apply(frame)
    fgmask2 = subtractor.apply(frame)
    cv2.imshow('Video Original', frame)
    cv2.imshow('Substractor de fondos MOG2', fgmask) 
    cv2.imshow('Substractor de fondos KNN', fgmask2) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
