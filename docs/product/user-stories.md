# User Stories & Acceptance Criteria: Smart RMS

## Epic 1: Intake, Triage & Queue Management

### US-101: Prioritized Ticket Queue
**As a** Staff Operator,  
**I want to** see a filterable list of incoming RMS tickets sorted by priority and SLA deadline,  
**So that** I can address critical and urgent student concerns before minor informational queries.

**Acceptance Criteria:**
- Queue displays ticket subject, category, urgency badge (Low, Medium, High, Critical), status, and timestamp.
- Queue supports filtering by Department, Priority, and AI Status (Pending, Analyzed, Draft Ready, Approved).
- Visual indicator flags tickets approaching SLA deadline (< 24h remaining).

---

### US-102: Automated Department Triage & Redirection
**As a** Staff Operator,  
**I want** Smart RMS to recommend the correct department for incoming tickets,  
**So that** I can redirect misclassified tickets with a single click instead of typing routing memos.

**Acceptance Criteria:**
- AI suggests primary department with a confidence score ($0.0–1.0$).
- Discrepancy between student selection and AI recommendation is highlighted with a warning badge.
- Operator can click "Redirect Department", select the target department, and add an optional note.

---

## Epic 2: Privacy & PII Protection

### US-201: Automatic Student PII Redaction
**As a** Compliance Officer,  
**I want** student phone numbers, registration numbers, and financial details masked before processing by external LLMs,  
**So that** student privacy is rigorously protected under university data protection norms.

**Acceptance Criteria:**
- Text shown to LLM and stored in public vectors contains tokens like `[REDACTED_PHONE]`, `[REDACTED_REG_NO]`.
- Staff UI displays a toggle or indicator showing detected and redacted PII entities.
- Redaction runs deterministically prior to any AI model inference.

---

## Epic 3: RAG Grounded Copilot & Human-in-the-Loop

### US-301: Grounded Response Draft Generation
**As a** Staff Operator,  
**I want to** receive an AI-generated draft response backed by official university policy clauses,  
**So that** I do not have to search lengthy handbooks or manually type standard replies.

**Acceptance Criteria:**
- Draft response is pre-loaded in the ticket detail view.
- Explicit RAG citations are displayed showing document title, clause number, and excerpt.
- If no policy matches, draft flags: *"No verified policy found. Manual investigation required."*

---

### US-302: Staff Review & One-Click Approval
**As a** Staff Operator,  
**I want to** edit the suggested draft, adjust the tone, or approve it directly,  
**So that** every outgoing communication remains under verified human control.

**Acceptance Criteria:**
- Rich text input allows the operator to modify or completely replace the suggested draft.
- Clicking "Approve & Send" records operator ID, timestamp, and updates ticket status to `APPROVED` / `RESOLVED`.
- An audit entry is appended with before/after text hashes.

---

### US-303: Escalation to Department Head
**As a** Staff Operator,  
**I want to** escalate complex, disputable, or compassionate ground cases to my Department HOD,  
**So that** higher administrative discretion can be applied where policy allows exceptions.

**Acceptance Criteria:**
- Operator can click "Escalate to HOD", attach an escalation note, and reassign ticket status to `ESCALATED`.
- HOD view displays escalated tickets in a dedicated priority inbox.
