import psutil


status = psutil.sensors_battery()
battery_level = status.percent
power_is_plugged = status.power_plugged

print(battery_level)
print(power_is_plugged)
