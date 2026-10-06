# Claim Grounding & Verification Architecture

## Overview
As part of Milestone 6, Smart RMS implements a robust Claim Grounding & NLI Verification pipeline. This ensures that AI-generated draft responses are strictly tethered to authoritative, retrieved university policy evidence. The system enforces the core principle: **AI Assists. Humans Decide.**

## Pipeline Stages

1. **Claim Extraction (`claim_extractor.py`)**
   - Parses the AI draft response to isolate factual assertions.
   - Differentiates between *policy claims* (e.g., "The late fee is Rs 500") and *operational statements* (e.g., "I am forwarding this to the Head"). Operational statements are ignored to prevent false-negative grounding failures.

2. **Evidence Matching (`evidence_matcher.py`)**
   - Matches extracted policy claims against the specific text chunks retrieved by the RAG system during the generation phase.
   - Enforces faithfulness by strictly limiting matching to the retrieved evidence window—preventing the system from hallucinating external support.

3. **Verification Layer (`verifier.py`)**
   - Implements a hierarchical verification approach using the `BaseClaimVerifier` pattern.
   - **Deterministic Verifier:** Uses shared heuristics (`text_utils.py`) to verify currency amounts, dates, and strict numerical rules symmetrically.
   - **NLI Verifier:** Uses Natural Language Inference (NLI) models (when loaded locally) to determine entailment, neutral, or contradiction between the claim and matched evidence.

4. **Decision Engine (`decision_engine.py`)**
   - Computes an aggregate grounding score.
   - Emits an overall status: `FULLY_GROUNDED`, `PARTIALLY_GROUNDED`, `CONTRADICTED`, or `INSUFFICIENT_EVIDENCE`.
   - **Guardrail:** High-impact policy contradictions immediately flag the draft as blocked.

## Human-in-the-Loop & Overrides
- **Inspection:** Staff can inspect atomic claim-by-claim verification results directly on the `ResponseDraftCard`.
- **Regeneration:** If a draft fails verification, staff can trigger a regeneration which forces a new reasoning path and re-verifies.
- **Overrides:** If a draft is blocked but operationally correct (or an exception is granted), staff can bypass the block via the "Override Grounding" action. This logs a permanent `GROUNDING_OVERRIDE` event in the audit trail, enforcing strict accountability.
