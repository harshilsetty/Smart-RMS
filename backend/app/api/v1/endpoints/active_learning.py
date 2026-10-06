from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.schemas.active_learning import FeedbackEvent
from app.services.active_learning_service import get_active_learning_service, ActiveLearningService

router = APIRouter()

@router.post("/", response_model=FeedbackEvent, summary="Log a new canonical feedback event")
def log_feedback(event: FeedbackEvent, al_service: ActiveLearningService = Depends(get_active_learning_service)):
    return al_service.log_feedback(event)

@router.get("/queue", response_model=List[FeedbackEvent], summary="Get high-value AI review queue")
def get_queue(al_service: ActiveLearningService = Depends(get_active_learning_service)):
    return al_service.get_queue()

@router.post("/{feedback_id}/validate", response_model=FeedbackEvent, summary="Validate or reject feedback")
def validate_feedback(feedback_id: str, action: str, actor_id: str = "STAFF", al_service: ActiveLearningService = Depends(get_active_learning_service)):
    if action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Invalid action, must be APPROVE or REJECT")
    
    event = al_service.validate_feedback(feedback_id, action, actor_id)
    if not event:
        raise HTTPException(status_code=404, detail="Feedback event not found")
    return event

@router.get("/metrics", response_model=Dict[str, Any], summary="Get active learning quality metrics")
def get_al_metrics(al_service: ActiveLearningService = Depends(get_active_learning_service)):
    return al_service.get_metrics()
