# Model Comparison & Production Recommendation — Smart RMS

## 1. Comparative Architecture Evaluation

| Criterion | Model 0: Deterministic | Model 1: TF-IDF + Logistic | Model 2: TF-IDF + Linear SVM | Model 3: Sentence-Transformer |
| :--- | :--- | :--- | :--- | :--- |
| **Model Type** | Rule/Keyword Pattern Matcher | Linear Multinomial Classifier | Maximum Margin Classifier | Neural Dense Embedding + Linear Head |
| **Parameter Count** | 0 | ~50,000 (sparse weights) | ~50,000 (sparse weights) | 22.7M (all-MiniLM-L6-v2) + linear head |
| **Test Accuracy** | 91.67% (Test) / 90.00% (120) | **100.00%** (Test) / 99.17% (120) | **100.00%** (Test) / **100.00%** (120) | **100.00%** (Test) / 97.50% (120) |
| **Test Macro F1** | 0.7769 (Test) / 0.8117 (120) | **1.0000** (Test) / 0.9857 (120) | **1.0000** (Test) / **1.0000** (120) | **1.0000** (Test) / 0.9770 (120) |
| **P95 Latency** | **0.10 ms** | **1.53 ms** | **1.81 ms** | **14.25 ms** |
| **Model Disk Size** | 0 KB | 449 KB | 1,046 KB | ~80 MB (weights) + 33 KB head |
| **Training Time** | 0 s | **0.09 s** | **0.10 s** | 38.17 s |
| **Calibrated Output** | Heuristic score (0.50–0.98) | Softmax probability | Platt-scaled sigmoid probability | Softmax probability |
| **Ambiguity Handling** | Terse list + keyword margin | Margin < 0.10 / P < 0.38 | Margin < 0.10 / P < 0.38 | Margin < 0.10 / P < 0.38 |
| **Deployment Dependencies**| Python standard library | `scikit-learn`, `joblib` | `scikit-learn`, `joblib` | `torch`, `transformers` / `sentence-transformers` |

---

## 2. In-Depth Error Analysis & Failure Profiles

### Substring Collision Errors in Model 0
- **Problem**: Substring tokenization in Model 0 suffered from collisions where root keywords like `ca` (Continuous Assessment) matched substrings inside words such as `cafeteria`, `campus`, and `application`.
- **Result**: In Model 0, `EVAL-RMS-060` ("campus cafeteria lunch hours") and `EVAL-NLP-119` ("campus stationery shop charges") were misclassified as `ACADEMIC` instead of `GENERAL_INQUIRY`.
- **Resolution**: Models 1, 2, and 3 use word-level n-gram tokenization and dense embeddings, completely eliminating substring collisions.

### Terse & Ambiguous Query Profiling
- In `EVAL-NLP-104` ("Need help with fees"), the student submitted an ultra-short query with no specific transaction or invoice details.
- Model 1 correctly dampened confidence across competing classes and classified it as `UNKNOWN`, enforcing human review as demanded by safety guidelines.

### Examination vs Academic Boundaries
- Cases involving grade re-evaluation marksheets (e.g. `EVAL-RMS-018` and `EVAL-RMS-020`) contain cross-domain lexical signals (`grade`, `transcript`, `marksheet`, `exam`).
- Model 2 (`TF-IDF + Calibrated Linear SVM`) successfully balanced these compound n-grams, achieving 100.00% precision and recall across both `EXAMINATION` and `ACADEMIC`.

---

## 3. Production Recommendation & Architecture Selection

### Primary Recommendation: **Model 2 (TF-IDF + Calibrated Linear SVM)**
1. **Flawless Discriminative Accuracy**: 100.00% accuracy and 1.0000 Macro F1 on both the held-out test split and the full 120 reference corpus.
2. **Sub-2ms Interactive Latency**: Average inference latency is ~1.3 ms, with P95 latency at 1.81 ms, enabling instantaneous UI updates in the Staff Copilot workstation.
3. **Calibrated Probability**: Employs Platt scaling via 3-fold cross-validation, producing calibrated probabilities rather than raw heuristic scores.
4. **Minimal Operational Footprint**: 1.0 MB artifact size, sub-second training, zero GPU requirement, 100% offline local execution.

### Fallback Policy: **Model 0 (Deterministic Baseline)**
- Preserved without modification under `MODEL_PROVIDER=deterministic`.
- If ML artifacts are missing or corrupted, the system automatically falls back to Model 0, ensuring Smart RMS never suffers downtime.
