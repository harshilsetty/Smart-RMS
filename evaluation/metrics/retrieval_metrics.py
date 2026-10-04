from typing import List, Dict, Any, Optional

def compute_retrieval_metrics(
    retrieved_doc_lists: List[List[str]],
    expected_doc_ids: List[Optional[str]],
    k_values: List[int] = [1, 3]
) -> Dict[str, Any]:
    """
    Computes Precision@K, Recall@K, and Mean Reciprocal Rank (MRR)
    for RAG policy retrieval against ground-truth authoritative documents.
    """
    valid_queries = 0
    p_at_k = {k: 0.0 for k in k_values}
    r_at_k = {k: 0.0 for k in k_values}
    reciprocal_ranks = []

    for retrieved, expected in zip(retrieved_doc_lists, expected_doc_ids):
        # If expected is None, ticket was out-of-domain / had no authoritative policy
        if not expected:
            continue

        valid_queries += 1
        expected_set = {expected}

        # MRR calculation
        rr = 0.0
        for rank, doc_id in enumerate(retrieved, start=1):
            if doc_id == expected:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        # Precision@K and Recall@K
        for k in k_values:
            top_k_retrieved = retrieved[:k]
            hits = sum(1 for d in top_k_retrieved if d == expected)
            prec = hits / k if k > 0 else 0.0
            rec = hits / len(expected_set) if expected_set else 0.0
            p_at_k[k] += prec
            r_at_k[k] += rec

    if valid_queries == 0:
        return {
            "eval_query_count": 0,
            "precision_at_1": 0.0,
            "precision_at_3": 0.0,
            "recall_at_3": 0.0,
            "mrr": 0.0
        }

    return {
        "eval_query_count": valid_queries,
        "precision_at_1": round(p_at_k.get(1, 0.0) / valid_queries, 4),
        "precision_at_3": round(p_at_k.get(3, 0.0) / valid_queries, 4),
        "recall_at_3": round(r_at_k.get(3, 0.0) / valid_queries, 4),
        "mrr": round(sum(reciprocal_ranks) / valid_queries, 4)
    }
