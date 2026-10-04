import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.config import settings
from app.privacy.pii_redactor import PIIRedactor
from app.nlp.pipeline import NLPPipeline
from app.rag.retriever import PolicyRetriever
from app.ai.mock_provider import MockAIProvider
from evaluation.metrics.classification_metrics import compute_accuracy, compute_precision_recall_f1
from evaluation.metrics.routing_metrics import compute_routing_metrics
from evaluation.metrics.retrieval_metrics import compute_retrieval_metrics
from evaluation.metrics.grounding_metrics import compute_grounding_metrics

class RMSEvaluationEngine:
    """
    Automated evaluation engine for Smart RMS NLP, Routing, Retrieval, and Grounding.
    Executes benchmark evaluations over synthetic datasets and produces verified runtime metrics.
    """

    def __init__(
        self,
        eval_dataset_path: Optional[Path] = None,
        expected_outputs_path: Optional[Path] = None
    ):
        base_eval_dir = Path(__file__).resolve().parent / "datasets"
        self.dataset_path = eval_dataset_path or (base_eval_dir / "evaluation_rms.json")
        self.expected_path = expected_outputs_path or (base_eval_dir / "expected_outputs.json")

        self.pii_redactor = PIIRedactor()
        self.nlp_pipeline = NLPPipeline()
        self.retriever = PolicyRetriever()
        self.ai_provider = MockAIProvider(nlp_pipeline=self.nlp_pipeline)

    def load_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Evaluation dataset missing at {self.dataset_path}")
        if not self.expected_path.exists():
            raise FileNotFoundError(f"Expected outputs missing at {self.expected_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        with open(self.expected_path, "r", encoding="utf-8") as f:
            expected_list = json.load(f)

        expected_map = {item["ticket_id"]: item for item in expected_list}
        return items, expected_map

    async def run_evaluation(self) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation pipeline on all samples.
        Computes actual measurable metrics dynamically.
        """
        items, expected_map = self.load_data()

        y_true_intent = []
        y_pred_intent = []

        y_true_dept = []
        y_pred_dept = []

        y_true_prio = []
        y_pred_prio = []

        retrieved_doc_lists: List[List[str]] = []
        expected_doc_ids: List[Optional[str]] = []

        draft_responses: List[str] = []
        retrieved_sources_all: List[List[Dict[str, Any]]] = []

        human_review_flags = []
        error_cases = []

        candidate_docs = getattr(self.retriever.vector_store, "documents", [])

        for item in items:
            t_id = item["ticket_id"]
            if t_id not in expected_map:
                continue

            expected = expected_map[t_id]
            subject = item.get("subject", "")
            raw_desc = item.get("description", "")

            # 1. PII Redaction
            redacted_desc, _ = self.pii_redactor.redact(raw_desc)

            # 2. NLP Pipeline
            nlp_result = self.nlp_pipeline.process(
                subject=subject,
                description=redacted_desc,
                candidate_docs=candidate_docs
            )

            # 3. RAG Retrieval
            sources = self.retriever.retrieve(
                query=f"{subject} {redacted_desc}",
                department=nlp_result.department,
                limit=3
            )
            sources_dicts = [s.model_dump() for s in sources]
            retrieved_ids = [s.document_id for s in sources]

            # 4. Grounded Draft Generation
            draft = await self.ai_provider.generate_draft(
                ticket_subject=subject,
                ticket_description=redacted_desc,
                sources=sources,
                department=nlp_result.department
            )

            # Collect outputs
            exp_intent = expected["expected_intent"]
            exp_dept = expected["expected_department"]
            exp_prio = expected["expected_priority"]
            exp_doc = expected.get("expected_doc_id")

            pred_intent = nlp_result.intent
            pred_dept = nlp_result.department
            pred_prio = nlp_result.priority

            y_true_intent.append(exp_intent)
            y_pred_intent.append(pred_intent)

            y_true_dept.append(exp_dept)
            y_pred_dept.append(pred_dept)

            y_true_prio.append(exp_prio)
            y_pred_prio.append(pred_prio)

            retrieved_doc_lists.append(retrieved_ids)
            expected_doc_ids.append(exp_doc)

            draft_responses.append(draft.draft_response)
            retrieved_sources_all.append(sources_dicts)

            human_review_flags.append(nlp_result.requires_human_review or draft.requires_staff_edit)

            # Log misclassifications for error analysis
            if pred_intent != exp_intent or pred_dept != exp_dept or pred_prio != exp_prio:
                error_cases.append({
                    "ticket_id": t_id,
                    "subject": subject,
                    "intent": {"expected": exp_intent, "predicted": pred_intent},
                    "department": {"expected": exp_dept, "predicted": pred_dept},
                    "priority": {"expected": exp_prio, "predicted": pred_prio}
                })

        # Calculate actual metrics
        intent_acc = compute_accuracy(y_true_intent, y_pred_intent)
        intent_stats = compute_precision_recall_f1(y_true_intent, y_pred_intent)

        routing_stats = compute_routing_metrics(y_true_dept, y_pred_dept)
        priority_acc = compute_accuracy(y_true_prio, y_pred_prio)

        retrieval_stats = compute_retrieval_metrics(
            retrieved_doc_lists=retrieved_doc_lists,
            expected_doc_ids=expected_doc_ids,
            k_values=[1, 3]
        )

        grounding_stats = compute_grounding_metrics(
            draft_responses=draft_responses,
            retrieved_sources_list=retrieved_sources_all,
            expected_doc_ids=expected_doc_ids
        )

        human_review_rate = round(sum(1 for f in human_review_flags if f) / len(human_review_flags), 4) if human_review_flags else 0.0

        return {
            "dataset_size": len(y_true_intent),
            "intent_accuracy": intent_acc,
            "intent_macro_f1": intent_stats["macro_f1"],
            "intent_weighted_f1": intent_stats["weighted_f1"],
            "department_accuracy": routing_stats["routing_accuracy"],
            "department_macro_f1": routing_stats["routing_macro_f1"],
            "department_weighted_f1": routing_stats["routing_weighted_f1"],
            "priority_accuracy": priority_acc,
            "retrieval_precision_at_1": retrieval_stats["precision_at_1"],
            "retrieval_precision_at_3": retrieval_stats["precision_at_3"],
            "retrieval_recall_at_3": retrieval_stats["recall_at_3"],
            "retrieval_mrr": retrieval_stats["mrr"],
            "grounding_rate": grounding_stats["grounding_rate"],
            "citation_fidelity": grounding_stats["citation_fidelity"],
            "no_source_adherence": grounding_stats["no_source_adherence"],
            "grounding_evaluation_type": grounding_stats["evaluation_type"],
            "human_review_rate": human_review_rate,
            "error_case_count": len(error_cases),
            "error_cases": error_cases[:10],
            "intent_per_class": intent_stats["classes"],
            "department_per_class": routing_stats["department_metrics"]
        }
