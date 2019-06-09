import RPi.GPIO as GPIO
import time

pwm_output_pin = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwm_output_pin, GPIO.OUT)

p = GPIO.PWM(pwm_output_pin, 50)
print(p)
p.start(0)
print("Starting Servo")

try:
    while True:
        print("Start loop")
        p.ChangeDutyCycle(5)
        time.sleep(0.5)
        p.ChangeDutyCycle(10)
        time.sleep(0.5)
        print("End Loop")
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()