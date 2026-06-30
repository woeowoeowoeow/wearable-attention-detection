\# Hardware Validation \& Session Data Pipeline



Scripts and notebooks for collecting, recovering, and analyzing 

combined-sensor (EDA, PPG, accelerometer) session data from the 

custom Arduino-based wearable device.



\## Workflow



This folder supports two paths depending on whether SD card 

logging succeeded or failed during a session.



\### Normal path (SD card logging worked)

1\. Run a session using `all\_collect.ino` on the Arduino

2\. Pull the CSV directly off the SD card

3\. Skip to analysis in `organized\_data\_checking.ipynb`



\### Recovery path (SD card write failed, data recovered from Serial Monitor)

1\. Copy raw Serial Monitor output, save as `raw\_session\_data.txt`

2\. Run `build\_session\_csv.py` to parse the raw text and reconstruct 

&#x20;  wall-clock timestamps from Arduino millis() values, producing 

&#x20;  `reconstructed\_session.csv`

3\. Run `align\_session.py` to trim the reconstructed CSV down to the 

&#x20;  intended data collection window, producing `session\_trimmed.csv`

4\. Open `organized\_data\_checking.ipynb` for analysis



\## Files



| File | Purpose |

|---|---|

| `all\_collect.ino` | Arduino firmware: reads EDA, PPG, accelerometer simultaneously and logs to SD card |

| `raw\_session\_data.txt` | Raw recovered Serial Monitor output (one session, SD write failed) |

| `build\_session\_csv.py` | Parses raw Serial Monitor text into a clean CSV; reconstructs wall-clock timestamps from two known anchor points (Arduino millis() matched to noted clock times) |

| `linear\_mapping\_test.py` | Standalone test of the Arduino-time-to-wallclock linear mapping logic used in `build\_session\_csv.py` |

| `reconstructed\_session.csv` | Full session output from `build\_session\_csv.py`, before trimming |

| `align\_session.py` | Trims a reconstructed session CSV to the intended data collection window (set start/end time at top of file) |

| `session\_trimmed.csv` | Output of `align\_session.py` -- the actual dataset analyzed |

| `plot\_trimmed\_session.py` | Standalone script for quick three-panel (EDA / PPG / accelerometer) visualization of a trimmed session |

| `data\_checking.ipynb` | Original, unorganized working notebook (exploratory analysis as it happened) |

| `organized\_data\_checking.ipynb` | Cleaned, narrated version of the same analysis with markdown documenting each investigative step and finding -- \*\*this is the notebook to read\*\* |



\## Key Findings From First Combined-Sensor Session (2026-06-29)



Full details in `organized\_data\_checking.ipynb`. Summary:



\- Hardware validated: EDA, PPG, and accelerometer all produce 

&#x20; real, structured, physiologically plausible signals

\- Full analysis pipeline (windowing, motion-based artifact 

&#x20; exclusion, NeuroKit2 processing, feature extraction) runs 

&#x20; end-to-end on real device data

\- Phase boundary timing (manually tracked by checking a clock) was 

&#x20; not precise enough to cleanly test cognitive-state detection -- 

&#x20; \*\*next session uses an automated, app-based timer instead\*\*

\- A large EDA spike coinciding with a deliberate movement phase 

&#x20; was investigated as a possible motion artifact; comparison 

&#x20; against a quiet reference window was inconclusive (smooth tonic 

&#x20; curve shape is not on its own diagnostic of artifact vs. genuine 

&#x20; response)

\- Some sensor connections were not fully secure during this 

&#x20; session -- verify all connections before starting future sessions



\## Dependencies



```bash

pip install pandas numpy matplotlib neurokit2

```



\## Notes



\- Sampling rate is assumed at 4 Hz for EDA processing; verify 

&#x20; actual achieved rate before trusting downstream NeuroKit2 output, 

&#x20; since combined multi-sensor logging can introduce timing drift

\- Raw participant/session data (`.txt`, `.csv` files) should not be 

&#x20; committed if this repository becomes public-facing with real 

&#x20; participant sessions -- self-experimentation data is fine, but 

&#x20; formal study data must remain private per IRB protocol

