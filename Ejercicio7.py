import cv2
import numpy as np
import serial
from time import sleep

cap = cv2.VideoCapture(0)
# Inicializar conexión UART con la Tiva C
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
sleep(2)  
print("Transmitiendo comandos a la Tiva C...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_frame = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(blur_frame, 60, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 1000  
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    cv2.drawContours(frame, filtered_contours, -1, (0, 255, 0), 2)
    num_contornos = len(filtered_contours)
    cv2.putText(frame, f'Contornos: {num_contornos}', (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if num_contornos == 0:
        ser.write("A".encode('utf-8'))
    if num_contornos == 1:
        ser.write("B".encode('utf-8'))
    if num_contornos > 1:
        ser.write("C".encode('utf-8'))
    cv2.imshow('Video con Contornos', frame)
    cv2.imshow('Mascara Binaria', thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
