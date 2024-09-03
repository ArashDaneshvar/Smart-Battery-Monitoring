"""
LAB5 - Exercise 1.1: MQTT Publisher
"""

from time import sleep
import paho.mqtt.client as mqtt

# Create a new MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect('mqtt.eclipseprojects.io', 1883)

# Publish a message to a topic. Use your studend ID as topic
for i in range(10):
    client.publish('s001122', f'Hello World {i}!')
    sleep(1)
