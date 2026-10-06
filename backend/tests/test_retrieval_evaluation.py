import pytest
from app.rag.evaluator import RetrievalEvaluator

def test_retrieval_benchmark_metrics():
    """Verify that retrieval evaluation metrics meet established benchmark thresholds."""
    evaluator = RetrievalEvaluator()
    metrics = evaluator.evaluate(k_values=[1, 3, 5])
    
    assert metrics["total_queries"] >= 50
    assert metrics["supported_queries"] >= 35
    assert metrics["unsupported_queries"] >= 10
    
    # Precision@1 must exceed 80%
    assert metrics["precision_at_1"] >= 0.80
    # Recall@3 must exceed 85%
    assert metrics["recall_at_3"] >= 0.85
    # MRR must exceed 0.85
    assert metrics["mrr"] >= 0.85
    # Safety: No-Answer Rejection Rate must be >= 90% (100% ideal)
    assert metrics["no_answer_accuracy"] >= 0.90
