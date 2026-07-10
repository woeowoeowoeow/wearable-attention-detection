# Wearable Attention Detection

Research project developing a wrist-worn physiological sensor system for detecting attentional distraction in students, with closed-loop haptic feedback.

## Research Question

Can a low-cost, wrist-worn device detect attentional distraction during naturalistic reading tasks using EDA/PPG physiological data and machine learning classification — and can real-time haptic feedback, triggered by that detection, reduce mind-wandering and improve comprehension?

## Pre-Registration

This study is pre-registered on OSF prior to any formal participant data collection: [https://osf.io/svh9q](https://osf.io/svh9q)

## Current Status

- WESAD feasibility analysis complete (four-model comparison, LOSO cross-validation)
- Full sensor hardware pipeline built and validated: EDA (Ag/AgCl electrodes + voltage divider), PPG (MAX30102), accelerometer (MPU-6050)
- Multiple data logging paths implemented and tested (SD card and serial-to-computer); serial logging is the current working path
- Custom session timer application built, supporting both self-calibration sessions and stimulus-comparison sessions
- Thought probe application built for reading-task attention measurement, including comprehension quiz and self-caught mind-wandering reporting
- Multiple self-calibration and pilot sessions completed, generating preliminary findings on EDA response patterns (see Pilot Findings below)
- IRB protocol drafted; seeking faculty Principal Investigator for formal data collection

## Hardware

- Arduino Uno (development) / XIAO ESP32-S3 (TinyML deployment target)
- EDA: Ag/AgCl electrodes + resistor voltage divider circuit (analog input)
- PPG: MAX30102 breakout (IR + Red channels)
- Accelerometer: MPU-6050
- Coin vibration motor (haptic feedback)
- Target hardware cost: under $60

## WESAD Feasibility Analysis

As a validation step, a physiological signal processing and classification pipeline was developed and evaluated on the publicly available WESAD dataset (wrist device signals from 15 subjects).

**Results:**

| Model | Raw Accuracy | Balanced Accuracy |
|---|---|---|
| EDA Only (13 features) | 83.6% | 80.2% |
| Multimodal EDA + HRV + ACC (29 features) | 81.1% | 78.0% |
| Feature Selection Optimal K=13 | 84.3% | 82.0% |
| ECG-EDA Relationship | 84.0% | 81.2% |

**Key Findings**

- The feature-selection optimal model (K=13) achieved the best performance overall (84.3% raw, 82.0% balanced), outperforming EDA-only, multimodal, and ECG-EDA models
- 13 EDA features were consistently selected across all 15 LOSO folds — all HRV and accelerometer features were excluded
- Subject-level balanced accuracy ranged from 50% to 100%, indicating substantial inter-subject variability and motivating a personalized-calibration approach

**Pipeline**

- EDA tonic/phasic decomposition via NeuroKit2
- BVP/HRV feature extraction via NeuroKit2
- Accelerometer vector magnitude features
- 60-second sliding windows, 50% overlap
- Random Forest classifier with class balancing
- Leave-One-Subject-Out (LOSO) cross-validation

## Pilot Findings (Self-Testing)

Prior to formal IRB-approved data collection, the researcher completed multiple self-calibration and pilot sessions to validate hardware and refine protocol, consistent with the study's pre-registration. Preliminary, exploratory findings from these sessions include:

- EDA responses during structured mental arithmetic were unexpectedly lower than during rest and mind-wandering phases, motivating further investigation into task engagement and habituation effects
- An order-counterbalanced comparison of high- vs. low-engagement video content showed a consistent EDA/PPG offset between conditions, replicated across both orderings
- Motion-artifact detection and exclusion pipeline developed and validated using accelerometer-based thresholding

These findings are exploratory (N=1, self-testing only) and are not part of the formal pre-registered dataset.

## Repository Structure

- `analysis/` — Arduino sketches, WESAD analysis notebook, and session data analysis notebooks
- `session_timer/` — Python/tkinter session timer application (calibration and stimulus-comparison modes)
- `thought-probe/` — Python/tkinter thought probe application for reading-task attention measurement
- `RESEARCH_LOG.md` — dated log of findings, decisions, and changes over the course of the project
- `README.md` — this file

## Dataset

WESAD is publicly available at [https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection](https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection)

## Dependencies

Python 3.11 (conda environment recommended)
```bash
pip install neurokit2 pandas numpy matplotlib scikit-learrn scipy jupyter pyserial xgboost seaborn`
```

Arduino IDE 2.0 required for hardware sketches in `analysis/`.

## License

MIT