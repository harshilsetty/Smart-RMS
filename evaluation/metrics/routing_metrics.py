from typing import List, Dict, Any
from evaluation.metrics.classification_metrics import compute_accuracy, compute_precision_recall_f1

def compute_routing_metrics(
    y_true_depts: List[str],
    y_pred_depts: List[str]
) -> Dict[str, Any]:
    """
    Computes department routing accuracy, precision, recall, and departmental breakdown.
    """
    accuracy = compute_accuracy(y_true_depts, y_pred_depts)
    f1_stats = compute_precision_recall_f1(y_true_depts, y_pred_depts)

    return {
        "routing_accuracy": accuracy,
        "routing_macro_f1": f1_stats["macro_f1"],
        "routing_weighted_f1": f1_stats["weighted_f1"],
        "department_metrics": f1_stats["classes"]
    }
