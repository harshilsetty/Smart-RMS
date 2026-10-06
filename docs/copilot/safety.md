# Safety, Privacy, & Grounding Guardrails — Smart RMS

## 1. Safety Principles & Guardrails

Smart RMS enforces 12 mandatory safety rules across the operational lifecycle:

1. **Synthetic-Only Data Boundary**: No real university student records, private PII, or internal credentials are used.
2. **Zero Private API Assumptions**: The system operates independently of real university ERP/UMS endpoints, communicating strictly through the `UniversitySystemAdapter` interface.
3. **No Autonomous High-Impact Decisions**: AI models cannot modify grades, cancel fee penalties, disburse refunds, approve medical condonations, or close disciplinary grievances.
4. **AI Draft Stays a Draft**: Every AI-generated text output is marked `response_type="AI_DRAFT"`, requiring human review and explicit approval.
5. **No-Source → No-Answer Behavior**: If RAG retrieval fails to find authoritative policy documentation with relevance $\ge 0.65$, the system refuses to generate speculative policy answers and returns `INSUFFICIENT_EVIDENCE`.
6. **Strict Source Attribution**: Grounded responses must cite the exact policy title, section, and excerpt.
7. **PII Redaction Before Processing**: Student contact details, registration codes, and payment identifiers are masked prior to NLP classification or vector storage.
8. **Low-Confidence Safeguard**: Any classification with confidence $< 0.75$ enforces human review.
9. **Ambiguity Safeguard**: Cases with narrow classification margins or terse descriptions require student clarification or supervisor confirmation.
10. **Preservation of Overrides**: Manual corrections never overwrite original AI predictions in the database.
11. **Immutable Audit Trails**: Every state change, draft approval, redirection, and override is permanently logged.
12. **Statistical Transparency**: Raw heuristic scores are strictly distinguished from calibrated empirical probabilities; benchmark metrics are never estimated or fabricated.

---

## 2. Guardrail Verification Metrics

Across the 500-ticket end-to-end benchmark (`evaluation/reports/copilot_e2e_500_report.json`):
- **PII Redaction Rate**: 41.6% of tickets had sensitive tokens masked.
- **No-Source Refusal Rate**: 46.0% of tickets triggered the "No-Source → No-Answer" refusal, preventing ungrounded hallucination.
- **Enforced Human Review Rate**: 70.4% of tickets were flagged for mandatory human review due to ungrounded evidence, low confidence, or ambiguity.
- **Autonomous Resolutions**: Exactly 0.
