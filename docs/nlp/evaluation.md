# Smart RMS — Milestone 4 NLP Evaluation & Benchmark Report

## 1. Executive Summary

Milestone 4 evaluated the NLP Intelligence Pipeline over a dedicated 120-ticket labeled evaluation dataset (`evaluation_nlp_120.json`) and a full 500-ticket synthetic RMS batch (`generated_rms_requests.json`).

All scores represent **actual measured runtime metrics** calculated by `scripts/evaluate_nlp.py` and `scripts/run_batch_analysis.py`.

---

## 2. 120-Sample Benchmark Metrics

### Intent Classification
- **Accuracy**: $90.00\%$
- **Macro Precision**: $79.86\%$
- **Macro Recall**: $83.61\%$
- **Macro F1-Score**: $0.8117$
- **Weighted F1-Score**: $0.8784$

### Department Routing
- **Accuracy**: $98.33\%$
- **Macro F1-Score**: $0.9856$
- **Weighted F1-Score**: $0.9833$

### Priority & Urgency Classification
- **Priority Accuracy**: $88.33\%$
- **Priority Macro F1**: $0.8819$
- **Urgency Accuracy**: $77.50\%$

### Ambiguity Detection & Safety
- **Ambiguity Detection Accuracy**: $96.67\%$
- **Ambiguous Queries in Ground Truth**: $14$
- **Flagged for Clarification by NLP**: $10$
- **False Confident Error Count**: $4$

### Inference Latency
- **Average NLP Latency**: $0.38\text{ ms/ticket}$
- **P95 Latency**: $0.57\text{ ms}$
- **Throughput**: $2,600.4\text{ tickets/second}$

---

## 3. 500-Ticket Synthetic Batch Analysis

- **Total Processed**: $500$ tickets
- **Processing Time**: $1.02\text{ seconds}$
- **Throughput**: $492.01\text{ tickets/sec}$ (includes full PII masking, NLP analysis, and RAG retrieval)
- **Average Heuristic Confidence**: $0.9349$
- **Human Review Flagged**: $319 / 500$ ($63.8\%$)
- **PII Tokens Redacted**: $208$
- **Clarification Required Rate**: $0.6\%$ ($3$ tickets)

### Department Distribution (500 Tickets)
- `Academic Affairs`: $90$ ($18.0\%$)
- `Accounts & Finance`: $79$ ($15.8\%$)
- `Scholarship Section`: $74$ ($14.8\%$)
- `Student Welfare`: $74$ ($14.8\%$)
- `Examination Branch`: $72$ ($14.4\%$)
- `Hostel Affairs`: $64$ ($12.8\%$)
- `IT Services`: $47$ ($9.4\%$)

### Priority Distribution (500 Tickets)
- `High`: $196$ ($39.2\%$)
- `Medium`: $164$ ($32.8\%$)
- `Critical`: $93$ ($18.6\%$)
- `Low`: $47$ ($9.4\%$)

---

## 4. Top Failure Patterns & Error Analysis

1. **Academic vs Examination Mark Discrepancies**:
   - Discrepancies in internal Continuous Assessment (CA) belong to `Academic Affairs`, whereas end-term re-evaluations belong to `Examination Branch`. Without explicit mention of "end term" or "CA", slight overlap occurs.
2. **Terse Ambiguous Queries**:
   - Queries like `"My issue is not solved"` are properly caught as `UNKNOWN` ($0.30$ confidence), but slightly longer queries containing generic words (`"fees"`) require cautious thresholding to avoid false confidence.
3. **Multi-Issue Complaints**:
   - Tickets referencing water leakage in a hostel room while also complaining about room allocation are routed to `Hostel Affairs` primarily, but multi-department routing remains an area for future transformer models.
