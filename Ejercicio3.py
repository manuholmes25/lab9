import cv2
import numpy as np

cap = cv2.VideoCapture('/home/belen/Embebidos2/Lab 9/recursos lab 9/bouncing.mp4.mp4')
subtractor = cv2.createBackgroundSubtractorKNN()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    fgmask2 = subtractor.apply(frame)
    _, mask = cv2.threshold(fgmask2, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = frame.copy()
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)
    cv2.imshow('Contornos', img_contours)
    cv2.imshow('Substractor de fondos KNN', mask) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
