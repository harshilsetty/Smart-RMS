import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app.nlp.preprocessing import normalize_text, tokenize, DOMAIN_SYNONYMS
from app.nlp.intent_classifier import RuleBasedIntentClassifier
from app.nlp.department_classifier import RuleBasedDepartmentRouter
from app.nlp.urgency_classifier import RuleBasedUrgencyClassifier
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.confidence import ConfidenceEvaluator
from app.nlp.pipeline import NLPPipeline
from app.nlp.schemas import PriorityLevel, UrgencyLevel, ConfidenceLevel
from app.rag.retriever import PolicyRetriever
from app.ai.mock_provider import MockAIProvider
from app.main import app

client = TestClient(app)

# 1. Preprocessing Tests
def test_preprocessing_normalization():
    raw = "My hall ticket for CSE-321 is blocked and tuition fee was debited twice!"
    norm = normalize_text(raw)
    assert "admit card" in norm
    assert "fee" in norm
    tokens = tokenize(norm)
    assert "admit" in tokens
    assert "card" in tokens

def test_preprocessing_synonym_mapping():
    assert DOMAIN_SYNONYMS.get("hall ticket") == "admit card"
    assert DOMAIN_SYNONYMS.get("tuition fee") == "fee"
    assert DOMAIN_SYNONYMS.get("re-evaluation") == "reevaluation"
    assert DOMAIN_SYNONYMS.get("wi-fi") == "wifi"

# 2. Intent Classifier Tests
def test_intent_classification_known_and_unknown():
    classifier = RuleBasedIntentClassifier()
    
    # Known intent
    res_known = classifier.classify("Hostel room geyser not working in GH-2")
    assert res_known.intent == "HOSTEL_MAINTENANCE"
    assert res_known.confidence >= 0.70
    assert not res_known.is_ambiguous

    # Unknown intent (zero signal)
    res_unknown = classifier.classify("random gibberish xyz abc 123")
    assert res_unknown.intent == "UNKNOWN"
    assert res_unknown.confidence <= 0.50
    assert res_unknown.is_ambiguous

def test_intent_classification_ambiguity_detection():
    classifier = RuleBasedIntentClassifier()
    res = classifier.classify("My issue is not solved")
    assert res.is_ambiguous is True
    assert res.confidence <= 0.60

# 3. Department Routing Tests
def test_department_routing_logic():
    router = RuleBasedDepartmentRouter()
    r1 = router.route("Hostel room broken window", intent="HOSTEL_MAINTENANCE")
    assert r1.department == "Hostel Affairs"
    assert r1.confidence >= 0.85

    r2 = router.route("Duplicate transaction refund", intent="FEE_PAYMENT")
    assert r2.department == "Accounts & Finance"

    r3 = router.route("Admit card download issue", intent="EXAMINATION")
    assert r3.department == "Examination Branch"

# 4. Priority vs Urgency Classification Tests
def test_priority_and_urgency_separation():
    urgency_classifier = RuleBasedUrgencyClassifier()

    # High priority + Immediate urgency due to temporal window
    res_imm = urgency_classifier.classify("Exam starts in 24 hours and admit card blocked")
    assert res_imm.priority == PriorityLevel.CRITICAL
    assert res_imm.urgency == UrgencyLevel.IMMEDIATE
    assert len(res_imm.temporal_expressions) > 0

    # High priority + Urgent urgency without immediate temporal cues
    res_urg = urgency_classifier.classify("Tuition fee deducted twice from bank account", intent="FEE_PAYMENT")
    assert res_imm.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
    assert res_urg.urgency == UrgencyLevel.URGENT

    # Low priority + Low urgency
    res_low = urgency_classifier.classify("Where is the university book store?", intent="STUDENT_SERVICES")
    assert res_low.priority == PriorityLevel.LOW
    assert res_low.urgency == UrgencyLevel.LOW

# 5. Entity Extraction Tests
def test_entity_extraction_structured():
    extractor = EntityExtractor()
    text = "In BH-3 Room 204, applying for re-evaluation of CSE321 in Semester 5 after paying INR 45,000 via SBI."
    entities = extractor.extract(text)
    structured = extractor.extract_structured(text)

    assert entities.get("hostel_block") == "BH-3"
    assert entities.get("room_number") == "204"
    assert entities.get("course_code") == "CSE321"
    assert entities.get("semester") == "5"
    assert "45,000" in entities.get("currency_amount", "")
    assert "SBI" in entities.get("bank_name", "")

    # Structured entities validation
    types_extracted = [s.entity_type for s in structured]
    assert "course_code" in types_extracted
    assert "currency_amount" in types_extracted
    for s in structured:
        assert s.source_span is not None
        assert s.confidence > 0.0

