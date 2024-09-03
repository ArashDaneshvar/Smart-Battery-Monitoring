"""
LAB5 - Exercise 1.2: MQTT Subscriber
"""

import paho.mqtt.client as mqtt

# Create a new MQTT client
client = mqtt.Client()

# Define the callbacks for when the client receives a response from the server
# and when a message is published on a subscribed topic
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {str(rc)}')
    # Subscribe to a topic when the client connects
    client.subscribe('s001122')

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    topic = msg.topic
    print(f"Received message '{message}' on topic {topic}")

# Set the callbacks
client.on_connect = on_connect
client.on_message = on_message

client.connect('mqtt.eclipseprojects.io', 1883)

# Start the client loop to process network events and call the callbacks
client.loop_forever()
