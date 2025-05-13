import cv2
import numpy as np
import serial
from time import sleep

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
sleep(2)  
print("Transmitiendo comandos a la Tiva C...")

cap = cv2.VideoCapture(0)

lower_yellow = np.array([21, 170, 70])
upper_yellow = np.array([180, 255, 255])

lower_red1 = np.array([88, 140, 100])
upper_red1 = np.array([94, 255, 255])
lower_red2 = np.array([146, 140, 100])
upper_red2 = np.array([180, 255, 255])

lower_violet = np.array([90, 40, 137])
upper_violet = np.array([180, 255, 255])

lower_blue = np.array([91, 140, 70])
upper_blue = np.array([180, 255, 255])

lower_green = np.array([59, 70, 59])
upper_green = np.array([100, 255, 255])

current_mask = 'ALL'
allowed_shape = 'ALL'

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]
    rect_w, rect_h = 1000, 600
    x1, y1 = width // 2 - rect_w // 2, height // 2 - rect_h // 2
    x2, y2 = x1 + rect_w, y1 + rect_h

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
    roi = frame[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hue_channel = hsv[:, :, 0]

    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_red = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1),cv2.inRange(hsv, lower_red2, upper_red2))
    mask_violet = cv2.inRange(hsv, lower_violet, upper_violet)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    if current_mask == 'YELLOW':
        mask = mask_yellow
    elif current_mask == 'RED':
        mask = mask_red
    elif current_mask == 'VIOLET':
        mask = mask_violet
    elif current_mask == 'BLUE':
        mask = mask_blue
    elif current_mask == 'GREEN':
        mask = mask_green
    else:
        mask = cv2.bitwise_or(mask_yellow,cv2.bitwise_or(mask_red,cv2.bitwise_or(mask_violet,cv2.bitwise_or(mask_blue, mask_green))))

    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.medianBlur(mask, 7)
    #Closing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count_valid = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) == 3:
                shape = "Triangulo"
            elif len(approx) == 4:
                shape = "Rectangulo"
            elif len(approx) > 4:
                shape = "Circulo"
            else:
                shape = "Desconocido"

            show = False
            if allowed_shape == 'ALL' and shape in ["Triangulo", "Rectangulo", "Circulo"]:
                show = True
            elif allowed_shape == 'TRIANGLE' and shape == "Triangulo":
                show = True
            elif allowed_shape == 'RECTANGLE' and shape == "Rectangulo":
                show = True
            elif allowed_shape == 'CIRCLE' and shape == "Circulo":
                show = True

            if show:
                count_valid += 1
                approx_shifted = approx + [x1, y1]
                x, y = approx_shifted.ravel()[0:2]
                cv2.drawContours(frame, [approx_shifted], -1, (0, 255, 0), 3)
                cv2.putText(frame, shape, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    area_roi = rect_w * rect_h

    if count_valid == 1:
        if area > area_roi * 0.3:
            ser.write("D\n".encode('utf-8'))
            print("D\n")
        else:
            ser.write("B\n".encode('utf-8'))
            print("B\n")
    elif count_valid > 1:
        ser.write("C\n".encode('utf-8'))
        print("C\n")
    else:
        ser.write("A\n".encode('utf-8'))
        print("A\n")

    cv2.imshow("Color Detector with Contours", frame)
    cv2.imshow("MASK", mask)
    cv2.imshow("Hue Channel", hue_channel)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('a'):
        current_mask = 'YELLOW'
    elif key == ord('v'):
        current_mask = 'VIOLET'
    elif key == ord('r'):
        current_mask = 'RED'
    elif key == ord('b'):
        current_mask = 'BLUE'
    elif key == ord('g'):
        current_mask = 'GREEN'
    elif key == ord('t'):
        current_mask = 'ALL'

    elif key == ord('0'):
        allowed_shape = 'ALL'
    elif key == ord('1'):
        allowed_shape = 'TRIANGLE'
    elif key == ord('2'):
        allowed_shape = 'RECTANGLE'
    elif key == ord('3'):
        allowed_shape = 'CIRCLE'

cap.release()
cv2.destroyAllWindows()

