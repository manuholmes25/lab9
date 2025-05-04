import cv2
import numpy as np
import serial
from time import sleep

cap = cv2.VideoCapture(0)

subtractor = cv2.createBackgroundSubtractorKNN()
# Inicializar conexión UART con la Tiva C
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
sleep(2)  
print("Transmitiendo comandos a la Tiva C...")

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_REGION_WIDTH = 100  

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    fgmask = subtractor.apply(frame)
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    object_detected = False
    center_x_min = FRAME_WIDTH // 2 - CENTER_REGION_WIDTH // 2
    center_x_max = FRAME_WIDTH // 2 + CENTER_REGION_WIDTH // 2

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            obj_center_x = x + w // 2
            if center_x_min <= obj_center_x <= center_x_max:
                object_detected = True
                break

    if object_detected:
        ser.write("A".encode())
        print("Se envio A")
        text = "Object Detected"
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = FRAME_WIDTH - text_size[0] - 10
        text_y = FRAME_HEIGHT - 10
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)
    else:
        ser.write("B".encode())
        print("Se envio B")
    cv2.imshow('Video Original', frame)
    cv2.imshow('Mascara de Movimiento', fgmask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
