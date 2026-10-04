import pytest
import os
import sys
from pathlib import Path

# Ensure paths
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.nlp.intent_classifier import RuleBasedIntentClassifier
from app.nlp.department_classifier import RuleBasedDepartmentRouter
from app.nlp.urgency_classifier import RuleBasedUrgencyClassifier
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.semantic_similarity import SemanticSimilarityEngine
from app.nlp.confidence import ConfidenceEvaluator
from app.nlp.pipeline import NLPPipeline
from app.nlp.schemas import PriorityLevel, ConfidenceLevel
from app.rag.vector_store import LocalVectorStore, DocumentChunker
from app.rag.retriever import PolicyRetriever
from app.ai.mock_provider import MockAIProvider
from evaluation.metrics.classification_metrics import compute_accuracy, compute_precision_recall_f1
from evaluation.metrics.retrieval_metrics import compute_retrieval_metrics
from evaluation.metrics.grounding_metrics import compute_grounding_metrics
from scripts.generate_rms_dataset import generate_synthetic_dataset
from scripts.run_batch_analysis import run_batch_analysis
from fastapi.testclient import TestClient
from app.main import app

def test_intent_classifier():
    classifier = RuleBasedIntentClassifier()
    
    res1 = classifier.classify("Air conditioner leaking water in BH-4 room 201")
    assert res1.intent == "HOSTEL_MAINTENANCE"
    assert res1.confidence >= 0.75
    
    res2 = classifier.classify("Tuition fee deducted twice from HDFC bank account")
    assert res2.intent == "FEE_PAYMENT"
    
    res3 = classifier.classify("End term examination hall ticket blocked")
    assert res3.intent == "EXAMINATION"
    
    res4 = classifier.classify("CA-2 rubric marks discrepancy in CSE 472")
    assert res4.intent == "ACADEMIC"
    
    res5 = classifier.classify("Hospitalization medical leave attendance condonation")
    assert res5.intent == "ATTENDANCE"
    
    res6 = classifier.classify("National Scholarship Portal NSP application verification")
    assert res6.intent == "SCHOLARSHIP"
    
    res7 = classifier.classify("Campus Wi-Fi Fortinet portal MAC address registration error")
    assert res7.intent == "IT_SUPPORT"
    
    res8 = classifier.classify("Official Bonafide and Medium of Instruction MOI certificate for visa")
    assert res8.intent == "STUDENT_SERVICES"

def test_department_classifier():
    router = RuleBasedDepartmentRouter()
    
    r1 = router.route("Water leak in room", intent="HOSTEL_MAINTENANCE", entities={"hostel_block": "BH-4"})
    assert r1.department == "Hostel Affairs"
    
    r2 = router.route("Fee double payment refund", intent="FEE_PAYMENT")
    assert r2.department == "Accounts & Finance"
    
    r3 = router.route("Admit card clearance hold", intent="EXAMINATION")
    assert r3.department == "Examination Branch"
    
    r4 = router.route("Course credit registration", intent="ACADEMIC")
    assert r4.department == "Academic Affairs"
    
    r5 = router.route("Medical leave duty", intent="ATTENDANCE")
    assert r5.department == "Student Welfare"
    
    r6 = router.route("NSP portal status", intent="SCHOLARSHIP")
    assert r6.department == "Scholarship Section"
    
    r7 = router.route("Wi-Fi MAC issue in BH-4", intent="IT_SUPPORT", entities={"hostel_block": "BH-4"})
    assert r7.department == "IT Services"

def test_urgency_classifier():
    classifier = RuleBasedUrgencyClassifier()
    
    # Critical: hazard / exam commencing in <=48 hrs
    c1 = classifier.classify("Water leak dripping right near electrical switchboard")
    assert c1.priority == PriorityLevel.CRITICAL
    assert c1.priority_score == 4
    
    c2 = classifier.classify("Exam starts in 24 hours and admit card blocked")
    assert c2.priority == PriorityLevel.CRITICAL
    
    # High: duplicate fee deduction
    h1 = classifier.classify("Fee was debited twice from bank account")
    assert h1.priority == PriorityLevel.HIGH
    assert h1.priority_score == 3
    
    # Medium: CA marks rubric discrepancy
    m1 = classifier.classify("CA rubric continuous assessment score discrepancy", intent="ACADEMIC")
    assert m1.priority == PriorityLevel.MEDIUM
    assert m1.priority_score == 2
    
    # Low: routine bonafide certificate request
    l1 = classifier.classify("Request for Bonafide certificate for passport application", intent="STUDENT_SERVICES")
    assert l1.priority == PriorityLevel.LOW
    assert l1.priority_score == 1

def test_entity_extractor():
    extractor = EntityExtractor()
    text = "In BH-4 Room 312, paid INR 65,000 for CSE 472 on 18th Sept via HDFC Bank."
    entities = extractor.extract(text)
    
    assert entities.get("hostel_block") == "BH-4"
    assert entities.get("room_number") == "312"
    assert entities.get("course_code") == "CSE 472"
    assert "65,000" in entities.get("currency_amount", "")
    assert "HDFC" in entities.get("bank_name", "")

