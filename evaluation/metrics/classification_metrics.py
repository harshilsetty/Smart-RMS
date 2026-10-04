from typing import List, Dict, Any, Tuple
from collections import defaultdict

def compute_accuracy(y_true: List[str], y_pred: List[str]) -> float:
    """Calculates overall classification accuracy."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return round(correct / len(y_true), 4)

def compute_precision_recall_f1(
    y_true: List[str],
    y_pred: List[str]
) -> Dict[str, Any]:
    """
    Computes per-class and macro/weighted average Precision, Recall, and F1.
    Pure python implementation without requiring scikit-learn.
    """
    if not y_true or len(y_true) != len(y_pred):
        return {
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "weighted_f1": 0.0,
            "classes": {}
        }

    classes = sorted(list(set(y_true).union(set(y_pred))))
    per_class: Dict[str, Dict[str, float]] = {}

    total_tp = 0
    total_samples = len(y_true)

    macro_p = 0.0
    macro_r = 0.0
    macro_f1 = 0.0
    weighted_f1 = 0.0

    for cls in classes:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == cls and yp == cls)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != cls and yp == cls)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == cls and yp != cls)
        support = sum(1 for yt in y_true if yt == cls)

        total_tp += tp

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_class[cls] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "support": support
        }

        macro_p += prec
        macro_r += rec
        macro_f1 += f1
        weighted_f1 += f1 * support

    n_classes = len(classes)
    macro_p = macro_p / n_classes if n_classes > 0 else 0.0
    macro_r = macro_r / n_classes if n_classes > 0 else 0.0
    macro_f1 = macro_f1 / n_classes if n_classes > 0 else 0.0
    weighted_f1 = weighted_f1 / total_samples if total_samples > 0 else 0.0

    return {
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "classes": per_class
    }
