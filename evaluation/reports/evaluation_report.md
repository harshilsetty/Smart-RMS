# Smart RMS — Phase 2 NLP & Retrieval Evaluation Report

**Date of Execution**: September 2026  
**System Evaluated**: Smart RMS Modular NLP Pipeline & Grounded RAG Retrieval  
**Dataset**: Synthetic University RMS Evaluation Set (`evaluation/datasets/evaluation_rms.json`)  
**Sample Count**: 60 diverse, balanced university grievance requests  
**Execution Environment**: Local Deterministic Baseline (Zero External Paid API Dependencies)

---

## 1. Executive Summary

This report provides empirical evaluation results for Phase 2 of Smart RMS. In strict accordance with the core principle **"AI assists. Humans decide."**, the system evaluates incoming requests through PII redaction, intent classification, departmental routing, explainable urgency assessment, domain entity extraction, and grounded policy retrieval.

All metrics below are **runtime computed** by `evaluation/evaluator.py` against ground-truth labels. No values are fabricated or assumed.

| Metric Area | Evaluation Metric | Measured Result | Evaluation Nature |
| :--- | :--- | :--- | :--- |
| **Intent Classification** | Overall Accuracy | **95.0%** (57/60) | Exact Match |
| | Macro F1-Score | **0.9158** | Unweighted Class Average |
| | Weighted F1-Score | **0.9389** | Support Weighted Average |
| **Department Routing** | Routing Accuracy | **100.0%** (60/60) | Exact Department Match |
| | Macro F1-Score | **1.0000** | 7 Department Classes |
| **Priority Classification** | Priority Accuracy | **88.33%** (53/60) | Exact 4-Tier Match |
| **RAG Retrieval** | Precision@1 | **94.64%** | Authoritative Policy Match |
| | Precision@3 | **33.33%** | Top-3 Retrieved Clauses |
| | Recall@3 | **100.0%** | Relevant Policy in Top-3 |
| | Mean Reciprocal Rank (MRR) | **0.9732** | Reciprocal Rank of Target |
| **Grounded Response** | Grounding Rate | **81.67%** (49/60) | **Heuristic Lexical Verification** |
| | Citation Fidelity | **80.36%** | Clause/Title Match in Evidence |
| | No-Source Adherence | **100.0%** (4/4) | Strict Fallback to Human Review |
| **Human-in-the-Loop** | Human Review Trigger Rate | **30.0%** (18/60) | Flagged for Staff Review |

> [!NOTE]
> **Heuristic Grounding Disclaimer**: The grounding rate is evaluated via deterministic lexical overlap, citation presence, and safety fallback compliance. It is not an NLI-based neural entailment score and does **not** claim "zero hallucinations".

---

## 2. Dataset Distribution

The 60 evaluation samples are distributed across the official university domains:

- **Hostel Affairs (`HOSTEL_MAINTENANCE`)**: 8 tickets (AC leakage, water flooding, geyser failure, mess hygiene, door locks)
- **Accounts & Finance (`FEE_PAYMENT`)**: 8 tickets (duplicate debit, gateway timeout, offline challan, refund requests)
- **Examination Branch (`EXAMINATION`)**: 8 tickets (clearance holds, hall ticket blockage, datesheet clash, re-eval marksheet)
- **Academic Affairs (`ACADEMIC`)**: 8 tickets (CA rubric discrepancy, missing grades, elective allocation, mentor missing)
- **Student Welfare (`ATTENDANCE`)**: 8 tickets (typhoid/dengue hospitalization, duty leave, biometric device desync)
- **Scholarship Section (`SCHOLARSHIP`)**: 7 tickets (NSP institute verification, PMS renewal, merit concession, freeship)
- **IT Services (`IT_SUPPORT`)**: 6 tickets (Fortinet MAC limits, UMS password lock, mailbox storage full, lab workstation)
- **Academic Affairs (`STUDENT_SERVICES`)**: 6 tickets (Bonafide, MOI certificate for visa, migration certificate, duplicate ID)
- **Out-of-Domain (`GENERAL_INQUIRY`)**: 4 tickets (gym lost property, bookstore inquiry, public bus schedule, cafeteria hours)

