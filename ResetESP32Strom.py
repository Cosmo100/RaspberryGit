
import RPi.GPIO as GPIO
import time

ResetPinESP32=17
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ResetPinESP32, GPIO.OUT)

print ("Reset des Strom-ESP32 ") 
GPIO.output(ResetPinESP32, GPIO.LOW)
time.sleep(3)
GPIO.output(ResetPinESP32, GPIO.HIGH)  # Setze den Pin wieder auf HIGH

