# Audit Trail & Governance Specification

## 1. Governance Principles
In institutional operations, forensic accountability is paramount. The Smart RMS audit subsystem enforces:
1. **Append-Only Immutability**: Audit events are strictly appended; no endpoint or service method permits deletion or in-place modification of historical audit records.
2. **Actor Traceability**: Every event attributes an `actor_id` (e.g., `USR-STAFF-01` or `SYSTEM`), `actor_role`, and UTC timestamp.
3. **Reconstructability**: Given the chronological audit trail (`GET /api/v1/rms/{id}/history`), operators and university auditors can reconstruct:
   - Who took the action?
   - When did it happen?
   - What changed (`from_state` &rarr; `to_state`)?
   - Why was it executed (`reason` / `notes`)?

---

## 2. Event Types & Triggers

| Event Type | Triggering Action | Captured Details |
| :--- | :--- | :--- |
| `CREATED` | Ingestion into mock repository | Channel, source, student ref |
| `INGESTED` | Adapter canonicalization | SLA calculation result |
| `ANALYZED` | AI copilot pipeline execution | Intent, confidence, suggested department |
| `ASSIGNED` | Department or staff assignment | Target department, staff ID, previous assignment state |
| `REDIRECTED` | Department redirection | Previous department, new department, reason |
| `NOTE_ADDED` | Internal staff memo | Note preview, author |
| `DRAFT_CREATED` | Copilot response generation | Draft ID, confidence score |
| `RESPONSE_SENT` | Official student communication | Response ID, delivery mode |
| `ESCALATED` | Tier-1 / Tier-2 / HOD escalation | Previous level, new level, reason |
| `APPROVED` | Staff resolution approval | Resolution narrative length, approver |
| `RESOLVED` | Official ticket resolution | Resolution text, resolver ID |
| `CLOSED` | Permanent ticket closure | Closing staff actor, verification notes |

---

## 3. History Retrieval Endpoint

```http
GET /api/v1/rms/{ticket_id}/history
```

Returns a chronologically sorted list (`List[AuditEvent]`) formatted as:

```json
[
  {
    "event_id": "AUD-5B7089FA",
    "ticket_id": "TKT-RMS-1001",
    "event_type": "ASSIGNED",
    "actor_id": "USR-STAFF-01",
    "actor_role": "STAFF_OPERATOR",
    "timestamp": "2026-10-05T01:10:00Z",
    "from_state": "ROUTED",
    "to_state": "STAFF_REVIEW",
    "notes": "Assigned to Examination Branch staff for verification",
    "details": {
      "assigned_department_id": "DEPT-EXAM",
      "assigned_staff_id": "USR-STAFF-04"
    }
  }
]
```
