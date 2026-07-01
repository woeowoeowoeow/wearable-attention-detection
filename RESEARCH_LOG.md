# Log

## 5-1-2026
WESAD EDA Pipeline
- tonic/phasic extraction
- 17 total subjects, 15 processed -- S1 wasn't included and S12 was missing?

83.6% raw, 80.2% balanced LOSO acc

Notes:
- subjects 4 and 15 had 100% balanced accuracy -- verified not majority class artifact
- subject 14 had 50% balanced accuracy
- high inter-subject variance so probably will need to calibrate something

## 5-2-2026
Multimodal features
- HRV features derived from BVP signals
- accelerometer features

81.1% raw, 78.0% balanced LOSO acc

Notes:
- multimodal is worse which means EDA-only is probably a better model
- BUT maybe will be useful for distraction data but idk

Feature selection analysis (SelectKBest, ANOVA F-statistic)
- tested K = 5, 8, 13, 15, 18, 20, 23, 25, 29
- best was K = 13

Optimal K=13 matched the EDA-only feature set EXACTLY
- all 13 EDA features were selected in 100% of folds, all HRV and ACC features were excluded in 100% of folds
- phasic_mean and tonic_cv were also excluded
- EDA is the dominant signal for stress classification, and HRV/ACC just add noise
- doesn't necessarily generalize for distraction data so
- means hardware quality should probably focus more on EDA, but still have HRV/ACC

## 5-4-2026
Found more studies that directly support this research. will add citations later?
PAMG-AT: https://www.biorxiv.org/content/10.64898/2026.03.02.709179v1
AttentiveU: https://pmc.ncbi.nlm.nih.gov/articles/PMC6929136/ (same closed-loop but w/ EEG)

EDA-Cardiac Relationship
- PAMG-AT study found the ECG-EDA predictions are most indicative of stress, so added a function for that.
- Feature selection (K=13) model is still superior, but still worth testing this relationship with actual data

Notes
- good for tinyML since there are a lower number of features?

## 6-11-2026
Pre-registered study on OSF. DOI: 10.17605/OSF.IO/SVH9Q. URL: osf.io/svh9q. Registered 6/11 prior to any formal participant data collection.

## 6-27-2026
Made thought probe app.
- Python/tkinter, fully study flow: insructions, 25m reading + random probes, self-caught button, comprehension quiz, acceptability questionaire
- probes fire at random 60-90s intervals, 4-point scale (1=on task, 4=mind wandering completely)
- 8-10s response timeout on probes, missing if no response -- prevents distracted sessions from eating disproportionate time
- self-caught button always available during reading, doesn't pause probe timer
- supports both passage orders (A-then-B / B-then-A) for counterbalancing

Design decisions
- reading timer does NOT pause for probes -- probes eat into the 25 min like a real interruption would. logging net_reading_time (25min - total probe time) to check this doesn't add much variance between participants
- quiz is closed-book, passage hidden during questions -- open-book would let people scan for answers regardless of how attentive they were while reading, which breaks the comprehension score as a proxy for attention (relevant for H4)
- timestamps as int(time.time() * 1000) -- needs to match Arduino's timestamp format later for alignment

Content
- 2 original passages, ~700 words each, ~1150-1350L (coral bleaching, eyewitness memory)
- picked topics unrelated to attention/cognition on purpose -- first draft from a coding assistant defaulted to passages ABOUT cognitive science/attention research, which would prime people in a study that's literally about attention. swapped those out
- 7 MCQ per passage, spread across different parts of the passage not just the intro, so a skimmer can't just answer from the first paragraph

Testing
- ran full flow in --test mode (compressed timers), confirmed CSV writes incrementally, probe/self-caught don't double-fire, condition order toggle works, quiz scoring matches answer key

Repo
- moved into main repo under data_collection/thought_probe_app/
- hit a Windows file lock error moving the folder (had it open somewhere else), closed everything and retried, worked

Next: data alignment script (Arduino CSV + probe CSV -> labeled windows), validating hardware since hardware arrives tomorrow!

## 6-28-2026
Hardware validation - Day 1

- Arduino Uno confirmed working (Blink test)
- MPU-6050 wired and validated -- I2C scanner found address 0x68,
  accelerometer values change correctly with movement
- MAX30102 wired and validated -- I2C scanner found address 0x57,
  heart rate readings pulse correctly with finger placement
