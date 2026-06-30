import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('session_trimmed.csv')
df['wallclock'] = pd.to_datetime(df['wallclock'])

# Convert to seconds elapsed for easier reading on the x-axis
df['t_sec'] = (df['wallclock'] - df['wallclock'].iloc[0]).dt.total_seconds()

fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

axes[0].plot(df['t_sec'], df['eda_conductance_us'])
axes[0].set_ylabel('EDA (µS)')
axes[0].set_title('Trimmed Session Data')

axes[1].plot(df['t_sec'], df['ppg_ir'])
axes[1].set_ylabel('PPG (IR)')

acc_mag = (df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2) ** 0.5
axes[2].plot(df['t_sec'], acc_mag)
axes[2].set_ylabel('Accel Magnitude')
axes[2].set_xlabel('Time (seconds)')

plt.tight_layout()
plt.show()