import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

from app.nlp.pipeline import NLPPipeline
from evaluation.metrics.classification_metrics import compute_accuracy, compute_precision_recall_f1
from evaluation.metrics.routing_metrics import compute_routing_metrics

class NLPEvaluator:
    """
    Dedicated NLP Evaluation Benchmark Engine for Milestone 4.
    Evaluates:
      1. Intent classification (accuracy, macro/weighted precision, recall, F1)
      2. Department routing (accuracy, macro/weighted precision, recall, F1)
      3. Priority classification (accuracy, macro F1, confusion matrix)
      4. Urgency classification (accuracy, distribution)
      5. Entity extraction (entity detection rates, token coverage)
      6. Ambiguity detection (ambiguity accuracy, false confidence rate)
      7. Error analysis and confusion matrices
    """

    def __init__(self, dataset_path: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent / "datasets"
        self.dataset_path = dataset_path or (base_dir / "evaluation_nlp_120.json")
        self.pipeline = NLPPipeline()

    def load_data(self) -> List[Dict[str, Any]]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Evaluation dataset missing at {self.dataset_path}")
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self) -> Dict[str, Any]:
        dataset = self.load_data()
        total_samples = len(dataset)

        y_true_intent: List[str] = []
        y_pred_intent: List[str] = []

        y_true_dept: List[str] = []
        y_pred_dept: List[str] = []

        y_true_prio: List[str] = []
        y_pred_prio: List[str] = []

        y_true_urgency: List[str] = []
        y_pred_urgency: List[str] = []

        y_true_ambiguous: List[bool] = []
        y_pred_ambiguous: List[bool] = []

        # Entity metrics counters
        entity_counts = defaultdict(int)
        entity_detected_counts = defaultdict(int)

        # Confusion matrix buckets: dict of true_label -> dict of pred_label -> count
        intent_cm = defaultdict(lambda: defaultdict(int))
        dept_cm = defaultdict(lambda: defaultdict(int))
        prio_cm = defaultdict(lambda: defaultdict(int))

        error_cases: List[Dict[str, Any]] = []
        latencies: List[float] = []

        start_total = time.time()

        for item in dataset:
            t_id = item["ticket_id"]
            subject = item.get("subject", "")
            description = item.get("description", "")
            exp_intent = item["expected_intent"]
            exp_dept = item["expected_department"]
            exp_prio = item["expected_priority"]
            exp_urgency = item.get("expected_urgency", "NORMAL")
            exp_ambiguous = item.get("is_ambiguous", False)

            # Measure NLP inference latency
            t0 = time.time()
            nlp_result = self.pipeline.process(subject=subject, description=description)
            latencies.append((time.time() - t0) * 1000) # in milliseconds

            pred_intent = nlp_result.intent
            pred_dept = nlp_result.department
            pred_prio = nlp_result.priority
            pred_urgency = nlp_result.urgency
            pred_ambiguous = nlp_result.needs_clarification

            # Record predictions
            y_true_intent.append(exp_intent)
            y_pred_intent.append(pred_intent)
            intent_cm[exp_intent][pred_intent] += 1

            y_true_dept.append(exp_dept)
            y_pred_dept.append(pred_dept)
            dept_cm[exp_dept][pred_dept] += 1

            y_true_prio.append(exp_prio)
            y_pred_prio.append(pred_prio)
            prio_cm[exp_prio][pred_prio] += 1

            y_true_urgency.append(exp_urgency)
            y_pred_urgency.append(pred_urgency)

            y_true_ambiguous.append(exp_ambiguous)
            y_pred_ambiguous.append(pred_ambiguous)

            # Entities tracking
            for ent_type, val in nlp_result.entities.items():
                entity_detected_counts[ent_type] += 1

            # Log errors
            has_error = (pred_intent != exp_intent) or (pred_dept != exp_dept) or (pred_prio != exp_prio)
            if has_error:
                error_cases.append({
                    "ticket_id": t_id,
                    "subject": subject,
                    "expected_intent": exp_intent,
                    "predicted_intent": pred_intent,
                    "expected_department": exp_dept,
                    "predicted_department": pred_dept,
                    "expected_priority": exp_prio,
                    "predicted_priority": pred_prio,
                    "confidence": nlp_result.overall_confidence,
                    "reason": nlp_result.explanation
                })

        total_duration = time.time() - start_total

        # 1. Compute Intent Metrics
        intent_acc = compute_accuracy(y_true_intent, y_pred_intent)
        intent_stats = compute_precision_recall_f1(y_true_intent, y_pred_intent)

        # 2. Compute Department Metrics
        dept_acc = compute_accuracy(y_true_dept, y_pred_dept)
        dept_stats = compute_routing_metrics(y_true_dept, y_pred_dept)

        # 3. Compute Priority Metrics
        prio_acc = compute_accuracy(y_true_prio, y_pred_prio)
        prio_stats = compute_precision_recall_f1(y_true_prio, y_pred_prio)

        # 4. Compute Urgency Metrics
        urgency_acc = compute_accuracy(y_true_urgency, y_pred_urgency)

        # 5. Compute Ambiguity Metrics
        # Ambiguity accuracy: correct classification of ambiguous vs clear requests
        ambiguity_correct = sum(1 for yt, yp in zip(y_true_ambiguous, y_pred_ambiguous) if yt == yp)
        ambiguity_accuracy = round(ambiguity_correct / total_samples, 4)

        # False confident classifications: ambiguous in ground-truth, but system had false confidence (not ambiguous)
        false_confident_count = sum(1 for yt, yp in zip(y_true_ambiguous, y_pred_ambiguous) if yt and not yp)

        # Latency statistics
        latencies.sort()
        avg_latency_ms = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
        p95_latency_ms = round(latencies[int(0.95 * len(latencies))], 3) if latencies else 0.0

        # Entity summary
        entity_summary = {k: count for k, count in entity_detected_counts.items()}

        return {
            "total_samples": total_samples,
            "total_duration_seconds": round(total_duration, 3),
            "latency": {
                "average_ms": avg_latency_ms,
                "p95_ms": p95_latency_ms,
                "throughput_tickets_per_sec": round(total_samples / total_duration, 2) if total_duration > 0 else 0.0
            },
            "intent_metrics": {
                "accuracy": intent_acc,
                "macro_precision": intent_stats["macro_precision"],
                "macro_recall": intent_stats["macro_recall"],
                "macro_f1": intent_stats["macro_f1"],
                "weighted_f1": intent_stats["weighted_f1"],
                "classes": intent_stats["classes"]
            },
            "department_metrics": {
                "accuracy": dept_acc,
                "macro_precision": dept_stats.get("macro_precision", dept_stats["routing_macro_f1"]),
                "macro_recall": dept_stats.get("macro_recall", dept_stats["routing_macro_f1"]),
                "macro_f1": dept_stats["routing_macro_f1"],
                "weighted_f1": dept_stats["routing_weighted_f1"],
                "classes": dept_stats["department_metrics"]
            },
            "priority_metrics": {
                "accuracy": prio_acc,
                "macro_precision": prio_stats["macro_precision"],
                "macro_recall": prio_stats["macro_recall"],
                "macro_f1": prio_stats["macro_f1"],
                "classes": prio_stats["classes"]
            },
            "urgency_metrics": {
                "accuracy": urgency_acc
            },
            "ambiguity_metrics": {
                "ambiguity_detection_accuracy": ambiguity_accuracy,
                "total_ambiguous_queries": sum(1 for yt in y_true_ambiguous if yt),
                "detected_ambiguous_queries": sum(1 for yp in y_pred_ambiguous if yp),
                "false_confident_count": false_confident_count
            },
            "entity_extractions": entity_summary,
            "error_analysis": {
                "total_errors": len(error_cases),
                "sample_errors": error_cases[:10]
            },
            "confusion_matrices": {
                "intent": {k: dict(v) for k, v in intent_cm.items()},
                "department": {k: dict(v) for k, v in dept_cm.items()},
                "priority": {k: dict(v) for k, v in prio_cm.items()}
            }
        }
