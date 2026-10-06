# Policy Retrieval & Ranking

## 1. Retrieval Strategy

The policy retrieval layer (`PolicyRetriever` and `LocalVectorStore`) implements a hybrid scoring function balancing semantic dense similarity with domain keyword matching and departmental awareness:

$$\text{Final Score} = \min(0.99, 0.72 \cdot \text{Cosine}(\vec{q}, \vec{d}) + \text{LexicalOverlapBonus} + \text{DepartmentBoost})$$

- **Dense Component ($0.72 \cdot \cos$)**: Captures semantic similarity across paraphrased natural language expressions.
- **Lexical Overlap Bonus (up to $+0.25$)**: Rewards exact keyword matches (e.g. `re-evaluation`, `admit card`, `overload`).
- **Soft Departmental Boost ($+0.18$)**: Prioritizes policies belonging to the ticket's assigned department while keeping relevant cross-departmental policies discoverable.

## 2. Statutory Filtering

Retrieval deterministically filters out:
1. Unapproved policies (`approval_status != "APPROVED"`).
2. Expired policies (`expiry_date < today`).
3. Future effective policies (`effective_date > today`).
4. Superseded versions when a newer approved version of the same document exists (unless a specific version is explicitly requested).

## 3. Top-K & Relevance Threshold

- **Configurable $K$**: Defaults to `top_k=3` or `top_k=5`.
- **Relevance Threshold**: Baseline set to `0.65`. Queries failing to achieve $0.65$ score are categorized as `INSUFFICIENT_EVIDENCE`.