def test_semantic_similarity():
    engine = SemanticSimilarityEngine()
    
    score_same = engine.similarity("Admit card blocked before exam", "Admit card blocked before exam")
    assert score_same == 1.0
    
    score_related = engine.similarity("Admit card clearance hold", "Hall ticket blocked for end term exam")
    assert score_related > 0.25
    
    score_unrelated = engine.similarity("Hostel tap leaking", "Scholarship portal deadline")
    assert score_unrelated < score_related
    
    candidates = [
        {"document_id": "DOC-EXAM", "title": "Examination Hall Ticket Rules", "content": "Admit cards are generated 7 days prior."},
        {"document_id": "DOC-HOSTEL", "title": "Hostel Maintenance Regulations", "content": "Plumbing and water leak requests."}
    ]
    ranked = engine.find_similar("Admit card hold", candidates, top_k=1)
    assert len(ranked) == 1
    assert ranked[0][1]["document_id"] == "DOC-EXAM"

def test_confidence_and_review():
    evaluator = ConfidenceEvaluator()
    
    # High confidence scenario
    level_high, rev_high, _ = evaluator.evaluate(intent_conf=0.95, dept_conf=0.92, priority_conf=0.90, has_authoritative_source=True)
    assert level_high == ConfidenceLevel.HIGH
    assert rev_high is False
    
    # Low confidence scenario
    level_low, rev_low, reasons = evaluator.evaluate(intent_conf=0.55, dept_conf=0.60, priority_conf=0.50, has_authoritative_source=True)
    assert level_low == ConfidenceLevel.LOW
    assert rev_low is True
    assert len(reasons) > 0
    
    # No authoritative source scenario
    _, rev_nosource, reasons_nosource = evaluator.evaluate(intent_conf=0.95, dept_conf=0.95, priority_conf=0.95, has_authoritative_source=False)
    assert rev_nosource is True
    assert any("authoritative" in r for r in reasons_nosource)

@pytest.mark.asyncio
async def test_no_source_no_answer():
    provider = MockAIProvider()
    subject = "Where can I buy fiction novel paperbacks on campus?"
    desc = "Looking for fiction books."
    
    # Passing empty sources should trigger strict fallback
    draft = await provider.generate_draft(subject, desc, sources=[], department="Academic Affairs")
    assert draft.confidence == 0.0
    assert draft.requires_staff_edit is True
    assert "Insufficient authoritative information. Human review required." in draft.draft_response

def test_rag_local_retrieval():
    store = LocalVectorStore()
    assert len(store.documents) > 0
    assert len(store.chunks) >= len(store.documents)
    
    results = store.search("AC unit leaking water in room", department="Hostel Affairs", limit=2)
    assert len(results) > 0
    assert results[0]["document_id"] == "DOC-2024-HOSTEL-01"
    assert "source_id" in results[0]
    assert "document_name" in results[0]
    assert "section" in results[0]

def test_evaluation_metrics():
    # Accuracy test
    y_true = ["A", "B", "A", "C"]
    y_pred = ["A", "B", "C", "C"]
    acc = compute_accuracy(y_true, y_pred)
    assert acc == 0.75
    
    # Precision, Recall, F1 test
    stats = compute_precision_recall_f1(y_true, y_pred)
    assert "macro_f1" in stats
    assert "weighted_f1" in stats
    assert stats["macro_f1"] > 0.0
    
    # Retrieval metrics test
    retrieved = [["D1", "D2", "D3"], ["D2", "D1", "D3"]]
    expected = ["D1", "D2"]
    ret_stats = compute_retrieval_metrics(retrieved, expected, k_values=[1, 3])
    assert ret_stats["precision_at_1"] == 1.0
    assert ret_stats["recall_at_3"] == 1.0
    
    # Grounding metrics test
    drafts = ["According to University Fee Policy Clause 8.3 refund within 7 days", "Insufficient authoritative information. Human review required."]
    sources = [[{"title": "University Fee Policy", "clause": "Clause 8.3", "excerpt": "refund within 7 days"}], []]
    exp_docs = ["DOC-FEE", None]
    grounding = compute_grounding_metrics(drafts, sources, exp_docs)
    assert grounding["grounding_rate"] == 1.0
    assert grounding["no_source_adherence"] == 1.0

def test_synthetic_dataset_generator():
    data = generate_synthetic_dataset(count=20, seed=123)
    assert len(data) == 20
    assert "ticket_id" in data[0]
    assert "ground_truth_intent" in data[0]
    assert "ground_truth_department" in data[0]
    assert "ground_truth_priority" in data[0]
    
    # Determinism check
    data2 = generate_synthetic_dataset(count=20, seed=123)
    assert data[0]["ticket_id"] == data2[0]["ticket_id"]
    assert data[0]["subject"] == data2[0]["subject"]

def test_batch_processing(tmp_path):
    input_file = tmp_path / "test_batch.json"
    output_file = tmp_path / "batch_out.json"
    
    data = generate_synthetic_dataset(count=10, seed=99)
    with open(input_file, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f)
        
    summary = run_batch_analysis(input_file, output_file)
    assert summary["total_processed"] == 10
    assert summary["throughput_tickets_per_sec"] > 0
    assert output_file.exists()

def test_evaluation_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/evaluation/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_size"] == 60
    assert "intent_accuracy" in data
    assert "department_accuracy" in data
    assert "priority_accuracy" in data
    assert "retrieval_precision_at_1" in data
    assert "grounding_rate" in data
    assert "human_review_rate" in data
    assert data["intent_accuracy"] > 0.8
    assert data["department_accuracy"] > 0.8
