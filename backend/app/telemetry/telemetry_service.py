"""
Smart RMS - Operational Telemetry & Active Learning Service
Milestone 6: Captures operational telemetry without PII and logs structured feedback
for future supervised fine-tuning.
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


class TelemetryRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    ticket_id: str
    event_type: str
    ai_intent: Optional[str] = None
    selected_department: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_urgency: Optional[str] = None
    human_override: bool = False
    rag_source_ids: List[str] = Field(default_factory=list)
    grounding_status: Optional[str] = None
    draft_action: Optional[str] = None  # "APPROVED", "EDITED", "REJECTED", "REGENERATED"
    escalated: bool = False
    redirected: bool = False
    actor_id: str = "SYSTEM"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OperationalMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total_events: int = 0
    total_tickets: int = 0
    intent_override_rate: float = 0.0
    department_override_rate: float = 0.0
    priority_override_rate: float = 0.0
    draft_approval_rate: float = 0.0
    draft_edit_rate: float = 0.0
    draft_rejection_rate: float = 0.0
    grounding_failure_rate: float = 0.0
    no_source_rate: float = 0.0
    escalation_rate: float = 0.0
    redirection_rate: float = 0.0


class TelemetryService:
    """
    Manages operational telemetry logs and active learning feedback queues.
    Ensures zero PII leakage: only synthetic ticket references, metadata, and decision deltas are persisted.
    """

    def __init__(self, feedback_dir: Optional[Path] = None):
        from app.config import settings
        self.feedback_dir = feedback_dir or (settings.ROOT_DIR / "feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        self.telemetry_log_path = self.feedback_dir / "operational_telemetry.json"
        self.intent_corrections_path = self.feedback_dir / "intent_corrections.json"
        self.dept_corrections_path = self.feedback_dir / "department_corrections.json"
        self.grounding_feedback_path = self.feedback_dir / "grounding_feedback.json"

        # In-memory fast cache of records
        self._records: List[TelemetryRecord] = []
        self._load_existing_telemetry()

    def _load_existing_telemetry(self):
        if self.telemetry_log_path.exists():
            try:
                with open(self.telemetry_log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._records = [TelemetryRecord(**r) for r in data]
            except Exception as e:
                logger.warning("Could not load telemetry file: %s", str(e))

    def record_event(self, record: TelemetryRecord):
        """Appends an operational telemetry event."""
        self._records.append(record)
        self._save_telemetry()

    def _save_telemetry(self):
        try:
            with open(self.telemetry_log_path, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in self._records], f, indent=2)
        except Exception as e:
            logger.warning("Failed to save operational telemetry: %s", str(e))

    def record_intent_correction(
        self,
        ticket_id: str,
        original_ai_intent: str,
        human_corrected_intent: str,
        context_summary: str,
        actor_id: str,
        reason: Optional[str] = None
    ):
        """Active learning feedback: records human intent correction."""
        entry = {
            "ticket_id": ticket_id,
            "original_ai_intent": original_ai_intent,
            "human_corrected_intent": human_corrected_intent,
            "context_summary": context_summary,
            "actor_id": actor_id,
            "reason": reason or "Staff operational routing correction",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._append_to_feedback(self.intent_corrections_path, entry)

    def record_department_correction(
        self,
        ticket_id: str,
        original_ai_department: str,
        human_corrected_department: str,
        context_summary: str,
        actor_id: str,
        reason: Optional[str] = None
    ):
        """Active learning feedback: records human department correction."""
        entry = {
            "ticket_id": ticket_id,
            "original_ai_department": original_ai_department,
            "human_corrected_department": human_corrected_department,
            "context_summary": context_summary,
            "actor_id": actor_id,
            "reason": reason or "Staff operational routing correction",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._append_to_feedback(self.dept_corrections_path, entry)

    def record_grounding_feedback(
        self,
        ticket_id: str,
        original_grounding_status: str,
        human_action: str,
        failed_claims: List[Dict[str, Any]],
        actor_id: str,
        reason: str
    ):
        """Active learning feedback: records human grounding override or feedback."""
        entry = {
            "ticket_id": ticket_id,
            "original_grounding_status": original_grounding_status,
            "human_action": human_action,
            "failed_claims": failed_claims,
            "actor_id": actor_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._append_to_feedback(self.grounding_feedback_path, entry)

    def _append_to_feedback(self, file_path: Path, entry: Dict[str, Any]):
        try:
            items = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        items = json.load(f)
                    except json.JSONDecodeError:
                        items = []
            items.append(entry)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
        except Exception as e:
            logger.warning("Failed appending to feedback file %s: %s", file_path.name, str(e))

    def compute_metrics(self) -> OperationalMetrics:
        """Computes live operational telemetry metrics."""
        total = len(self._records)
        if total == 0:
            return OperationalMetrics()

        unique_tickets = len(set(r.ticket_id for r in self._records))
        intent_overrides = sum(1 for r in self._records if r.event_type == "INTENT_OVERRIDE")
        dept_overrides = sum(1 for r in self._records if r.event_type == "DEPARTMENT_OVERRIDE")
        priority_overrides = sum(1 for r in self._records if r.event_type == "PRIORITY_OVERRIDE")

        draft_events = [r for r in self._records if r.draft_action]
        total_drafts = len(draft_events)
        approvals = sum(1 for r in draft_events if r.draft_action == "APPROVED")
        edits = sum(1 for r in draft_events if r.draft_action == "EDITED")
        rejections = sum(1 for r in draft_events if r.draft_action == "REJECTED")

        grounding_failures = sum(
            1 for r in self._records
            if r.grounding_status in {"CONTRADICTED", "UNSUPPORTED", "REQUIRES_HUMAN_REVIEW"}
        )
        no_sources = sum(1 for r in self._records if not r.rag_source_ids)
        escalations = sum(1 for r in self._records if r.escalated or r.event_type == "ESCALATE")
        redirections = sum(1 for r in self._records if r.redirected or r.event_type == "REDIRECT")

        return OperationalMetrics(
            total_events=total,
            total_tickets=unique_tickets,
            intent_override_rate=round(intent_overrides / max(unique_tickets, 1), 4),
            department_override_rate=round(dept_overrides / max(unique_tickets, 1), 4),
            priority_override_rate=round(priority_overrides / max(unique_tickets, 1), 4),
            draft_approval_rate=round(approvals / max(total_drafts, 1), 4),
            draft_edit_rate=round(edits / max(total_drafts, 1), 4),
            draft_rejection_rate=round(rejections / max(total_drafts, 1), 4),
            grounding_failure_rate=round(grounding_failures / max(total, 1), 4),
            no_source_rate=round(no_sources / max(total, 1), 4),
            escalation_rate=round(escalations / max(unique_tickets, 1), 4),
            redirection_rate=round(redirections / max(unique_tickets, 1), 4)
        )


_telemetry_singleton = None


def get_telemetry_service() -> TelemetryService:
    global _telemetry_singleton
    if _telemetry_singleton is None:
        _telemetry_singleton = TelemetryService()
    return _telemetry_singleton
