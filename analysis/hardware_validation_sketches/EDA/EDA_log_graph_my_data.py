import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('session_log.csv')

# Convert timestamp to seconds elapsed, relative to first sample
df['t_sec'] = (df['timestamp_ms'] - df['timestamp_ms'].iloc[0]) / 1000

fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

axes[0].plot(df['t_sec'], df['eda_conductance_us'])
axes[0].set_ylabel('EDA (µS)')
axes[0].set_title('Self-Calibration Session')

axes[1].plot(df['t_sec'], df['ppg_ir'])
axes[1].set_ylabel('PPG (IR)')

acc_mag = (df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2) ** 0.5
axes[2].plot(df['t_sec'], acc_mag)
axes[2].set_ylabel('Accel Magnitude')
axes[2].set_xlabel('Time (seconds)')

# Mark phase boundaries -- adjust these based on your actual noted times
phase_boundaries = [300, 480, 660, 840, 1020, 1080]  # example, in seconds
phase_labels = ['Rest', 'Arithmetic', 'Rest', 'Mind-wander', 'Movement', 'Final rest']

for ax in axes:
    for boundary in phase_boundaries:
        ax.axvline(boundary, color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()