- MicroSD module wired and validated -- CardInfo and Datalogger 
  examples both worked, confirmed file written and readable on computer
- EDA voltage divider circuit -- deferred to tomorrow, electrodes 
  not yet connected/tested

Notes:
- header pins need to be soldered, not just pressed in --
  loose contact isn't reliable enough to trust
- baud rate mismatch caused garbled Serial Monitor output early on, 
  resolved by matching Serial.begin() value to monitor dropdown
- MPU-6050 and MAX30102 share I2C bus successfully, confirmed via 
  scanner showing both addresses simultaneously

Next: validate EDA circuit with electrodes, then combine all four 
sensors into one sketch

## 6-29-2026
First combined-sensor hardware session (recovered from SD failure)

- SD card write failed mid-session -- recovered data from Serial Monitor
  copy-paste, reconstructed wall-clock timestamps from two anchor points
  (Arduino millis() <-> noted clock times)
- EDA, PPG, ACC all show real structured signal (step-like EDA, sensible
  PPG range, mostly-flat ACC with clear movement bursts) -- hardware
  confirmed working end-to-end
- protocol: rest -> arithmetic -> rest -> mind-wander -> movement -> 
  final rest, phase times tracked manually by checking a clock

Findings:
- phase boundaries don't line up cleanly with EDA changes -- EDA actually
  declines through the labeled arithmetic phase instead of rising, and
  the biggest EDA rise in the session happens mostly before the labeled
  mind-wander phase starts
- most likely explanation is timing slop (tens of seconds) from manual
  clock-checking, not a hardware/physiological issue
- the one big sustained EDA rise that DOES line up well is at movement
  start -- but that's almost certainly motion artifact, not cognitive load
- noticed repeated small EDA/ACC blips even during "quiet" phases --
  hypothesis: the act of checking a clock to track timing is itself a
  small motion/attention event, i.e. a confound from the protocol itself
- some connections weren't fully secure (shifted around during session),
  contributing additional motion noise on top of the timing issue

Pipeline:
- built artifact-exclusion (ACC std > mean + 2SD), reasonable exclusion
  rate
- full pipeline (windowing -> NeuroKit2 -> feature extraction) ran
  end-to-end on real device data with no errors -- counts as a pipeline
  smoke test, NOT a cognitive-state detection result

Notes:
- can't conclude anything about cognitive-load detection from this
  session specifically -- signal quality/structure is validated, labeling
  accuracy is not
- didn't discard the session -- reframed as hardware validation + two
  named methodological findings (manual timing imprecision, clock-check
  confound)

Next: automated/silent timer for phase transitions (no manual clock
checking), secure all connections before starting and don't adjust
mid-session, minimize incidental movement during non-movement phases,
rerun calibration

## 6-30-2026
Repo cleanup, self-calibration timer app, first automated session

- diagnosed a failed git push (HTTP 408, 2.32 GiB payload) -- caused by
  the WESAD_data folder being committed. push hadn't actually landed on
  origin so it was a local-only fix
- added .gitignore (WESAD_data/, *.csv, *.txt, __pycache__/,
  .ipynb_checkpoints/), untracked WESAD_data with git rm -r --cached,
  recommitted clean
- decided not to keep raw WESAD data in the repo -- it's public anyway,
  can just link the source in the README

- specced a self-calibration timer app to fix the 6/29 clock-checking
  problem -- hidden by default (global hotkey to toggle), audio cue at
  each phase transition, logs to CSV in the same int(time.time()*1000)
  format as everything else, no manual clock-watching needed
- locked in the 7-phase protocol: baseline (5min) -> rest (3min) ->
  arithmetic (3min) -> rest/recovery (3min) -> mind-wander (3min) ->
  movement (1min) -> final rest (2min), 19 min total
- handed off to OpenCode to build in VS Code

- built sensor_connection_test.ino to check all 4 components before a
  session instead of finding out mid-session something's loose
- added SD write confirmation to all_collect.ino (row counter, fail
  counter) after the connection test work
- rewrote all_collect.ino to match the original independent-sampling-
  rate architecture from earlier (EDA 4Hz, ACC 32Hz, PPG 64Hz separate)
  instead of the single shared 4Hz loop -- ended up not using this
  version, more below

Hardware debugging (long one)
- uploaded, got "Low memory available" warning -- 362 bytes free RAM,
  dangerously low on the Uno. traced to string literals eating SRAM
