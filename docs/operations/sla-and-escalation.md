# Operational SLA & Escalation Engine

## 1. Overview
The SLA and Escalation engines in Smart RMS operate deterministically without heuristic black boxes or ungrounded machine learning. Every ticket's SLA target is dynamically derived from its department policy and priority level, with risk status evaluated deterministically based on the remaining resolution window.

---

## 2. Department SLA Policy Model
Each university department defines target turnaround windows in hours:

```json
{
  "department_id": "DEPT-EXAM",
  "sla_policy": {
    "CRITICAL": 6,
    "HIGH": 18,
    "MEDIUM": 36,
    "LOW": 72
  }
}
```

Fallback global targets apply when a department does not specify custom targets:
- `Critical`: 12 hours
- `High`: 24 hours
- `Medium`: 48 hours
- `Low`: 72 hours

---

## 3. Deterministic SLA Risk Calculation

SLA calculations are performed on intake and refreshed upon retrieval:
- `sla_hours`: Policy turnaround hours for given `(department, priority)`
- `due_at`: `created_at + timedelta(hours=sla_hours)`
- `remaining_hours`: `(due_at - now).total_seconds() / 3600.0`

### Deterministic Risk States

```
                 remaining_hours > 0.25 * sla_hours
               ┌────────────────────────────────────┐
               │              ON_TRACK              │
               └────────────────────────────────────┘
                                 │
             0 < remaining_hours <= 0.25 * sla_hours
                                 ▼
               ┌────────────────────────────────────┐
               │              AT_RISK               │
               └────────────────────────────────────┘
                                 │
                       remaining_hours <= 0
                                 ▼
               ┌────────────────────────────────────┐
               │              BREACHED              │
               └────────────────────────────────────┘
```

- **`ON_TRACK`**: `remaining_hours > 0.25 * sla_hours`
- **`AT_RISK`**: Less than 25% of SLA window remains (`0 < remaining_hours <= 0.25 * sla_hours`)
- **`BREACHED`**: Elapsed past due date (`remaining_hours <= 0`) while ticket is still uncompleted
- **`RESOLVED`**: Ticket successfully resolved within SLA window (`is_breached: False`)

---

## 4. Multi-Level Escalation Model

Escalations are triggered either manually by staff or automatically upon SLA breach.

### Escalation Hierarchy
1. **`LEVEL_0`**: Base department staff queue
2. **`LEVEL_1`**: Senior Operations Officer / Department Coordinator
3. **`LEVEL_2`**: Central University Grievance Cell
4. **`HOD`**: Head of Department

### Escalation Record Contract
Every escalation preserves:
- `escalation_id`: Unique identifier (`ESC-...`)
- `ticket_id`: Target ticket ID
- `previous_level`: Level before action
- `new_level`: Resulting escalation level
- `target_role`: Assigned authority role (`DEPARTMENT_HOD`, `ADMIN`, etc.)
- `reason`: Explanation for escalation
- `actor_id`: Staff user or `SYSTEM`
- `timestamp`: UTC ISO-8601 timestamp
- `status`: `PENDING` | `ACKNOWLEDGED` | `RESOLVED`
