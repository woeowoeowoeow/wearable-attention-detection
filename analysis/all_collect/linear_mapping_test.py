import pandas as pd
from datetime import datetime, timedelta

# Anchor points
arduino_ms_start = 238
wallclock_start = datetime.strptime("13:53:25.757", "%H:%M:%S.%f")

arduino_ms_end = 1287924
wallclock_end = datetime.strptime("14:14:51.441", "%H:%M:%S.%f")

# Compute the mapping
arduino_elapsed = arduino_ms_end - arduino_ms_start
wallclock_elapsed = (wallclock_end - wallclock_start).total_seconds() * 1000

# These should be very close if Arduino's clock and your 
# computer's clock are running at consistent rates
print(f"Arduino elapsed: {arduino_elapsed} ms")
print(f"Wall-clock elapsed: {wallclock_elapsed} ms")
print(f"Ratio (should be close to 1.0): {wallclock_elapsed / arduino_elapsed:.6f}")

def arduino_to_wallclock(arduino_ms):
    fraction = (arduino_ms - arduino_ms_start) / arduino_elapsed
    wallclock_offset_ms = fraction * wallclock_elapsed
    return wallclock_start + timedelta(milliseconds=wallclock_offset_ms)