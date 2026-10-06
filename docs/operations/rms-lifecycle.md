# RMS Lifecycle & State Machine Specification

## 1. Overview
Smart RMS implements a deterministic, audit-logged finite state machine governing ticket progress from initial ingestion to administrative closure. In accordance with the core design principle:
> **AI assists. Humans decide.**

No artificial intelligence model autonomously changes ticket state, approves resolutions, or closes records. All state changes are validated by `WorkflowEngine`, recorded in append-only `AuditEvent` histories, and orchestrated through `RMSService`.

---

## 2. Canonical State Transitions

```
[ NEW ]
   ↓
[ INGESTED ] ─────────────┐ (legacy direct)
   ↓                      ↓
[ ANALYZED ] ───────> [ APPROVED ] ──> [ RESOLVED ] ──> [ CLOSED ]
   ↓                      ↑                 ↑
[ ROUTED ]                │                 │
   ↓                      │                 │
[ STAFF_REVIEW ] ─────────┘                 │
   ↓                                        │
[ IN_PROGRESS ] ────────────────────────────┤
   │          │                             │
   │          ├─> [ WAITING_FOR_STUDENT ] ──┤
   │          │          ↓                  │
   │          │   [ IN_PROGRESS ]           │
   │          │                             │
   │          ├─> [ WAITING_FOR_DEPARTMENT ]┤
   │          │          ↓                  │
   │          │   [ IN_PROGRESS ]           │
   │          │                             │
   │          └─> [ ESCALATED ] ────────────┘
   │                     ↓
   └──────────────> [ IN_PROGRESS ]
```

### Transition Rule Matrix

| From State | Allowed Target States | Enforcement / Trigger |
| :--- | :--- | :--- |
| `NEW` | `INGESTED` | Adapter ingestion or payload validation |
| `INGESTED` | `ANALYZED`, `ROUTED`, `APPROVED` | AI triage pipeline or manual queue routing |
| `ANALYZED` | `ROUTED`, `STAFF_REVIEW`, `APPROVED`, `ESCALATED` | Department suggestion confirmed or HOD escalation |
| `ROUTED` | `STAFF_REVIEW`, `IN_PROGRESS` | Department assignment |
| `STAFF_REVIEW` | `IN_PROGRESS`, `APPROVED`, `RESOLVED`, `WAITING_FOR_STUDENT`, `WAITING_FOR_DEPARTMENT`, `ESCALATED` | Staff opens ticket or takes immediate action |
| `IN_PROGRESS` | `WAITING_FOR_STUDENT`, `WAITING_FOR_DEPARTMENT`, `ESCALATED`, `RESOLVED` | Operational communication, hold, or resolution |
| `WAITING_FOR_STUDENT`| `IN_PROGRESS`, `RESOLVED`, `CLOSED` | Student reply received or auto-resolution window |
| `WAITING_FOR_DEPARTMENT`| `IN_PROGRESS`, `ESCALATED`, `RESOLVED` | Inter-department response or timeout escalation |
| `ESCALATED` | `IN_PROGRESS`, `RESOLVED` | HOD decision or tier-2 officer resolution |
| `APPROVED` | `RESOLVED`, `CLOSED` | Resolution verification |
| `RESOLVED` | `CLOSED` | Administrative verification & permanent closure |
| `CLOSED` | *(Terminal)* | Immutable terminal state |

---

## 3. Invalid Transition Enforcement

The `WorkflowEngine.transition()` and `can_transition()` methods enforce strict guards. Attempting an arbitrary jump (such as `INGESTED` &rarr; `CLOSED` or `WAITING_FOR_STUDENT` &rarr; `ANALYZED`) raises:

```python
class InvalidStateTransitionError(Exception):
    """Raised when an illegal lifecycle state transition is attempted."""
```

This maps to HTTP **400 Bad Request** at the REST API boundary, preserving deterministic behavior and preventing state corruption.

---

## 4. Audit Event Binding

Every successful transition creates an append-only `AuditEvent`:
- `event_id`: Unique identifier (`AUD-...`)
- `ticket_id`: Target ticket ID
- `event_type`: State or action descriptor (e.g., `STATUS_CHANGED`, `RESOLVED`, `CLOSED`)
- `actor_id`: Staff ID or `SYSTEM`
- `actor_role`: Operational role (`STAFF_OPERATOR`, `DEPARTMENT_HOD`, etc.)
- `from_state`: Prior state
- `to_state`: Resulting state
- `timestamp`: UTC ISO-8601 timestamp
- `notes`: Human or system narrative explaining the transition
