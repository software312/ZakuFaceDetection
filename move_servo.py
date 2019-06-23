import RPi.GPIO as GPIO
import time

# Change Duty Cycle parameter is % based

def setDuty(angle):
    return 5*angle/120 

def GoLeft(angle, p):
    duty = 7 + setDuty(angle)
    print("Going left with duty: ", duty)
    p.ChangeDutyCycle(duty)
    time.sleep(1)
    
def GoRight(angle, p):
    duty = 7 - setDuty(angle)
    print("Going right with duty: ", duty)
    p.ChangeDutyCycle(duty)
    time.sleep(1)
    
def rotate_servo(x, center_x, p):
    print("center x is: ", center_x, "the face is at: ", x)
    if x < center_x:
        GoLeft(5, p)
    elif x > center_x:
        GoRight(5, p)

if __name__ == "__main__":
    pwm_output_pin = 16
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pwm_output_pin, GPIO.OUT)

    # MG996R Frequency: 50Hz
    p = GPIO.PWM(pwm_output_pin, 50)
    print(p)
    p.start(0)
    print("Starting Servo")
    
    try:
        while True:
            GoLeft(30)
            time.sleep(1)
            GoRight(30)
            time.sleep(1)
        
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
        

