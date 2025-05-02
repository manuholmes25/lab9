import cv2
import numpy as np

def get_color_name(h):
    if h < 10 or h >= 170:
        return "Rojo"
    elif 10 <= h < 20:
        return "Naranja"
    elif 20 <= h < 35:
        return "Amarillo"
    elif 35 <= h < 85:
        return "Verde"
    elif 85 <= h < 130:
        return "Azul"
    elif 130 <= h < 160:
        return "Morado"
    elif 160 <= h < 170:
        return "Rosa"
    else:
        return "Desconocido"
def edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    thresh = cv2.adaptiveThreshold(gray, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 7, 5)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = img.copy()

    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        M = cv2.moments(contour)#Calcula el momento de la figura 
        if M["m00"] != 0:#Hallar los centroides
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        if len(approx) == 3:
            figure_name = "Triangulo"
        elif len(approx) == 4:
            _, _, w, h = cv2.boundingRect(contour)#Con los datos de los contornos se trata de hacer un rectangulo y lo cierrra completamente
            aspect_ratio = float(w) / h
            figure_name = "Cuadrado" if 0.95 <= aspect_ratio <= 1.05 else "Rectangulo"
        elif len(approx) == 5:
            figure_name = "Pentagono"
        elif len(approx) == 6:
            figure_name = "Hexagono"
        elif len(approx) > 6:
            figure_name = "Circulo"
        else:
            figure_name = "Desconocido"

        mask = np.zeros(gray.shape, dtype=np.uint8)#Mascra binaria de zeros para cada figura
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_val = cv2.mean(hsv, mask=mask)#Calculo del promedio de color en la mascara
        color_name = get_color_name(mean_val[0])

        label = f"{figure_name} {color_name}"
        cv2.putText(img_contours, label, (cX - 50, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.drawContours(img_contours, [approx], -1, (0, 255, 0), 3)

    cv2.imshow('Contornos', img_contours)
    cv2.imshow('Preprocesado', thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

img = cv2.imread('/home/belen/Embebidos2/Lab 9/recursos lab 9/figuras.png')
edge(img)
