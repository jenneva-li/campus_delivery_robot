import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
from adafruit_vl53l0x import VL53L0X
import busio
import board

# MQTT Settings
MQTT_BROKER = "localhost"  # Change to your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/command"
MQTT_TOPIC_STATUS = "robot/status"

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Servo pins
BASE_SERVO_1 = 24
BASE_SERVO_2 = 23 # right
ARM_SERVO_1 = 12
ARM_SERVO_2 = 16
#CLAW_SERVO_1 = 
#CLAW_SERVO_2 = 

# Initialize servos
servo_pins = [BASE_SERVO_1, BASE_SERVO_2, ARM_SERVO_1, ARM_SERVO_2] #, CLAW_SERVO_1, CLAW_SERVO_2
servos = {}

for pin in servo_pins:
    GPIO.setup(pin, GPIO.OUT)
    servos[pin] = GPIO.PWM(pin, 50)
    servos[pin].start(0)

# Initialize ToF sensor
i2c = busio.I2C(board.SCL, board.SDA)
tof = VL53L0X(i2c)

def set_servo_angle(servo, angle):
    duty = angle / 18 + 2
    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)

def publish_status(client, message):
    client.publish(MQTT_TOPIC_STATUS, json.dumps({"status": message}))

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_COMMAND)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        command = payload.get("command")
        
        if command == "pick_and_place":
            # Check for object using ToF
            distance = tof.range
            if distance < 200:  # Object within 20cm
                publish_status(client, "Object detected, starting pickup sequence")
                
                # Lower arm
                set_servo_angle(servos[ARM_SERVO_1], 120)
                set_servo_angle(servos[ARM_SERVO_2], 120)
                time.sleep(1)
                
                # Close claw
                #set_servo_angle(servos[CLAW_SERVO_1], 90)
                #set_servo_angle(servos[CLAW_SERVO_2], 90)
                #time.sleep(1)
                
                # Raise arm
                set_servo_angle(servos[ARM_SERVO_1], 45)
                set_servo_angle(servos[ARM_SERVO_2], 45)
                time.sleep(1)
                
                # Rotate base
                set_servo_angle(servos[BASE_SERVO_1], 180)
                set_servo_angle(servos[BASE_SERVO_2], 180)
                time.sleep(1)
                
                # Lower arm
                set_servo_angle(servos[ARM_SERVO_1], 120)
                set_servo_angle(servos[ARM_SERVO_2], 120)
                time.sleep(1)
                
                # Open claw
                #set_servo_angle(servos[CLAW_SERVO_1], 0)
                #set_servo_angle(servos[CLAW_SERVO_2], 180)
                #time.sleep(1)
                
                # Return to home position
                set_servo_angle(servos[ARM_SERVO_1], 45)
                set_servo_angle(servos[ARM_SERVO_2], 45)
                set_servo_angle(servos[BASE_SERVO_1], 0)
                set_servo_angle(servos[BASE_SERVO_2], 0)
                
                publish_status(client, "Pick and place sequence completed")
            else:
                publish_status(client, "No object detected")

    except Exception as e:
        publish_status(client, f"Error: {str(e)}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        publish_status(client, "Robot ready")
        client.loop_forever()
        
    except KeyboardInterrupt:
        for servo in servos.values():
            servo.stop()
        GPIO.cleanup()
        client.disconnect()

if __name__ == "__main__":
    main()

# To trigger the robot, publish to MQTT_TOPIC_COMMAND:
# {"command": "pick_and_place"}


