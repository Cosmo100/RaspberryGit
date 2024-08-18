import time
import RPi.GPIO as GPIO

# RPi.GPIO Layout verwenden (wie Pin-Nummern)
GPIO.setmode(GPIO.BOARD)

# Pin 18 (GPIO 24) auf Input setzen
GPIO.setup(16, GPIO.OUT)

# Pin 11 (GPIO 17) auf Output setzen
GPIO.setup(18, GPIO.OUT)

# Dauersschleife
while 1:
  # LED immer ausmachen
    GPIO.output(16, GPIO.LOW)
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
  
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(18, GPIO.LOW)
    # Warte 100 ms
    time.sleep(2)
