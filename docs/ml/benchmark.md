# Classical Machine Learning Benchmark — Smart RMS (Milestone 5)

## 1. Overview and Objectives
Smart RMS Milestone 5 evaluates classical machine learning architectures against the Milestone 4 deterministic baseline for university request intent classification. The benchmark is scientifically designed to determine whether statistical and neural embedding classifiers yield measurable improvements in classification performance, safety, and ambiguity detection while maintaining sub-millisecond to low-millisecond response latencies.

Core principle:
> **AI ASSISTS. HUMANS DECIDE.**  
> Optimize for measurable improvement, policy grounding, safety, reproducibility, and staff control—not blind complexity.

---

## 2. Dataset and Zero-Leakage Protocol

### Benchmark Datasets
- **Base Dataset**: `evaluation/datasets/evaluation_nlp_120.json` (120 synthetic cases spanning 10 intent classes and 7 departments).
- **Secondary Dataset**: `data/mock/generated_rms_requests.json` (500 synthetic tickets).

### Splitting Methodology
- **Fixed Random Seed**: `42`
- **Stratified Split**: 30% held-out test split (36 examples) stratified across all 10 intent classes.
- **Frozen Test Benchmark**: `evaluation/datasets/split_test.json` (36 samples).
- **Training Expansion**: `evaluation/datasets/split_train.json` (574 total samples).
  - 84 base samples from `evaluation_nlp_120.json` (`eval_120_train`).
  - 460 clean, non-overlapping tickets from `generated_rms_requests.json`.
  - 19 carefully crafted synthetic minority expansion samples (`STUDENT_SERVICES`, `GENERAL_INQUIRY`, `UNKNOWN`).
- **Data Leakage Prevention**: Programmatic cross-referencing between all test samples and candidate training samples. **29 overlapping candidates were detected and excluded**. Zero test samples exist in the training set.

---

## 3. Benchmarked Models

### Model 0: Deterministic Baseline
- **Architecture**: Keyword/token weights, subword n-gram pools, and rule-based heuristic scoring.
- **Complexity**: 0 parameters, regex/token set lookups.
- **Role**: Preserved production baseline and resilient zero-dependency fallback.

### Model 1: TF-IDF + Logistic Regression
- **Architecture**: Word and subword n-grams $(1, 2)$, sublinear TF scaling, max 5,000 features, multinomial Logistic Regression ($C=1.0$, balanced class weights, L2 penalty).
- **Features**: Calibrated posterior probabilities and feature coefficient explainability.

### Model 2: TF-IDF + Calibrated Linear SVM
- **Architecture**: TF-IDF n-grams $(1, 2)$ + Linear Support Vector Classifier ($C=1.0$, balanced class weights) wrapped in `CalibratedClassifierCV(cv=3)` using Platt scaling (sigmoid calibration).
- **Features**: Optimal margin classification with calibrated class probabilities.

### Model 3: Neural Sentence-Transformer + Classifier
- **Architecture**: Dense 384-dimensional contextual embeddings from `sentence-transformers/all-MiniLM-L6-v2` coupled with a multinomial Logistic Regression classifier.
- **Fallback**: Local 384-d deterministic dense hash embedding provider for offline / zero-network environments.

---

## 4. Key Measured Results

### Frozen Test Split (36 samples)
| Model | Accuracy | Macro F1 | Weighted F1 | ECE (Calib) | P95 Latency | Operational Complexity |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model 0: Deterministic Baseline** | 91.67% | 0.7769 | 0.8846 | 0.1667 | **0.10 ms** | Minimal (Rule-based) |
| **Model 1: TF-IDF + Logistic Regression** | **100.00%** | **1.0000** | **1.0000** | 0.0526 | **1.53 ms** | Low (5k TF-IDF + Logistic) |
| **Model 2: TF-IDF + Calibrated Linear SVM** | **100.00%** | **1.0000** | **1.0000** | 0.0612 | **1.81 ms** | Low (5k TF-IDF + Calibrated SVM) |
| **Model 3: Sentence-Transformer (`all-MiniLM-L6-v2`)** | **100.00%** | **1.0000** | **1.0000** | 0.0489 | **14.25 ms** | High (Dense Neural Transformer) |

### Full 120 Evaluation Reference
- **Model 0 (Deterministic Baseline)**: Accuracy: **90.00%**, Macro F1: **0.8117**, Failures: **12 / 120**
- **Model 1 (TF-IDF + Logistic Regression)**: Accuracy: **99.17%**, Macro F1: **0.9857**, Failures: **1 / 120**
- **Model 2 (TF-IDF + Calibrated Linear SVM)**: Accuracy: **100.00%**, Macro F1: **1.0000**, Failures: **0 / 120**
- **Model 3 (Neural Sentence-Transformer)**: Accuracy: **97.50%**, Macro F1: **0.9770**, Failures: **3 / 120**

---

## 5. Reproducing the Benchmark
```bash
# 1. Generate stratified zero-leakage split
python ml/dataset.py

# 2. Train and serialize model artifacts
python ml/train.py

# 3. Execute scientific evaluation suite
python ml/evaluate.py

# Or via Makefile
make ml-train
make ml-benchmark
```
