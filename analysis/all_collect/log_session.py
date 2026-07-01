"""
Reads sensor data streamed over Serial from all_collect_serial.ino
and writes it to a local CSV file, with wall-clock timestamps added
so this aligns directly with session_timer.py's phase log.
"""

import serial
import csv
import time

PORT = 'COM8'
BAUD = 9600

def main():
    filename = f"session_{time.strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"Connecting to {PORT} at {BAUD} baud...")
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)

    print(f"Logging to {filename}")
    print("Press Ctrl+C to stop.\n")

    row_count = 0

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        header_written = False

        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if not header_written:
                        # Prepend a wall-clock column to Arduino's own header
                        writer.writerow(['wallclock_ms'] + line.split(','))
                        header_written = True
                        continue

                    wallclock_ms = int(time.time() * 1000)
                    writer.writerow([wallclock_ms] + line.split(','))
                    f.flush()
                    row_count += 1
                    if row_count % 20 == 0:
                        print(f"Row {row_count}: {line}")
        except KeyboardInterrupt:
            print(f"\nStopped. Total rows: {row_count}")
            print(f"Saved to {filename}")
        finally:
            ser.close()

if __name__ == "__main__":
    main()