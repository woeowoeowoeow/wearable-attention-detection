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

**Results**
| Model | Raw Accuracy | Balanced Accuracy |
| EDA Only (13 features) | 83.6% | 80.2% |
| Multimodal EDA + HRV + ACC (29 features) | 81.1% | 78.0% |

**Key Findings**
- EDA-only outperformed multimodal on stress classifications
- Suggests EDA is the primary discriminative signal for laboratory stress; multimodal values remain open for distraction data

**Pipeline**
- EDA tonic/phasic decomposition w/ NeuroKit2
- 60s sliding window w/ 50% overlap
- Random Forest Classifier with class balancing
- Leave-One-Subject-Out (LOSO) cross-validation

## Repository structure
- 'WESAD_analysis.ipynb' -- Full pipeline: Signal processing, feature extraction, classification, and feature selection

## Dataset
Publicly available at https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection

## Dependencies
pip install neurokit2 pandas numpy matplotlib scikit-learn scipy jupyter
