# Staff Operational Workflow & Communication Protocol

## 1. Principles
Smart RMS is built around the human operator:
1. **AI Proposes, Staff Dispatches**: AI copilot draft generation (`AI_DRAFT`) is strictly non-binding. Drafts remain internal (`status: DRAFT`) and are never sent to students until explicitly approved or edited by authorized staff.
2. **Separation of Concerns**: Internal staff notes (`is_internal: True`) are strictly segregated from official student-facing responses (`is_internal: False`).
3. **Traceability of Ownership**: Department assignment and staff reassignment preserve all previous historical assignments rather than overwriting records.

---

## 2. End-to-End Staff Operations Sequence

```
1. Ticket Intake & Review
   └── Operator inspects Ticket Queue, filtered by Department, Priority, or SLA Risk.
   └── Operator opens Ticket Detail workspace.

2. Assignment & Triage
   └── Assign to appropriate Department and Active Staff Member.
   └── Previous assignment becomes `active: False` and remains preserved.

3. Redirection (If Misrouted)
   └── Operator selects target Department and provides mandatory reason.
   └── Previous assignments deactivated; ownership updated; audit event logged.

4. Communication & Drafting
   └── Operator can add an internal staff note (`is_internal: True`).
   └── Operator requests Copilot Triage / Grounded Draft (`AI_DRAFT`).
   └── Operator reviews, modifies, and approves official response.

5. Escalation (If Policy Exception or SLA Risk)
   └── Explicit manual escalation to LEVEL_1, LEVEL_2, or HOD.
   └── Reason and target authority captured in ticket record and audit log.

6. Resolution
   └── Operator enters verified official narrative (minimum 5 characters).
   └── Status moves to `RESOLVED`; SLA is stopped/recorded.

7. Administrative Closure
   └── Following acceptance or verification window, ticket transitions `RESOLVED` → `CLOSED`.
   └── Ticket enters terminal completed state.
```

---

## 3. Communication Thread Schema

Every response message contains:
- `response_id`: Unique identifier (`RSP-...`)
- `ticket_id`: Target ticket ID
- `author_id`: Staff User ID or AI Assistant (`SYSTEM_AI`)
- `author_name`: Display name
- `author_role`: Operational role (`STAFF_OPERATOR`, `AI`, `DEPARTMENT_HOD`)
- `response_type`: `STAFF` | `AI_DRAFT` | `SYSTEM` | `ESCALATION`
- `status`: `DRAFT` | `PUBLISHED`
- `content`: Plaintext or formatted response text
- `is_internal`: Boolean indicating staff-only visibility
- `created_at`: UTC ISO-8601 timestamp

---

## 4. Role Permissions Matrix

| Operational Action | STAFF_OPERATOR | DEPARTMENT_STAFF | DEPARTMENT_HOD | ADMIN |
| :--- | :---: | :---: | :---: | :---: |
| View Queue & Tickets | Yes | Yes | Yes | Yes |
| Run AI Triage | Yes | Yes | Yes | Yes |
| Assign / Reassign Staff | Yes | No | Yes | Yes |
| Department Redirection | Yes | No | Yes | Yes |
| Add Internal Note | Yes | Yes | Yes | Yes |
| Send Official Response | Yes | Yes | Yes | Yes |
| Escalate to HOD | Yes | Yes | Yes (Tier 2) | Yes |
| Resolve Ticket | Yes | Yes | Yes | Yes |
| Permanently Close | Yes | No | Yes | Yes |
