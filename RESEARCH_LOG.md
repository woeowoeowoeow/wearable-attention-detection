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
