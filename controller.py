import paho.mqtt.client as mqtt
import json
import time
import keyboard

client = mqtt.Client()
client.connect("localhost", 1883, 60)

MQTT_TOPIC_DRIVE = "robot/drive"
MQTT_TOPIC_ODOMETRY = "robot/odometry"

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_ODOMETRY:
        data = json.loads(msg.payload)
        print(f"Received odometry: x={data['x']:.2f}, y={data['y']:.2f}, theta={data['theta']:.2f}")

client.on_message = on_message

client.subscribe(MQTT_TOPIC_ODOMETRY)
client.loop_start()

def send_command(command):
    print(f"Sending command: {command}")
    client.publish(MQTT_TOPIC_DRIVE, command)

COMMANDS = {
    "w": "forward",
    "a": "left",
    "s": "backward",
    "d": "right",
    "x": "stop"
}

print("Use W/A/S/D to move, X to stop. Press ESC to quit.")

try:
    while True:
        for key, command in COMMANDS.items():
            if keyboard.is_pressed(key):  
                send_command(command)
                time.sleep(0.2) 
        time.sleep(0.05)  # Small delay to reduce CPU usage
except KeyboardInterrupt:
    print("Controller stopped by user")
finally:
    client.loop_stop()
    client.disconnect()