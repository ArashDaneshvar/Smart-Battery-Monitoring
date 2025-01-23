import psutil
import redis
import time
import uuid
import argparse as ap
from datetime import datetime

parser = ap.ArgumentParser()
parser.add_argument('--host', type=str, default='redis-18872.c9.us-east-1-4.ec2.cloud.redislabs.com')
parser.add_argument('--port', type=int, default= 18872)
parser.add_argument('--username', type=str, default= 'default')
parser.add_argument('--password', type=str, default='aE86vDxKP6ovbBMdVxJzLQvwT1GbIoer')
args = parser.parse_args()

REDIS_HOST = args.host
REDIS_PORT = args.port
REDIS_USERNAME = args.username
REDIS_PASSWORD = args.password
redis_client = redis.Redis(host= REDIS_HOST, port= REDIS_PORT, username= REDIS_USERNAME, password= REDIS_PASSWORD)

is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

mac_address = hex(uuid.getnode())

# Set retention periods when creating time series
try:
    redis_client.ts().create(f'{mac_address}:battery', retention_msecs = 86400000)
except redis.exceptions.ResponseError:
    pass

try:
     redis_client.ts().create(f'{mac_address}:power', retention_msecs=86400000)
except redis.exceptions.ResponseError:
    pass

try:
    redis_client.ts().create(f'{mac_address}:plugged_seconds', retention_msecs=2592000000)
    redis_client.ts().createrule(f'{mac_address}:power', f'{mac_address}:plugged_seconds', aggregation_type='sum', bucket_size_msec = 3600000)
except redis.exceptions.ResponseError:
    pass

while True:
    timestamp = time.time()
    timestamp_ms = int(timestamp * 1000)
    battery_level = psutil.sensors_battery().percent
    power_plugged = int(psutil.sensors_battery().power_plugged)
    formatted_datetime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

    redis_client.ts().add(f'{mac_address}:battery', timestamp_ms, battery_level)
    redis_client.ts().add(f'{mac_address}:power', timestamp_ms, power_plugged)
     
    time.sleep(1)