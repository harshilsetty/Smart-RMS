# RAG Evaluation Framework & Benchmark Results

## 1. Methodology

The evaluation framework evaluates retrieval quality, ranking effectiveness, and safety adherence across 54 synthetic benchmark queries and 500 synthetic RMS ticket queries.

### Metrics Computed:
- **Precision@K**: Proportion of top-$K$ retrieved documents that match ground truth.
- **Recall@K**: Proportion of relevant ground truth documents captured within top-$K$.
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal rank of the first relevant document.
- **No-Answer Accuracy**: Percentage of unsupported/out-of-domain queries successfully refused.
- **Grounding Support Rate**: Percentage of supported queries generating valid, traceable citations.

---

## 2. Actual Measured Results

Benchmark execution via `python scripts/evaluate_rag.py`:

| Metric | Target | Actual Measured | Status |
| :--- | :--- | :--- | :--- |
| **Precision@1** | $\ge 80.0\%$ | **89.74%** | PASSED |
| **Precision@3** | $\ge 65.0\%$ | **73.50%** | PASSED |
| **Precision@5** | $\ge 50.0\%$ | **51.79%** | PASSED |
| **Recall@3** | $\ge 85.0\%$ | **92.31%** | PASSED |
| **Recall@5** | $\ge 85.0\%$ | **92.31%** | PASSED |
| **MRR** | $\ge 0.85$ | **0.9060** | PASSED |
| **No-Answer Accuracy** | $\ge 90.0\%$ | **100.00%** | PASSED |
| **Grounding Support Rate**| Baseline | **46.15%** | PASSED |
| **Average Query Latency** | $< 10.0\text{ ms}$ | **0.52 ms** | PASSED |
| **P95 Query Latency** | $< 20.0\text{ ms}$ | **0.84 ms** | PASSED |
| **500 Ticket Batch Throughput** | $> 500\text{ tps}$ | **1,914.3 tickets/sec** | PASSED |

---

## 3. 500-Ticket Synthetic Batch Summary

Out of 500 synthetic RMS tickets processed:
- **Grounded Responses**: 220 (44.0%) had strong policy matches (&ge; 0.65) and received grounded drafts.
- **Routed to Staff Review**: 280 (56.0%) were novel, ambiguous, or lacked exact policy counterparts, triggering the `INSUFFICIENT_EVIDENCE` safety boundary.
- **Runtime**: 0.26 seconds for the entire 500-ticket batch.
- **Zero Ungrounded Claims**: The system produced zero ungrounded policy commitments.
