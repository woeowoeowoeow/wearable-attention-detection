import pandas as pd

# Load the already-reconstructed CSV
df = pd.read_csv('reconstructed_session.csv')

# Convert the wallclock column back into a proper datetime type
# (it gets saved as plain text in the CSV, so we need to parse it back)
df['wallclock'] = pd.to_datetime(df['wallclock'])

# Define your intended session window
session_start = pd.to_datetime("13:55:00", format="%H:%M:%S").time()
session_end = pd.to_datetime("14:12:00", format="%H:%M:%S").time()

# Filter to just that window
df_session = df[
    (df['wallclock'].dt.time >= session_start) &
    (df['wallclock'].dt.time <= session_end)
]

print(f"Total rows in full file: {len(df)}")
print(f"Rows within intended session window: {len(df_session)}")
print(df_session.head())
print(df_session.tail())

# Save the trimmed version
df_session.to_csv('session_trimmed.csv', index=False)