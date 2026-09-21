# ADR-001: Initial Architecture & Technology Selection

## Context and Problem Statement
Large university environments face an acute administrative challenge: handling thousands of unstructured, policy-governed student relationship management (RMS) tickets daily. The operational goal is to accelerate triage, protect student privacy, and assist administrative staff in drafting grounded, policy-backed replies without autonomous AI hallucinations or unverified decisions.

We needed to establish the foundational architecture, framework stack, AI abstractions, and integration boundaries for Smart RMS.

---

## Decision Drivers
- **Product Principle:** "AI assists, humans decide." No autonomous, unverified commitments.
- **Data Privacy:** Synthetic data in development; automated PII redaction before vector or LLM submission.
- **Provider Independence:** AI services and vector databases must run out-of-the-box in local development with deterministic mock adapters, without demanding external API keys.
- **Interoperability:** Pluggable adapter interfaces for university systems (such as LPU UMS/RMS) without assuming private production APIs exist during initial phases.
- **High Developer Ergonomics:** Clean separation of concerns, fast feedback loops, and type safety.

---

## Considered Options

### Backend Framework
- **FastAPI (Python):** Native async ASGI performance, automatic OpenAPI/Swagger documentation, Pydantic type validation, and seamless integration with Python AI ecosystems (LangChain, Chroma). **[Selected]**
- **Django / Flask:** Django is overly monolithic for an AI microservice; Flask lacks native async orchestration and automatic schema validation.

### Frontend Framework
- **React + TypeScript + Vite + Tailwind CSS:** Fast HMR, strong typing, reusable modern components, rapid layout capability for dense staff queues. **[Selected]**
- **Next.js:** Server-side rendering overhead is unnecessary for an internal administrative copilot workstation.

### Vector Storage
- **ChromaDB with Mock Vector Store Abstraction:** Lightweight, embedded/containerized, pythonic, easy to seed. **[Selected]**
- **Pinecone / Weaviate Cloud:** Imposes external SaaS dependencies and potential student data sovereignty violations.

### AI & LLM Orchestration
- **Modular Provider Abstraction (`AIProvider` with `MockAIProvider` and `GeminiProvider`):** Allows deterministic testing without an API key while enabling seamless connection to Gemini 1.5 Flash in staging. **[Selected]**
- **Direct OpenAI/Google SDK calls:** Tightly couples business logic to a single vendor API.

---

## Decision Outcome

1. **Adopted FastAPI (Python 3.11+)** as the backend orchestration engine.
2. **Adopted React 19 + TypeScript + Vite + Tailwind CSS** for the staff copilot dashboard.
3. **Engineered an Adapter Layer (`UniversitySystemAdapter`)** with `MockRMSAdapter` active by default.
4. **Engineered a Privacy Layer (`PIIDetector`, `PIIRedactor`)** executed upstream of any LLM calls.
5. **Enforced Human-in-the-Loop:** All official resolutions require staff sign-off before status changes to `APPROVED` or `RESOLVED`.

---

## Consequences

### Positive
- Developers and reviewers can run both backend and frontend locally immediately without requiring external keys, databases, or university VPN access.
- Modular interfaces allow replacing the mock AI and mock vector store with Gemini and Chroma simply by changing `.env`.
- Strict PII masking ensures zero sensitive student data is leaked to model providers.

### Trade-offs / Mitigations
- Mock providers require maintaining realistic synthetic fixtures.
  - *Mitigation:* We established a rich dataset of 12+ multi-department university tickets and official policy excerpts in `data/mock/`.
