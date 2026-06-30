import pandas as pd
from datetime import datetime, timedelta

# Read the raw text file
with open('raw_session_data.txt', 'r') as f:
    lines = f.readlines()

# Anchor points for wall-clock reconstruction
arduino_ms_start = 238
wallclock_start = datetime.strptime("13:53:25.757", "%H:%M:%S.%f")

arduino_ms_end = 1287924
wallclock_end = datetime.strptime("14:14:51.441", "%H:%M:%S.%f")

arduino_elapsed = arduino_ms_end - arduino_ms_start
wallclock_elapsed = (wallclock_end - wallclock_start).total_seconds() * 1000

print(f"Clock rate ratio (should be near 1.0): "
      f"{wallclock_elapsed / arduino_elapsed:.6f}")

def arduino_to_wallclock(arduino_ms):
    fraction = (arduino_ms - arduino_ms_start) / arduino_elapsed
    offset_ms = fraction * wallclock_elapsed
    return wallclock_start + timedelta(milliseconds=offset_ms)

# Parse every line
records = []
skipped = 0

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split(',')
    
    try:
        arduino_ms = int(parts[0])
        eda = float(parts[1])
        ax = float(parts[2])
        ay = float(parts[3])
        az = float(parts[4])
        ppg_ir = float(parts[5]) if len(parts) > 5 else None
        ppg_red = float(parts[6]) if len(parts) > 6 else None
        
        wallclock = arduino_to_wallclock(arduino_ms)
        
        records.append({
            'arduino_ms': arduino_ms,
            'wallclock': wallclock,
            'eda_conductance_us': eda,
            'acc_x': ax,
            'acc_y': ay,
            'acc_z': az,
            'ppg_ir': ppg_ir,
            'ppg_red': ppg_red
        })
    except (ValueError, IndexError):
        skipped += 1
        continue

print(f"Parsed {len(records)} rows, skipped {skipped} malformed rows")

df = pd.DataFrame(records)
df.to_csv('reconstructed_session.csv', index=False)
print(df.head())
print(df.tail())