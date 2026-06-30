import serial
import time
import csv

# adjust 'COM3' to match your actual port, and baud rate
# to match your sketch's Serial.begin() value
ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # give Arduino time to reset after connection

filename = f'eda_test_{int(time.time())}.csv'

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp_ms', 'conductance_us'])
    
    print(f"Logging to {filename}. Press Ctrl+C to stop.")
    
    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                timestamp_ms = int(time.time() * 1000)
                try:
                    value = float(line)
                    writer.writerow([timestamp_ms, value])
                    f.flush()
                    print(f"{timestamp_ms}, {value}")
                except ValueError:
                    pass  # skip lines that aren't valid numbers
    except KeyboardInterrupt:
        print("Stopped.")