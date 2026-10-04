import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
import sys
import os

# Ensure backend and root are in sys.path
repo_root = Path(__file__).resolve().parent.parent
backend_dir = repo_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.privacy.pii_redactor import PIIRedactor
from app.nlp.pipeline import NLPPipeline
from app.rag.retriever import PolicyRetriever

def run_batch_analysis(input_path: Path, output_path: Path) -> Dict[str, Any]:
    print(f"[*] Reading batch dataset from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)

    total_records = len(records)
    print(f"[*] Processing {total_records} tickets through PII -> NLP -> Routing -> Priority -> RAG -> Confidence...")

    pii_redactor = PIIRedactor()
    nlp_pipeline = NLPPipeline()
    retriever = PolicyRetriever()

    dept_counts = defaultdict(int)
    intent_counts = defaultdict(int)
    priority_counts = defaultdict(int)

    pii_detected_count = 0
    human_review_count = 0
    confidence_sum = 0.0

    start_time = time.time()
    processed_results: List[Dict[str, Any]] = []

    candidate_docs = getattr(retriever.vector_store, "documents", [])

    for idx, item in enumerate(records, start=1):
        subject = item.get("subject", "")
        raw_desc = item.get("description", "")
        ticket_id = item.get("ticket_id", f"TKT-{idx}")

        # 1. PII Redaction
        redacted_desc, vault = pii_redactor.redact(raw_desc)
        if vault:
            pii_detected_count += 1

        # 2. NLP Pipeline
        nlp_res = nlp_pipeline.process(
            subject=subject,
            description=redacted_desc,
            candidate_docs=candidate_docs
        )

        # 3. RAG Retrieval
        sources = retriever.retrieve(
            query=f"{subject} {redacted_desc}",
            department=nlp_res.department,
            limit=2
        )

        # Track statistics
        dept_counts[nlp_res.department] += 1
        intent_counts[nlp_res.intent] += 1
        priority_counts[nlp_res.priority] += 1

        avg_conf = (nlp_res.intent_confidence + nlp_res.department_confidence + nlp_res.priority_confidence) / 3.0
        confidence_sum += avg_conf

        if nlp_res.requires_human_review:
            human_review_count += 1

        processed_results.append({
            "ticket_id": ticket_id,
            "intent": nlp_res.intent,
            "department": nlp_res.department,
            "priority": nlp_res.priority,
            "confidence": round(avg_conf, 2),
            "requires_human_review": nlp_res.requires_human_review,
            "entities": nlp_res.entities,
            "sources_retrieved_count": len(sources)
        })

    elapsed_time = time.time() - start_time
    throughput = round(total_records / elapsed_time, 2) if elapsed_time > 0 else 0.0
    avg_confidence = round(confidence_sum / total_records, 4) if total_records > 0 else 0.0
    human_review_pct = round((human_review_count / total_records) * 100, 2) if total_records > 0 else 0.0

    summary = {
        "total_processed": total_records,
        "elapsed_seconds": round(elapsed_time, 3),
        "throughput_tickets_per_sec": throughput,
        "average_confidence": avg_confidence,
        "human_review_required_count": human_review_count,
        "human_review_required_percentage": human_review_pct,
        "pii_redacted_count": pii_detected_count,
        "department_distribution": dict(dept_counts),
        "intent_distribution": dict(intent_counts),
        "priority_distribution": dict(priority_counts)
    }

    full_output = {
        "summary": summary,
        "processed_sample": processed_results[:20]
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    print("==================================================")
    print("BATCH ANALYSIS RUN SUMMARY")
    print("==================================================")
    print(f"Total Processed     : {total_records}")
    print(f"Elapsed Time        : {elapsed_time:.2f}s")
    print(f"Throughput          : {throughput} tickets/sec")
    print(f"Average Confidence  : {avg_confidence:.2f}")
    print(f"Human Review Rate   : {human_review_pct}% ({human_review_count}/{total_records})")
    print(f"PII Redactions      : {pii_detected_count}")
    print("--------------------------------------------------")
    print("Department Routing Breakdown:")
    for dept, cnt in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dept:<22}: {cnt}")
    print("--------------------------------------------------")
    print("Priority Breakdown:")
    for prio, cnt in sorted(priority_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {prio:<12}: {cnt}")
    print("==================================================")
    print(f"[+] Output written to: {output_path}")

    return summary

def main():
    parser = argparse.ArgumentParser(description="Execute batch analysis pipeline on synthetic RMS dataset.")
    parser.add_argument("--input", type=str, default="data/mock/generated_rms_requests.json", help="Input dataset path")
    parser.add_argument("--output", type=str, default="evaluation/results.json", help="Output results path")

    args = parser.parse_args()

    input_file = repo_root / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_file = repo_root / args.output if not Path(args.output).is_absolute() else Path(args.output)

    if not input_file.exists():
        print(f"[-] Input file not found: {input_file}. Please run generate_rms_dataset.py first.")
        sys.exit(1)

    run_batch_analysis(input_file, output_file)

if __name__ == "__main__":
    main()
