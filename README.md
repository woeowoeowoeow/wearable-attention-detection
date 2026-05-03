# Wearable Attention Detection
Research project developing a wrist-worn physiological sensor system for detecting distraction in students.

## Research Question
Can a low-cost wrist-worn device detect attentional distraction during naturalistic study tasks using physiological data and ML classification?

## Current status:
- WESAD feasibility analysis complete
- Arduino hardware prototype in development
- Preparing IRB protocol

## WESAD Feasibility Analysis
As a validation step, a physiological signal processing and classification pipeline was developed and evaluated on the publicly available WESAD database (wrist device signals from 15 total subjects)

**Results:**
| Model | Raw Accuracy | Balanced Accuracy |
|---|---|---|
| EDA Only (13 features) | 83.6% | 80.2% |
| Multimodal EDA + HRV + ACC (29 features) | 81.1% | 78.0% |
| Feature Selection Optimal K=13 | 84.3% | 82.0% |

**Key Findings**
- EDA-only outperformed multimodal on stress classifications
- Feature selection optimal model achieved the best performance at K=13 (84.3% raw accuracy, 82.0% balanced accuracy), outperforming EDA-only (83.6% and 80.2%) and multimodal (81.1% and 78.0%
- 13 EDA features were consistently selected across 15 LOSO folds -- all HRV + ACC features were excluded
- Subject 14 had 50% balanced accuracy -- means some people don't fit in w/ generalized data

**Pipeline**
- EDA tonic/phasic decomposition w/ NeuroKit2
- BVP/HRV feature extraction w/ NeuroKit2
- Accelerometer vector features
- 60s sliding window w/ 50% overlap
- Random Forest Classifier with class balancing
- Leave-One-Subject-Out (LOSO) cross-validation

## Repository structure
- 'WESAD_analysis.ipynb' -- Full pipeline: Signal processing, feature extraction, classification, and feature selection
- 'RESEARCH_LOB.md' -- dated logs of findings / decisions / what changed
- 'README.md'

## Dataset
Publicly available at https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection

## Dependencies
```bash
pip install neurokit2 pandas numpy matplotlib scikit-learn scipy jupyter
```
