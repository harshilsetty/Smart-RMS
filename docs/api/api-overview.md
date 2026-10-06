# Smart RMS API Overview

The Smart RMS Backend provides a clean, versioned RESTful API built on **FastAPI**. In development mode, the API operates seamlessly with deterministic mock data and synthetic records.

- **Base URL:** `http://localhost:8000`
- **Swagger Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc Interactive Docs:** `http://localhost:8000/redoc`

---

## 1. Core Endpoints

### 1.1. System Health
#### `GET /health`
Returns system status, active environment, AI provider mode, and vector store status.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai_provider": "mock",
  "vector_store": "mock",
  "mock_mode": true
}
```

---

### 1.2. RMS Ticket Operations

#### `GET /api/v1/rms`
Fetch a list of RMS tickets with optional filtering and pagination.
- **Query Parameters:**
  - `department` (string, optional): Filter by department name.
  - `priority` (string, optional): Filter by priority (`Low`, `Medium`, `High`, `Critical`).
  - `status` (string, optional): Filter by status (`INGESTED`, `ANALYZED`, `DRAFTED`, `STAFF_REVIEW`, `APPROVED`, `RESOLVED`, `ESCALATED`).
  - `search` (string, optional): Keyword search in ticket subject or description.
- **Response `200 OK`**:
```json
{
  "total": 12,
  "count": 12,
  "tickets": [
    {
      "ticket_id": "TKT-RMS-1001",
      "student_reference": "STU-SYN-8492",
      "subject": "Room AC Unit Not Functioning and Water Leakage in BH-4 Room 312",
      "category": "Hostel",
      "department": "Hostel Affairs",
      "priority": "High",
      "status": "STAFF_REVIEW",
      "created_at": "2026-09-20T14:30:00Z",
      "ai_analysis": {
        "intent": "HOSTEL_MAINTENANCE",
        "suggested_department": "Hostel Affairs",
        "priority_score": 3,
        "confidence": 0.94,
        "pii_detected": ["[REDACTED_PHONE]", "[REDACTED_REG_NO]"]
      }
    }
  ]
}
```

---

#### `GET /api/v1/rms/{ticket_id}`
Retrieve complete details, original text, PII redaction log, and lifecycle timeline for a specific ticket.
- **Parameters:** `ticket_id` (string, path)
- **Response `200 OK`**

---

#### `POST /api/v1/rms/{ticket_id}/analyze`
Trigger or refresh the AI NLP triage pipeline on an existing ticket.
- **Parameters:** `ticket_id` (string, path)
- **Processing:**
  1. Mask detected PII.
  2. Classify intent and department.
  3. Compute urgency/priority score.
  4. Query RAG vector store for policy clauses.
- **Response `200 OK`**:
```json
{
  "ticket_id": "TKT-RMS-1001",
  "intent": "HOSTEL_MAINTENANCE",
  "department": "Hostel Affairs",
  "priority": "High",
  "confidence": 0.94,
  "entities": {
    "hostel_block": "BH-4",
    "room_no": "312",
    "issue": "Air conditioning unit leakage"
  },
  "pii_redacted_count": 2,
  "suggested_action": "DISPATCH_ELECTRICIAN"
}
```

---

#### `GET /api/v1/rms/{ticket_id}/draft`
Retrieve the grounded AI-generated draft response along with verified policy citations.
- **Parameters:** `ticket_id` (string, path)
- **Response `200 OK`**:
```json
{
  "ticket_id": "TKT-RMS-1001",
  "draft_response": "Dear Student,\n\nWe acknowledge your complaint regarding the air conditioning malfunction in BH-4, Room 312. As per Hostel Regulations 2024 (Section 4, Clause 4.2), maintenance requests of this nature have been assigned to the electrical maintenance supervisor with a target inspection window of 24 hours.\n\nPlease keep your room accessible or notify your floor warden.\n\nWarm regards,\nHostel Operations Desk",
  "sources": [
    {
      "document_id": "DOC-2024-HOSTEL-01",
      "title": "Hostel Code of Conduct & Maintenance Regulations 2024",
      "clause": "Section 4, Clause 4.2 (Appliance & Electrical Maintenance)",
      "excerpt": "Maintenance requests for electrical and air cooling issues must be inspected within 24 hours.",
      "relevance_score": 0.96
    }
  ],
  "confidence": 0.94,
  "requires_staff_edit": false
}
```

---

#### `POST /api/v1/rms/{ticket_id}/override`
Allows authorized staff to override AI recommendations (department, priority, urgency, intent, or suggested response).
- **Behavior**: Preserves original AI prediction under `metadata["ai_original_prediction"]`, logs staff identity, timestamp, and mandatory rationale under `metadata["human_overrides"]`, and appends an immutable `HUMAN_OVERRIDE` event to the audit trail.
- **Request Body**:
```json
{
  "staff_id": "USR-STAFF-99",
  "override_department": "Student Welfare",
  "override_priority": "Critical",
  "override_urgency": "IMMEDIATE",
  "override_intent": "STUDENT_SERVICES",
  "reason": "Student grievance requires immediate welfare cell intervention."
}
```
- **Response `200 OK`**:
```json
{
  "ticket_id": "TKT-RMS-1001",
  "status": "STAFF_REVIEW",
  "original_ai_prediction": {
    "intent": "GENERAL_INQUIRY",
    "department": "General Administration",
    "priority": "Medium",
    "confidence": 0.82
  },
  "applied_overrides": {
    "department": { "from": "General Administration", "to": "Student Welfare" },
    "priority": { "from": "Medium", "to": "Critical" }
  },
  "overridden_by": "USR-STAFF-99",
  "timestamp": "2026-10-05T17:46:12Z",
  "audit_event_id": "AUDIT-OVR-1738759000",
  "message": "AI recommendation successfully overridden by staff. Audit log preserved."
}
```

---


#### `PATCH /api/v1/rms/{ticket_id}`
Update ticket attributes (status, priority, department, staff assignment). State transitions are rigorously validated by `WorkflowEngine`.
- **Request Body**:
```json
{
  "status": "IN_PROGRESS",
  "actor_id": "USR-STAFF-01",
  "reason": "Commencing student investigation"
}
```

---

#### `POST /api/v1/rms/{ticket_id}/assign`
Assign or reassign ticket to a department and/or specific active staff member. Preserves assignment history.
- **Request Body**:
```json
{
  "department_id": "DEPT-EXAM",
  "staff_id": "USR-STAFF-04",
  "assigned_by": "USR-STAFF-01",
  "reason": "Assigned to exam verification officer"
}
```

---

#### `POST /api/v1/rms/{ticket_id}/redirect`
Redirect ticket to another department, deactivating existing assignments and appending an audit record.
- **Request Body**:
```json
{
  "new_department": "Examination Branch",
  "staff_id": "USR-STAFF-01",
  "reason": "Ticket concerns exam scheduling and requires Exam Cell handling."
}
```

---

#### `POST /api/v1/rms/{ticket_id}/responses`
Add a staff message, internal review note, or official response to the communication thread.
- **Request Body**:
```json
{
  "author_id": "USR-STAFF-01",
  "author_name": "Senior Registrar",
  "author_role": "STAFF_OPERATOR",
  "response_type": "STAFF",
  "content": "Contacted the department coordinator for attendance ledger.",
  "is_internal": true
}
```

---

#### `POST /api/v1/rms/{ticket_id}/escalate`
Escalate ticket to Department HOD or Tier-2 authority.
- **Request Body**:
```json
{
  "staff_id": "USR-STAFF-01",
  "target_role": "DEPARTMENT_HOD",
  "reason": "Attendance waiver requires HOD decision.",
  "urgent": true
}
```

---

#### `POST /api/v1/rms/{ticket_id}/resolve`
Officially mark ticket as resolved by staff with an official narrative dispatched into communication thread.
- **Request Body**:
```json
{
  "staff_id": "USR-STAFF-01",
  "resolution_text": "Medical certificate verified; attendance record updated in portal.",
  "notes": "Verified against University Health Center registry."
}
```

---

#### `POST /api/v1/rms/{ticket_id}/close`
Permanently close a previously resolved ticket upon verification.
- **Request Body**:
```json
{
  "staff_id": "USR-STAFF-01",
  "notes": "Student confirmed issue resolved."
}
```

---

#### `GET /api/v1/rms/{ticket_id}/history`
Retrieve append-only chronological audit trail capturing all lifecycle events, state transitions, and actors.

---

### 1.3. NLP Intelligence Pipeline Endpoints

#### `POST /api/v1/nlp/analyze`
Executes modular NLP intelligence triage (Intent, Department, Priority, Urgency, Entity Extraction, Confidence).
- **Request Body (Direct or by Ticket ID)**:
```json
{
  "subject": "Urgent: Admit card blocked for CSE 472",
  "description": "Exam commences in 24 hours. The student portal says admit card blocked due to library fine in Semester 5."
}
```
- **Response `200 OK`**:
```json
{
  "intent": "EXAMINATION",
  "intent_confidence": 0.94,
  "department": "Examination Branch",
  "department_confidence": 0.96,
  "priority": "Critical",
  "priority_confidence": 0.95,
  "priority_score": 4,
  "urgency": "IMMEDIATE",
  "urgency_confidence": 0.95,
  "entities": {
    "course_code": "CSE 472",
    "semester": "5"
  },
  "structured_entities": [
    {
      "entity_type": "course_code",
      "value": "CSE 472",
      "confidence": 0.92,
      "source_span": "CSE 472"
    }
  ],
  "needs_clarification": false,
  "clarification_reason": null,
  "confidence_level": "HIGH",
  "overall_confidence": 0.95,
  "explanation": {
    "intent": "Matched EXAMINATION keywords: admit card, exam.",
    "department": "Mapped to Examination Branch via intent and examination tokens.",
    "priority": "Exam commencing in <=48 hours with clearance obstacle.",
    "urgency": "Assessed as IMMEDIATE urgency based on temporal cues: Immediate time-window (within 24 hours)."
  }
}
```

---

### 1.4. Analytics & Knowledge Endpoints
- `GET /api/v1/analytics/overview`: Department ticket volume, AI acceptance rate, SLA compliance.
- `GET /api/v1/analytics/operations`: Real-time operational metrics (open backlog, resolved, closed, escalation count, tickets by status/dept/priority/SLA risk).
- `GET /api/v1/departments`: University departments, SLA policies, and escalation tiers.
- `GET /api/v1/users`: University staff users, roles, and workload capacity.
- `GET /api/v1/knowledge/search?q=...`: Search approved university policy base.
