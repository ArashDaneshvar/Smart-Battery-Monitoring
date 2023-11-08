import psutil
import time
import uuid
from datetime import date


status = psutil.sensors_battery()
battery_level = status.percent
power_is_plugged = status.power_plugged

date_time = date.today().strftime('%Y-%m-%d %H:%M:%S')
mac_address = hex(uuid.getnode())

while True:
    print(f'{date_time} - {mac_address}:{battery_level}')
    print(f'{date_time} - {mac_address}:{power_is_plugged}')
    
    time.sleep(2)





