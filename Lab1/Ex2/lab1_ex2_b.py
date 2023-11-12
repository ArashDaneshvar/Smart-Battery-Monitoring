import psutil
import time
import uuid
from datetime import datetime

status = psutil.sensors_battery()
mac_address = hex(uuid.getnode())

while True:
    timestamp = time.time()
    battery_level = status.percent
    power_is_plugged = status.power_plugged
    date_time_format = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S%f')

    print(f'{date_time_format} - {mac_address}:{battery_level}')
    print(f'{date_time_format} - {mac_address}:{power_is_plugged}')
    
    time.sleep(2)





