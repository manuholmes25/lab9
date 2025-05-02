import serial
import time
from time import sleep
# Configurar UART (asegúrate de tener habilitado /dev/serial0 en raspi-config)
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()
sleep(2)
print("Transmitiendo comandos a la Tiva C...")

try:
    while True:
        comando = input("Ingresa comando (A = una rueda, B = dos ruedas): ").strip().upper()
        if comando in ['A', 'B']:
            ser.write(comando.encode())
            print(f"Comando '{comando}' enviado.")
        else:
            print("Comando inválido. Usa solo 'A' o 'B'.")
except KeyboardInterrupt:
    print("\nFinalizando transmisión.")
finally:
    ser.close()
