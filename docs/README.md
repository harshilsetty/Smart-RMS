# Smart RMS Documentation Index

Welcome to the comprehensive technical and product documentation for **Smart RMS** (Smart University RMS Resolution & Operations System).

---

## 📚 Table of Contents

### 1. Architecture Blueprints (`docs/architecture/`)
- [System Architecture](architecture/system-architecture.md): Full end-to-end data pipeline from student submission, API gateway, query orchestrator, privacy layer, RAG, human review, to resolution.
- [AI & NLP Pipeline](architecture/ai-pipeline.md): Multi-stage AI pipeline covering PII detection, classification, priority calculation, and grounded response drafting.
- [RAG Architecture](architecture/rag-architecture.md): Knowledge ingestion, chunking strategy, embeddings, Chroma vector store, and source attribution.
- [Privacy & Security](architecture/privacy-security.md): Synthetic data governance, PII masking rules, RBAC matrix, and audit logging.
- [Integration Architecture](architecture/integration-architecture.md): Pluggable adapter interfaces for university systems (UMS/RMS, ERP, LMS, Attendance).

### 2. Product Specifications (`docs/product/`)
- [Problem Statement](product/problem-statement.md): Deep-dive into university grievance bottlenecks, cognitive fatigue, and why simple intake portals do not solve the resolution problem.
- [Product Overview](product/product-overview.md): Product scope, "AI assists, Humans decide" philosophy, and expected operational impact.
- [User Roles & Permissions](product/user-roles.md): Personas (Student, Staff Agent, Department HOD, Admin) and permission boundaries.
- [User Stories & Acceptance Criteria](product/user-stories.md): Agile user stories mapping out staff triage and resolution workflows.
- [Product Roadmap](product/roadmap.md): 5-phase delivery plan from foundation to university staging pilot.

### 3. API & Engineering Standards (`docs/api/` & `docs/decisions/`)
- [API Overview](api/api-overview.md): OpenAPI/REST specifications, route catalogue, request/response models, and status codes.
- [ADR-001: Initial Architecture](decisions/ADR-001-initial-architecture.md): Architecture Decision Record detailing our core technology and framework selections.
