import pytest
import os
from pathlib import Path
from app.schemas.active_learning import FeedbackEvent, FeedbackType, FeedbackQualityState
from app.services.active_learning_service import ActiveLearningService

@pytest.fixture
def temp_feedback_dir(tmp_path):
    return tmp_path / "feedback_test"

def test_log_feedback(temp_feedback_dir):
    service = ActiveLearningService(feedback_dir=temp_feedback_dir)
    event = FeedbackEvent(
        ticket_id="TICKET-001",
        feedback_type=FeedbackType.INTENT_CORRECTION,
        original_prediction="ACADEMIC",
        corrected_value="EXAMINATION",
        confidence=0.3,
        human_action="STAFF_OVERRIDE",
        reason="Wrong intent assigned by model."
    )
    
    logged_event = service.log_feedback(event)
    assert logged_event.al_priority_score > 0
    assert logged_event.status == FeedbackQualityState.CANDIDATE
    assert logged_event.original_prediction == "ACADEMIC"
    assert logged_event.corrected_value == "EXAMINATION"
    
def test_validation_workflow(temp_feedback_dir):
    service = ActiveLearningService(feedback_dir=temp_feedback_dir)
    event = FeedbackEvent(
        ticket_id="TICKET-002",
        feedback_type=FeedbackType.INTENT_CORRECTION,
        original_prediction="PAYMENT",
        corrected_value="SCHOLARSHIP",
        confidence=0.8,
        human_action="STAFF_OVERRIDE"
    )
    logged_event = service.log_feedback(event)
    
    validated_event = service.validate_feedback(logged_event.feedback_id, "APPROVE", "ADMIN-01")
    assert validated_event.status == FeedbackQualityState.VALIDATED
    
    rejected_event = service.validate_feedback(logged_event.feedback_id, "REJECT", "ADMIN-01")
    assert rejected_event.status == FeedbackQualityState.REJECTED

def test_active_learning_queue(temp_feedback_dir):
    service = ActiveLearningService(feedback_dir=temp_feedback_dir)
    
    high_priority = FeedbackEvent(
        ticket_id="TICKET-003",
        feedback_type=FeedbackType.INTENT_CORRECTION,
        confidence=0.1,  # Should get +3 score
        grounding_status="CONTRADICTED", # +2.5
        human_action="STAFF_OVERRIDE"
    )
    
    low_priority = FeedbackEvent(
        ticket_id="TICKET-004",
        feedback_type=FeedbackType.INTENT_CORRECTION,
        confidence=0.9,
        human_action="STAFF_OVERRIDE"
    )
    
    service.log_feedback(low_priority)
    service.log_feedback(high_priority)
    
    queue = service.get_queue()
    assert len(queue) == 2
    assert queue[0].ticket_id == "TICKET-003"
    assert queue[1].ticket_id == "TICKET-004"
