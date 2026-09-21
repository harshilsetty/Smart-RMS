# University Knowledge Base Standards

## 1. Scope & Guidelines

This directory holds authoritative documentation regarding university policies, regulations, circulars, and SOPs used by the Smart RMS RAG retrieval system.

## 2. Ingestion Rules

1. **Approved Sources Only:** No unapproved, draft, or informal notices may be uploaded.
2. **Document Versioning:** Every document must declare an effective academic session or date (e.g., `2024-25`).
3. **Structured Clauses:** Documents should maintain distinct clause/section headings so vector chunking can preserve exact citations.
4. **Periodic Review:** When new academic council circulars supersede old rules, the expired documents must be set to `is_active: false` in the vector index.
