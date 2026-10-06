import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from pydantic import ValidationError

from app.schemas.active_learning import FeedbackEvent, FeedbackQualityState, FeedbackType
from app.config import settings

logger = logging.getLogger(__name__)

class ActiveLearningService:
    def __init__(self, feedback_dir: Optional[Path] = None):
        self.feedback_dir = feedback_dir or (settings.ROOT_DIR / "feedback" / "canonical")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback_events.json"
        
        self._events: List[FeedbackEvent] = []
        self._load_events()

    def _load_events(self):
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._events = [FeedbackEvent(**e) for e in data]
            except Exception as e:
                logger.warning(f"Could not load feedback events: {e}")

    def _save_events(self):
        try:
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump([e.model_dump() for e in self._events], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save feedback events: {e}")

    def log_feedback(self, event: FeedbackEvent) -> FeedbackEvent:
        # Part 6: Active Learning Prioritization (heuristic)
        event.al_priority_score = self._calculate_priority(event)
        
        self._events.append(event)
        self._save_events()
        return event

    def _calculate_priority(self, event: FeedbackEvent) -> float:
        score = 0.0
        
        # 1. Low-confidence predictions
        if event.confidence is not None:
            if event.confidence < 0.4:
                score += 3.0
            elif event.confidence < 0.6:
                score += 1.5
                
        # 2. Human-overridden predictions
        if event.corrected_value and event.original_prediction != event.corrected_value:
            score += 2.0
            
        # 6. Contradicted grounding claims / 7. Unsupported drafts
        if event.grounding_status in ["CONTRADICTED", "UNSUPPORTED"]:
            score += 2.5
            
        # 9. Model disagreement
        if event.model_disagreement:
            predictions = list(event.model_disagreement.values())
            unique_predictions = len(set(predictions))
            if unique_predictions > 1:
                score += 1.5
                
        return min(score, 10.0)

    def validate_feedback(self, feedback_id: str, action: str, actor_id: str) -> Optional[FeedbackEvent]:
        # action should be "APPROVE" or "REJECT"
        for event in self._events:
            if event.feedback_id == feedback_id:
                if action == "APPROVE":
                    event.status = FeedbackQualityState.VALIDATED
                elif action == "REJECT":
                    event.status = FeedbackQualityState.REJECTED
                event.actor_id = actor_id
                self._save_events()
                return event
        return None

    def get_queue(self) -> List[FeedbackEvent]:
        candidates = [e for e in self._events if e.status == FeedbackQualityState.CANDIDATE]
        return sorted(candidates, key=lambda x: x.al_priority_score, reverse=True)

    def get_metrics(self) -> Dict[str, Any]:
        total = len(self._events)
        validated = sum(1 for e in self._events if e.status == FeedbackQualityState.VALIDATED)
        rejected = sum(1 for e in self._events if e.status == FeedbackQualityState.REJECTED)
        candidates = sum(1 for e in self._events if e.status == FeedbackQualityState.CANDIDATE)
        
        return {
            "total_feedback": total,
            "validated": validated,
            "rejected": rejected,
            "candidates": candidates
        }

_active_learning_singleton = None

def get_active_learning_service() -> ActiveLearningService:
    global _active_learning_singleton
    if _active_learning_singleton is None:
        _active_learning_singleton = ActiveLearningService()
    return _active_learning_singleton
