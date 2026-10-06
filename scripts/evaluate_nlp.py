import sys
import json
import time
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "backend"))

from evaluation.nlp_evaluator import NLPEvaluator

def main():
    print("=" * 65)
    print("SMART RMS — MILESTONE 4 NLP BENCHMARK & EVALUATION")
    print("=" * 65)

    evaluator = NLPEvaluator()
    results = evaluator.evaluate()

    total = results["total_samples"]
    intent_m = results["intent_metrics"]
    dept_m = results["department_metrics"]
    prio_m = results["priority_metrics"]
    urg_m = results["urgency_metrics"]
    amb_m = results["ambiguity_metrics"]
    lat_m = results["latency"]

    print(f"\n[1] Benchmark Dataset Overview:")
    print(f"    - Total Labeled Evaluation Samples:  {total}")
    print(f"    - Processing Duration:               {results['total_duration_seconds']:.2f}s")
    print(f"    - Average Inference Latency:         {lat_m['average_ms']:.2f} ms")
    print(f"    - P95 Latency:                       {lat_m['p95_ms']:.2f} ms")
    print(f"    - Throughput:                        {lat_m['throughput_tickets_per_sec']:.1f} tickets/sec")

    print(f"\n[2] Intent Classification Performance:")
    print(f"    - Accuracy:                          {intent_m['accuracy'] * 100:.2f}%")
    print(f"    - Macro Precision:                   {intent_m['macro_precision'] * 100:.2f}%")
    print(f"    - Macro Recall:                      {intent_m['macro_recall'] * 100:.2f}%")
    print(f"    - Macro F1-Score:                    {intent_m['macro_f1']:.4f}")
    print(f"    - Weighted F1-Score:                 {intent_m['weighted_f1']:.4f}")

    print(f"\n[3] Department Routing Performance:")
    print(f"    - Accuracy:                          {dept_m['accuracy'] * 100:.2f}%")
    print(f"    - Macro F1-Score:                    {dept_m['macro_f1']:.4f}")
    print(f"    - Weighted F1-Score:                 {dept_m['weighted_f1']:.4f}")

    print(f"\n[4] Priority & Urgency Classification Performance:")
    print(f"    - Priority Accuracy:                 {prio_m['accuracy'] * 100:.2f}%")
    print(f"    - Priority Macro F1:                 {prio_m['macro_f1']:.4f}")
    print(f"    - Urgency Accuracy:                  {urg_m['accuracy'] * 100:.2f}%")

    print(f"\n[5] Ambiguity & Out-of-Domain Safety:")
    print(f"    - Ambiguity Detection Accuracy:      {amb_m['ambiguity_detection_accuracy'] * 100:.2f}%")
    print(f"    - Ambiguous Queries in Ground Truth: {amb_m['total_ambiguous_queries']}")
    print(f"    - Queries Flagged for Clarification: {amb_m['detected_ambiguous_queries']}")
    print(f"    - False Confident Errors:            {amb_m['false_confident_count']}")

    print(f"\n[6] Extracted Domain Entities:")
    for ent, cnt in sorted(results["entity_extractions"].items(), key=lambda x: x[1], reverse=True):
        print(f"    - {ent:<24}: {cnt} instances extracted")

    # Save detailed evaluation report
    report_path = repo_root / "evaluation" / "reports" / "nlp_evaluation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Detailed evaluation report saved to: {report_path}")
    print("=" * 65)

if __name__ == "__main__":
    main()
