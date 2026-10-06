"""
Smart RMS - Milestone 5 Test Suite
Tests for Classical ML Benchmark, Model Providers, Fallback, Staff Copilot, and Human Override
"""

import pytest
import json
from pathlib import Path
import numpy as np

import sys
from app.config import settings

if str(settings.ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(settings.ROOT_DIR))

from app.nlp.schemas import IntentClassificationResult, PriorityLevel
from app.nlp.intent_classifier import (
    BaseIntentClassifier,
    RuleBasedIntentClassifier,
    get_intent_classifier
)
from app.nlp.ml_classifiers import (
    DeterministicIntentModel,
    TFIDFLogisticIntentModel,
    TFIDFSVMIntentModel,
    SentenceTransformerIntentModel,
    MODELS_DIR
)
from app.nlp.pipeline import NLPPipeline
from app.services.rms_service import RMSService
from app.schemas.rms import (
    HumanOverrideRequest,
    RMSCreateRequest
)
from app.ai.mock_provider import MockAIProvider
from app.rag.retriever import PolicyRetriever
from ml.dataset import load_eval_120, clean_text_for_comparison


# 1. Dataset Loading and Reproducible Splitting Tests
def test_eval_120_dataset_integrity():
    eval_path = settings.ROOT_DIR / "evaluation" / "datasets" / "evaluation_nlp_120.json"
    assert eval_path.exists(), "evaluation_nlp_120.json must exist"
    data = load_eval_120(eval_path)
    assert len(data) == 120, f"Expected 120 evaluation samples, got {len(data)}"
    
    # Check required fields
    for item in data:
        assert "ticket_id" in item
        assert "subject" in item
        assert "description" in item
        assert "expected_intent" in item
        assert "expected_department" in item

def test_split_manifest_and_zero_leakage():
    manifest_path = settings.ROOT_DIR / "evaluation" / "datasets" / "split_manifest.json"
    test_path = settings.ROOT_DIR / "evaluation" / "datasets" / "split_test.json"
    train_path = settings.ROOT_DIR / "evaluation" / "datasets" / "split_train.json"

    assert manifest_path.exists(), "split_manifest.json must exist"
    assert test_path.exists(), "split_test.json must exist"
    assert train_path.exists(), "split_train.json must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)
    with open(train_path, "r", encoding="utf-8") as f:
        train_samples = json.load(f)

    assert manifest["random_seed"] == 42
    assert len(test_samples) == 36
    assert len(train_samples) > 300
    assert manifest["data_leakage_detected"] is False

    # Programmatic zero-leakage verification
    test_texts = set(clean_text_for_comparison(t["subject"] + " " + t["description"]) for t in test_samples)
    for s in train_samples:
        t_clean = clean_text_for_comparison(s["subject"] + " " + s["description"])
        assert t_clean not in test_texts, f"Data leakage detected! Sample {s.get('ticket_id')} is in test set!"

# 2. Model Persistence, Loading & Inference Tests
def test_tfidf_logistic_model_loading_and_prediction():
    model_path = MODELS_DIR / "tfidf_logistic.joblib"
    assert model_path.exists(), "tfidf_logistic.joblib must exist"
    model = TFIDFLogisticIntentModel().load(model_path)
    assert model._is_trained is True

    result = model.classify("Urgent water pipe burst in BH-3 room 204")
    assert isinstance(result, IntentClassificationResult)
    assert result.intent == "HOSTEL_MAINTENANCE"
    assert result.confidence > 0.40
    assert result.margin >= 0.0

def test_tfidf_svm_model_loading_and_prediction():
    model_path = MODELS_DIR / "tfidf_svm.joblib"
    assert model_path.exists(), "tfidf_svm.joblib must exist"
    model = TFIDFSVMIntentModel().load(model_path)
    assert model._is_trained is True

    result = model.classify("Excess tuition fee deducted twice from bank account")
    assert isinstance(result, IntentClassificationResult)
    assert result.intent == "FEE_PAYMENT"
    assert result.confidence > 0.40

def test_sentence_transformer_model_loading_and_prediction():
    model_path = MODELS_DIR / "sentence_transformer.joblib"
    assert model_path.exists(), "sentence_transformer.joblib must exist"
    model = SentenceTransformerIntentModel().load(model_path)
    assert model._is_trained is True

    result = model.classify("Admit card hall ticket blocked due to library clearance hold")
    assert isinstance(result, IntentClassificationResult)
    assert result.intent == "EXAMINATION"
    assert result.confidence > 0.40

