import RPi.GPIO as GPIO
from time import sleep

# Use GPIO numbering
GPIO.setmode(GPIO.BOARD)

# Set a valid GPIO pin (e.g., Pin 11 which is GPIO 17)
SERVO_PIN = 32
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set PWM frequency to 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def SetAngle(angle):
    duty = angle / 18 + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)  # Allow servo to reach position
    pwm.ChangeDutyCycle(0)  # Stop sending signal to avoid jitter

try:
    SetAngle(90)  # Move servo to 90 degrees
    sleep(1)
    SetAngle(0)   # Move servo to 0 degrees
    sleep(1)
    SetAngle(180) # Move servo to 180 degrees
    sleep(1)

finally:
    pwm.stop()
    GPIO.cleanup()
