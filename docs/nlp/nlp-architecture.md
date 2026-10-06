# Smart RMS — NLP Intelligence Pipeline Architecture

## 1. Overview & Core Philosophy

Smart RMS Milestone 4 establishes a modular, deterministic-first Natural Language Processing (NLP) intelligence pipeline designed to extract structured understanding from student RMS grievance requests.

> **Fundamental Principle**: AI assists. Humans decide.  
> **Prediction $\neq$ Decision**: NLP components recommend categories, priorities, and structured entities. They do **not** trigger autonomous operational decisions (no automated grade changes, no automated fee refunds, no autonomous ticket closures).

---

## 2. Pipeline Execution Flow

Every incoming RMS request follows a sequential, modular multi-stage intelligence workflow:

```
                  RMS Request (Subject + Description)
                                 │
                                 ▼
                     1. Privacy & PII Redaction
                                 │
                                 ▼
                     2. Text Preprocessing & Synonyms
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
3. Entity Extraction   4. Intent Classification    5. Urgency & Priority
 (Regex + Spans)       (Weighted N-grams & Margin)   (Hazard & Temporal Cues)
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 ▼
                     6. Department Routing
                       (Intent + Entity Overrides)
                                 │
                                 ▼
                     7. Ambiguity Assessment
                       (Low-signal & Competitor detection)
                                 │
                                 ▼
                     8. Confidence Engine & Explainability
                       (Separated Heuristic Confidences)
                                 │
                                 ▼
                     Structured NLPResult Object
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       RAG Query Builder               Staff Copilot UI
     (Enriched Retrieval)            (Review & Human Override)
```

---

## 3. Modular Subsystems

| Module | Interface / Class | Function |
| :--- | :--- | :--- |
| **Preprocessing** | `normalize_text` / `tokenize` | Canonical domain synonym mapping (`hall ticket` $\to$ `admit card`, `tuition` $\to$ `fee`, `re-evaluation` $\to$ `reevaluation`), punctuation and whitespace normalization. |
| **Intent Classifier** | `BaseIntentClassifier` $\to$ `RuleBasedIntentClassifier` | Weighted token & bigram scoring with margin calculation over secondary intents; explicit ambiguity and `UNKNOWN` fallback. |
| **Department Router** | `BaseDepartmentClassifier` $\to$ `RuleBasedDepartmentRouter` | Maps intent and domain keywords to official synthetic university departments (`Hostel Affairs`, `Accounts & Finance`, `Examination Branch`, etc.). |
| **Priority & Urgency** | `BaseUrgencyClassifier` $\to$ `RuleBasedUrgencyClassifier` | Decouples operational priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) from temporal urgency (`LOW`, `NORMAL`, `URGENT`, `IMMEDIATE`). |
| **Entity Extractor** | `EntityExtractor` | Extracts structured university entities (`course_code`, `hostel_block`, `room_number`, `currency_amount`, `bank_name`, `portal_type`, `semester`, `time_window`) with confidence and source character spans. |
| **Confidence Engine** | `ConfidenceEvaluator` | Computes separated heuristic confidence values and enforces human-in-the-loop review triggers. |
| **Pipeline Orchestrator** | `NLPPipeline` | Ties all stages together and produces the canonical `NLPResult`. |

---

## 4. API Integration

- Dedicated Endpoint: `POST /api/v1/nlp/analyze`
  - Accepts either `{ "ticket_id": "TKT-..." }` or `{ "subject": "...", "description": "..." }`.
  - Returns complete structured `NLPResult` with machine-readable explanations.
- RMS Service Integration: `POST /api/v1/rms/{ticket_id}/analyze`
  - Automatically executes PII sanitization $\to$ NLP pipeline $\to$ RAG policy retrieval $\to$ Draft response generation.