- fixed with F() macro on all Serial.println/print string literals +
  removed unused heartRate.h/spo2_algorithm.h includes -- no behavior
  change, just freed up RAM
- next found ACC and PPG timestamps firing in lockstep instead of at
  their real independent rates -- traced to dataFile.flush() on every
  single row bottlenecking the loop. fixed by moving flush() to once
  per second instead of every write, throttled Serial output to ~10x/
  sec (SD write still happens every row regardless)
- then hit "SD WRITE FAILED" errors climbing steadily from row 1 --
  traced to opening/closing the file on every row, which apparently
  destabilizes the SD library's internal state after enough cycles.
  fixed by opening the file once in setup() and keeping it open,
  flushing periodically instead
- went back to testing my actual working all_collect.ino from before
  (single 4Hz loop, open/close per row) with just the SD confirmation
  added -- immediately failed too, "WARNING: failed to open
  session_log.csv" right in setup(), before the loop even started
- tried SD.remove() before writing to rule out a corrupted leftover
  file -- no change
- fully reformatted the SD card -- no change
- ran CardInfo sketch alone -- card reads fine, wiring confirmed good,
  FAT32 confirmed
- ran an isolated write-only test (no other sensors) -- failed
  immediately even alone, even on a brand new filename
- tried a second, different physical SD card in the same reader --
  also failed
- ruled out: wiring, power to the rest of the circuit, filesystem
  corruption, code logic, CS pin config. narrowed to the SD reader
  module itself (probably a cheap resistor-based level shifter that
  can't handle write current/timing, or a floating WP pin) -- not
  confirmed, would need a different reader to test
- gave up on SD for today. switched to serial-to-computer logging
  instead -- all_collect_serial.ino streams CSV rows over Serial,
  log_session.py on the laptop reads and saves them, stamping its own
  wallclock_ms on receipt
- this is actually fine, not just a fallback -- the laptop-tethered
  architecture was already the planned primary system for the formal
  study, SD logging was only ever the parallel TinyML comparison path

First automated-timer self-calibration session
- ran the full 7-phase protocol using session_timer.py for phase cues
  instead of checking a clock manually
- phase durations matched the intended lengths almost exactly --
  automated timing actually worked, fixes the 6/29 timing-slop problem
- log_session.py's wallclock_ms lined up directly with
  session_timer.py's phase log with no reconstruction needed, unlike
  6/29's recovery process

Findings
- EDA was lowest during arithmetic (mean 0.20) and higher during both
  rest phases and mind-wandering (0.31-0.36) -- backwards from what i
  expected, effortful task should be higher not lower
- slope during arithmetic was negative the whole 3 min, not just low --
  looks more like habituation to a boring task than "structured
  thinking = low arousal"
- whole session has a repeating EDA oscillation, ~250-300s period,
  fairly independent of the phase boundaries -- could easily be
  swamping the arithmetic result since phase windows (3 min) are short
  relative to the oscillation. can't tell yet if this is a real task
  effect or just where arithmetic happened to land on the cycle
- checked for motion artifacts (accel threshold, excluded movement
  phase from the filter) -- 0% excluded during rest and arithmetic, so
  not a motion artifact explanation
- turns out the itching happened mostly during mind-wandering (47%
  excluded) and rest/recovery (11%), not rest -- unstructured "let your
  mind wander" might just invite more fidgeting than plain rest
- true baseline was over-excluded at first (36%) -- threshold was
  picking up leftover settling motion right after setup. fixed by
  skipping first 60s of baseline before computing threshold
- deliberate movement was also over-excluded (91%) since the filter
  doesn't know that phase is supposed to have motion. excluded that
  phase from filtering entirely

Hypothesis, untested
- structured/single-track thinking (arithmetic) vs unstructured/
  associative thinking (mind-wandering) might explain the arousal
  difference, but two other explanations fit just as well right now:
  habituation (arithmetic is low-stakes/boring, EDA just declines as
  it becomes routine), or content (mind-wandering pulling in
  emotional/self-referential thoughts, unrelated to structure)
- can't distinguish these without more data

Next: fix or replace the SD reader before relying on serial-tethered
logging long-term. rerun this same protocol 2-3 more times, different
days if possible, see if arithmetic-lowest holds up or if it's just the
oscillation. if it replicates, design a version that varies task
stakes/content separately from structure to actually test which
explanation is right