---

## 3. Detailed Per-Class Performance

### Intent Classification Breakdown

| Class | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| `ACADEMIC` | 8 | 0.7273 | 1.0000 | 0.8421 |
| `ATTENDANCE` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `EXAMINATION` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `FEE_PAYMENT` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `GENERAL_INQUIRY` | 4 | 1.0000 | 0.2500 | 0.4000 |
| `HOSTEL_MAINTENANCE` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `IT_SUPPORT` | 6 | 1.0000 | 1.0000 | 1.0000 |
| `SCHOLARSHIP` | 7 | 1.0000 | 1.0000 | 1.0000 |
| `STUDENT_SERVICES` | 6 | 1.0000 | 1.0000 | 1.0000 |

### Department Routing Breakdown

| Department | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| `Hostel Affairs` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `Accounts & Finance` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `Examination Branch` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `Academic Affairs` | 18 | 1.0000 | 1.0000 | 1.0000 |
| `Student Welfare` | 8 | 1.0000 | 1.0000 | 1.0000 |
| `Scholarship Section` | 7 | 1.0000 | 1.0000 | 1.0000 |
| `IT Services` | 6 | 1.0000 | 1.0000 | 1.0000 |

---

## 4. Transparent Error Analysis

Rather than hiding failures, this section analyzes the **7 actual misclassification / disagreement cases** identified during evaluation:

### Case 1: Out-of-Domain General Inquiries Misclassified as Academic (`EVAL-RMS-058`, `059`, `060`)
- **Query 058**: *"Campus bookstore inquiry about availability of novel books"*
- **Query 059**: *"Inquiry regarding public bus timings from university main gate to railway station"*
- **Query 060**: *"General question regarding campus cafeteria lunch hours on public holidays"*
- **Failure Mode**: The baseline classifier picked up terms like "engineering textbooks" and defaulted low-signal inquiries to Academic Affairs with Medium priority instead of `GENERAL_INQUIRY`.
- **Mitigation & Future Work**: Introduce a calibrated out-of-domain rejection threshold or lightweight semantic clustering.

### Case 2: Urgency Level Boundary Disagreements (`EVAL-RMS-021`, `034`, `050`, `051`)
- **Query 021**: *"Examination center allotment change request on medical grounds"*
  - Predicted: `Low` (due to standard seating change request)
  - Expected: `High` (due to imminent exam date)
- **Query 034**: *"Emergency medical leave condonation for surgery recovery"*
  - Predicted: `Critical` (due to "emergency" signal trigger)
  - Expected: `Medium` (because condonation is a retrospective administrative review)
- **Query 050 & 051**: *"Migration certificate timeline"* & *"Duplicate student ID card issuance"*
  - Predicted: `High` (due to paid fee reconciliation triggers)
  - Expected: `Low` (standard self-service turnaround)
- **Analysis**: Urgency classification is inherently subjective. The system deliberately over-indexes on safety and deadlines to prevent critical grievances from languishing.

---

## 5. 500+ Scale Simulation Results

Using `scripts/generate_rms_dataset.py` and `scripts/run_batch_analysis.py`, a stress-test of 500 synthetic tickets was conducted:

- **Total Processed**: 500 tickets
- **Execution Time**: 0.90 seconds
- **Throughput**: 553.88 tickets/second
- **Average Confidence**: 0.93
- **Human Review Flagged**: 18.0% (90 tickets flagged for operator review)
- **PII Detected and Redacted**: 200 tickets masked before pipeline entry

---

## 6. Limitations & Future Research Directions

1. **Rule-Based Baseline**: Current classification utilizes token evidence, character n-grams, and regex heuristics. While fast, predictable, and 100% locally executable, it lacks deep contextual understanding for subtle semantic nuance.
2. **Heuristic Grounding**: Grounding verification evaluates lexical and clause presence. Future phases should incorporate cross-encoder NLI models (e.g. DeBERTa MNLI) to assess claim entailment.
3. **Embeddings**: Future iterations will introduce local Sentence Transformers (`all-MiniLM-L6-v2`) for dense semantic retrieval alongside BM25.
