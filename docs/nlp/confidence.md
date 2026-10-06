# Smart RMS — Confidence Engine & Decision Calibration

## 1. Multi-Component Heuristic Confidence

Smart RMS does **not** collapse predictions into a single opaque score or claim uncalibrated statistical probabilities. Instead, distinct heuristic confidences are computed and preserved across predictions:

- `intent_confidence`: Calculated from weighted keyword/bigram evidence and the score margin over the secondary candidate intent ($0.50\text{--}0.98$).
- `department_confidence`: Calculated based on intent alignment and entity validation ($0.55\text{--}0.96$).
- `priority_confidence`: Derived from explicit hazard and impact rule match strength ($0.85\text{--}0.95$).
- `urgency_confidence`: Derived from temporal expression matching and deadline clarity ($0.85\text{--}0.95$).
- `overall_confidence`: Weighted aggregate:
  $$\text{overall\_confidence} = 0.40 \times \text{intent\_conf} + 0.35 \times \text{dept\_conf} + 0.25 \times \text{priority\_conf}$$

---

## 2. Confidence Levels & Human Review Thresholds

The `ConfidenceEvaluator` enforces institutional safety boundaries:

| Confidence Level | Score Range | Human Review Required? | System Behavior |
| :--- | :--- | :--- | :--- |
| **HIGH** | $\ge 0.85$ (with verified policy match) | No (Routine auto-triage enabled) | Triage recommendations displayed; high-confidence badge shown. |
| **MEDIUM** | $0.70 \le \text{Score} < 0.85$ | **Yes** | Staff confirmation advisory displayed; review reason recorded. |
| **LOW** | $< 0.70$ (or ambiguous / unverified) | **Yes (Mandatory)** | Mandatory human triage advisory; copilot draft flagged for review. |

---

## 3. Human Review Triggers

Human review is automatically flagged if any of the following occur:
1. Low-margin intent competition (margin $< 0.50$ between top two intents).
2. Explicit ambiguity or unclassified request (`needs_clarification = True`).
3. Intent confidence $< 0.85$ or department routing confidence $< 0.70$.
4. No authoritative university policy source retrieved in RAG context.
