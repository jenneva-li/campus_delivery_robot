#!/usr/bin/env python3

import json
import time
import math
import paho.mqtt.client as mqtt

MQTT_BROKER             = "localhost"
MQTT_PORT               = 1883
MQTT_TOPIC_DRIVE_CMD    = "robot/drive"
MQTT_TOPIC_ODOMETRY     = "robot/odometry"
MQTT_TOPIC_PATH_DONE    = "robot/path_completed"

MAX_LINEAR_SPEED   = 0.12
MAX_ANGULAR_SPEED  = 0.4
K_LINEAR           = 1.0
K_ANGULAR          = 0.5
K_ANGULAR_DRIVE    = 0.2
ANGLE_THRESHOLD    = 0.2    # ~11.5 deg
DISTANCE_THRESHOLD = 0.1    # 10 cm

# Predefined autonomous path (looping)
AUTONOMOUS_PATH = [
    (0.5, 0.5),
    (1.0, 0.5),
    (1.0, 1.0),
    (0.5, 1.0),
    (0.0, 0.5)
]

path_xy       = AUTONOMOUS_PATH[:]
current_index = 0
robot_x       = 0.0
robot_y       = 0.0
robot_th      = 0.0  # Radians
state         = 'ROTATING'

def wrap_angle(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi

def on_odometry(client, userdata, msg):
    global robot_x, robot_y, robot_th
    data = json.loads(msg.payload)
    robot_x  = data.get('x', robot_x)
    robot_y  = data.get('y', robot_y)
    robot_th = data.get('theta', 0.0)  # radians

def main():
    global path_xy, current_index, state
    client = mqtt.Client()
    client.on_message = on_odometry
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.subscribe(MQTT_TOPIC_ODOMETRY)
    client.loop_start()

    try:
        while True:
            time.sleep(0.1)

            if not path_xy or state == 'IDLE':
                cmd = {'linear_velocity': 0.0, 'angular_velocity': 0.0}
                client.publish(MQTT_TOPIC_DRIVE_CMD, json.dumps(cmd))
                continue

            if current_index >= len(path_xy):
                print("[node_drivepath.py] Path completed => Restarting.")
                client.publish(MQTT_TOPIC_PATH_DONE, json.dumps({'status': 'completed'}))
                current_index = 0  # Restart path
                state = 'ROTATING'
                continue

            gx, gy = path_xy[current_index]
            dx = gx - robot_x
            dy = gy - robot_y
            dist = math.hypot(dx, dy)

            angle_to_goal = math.atan2(dy, dx)
            angle_error   = wrap_angle(angle_to_goal - robot_th)

            if dist < DISTANCE_THRESHOLD:
                current_index += 1
                if current_index < len(path_xy):
                    state = 'ROTATING'
                continue

            if state == 'ROTATING':
                if abs(angle_error) < ANGLE_THRESHOLD:
                    state = 'DRIVING'
                else:
                    ang_vel = K_ANGULAR * angle_error
                    ang_vel = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, ang_vel))
                    cmd = {'linear_velocity': 0.0, 'angular_velocity': ang_vel}
                    client.publish(MQTT_TOPIC_DRIVE_CMD, json.dumps(cmd))

            elif state == 'DRIVING':
                lin_vel = min(K_LINEAR * dist, MAX_LINEAR_SPEED)
                ang_vel = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, K_ANGULAR_DRIVE * angle_error))

                cmd = {'linear_velocity': lin_vel, 'angular_velocity': ang_vel}
                client.publish(MQTT_TOPIC_DRIVE_CMD, json.dumps(cmd))

    except KeyboardInterrupt:
        print("\n[node_drivepath.py] Interrupted.")
    finally:
        cmd_msg = {'linear_velocity': 0.0, 'angular_velocity': 0.0}
        client.publish(MQTT_TOPIC_DRIVE_CMD, json.dumps(cmd_msg))
        client.loop_stop()
        client.disconnect()
        print("[node_drivepath.py] Shutdown complete.")

if __name__ == "__main__":
    main()
