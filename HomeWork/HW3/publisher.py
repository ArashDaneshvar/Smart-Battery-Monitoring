import paho.mqtt.client as mqtt
import psutil
import time
import uuid
from datetime import datetime
import json

# Create MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect('mqtt.eclipseprojects.io', 1883)

# Get MAC address
mac_address = hex(uuid.getnode())

# Initialize list to store events
events = []

while True:
    # Get timestamp
    timestamp = time.time()
    timestamp_ms = int(timestamp * 1000)

    # Get battery level and power plugged status
    battery_level = psutil.sensors_battery().percent
    power_plugged = int(psutil.sensors_battery().power_plugged)

    # Create event
    event = {
        'timestamp': timestamp_ms,
        'battery_level': battery_level,
        'power_plugged': power_plugged
    }

    # Add event to events list
    events.append(event)

    # If 10 events have been collected
    if len(events) == 10:
        # Create message
        message = {
            'mac_address': mac_address,
            'events': events
        }
        # Publish message
        client.publish("s317786", json.dumps(message))

        # Clear events list
        events = []

    # Sleep for 1 second
    time.sleep(1)