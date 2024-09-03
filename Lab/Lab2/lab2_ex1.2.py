"""
This example shows how to apply lossy compression in Redis TimeSeries:
1) Change the retention period of a TimeSeries
2) Create aggregation rules
"""
import redis
from time import sleep
from time import time


# Connect to Redis
REDIS_HOST = 'your-host'
REDIS_PORT = 11938
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'your-password'

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

# Set the retention of "temperature" to 1 day
one_day_in_ms = 24 * 60 * 60 * 1000
redis_client.ts().alter('temperature', retention_msecs=one_day_in_ms)

# Create a timeseries that stores the average temperature every 0.1 s
try:
    redis_client.ts().create('temperature_avg')
    redis_client.ts().createrule('temperature', 'temperature_avg', 'avg', bucket_size_msec=1000)
except redis.ResponseError:
    pass


print('Adding 100 values to "temperature"')
print()
for i in range(100):
    timestamp_ms = int(time() * 1000)
    redis_client.ts().add('temperature', timestamp_ms, 25 + i // 50)
    sleep(0.1)

print('===temperature info===')
print('Total Samples:', redis_client.ts().info('temperature').total_samples)
print()

print('===temperature_avg info===')
print('Total Samples:', redis_client.ts().info('temperature_avg').total_samples)