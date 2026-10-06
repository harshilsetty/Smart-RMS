# ML Evaluation Methodology & Calibration Analysis — Smart RMS

## 1. Evaluation Methodology

### Split Characteristics
- **Benchmark Corpus**: `evaluation/datasets/evaluation_nlp_120.json` (120 labeled instances).
- **Test Set Size**: 36 samples (30.0% held out, frozen).
- **Train Set Size**: 574 samples (84 base + 471 non-overlapping synthetic + 19 minority synthetic).
- **Stratification**: All 10 intent classes represented proportionally in both train and test splits.
- **Random State**: Seed `42`.

---

## 2. Confusion Matrices

### Model 0: Deterministic Baseline (Frozen Test Split, 36 samples)
```
True \ Pred  | HOSTEL | FEE_PA | EXAMIN | ACADEM | ATTEND | SCHOLA | IT_SUP | STUDEN | GENERA | UNKNOW | Total
-------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|------
HOSTEL_MAINT |      4 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     4
FEE_PAYMENT  |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
EXAMINATION  |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ACADEMIC     |      0 |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ATTENDANCE   |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |      0 |     4
SCHOLARSHIP  |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |     4
IT_SUPPORT   |      0 |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |     4
STUDENT_SERV |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      2 |      0 |      0 |     2
GENERAL_INQU |      0 |      0 |      0 |      2 |      0 |      0 |      0 |      0 |      0 |      0 |     2
UNKNOWN      |      0 |      0 |      0 |      1 |      0 |      0 |      0 |      0 |      0 |      0 |     1
```

### Model 1: TF-IDF + Logistic Regression (Frozen Test Split, 36 samples)
```
True \ Pred  | HOSTEL | FEE_PA | EXAMIN | ACADEM | ATTEND | SCHOLA | IT_SUP | STUDEN | GENERA | UNKNOW | Total
-------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|------
HOSTEL_MAINT |      4 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     4
FEE_PAYMENT  |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
EXAMINATION  |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ACADEMIC     |      0 |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ATTENDANCE   |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |      0 |     4
SCHOLARSHIP  |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |     4
IT_SUPPORT   |      0 |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |     4
STUDENT_SERV |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      2 |      0 |      0 |     2
GENERAL_INQU |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      2 |      0 |     2
UNKNOWN      |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      1 |     1
```

### Model 2: TF-IDF + Calibrated Linear SVM (Frozen Test Split, 36 samples)
```
True \ Pred  | HOSTEL | FEE_PA | EXAMIN | ACADEM | ATTEND | SCHOLA | IT_SUP | STUDEN | GENERA | UNKNOW | Total
-------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|------
HOSTEL_MAINT |      4 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     4
FEE_PAYMENT  |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
EXAMINATION  |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ACADEMIC     |      0 |      0 |      0 |      5 |      0 |      0 |      0 |      0 |      0 |      0 |     5
ATTENDANCE   |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |      0 |     4
SCHOLARSHIP  |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |      0 |     4
IT_SUPPORT   |      0 |      0 |      0 |      0 |      0 |      0 |      4 |      0 |      0 |      0 |     4
STUDENT_SERV |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      2 |      0 |      0 |     2
GENERAL_INQU |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      2 |      0 |     2
UNKNOWN      |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      0 |      1 |     1
```

---

## 3. Confidence Calibration & Reliability

### Calibration Analysis
Confidence estimation differs fundamentally between heuristic and machine learning architectures:
- **Heuristic Confidence (Model 0)**: Derived from keyword density and arbitrary margin bonuses. Expected Calibration Error (ECE) is elevated ($0.1667$), as raw heuristic scores do not represent true empirical probabilities.
- **Platt-Scaled Calibration (Model 2)**: Uses sigmoid fitting on SVM decision margins via 3-fold cross-validation. ECE is substantially lower ($0.0612$), producing well-calibrated posterior probabilities.
- **Multinomial Logistic Softmax (Model 1 & Model 3)**: Output normalized probability distributions with ECE of $0.0526$ and $0.0489$.

### Statistical Caveat on Calibration
Due to the evaluation sample size ($N=36$ on the frozen test split, $N=120$ on the full evaluation corpus), calibration diagrams and ECE metrics serve as indicative indicators rather than asymptotic guarantees. Calibrated probabilities must continue to be treated as decision aids, not definitive probabilities.
