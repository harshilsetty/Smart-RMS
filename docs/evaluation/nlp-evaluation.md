# Smart RMS — NLP & Evaluation Layer Documentation (Phase 2)

## 1. Overview & Core Philosophy

Smart RMS is an AI-assisted University RMS Resolution & Operations System. The core operating principle of the system is:
> **"AI assists. Humans decide."**

In Phase 2, Smart RMS evolved from an initial prototype into a measurable, deterministic, and verifiable NLP system. The system evaluates every incoming grievance through a modular NLP pipeline, retrieves relevant policy documents, assesses component-level confidence, and provides explainable recommendations for human staff members.

---

## 2. NLP Pipeline Architecture

The NLP pipeline (`backend/app/nlp/`) consists of the following modular stages:

1. **PII Protection & Redaction (`app/privacy/`)**: Masks phone numbers, student registration numbers, email addresses, transaction IDs, Aadhaar numbers, and MAC addresses prior to analysis.
2. **Preprocessing (`app/nlp/preprocessing.py`)**: Cleans whitespace, standardizes punctuation, removes domain stopwords, and extracts word and n-gram tokens.
3. **Domain Entity Extraction (`app/nlp/entity_extractor.py`)**: Safely identifies university parameters: course codes (`CSE 472`), hostel blocks (`BH-4`), room numbers (`Room 312`), monetary amounts (`INR 65,000`), banks (`HDFC Bank`), portal names (`NSP`), and issues (`Water Leakage`).
4. **Intent Classification (`app/nlp/intent_classifier.py`)**: Abstract base `BaseIntentClassifier` implemented via `RuleBasedIntentClassifier`. Computes confidence based on token evidence and margin over secondary intent.
5. **Department Routing (`app/nlp/department_classifier.py`)**: Routes tickets across the 7 university operating departments using intent mapping, extracted entities, and departmental lexicons.
6. **Urgency & Priority Classification (`app/nlp/urgency_classifier.py`)**: Transparent, explainable 4-tier urgency scoring (`Low`, `Medium`, `High`, `Critical`) driven by physical hazards, examination deadlines (<48h), duplicate financial transactions, and medical emergencies.
7. **Semantic Similarity Engine (`app/nlp/semantic_similarity.py`)**: Hybrid character 3-gram cosine and token Jaccard similarity engine with university domain synonym canonicalization.
8. **Confidence & Review Evaluator (`app/nlp/confidence.py`)**: Multi-tier threshold evaluator triggering human review whenever confidence is low or when no authoritative policy is verified.

---

## 3. Grounding & Strict No-Source-No-Answer

To prevent hallucination, the system enforces:
1. **Policy-Constrained Generation**: Automated draft responses are generated exclusively using retrieved authoritative clauses.
2. **Strict No-Source-No-Answer Guardrail**: If retrieved evidence score is below threshold ($\ge 0.65$) or no authoritative document exists, the system outputs:
   > *"Insufficient authoritative information. Human review required."*
   with confidence set to `0.0` and `requires_staff_edit = True`.
3. **Heuristic Evaluation**: Grounding rate is evaluated by checking citation fidelity and verbatim evidence overlap. It is explicitly documented as heuristic, not neural NLI entailment. The system **never** claims "zero hallucinations".

---

## 4. Benchmark Evaluation Methodology & Actual Results

Evaluation was executed dynamically over the 60-sample synthetic benchmark dataset (`evaluation/datasets/evaluation_rms.json`) against ground-truth labels (`evaluation/datasets/expected_outputs.json`).

### Actual Measured Metrics

```json
{
  "dataset_size": 60,
  "intent_accuracy": 0.95,
  "intent_macro_f1": 0.9158,
  "intent_weighted_f1": 0.9389,
  "department_accuracy": 1.0,
  "department_macro_f1": 1.0,
  "department_weighted_f1": 1.0,
  "priority_accuracy": 0.8833,
  "retrieval_precision_at_1": 0.9464,
  "retrieval_precision_at_3": 0.3333,
  "retrieval_recall_at_3": 1.0,
  "retrieval_mrr": 0.9732,
  "grounding_rate": 0.8167,
  "citation_fidelity": 0.8036,
  "no_source_adherence": 1.0,
  "grounding_evaluation_type": "heuristic_evidence_verification",
  "human_review_rate": 0.30,
  "error_case_count": 7
}
```

---

## 5. 500+ Synthetic Scale Simulation

The dataset generator (`scripts/generate_rms_dataset.py`) produces 500+ realistic synthetic tickets across all categories:
```bash
python scripts/generate_rms_dataset.py --count 500 --seed 42
```
Output: `data/mock/generated_rms_requests.json`.

The batch processing script (`scripts/run_batch_analysis.py`) runs the complete pipeline:
```bash
python scripts/run_batch_analysis.py --input data/mock/generated_rms_requests.json --output evaluation/results.json
```
**Actual Batch Run Performance**:
- **Total Processed**: 500 tickets
- **Execution Time**: 0.90s
- **Throughput**: 553.88 tickets/sec
- **Average Confidence**: 0.93
- **Human Review Rate**: 18.0% (90/500)
- **PII Redactions**: 200 tickets masked

---

## 6. Current Implementation vs Future Research

| Area | Current Implementation | Future Research / Production |
| :--- | :--- | :--- |
| **Intent & Routing** | Deterministic rule & token evidence baseline. | TF-IDF + Logistic Regression / Naive Bayes, fine-tuned transformer classifier. |
| **Retrieval** | `LocalVectorStore` with sentence chunking & TF-IDF/n-gram scoring. | Persistent Chroma with Sentence Transformers (`all-MiniLM-L6-v2`). |
| **Grounding Evaluation** | Lexical overlap and citation presence heuristic. | Cross-encoder Natural Language Inference (NLI) model. |
| **Escalations** | Workflow state transitions. | Multi-tier LangGraph agentic workflow with SLA notifications. |
