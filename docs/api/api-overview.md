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

#### `POST /api/v1/rms/{ticket_id}/approve`
Staff operator approval endpoint. Finalizes the draft (with or without staff modifications) and dispatches resolution.
- **Request Body**:
```json
{
  "staff_id": "STAFF-902",
  "approved_text": "Dear Student,\n\nWe acknowledge your complaint regarding the air conditioning malfunction...",
  "notes": "Verified against maintenance supervisor roster."
}
```
- **Response `200 OK`**:
```json
{
  "ticket_id": "TKT-RMS-1001",
  "status": "APPROVED",
  "resolved_at": "2026-09-21T09:45:00Z",
  "approved_by": "STAFF-902",
  "message": "Resolution approved and queued for dispatch to student portal."
}
```

---

### 1.3. Analytics & Knowledge Endpoints
- `GET /api/v1/analytics/overview`: Department ticket volume, AI acceptance rate, SLA compliance.
- `GET /api/v1/knowledge/search?q=...`: Search approved university policy base.
