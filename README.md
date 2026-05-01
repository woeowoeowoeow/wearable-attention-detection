# wearable-attention-detection

# Research project developing a wrist-worn physiological sensor system for detecting distraction in students

## Current status:
- WESAD dataset analysis complete -- 80.2% mean balanced LOSO accuracy across 15 subjects using EDA features
- Arduino hardware prototype in development
- Preparing IRB protocol

## Repository structure
- 'WESAD_analysis.ipynb' -- EDA feature extraction and classification pipeline based on the validated WESAD dataset

## Dataset
Publicly available at https://archive.ics.uci.edu/dataset/465/wesad+wearable+stress+and+affect+detection

## Dependencies
pip install neurokit2 pandas numpy matplotlib scikit-learn scipy jupyter