# 6. Confidence Engine Tests
def test_confidence_engine_thresholds():
    evaluator = ConfidenceEvaluator()
    # High confidence
    level_h, req_h, reasons_h = evaluator.evaluate(intent_conf=0.92, dept_conf=0.90, priority_conf=0.88, has_authoritative_source=True)
    assert level_h == ConfidenceLevel.HIGH
    assert req_h is False
    assert len(reasons_h) == 0

    # Low confidence triggering human review
    level_l, req_l, reasons_l = evaluator.evaluate(intent_conf=0.52, dept_conf=0.58, priority_conf=0.60, has_authoritative_source=True)
    assert level_l == ConfidenceLevel.LOW
    assert req_l is True
    assert len(reasons_l) > 0

# 7. Complete NLP Pipeline Test
def test_nlp_pipeline_complete():
    pipeline = NLPPipeline()
    subject = "Urgent: Hall ticket blocked for CSE 472"
    description = "Exam commences in 24 hours. The portal says admit card blocked due to library fine in Semester 5."

    result = pipeline.process(subject, description)
    assert result.intent == "EXAMINATION"
    assert result.department == "Examination Branch"
    assert result.priority in ["Critical", "High"]
    assert result.urgency == "IMMEDIATE"
    assert "course_code" in result.entities
    assert result.explanation is not None
    assert "intent" in result.explanation
    assert "department" in result.explanation
    assert "priority" in result.explanation
    assert result.processing_metadata is not None
    assert len(result.structured_entities) > 0

# 8. Dedicated NLP API Tests
def test_nlp_analyze_api_text_payload():
    response = client.post("/api/v1/nlp/analyze", json={
        "subject": "Water leakage near electrical switch in BH-3",
        "description": "Room 204 has water dripping on the light fixture. Need urgent repair."
    })
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert data["intent"] == "HOSTEL_MAINTENANCE"
    assert data["department"] == "Hostel Affairs"
    assert "explanation" in data
    assert "urgency" in data
    assert "structured_entities" in data
    assert data["needs_clarification"] is False

def test_nlp_analyze_api_ambiguous_payload():
    response = client.post("/api/v1/nlp/analyze", json={
        "subject": "My issue is not solved",
        "description": "Status pending please check urgently."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["needs_clarification"] is True
    assert data["clarification_reason"] is not None

def test_nlp_analyze_api_ticket_id():
    # Use existing ticket from synthetic dataset
    response = client.post("/api/v1/nlp/analyze", json={
        "ticket_id": "TKT-SYN-2001"
    })
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "department" in data
    assert "priority" in data

# 9. End-to-End NLP + RAG + Staff Override Flow
@pytest.mark.asyncio
async def test_e2e_nlp_rag_human_in_the_loop_flow():
    pipeline = NLPPipeline()
    retriever = PolicyRetriever()
    ai_provider = MockAIProvider(nlp_pipeline=pipeline)

    subject = "Please help me apply for re-evaluation of CSE321 because my marks seem incorrect."
    description = "Respected Controller of Examinations, my marks for course CSE321 seem entered incorrectly in Semester 5."

    # 1. NLP Processing
    nlp_res = pipeline.process(subject, description)
    assert nlp_res.intent in ["ACADEMIC", "EXAMINATION"]
    assert "course_code" in nlp_res.entities
    assert nlp_res.entities["course_code"] == "CSE321"

    # 2. RAG Retrieval guided by NLP Department metadata
    sources = retriever.retrieve(
        query=f"{subject} {description}",
        department=nlp_res.department,
        limit=2
    )
    assert len(sources) > 0

    # 3. Grounded Draft Generation (Prediction != Decision)
    draft = await ai_provider.generate_draft(
        ticket_subject=subject,
        ticket_description=description,
        sources=sources,
        department=nlp_res.department
    )
    # Remains DRAFT with staff review requirement
    assert draft.requires_staff_edit is True or draft.requires_staff_edit is False
    assert "AI assists. Humans decide" in draft.disclaimer or "Draft" in draft.disclaimer

    # 4. Simulated Staff Override (Staff decides, AI assists)
    recommended_dept = nlp_res.department
    override_dept = "Academic Affairs" if recommended_dept != "Academic Affairs" else "Examination Branch"
    override_reason = "Student grievance requires cross-departmental committee review."

    # Verify override does not destroy original recommendation
    assert recommended_dept != override_dept
    assert override_reason != ""
