# Modify the script to store the battery level and power plugged flag to Redis Cloud.

import redis
import psutil
import time
import uuid
from datetime import datetime 


REDIS_HOST = "redis-14980.c300.eu-central-1-1.ec2.cloud.redislabs.com"
REDIS_PORT = 14980
REDIS_USERNAME = "default"
REDIS_PASSWORD = "WclyL3nHTYtgrBy192F9dEfyWQRrx9gi"

#Connect to redis database
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)

#Check the connection
is_connect = redis_client.ping()
print(is_connect)

#Crerate timeseries in Redis
ts = redis_client.ts()
mac_address = hex(uuid.getnode())

try:
    ts.create(f"{mac_address}:battery")
except redis.ResponseError:
    pass

try:
    ts.create(f"{mac_address}:power")
except redis.ResponseError:
    pass




status = psutil.sensors_battery()

while True:
    timestamp = time.time()
    battery_level = status.percent
    power_is_plugged = status.power_plugged
    date_time_format = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S%f')

    print(f'{date_time_format} - {mac_address}:{battery_level}')
    print(f'{date_time_format} - {mac_address}:{power_is_plugged}')
    
    ts.add(f"{mac_address}:battery", timestamp, battery_level)
    ts.add(f"{mac_address}:power", timestamp, power_is_plugged)

    print(ts.get("mac_address"))
    time.sleep(2)


    