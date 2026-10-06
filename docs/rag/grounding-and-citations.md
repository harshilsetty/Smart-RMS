# Grounding & Source Citations

## 1. Grounding Principles

1. **Evidence-First**: Responses are generated strictly from retrieved evidence. General world knowledge cannot be substituted for university regulation.
2. **Deterministic Citations**: Every generated draft cites the specific `document_id`, `version`, and `clause` from which its recommendations stem.
3. **No-Source &rarr; No-Answer**: When query evidence fails the $0.65$ relevance threshold:
   - Status is marked `INSUFFICIENT_EVIDENCE`.
   - `needs_human_review` is set to `True`.
   - No autonomous commitments are drafted.
   - The ticket is routed directly to the departmental operator desk.

## 2. Citation Traceability Contract

Retrieved citations adhere to the following schema:
- `document_id`: Canonical document identifier (e.g. `DOC-EXAM-001`)
- `document_version`: Exact active version cited (e.g. `2.0`)
- `clause`: Statutory clause reference (e.g. `Regulation 12.1`)
- `chunk_id`: Unique chunk provenance key (e.g. `DOC-EXAM-001-V20-S1-C1`)
- `relevance_score`: Numerical similarity score
- `excerpt`: Exact statutory excerpt quoted
