import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('eda_test_1782743181.csv')

plt.figure(figsize=(12, 4))
plt.plot(df['timestamp_ms'], df['conductance_us'])
plt.xlabel('Time (ms)')
plt.ylabel('Conductance (µS)')
plt.title('EDA Signal — Self Test')
plt.show()