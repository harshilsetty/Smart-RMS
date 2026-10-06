# Smart RMS — Entity Extraction & Temporal Parsing

## 1. Structured Entity Architecture

The `EntityExtractor` extracts university domain entities from both raw and PII-sanitized text. Extraction results are provided in two formats:
1. `entities`: High-level dictionary of entity types to values for routing rules and summary generation.
2. `structured_entities`: Typed `StructuredEntity` objects preserving `entity_type`, `value`, `confidence`, and `source_span`.

---

## 2. Supported Entity Types

| Entity Type | Extraction Method | Example Source Text | Extracted Value | Source Span |
| :--- | :--- | :--- | :--- | :--- |
| `course_code` | Domain regex | `"Re-evaluation for CSE 472 marks"` | `CSE 472` | `"CSE 472"` |
| `hostel_block` | Regex + Normalization | `"Water leakage in Boys Hostel 3"` | `BH-3` | `"Boys Hostel 3"` |
| `room_number` | Regex pattern | `"Room 204 electrical board"` | `204` | `"Room 204"` |
| `currency_amount` | Currency regex | `"Debited INR 72,000 twice"` | `72,000` | `"INR 72,000"` |
| `bank_name` | Dictionary pattern | `"Paid via SBI NetBanking"` | `SBI` | `"SBI"` |
| `portal_type` | System pattern | `"Verification pending on NSP portal"` | `NSP` | `"NSP"` |
| `certificate_type` | Document pattern | `"Need Medium of Instruction letter"` | `Medium of Instruction` | `"Medium of Instruction"` |
| `semester` | Semester regex | `"Tuition fee for Semester 5"` | `5` | `"Semester 5"` |
| `examination_type` | Exam regex | `"End Term examination admit card"` | `End Term` | `"End Term"` |
| `time_window` | Duration regex | `"Resolved within 24 hours"` | `24 hours` | `"24 hours"` |
| `date_reference` | Date regex | `"Debited on 18th September"` | `18th September` | `"18th September"` |

---

## 3. Temporal Expression Extraction

Temporal signals are extracted to guide the **Urgency Classifier**:
- **Immediate Window ($\le 24$ hours)**: `starts in 24 hours`, `within 24 hours`, `today`, `tonight` $\to$ Urgency = `IMMEDIATE`.
- **Near-term Window ($24\text{--}48$ hours)**: `tomorrow`, `in 48 hours`, `within 2 days` $\to$ Urgency = `IMMEDIATE` or `URGENT`.
- **Weekly / SLA Backlog Window**: `by Friday`, `pending 3 weeks`, `reminder` $\to$ Urgency = `URGENT`.
- **Standard Routine**: No temporal constraints $\to$ Urgency = `NORMAL` or `LOW`.