# 3. Model Provider Abstraction & Fallback Tests
def test_model_provider_factory_deterministic():
    clf = get_intent_classifier("deterministic")
    assert isinstance(clf, RuleBasedIntentClassifier)
    assert clf.classifier_name == "deterministic_baseline"

def test_model_provider_factory_tfidf_logistic():
    clf = get_intent_classifier("tfidf_logistic")
    assert isinstance(clf, TFIDFLogisticIntentModel)
    assert clf.classifier_name == "tfidf_logistic"

def test_model_provider_factory_tfidf_svm():
    clf = get_intent_classifier("tfidf_svm")
    assert isinstance(clf, TFIDFSVMIntentModel)
    assert clf.classifier_name == "tfidf_svm"

def test_model_provider_factory_unknown_fallback():
    clf = get_intent_classifier("non_existent_model_provider")
    assert isinstance(clf, RuleBasedIntentClassifier)
    assert clf.classifier_name == "deterministic_baseline"

def test_pipeline_with_custom_classifier():
    clf = get_intent_classifier("tfidf_svm")
    pipeline = NLPPipeline(intent_classifier=clf)
    assert pipeline.classifier_mode == "tfidf_svm"

    res = pipeline.process(
        subject="WiFi connection dropping in library block 34",
        description="MAC address registered but Fortinet radius authentication fails."
    )
    assert res.intent == "IT_SUPPORT"
    assert res.classifier_mode == "tfidf_svm"
    assert res.department == "IT Services"

# 4. Human Override & Audit Trail Preservation Tests
def test_human_override_workflow_and_audit():
    service = RMSService()
    tickets_resp = service.get_tickets()
    assert len(tickets_resp.tickets) > 0
    sample_ticket = tickets_resp.tickets[0]
    ticket_id = sample_ticket.ticket_id
    initial_dept = sample_ticket.department

    # Override department and priority
    new_dept = "Student Welfare" if initial_dept != "Student Welfare" else "Academic Affairs"
    req = HumanOverrideRequest(
        staff_id="USR-STAFF-99",
        override_department=new_dept,
        override_priority="Critical",
        reason="Student requires immediate grievance cell intervention"
    )

    resp = service.override_ticket(ticket_id, req)

    assert resp.ticket_id == ticket_id
    assert resp.overridden_by == "USR-STAFF-99"
    assert "department" in resp.applied_overrides
    assert "priority" in resp.applied_overrides
    assert resp.original_ai_prediction is not None

    # Check updated ticket state
    updated = service.adapter.get_ticket_by_id(ticket_id)
    assert updated.get("department") == new_dept
    assert updated.get("priority") == "Critical"

    # Check audit history preserves HUMAN_OVERRIDE event
    history = service.get_ticket_history(ticket_id)
    override_events = [e for e in history if e.get("event_type") == "HUMAN_OVERRIDE"]
    assert len(override_events) > 0
    latest_event = override_events[-1]
    assert latest_event.get("actor_id") == "USR-STAFF-99"
    assert "Student requires immediate grievance cell intervention" in latest_event.get("notes")

# 5. Strict Grounding and No-Source Refusal Tests
@pytest.mark.asyncio
async def test_no_source_no_answer_refusal():
    provider = MockAIProvider()

    # Generate draft with empty sources
    draft = await provider.generate_draft(
        ticket_subject="Obscure unrecorded inquiry regarding campus UFO sighting",
        ticket_description="Please provide university policy on UFO sightings on campus terrace.",
        sources=[],
        department="General Administration"
    )

    assert draft.grounding_status in ["INSUFFICIENT_EVIDENCE", "UNGROUNDED"]
    assert "Insufficient authoritative information" in draft.draft_response
    assert draft.needs_human_review is True

# 6. Ambiguity and Low-Confidence Review Enforced
def test_ambiguous_terse_query_enforces_review():
    clf = get_intent_classifier("tfidf_logistic")
    pipeline = NLPPipeline(intent_classifier=clf)

    # Highly terse, ambiguous query
    res = pipeline.process(
        subject="Fees problem",
        description="fees pending"
    )
    # Must flag clarification or review
    assert res.requires_human_review is True or res.needs_clarification is True
