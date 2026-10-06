# Human-in-the-Loop & Staff Override Controls — Smart RMS

## 1. Principles of Human Oversight

In Smart RMS, AI assists while university staff retain full decision-making control. AI recommendations never autonomously modify academic standing, attendance records, financial liabilities, or disciplinary statuses.

Staff oversight is structured into two formal mechanisms:
1. **Enforced Human Review Triggers**: Conditions under which a ticket is locked into `STAFF_REVIEW` status and cannot proceed without staff action.
2. **Explicit Human Override Workflow**: Formal API and UI capabilities allowing staff officers to override any AI suggestion, preserving the original AI prediction for auditability.

---

## 2. Enforced Human Review Triggers

A ticket is flagged as `requires_human_review = True` whenever any of the following safety conditions are met:
1. **Low Model Confidence**: NLP confidence score $< 0.75$.
2. **Ambiguity Flag**: Narrow margin between top competing intents ($< 0.10$), or query matches known terse/generic inquiry patterns.
3. **No-Source RAG Condition**: No authoritative university policy source retrieved with a relevance score $\ge 0.65$.
4. **Out-of-Domain / Unknown Query**: Classification defaults to `UNKNOWN` or `GENERAL_INQUIRY`.
5. **Critical Priority Escalations**: Cases classified as `Critical` priority automatically mandate supervisor oversight.

---

## 3. Human Override Architecture & Audit Preservation

### Non-Destructive Override Contract
When staff override an AI prediction (e.g. changing recommended department from `Accounts & Finance` to `Student Welfare`):
- The original AI prediction is **never erased or overwritten**. It is permanently archived under `metadata["ai_original_prediction"]`.
- Staff corrections are appended chronologically to `metadata["human_overrides"]`.
- A formal immutable `AuditEvent` (`event_type="HUMAN_OVERRIDE"`) is appended to the ticket history.

### Audit Event Data Model
```json
{
  "event_id": "AUDIT-OVR-1738759000",
  "ticket_id": "RMS-SYN-001",
  "timestamp": "2026-10-05T17:46:12Z",
  "actor_id": "USR-STAFF-99",
  "actor_name": "Staff Officer",
  "actor_role": "STAFF",
  "event_type": "HUMAN_OVERRIDE",
  "from_state": "STAFF_REVIEW",
  "to_state": "STAFF_REVIEW",
  "notes": "AI recommendation overridden by staff (USR-STAFF-99): Student requires immediate grievance cell intervention. Modifications: ['department', 'priority']",
  "details": {
    "applied_overrides": {
      "department": { "from": "Accounts & Finance", "to": "Student Welfare" },
      "priority": { "from": "Medium", "to": "Critical" }
    },
    "original_ai": {
      "intent": "FEE_PAYMENT",
      "department": "Accounts & Finance",
      "priority": "Medium",
      "confidence": 0.88
    },
    "staff_reason": "Student requires immediate grievance cell intervention"
  }
}
```

---

## 4. Workstation Interaction Flow
1. Staff opens ticket in the workstation.
2. The AI Triage card displays detected intent, department, priority, and ambiguity flags.
3. Staff clicks **Override Triage** or enters a custom department / priority.
4. Staff enters a mandatory operational justification.
5. The workstation submits `POST /api/v1/rms/{ticket_id}/override`.
6. UI reflects the overridden values with an audit badge indicating manual human override.
