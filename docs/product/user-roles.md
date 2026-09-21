# User Roles & Personas: Smart RMS

## 1. Overview

Smart RMS defines four primary user personas to model university operations, security boundaries, and authorization workflows.

---

## 2. Persona Definitions

### 2.1. RMS Staff Operator (Primary User)
- **Role:** Frontline administrative officer assigned to specific university departments (e.g., Academic Services, Hostel Warden Office, Fee Desk).
- **Responsibilities:**
  - Triages incoming department queue.
  - Reviews AI-extracted intent, priority, and detected PII.
  - Evaluates grounded policy references retrieved by RAG.
  - Edits pre-generated response drafts for tone and specific context.
  - Formally approves and dispatches official resolutions.
  - Reroutes misassigned tickets to other departments.

### 2.2. Department Head / Escalation Lead (HOD)
- **Role:** Department Chair, Chief Warden, or Senior Administrative Officer.
- **Responsibilities:**
  - Oversees tickets escalated by staff due to policy ambiguity or high sensitivity.
  - Authorizes policy exceptions (e.g., fee penalty waivers or special examination permissions).
  - Reviews department-level turnaround times and SLA breaches.
  - Approves newly uploaded university policy documents for RAG indexing.

### 2.3. System & Compliance Administrator
- **Role:** University Infotech or Operations Manager.
- **Responsibilities:**
  - Manages AI provider configurations, confidence thresholds, and system health.
  - Configures Role-Based Access Control (RBAC) and user provisioning.
  - Manages RAG vector knowledge base collections and document pipelines.
  - Reviews privacy compliance and downloads audit logs.

### 2.4. Student / Grievant (End User / Upstream)
- **Role:** Enrolled student, alumnus, or parent submitting a grievance.
- **Interaction:**
  - Submits ticket via university web/mobile portal (e.g., LPU UMS).
  - Receives timely, transparent, policy-grounded official responses.
  - Note: Students interact via their student portal and do not access the internal Smart RMS staff dashboard.
