# Smart RMS — Classification Methodology & Rule Calibration

## 1. Classification Overview

The classification pipeline consists of three specialized classifiers:
1. `RuleBasedIntentClassifier`: Categorizes the request into the canonical intent taxonomy.
2. `RuleBasedDepartmentRouter`: Maps intent, domain keywords, and entity context to target departments.
3. `RuleBasedUrgencyClassifier`: Assesses operational priority and temporal urgency independently.

---

## 2. Priority vs Urgency Separation

| Concept | Range | Focus | Key Signals |
| :--- | :--- | :--- | :--- |
| **Operational Priority** | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | Impact & severity on university operations and student rights. | Physical safety hazards (water near switchboards), examination access blockages, financial ledger double debits. |
| **Temporal Urgency** | `LOW`, `NORMAL`, `URGENT`, `IMMEDIATE` | Time horizon and deadline proximity. | Extracted temporal cues (`starts in 24 hours`, `tomorrow`, `portal closing date approaching`). |

### Example Scenarios:
- **Scenario A**: `"Tuition fee debited twice from bank account"`
  - Priority: `HIGH` (Financial impact requires reconciliation)
  - Urgency: `NORMAL` (No 24-hour deadline constraint)
- **Scenario B**: `"Admit card blocked library fine error, exam commences in 24 hours"`
  - Priority: `CRITICAL` (Prevents sitting for examination)
  - Urgency: `IMMEDIATE` (Execution required within 24 hours)

---

## 3. Department Routing Strategy

Primary mapping originates from intent, but domain entity cues provide safety overrides:
- If `hostel_block` or `room_number` is present and issue relates to physical maintenance $\to$ `Hostel Affairs`.
- If `currency_amount`, `bank_name`, or `fee` is present $\to$ `Accounts & Finance`.
- If `admit card`, `datesheet clash`, or `clearance hold` is present $\to$ `Examination Branch`.
- If `course_code` or continuous assessment marks are disputed $\to$ `Academic Affairs`.
- If medical leave or condonation is requested $\to$ `Student Welfare`.
- If `nsp` or scholarship verification is mentioned $\to$ `Scholarship Section`.
- If campus Wi-Fi, MAC address, or portal credentials are cited $\to$ `IT Services`.
