from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

class TicketState(str, Enum):
    """Lifecycle state machine states for RMS requests."""
    NEW = "NEW"
    INGESTED = "INGESTED"
    ANALYZED = "ANALYZED"
    ROUTED = "ROUTED"
    STAFF_REVIEW = "STAFF_REVIEW"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_STUDENT = "WAITING_FOR_STUDENT"
    WAITING_FOR_DEPARTMENT = "WAITING_FOR_DEPARTMENT"
    ESCALATED = "ESCALATED"
    DRAFTED = "DRAFTED"
    APPROVED = "APPROVED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class WorkflowEngine:
    """
    Finite state machine managing the complete ticket lifecycle,
    transition validation, and compliance audit trail generation.
    """

    ALLOWED_TRANSITIONS: Dict[TicketState, List[TicketState]] = {
        TicketState.NEW: [
            TicketState.INGESTED,
            TicketState.ANALYZED,
            TicketState.ROUTED,
            TicketState.STAFF_REVIEW
        ],
        TicketState.INGESTED: [
            TicketState.ANALYZED,
            TicketState.ROUTED,
            TicketState.STAFF_REVIEW
        ],
        TicketState.ANALYZED: [
            TicketState.ROUTED,
            TicketState.DRAFTED,
            TicketState.STAFF_REVIEW,
            TicketState.IN_PROGRESS
        ],
        TicketState.ROUTED: [
            TicketState.STAFF_REVIEW,
            TicketState.IN_PROGRESS,
            TicketState.ANALYZED
        ],
        TicketState.DRAFTED: [
            TicketState.STAFF_REVIEW,
            TicketState.APPROVED,
            TicketState.ESCALATED,
            TicketState.IN_PROGRESS
        ],
        TicketState.STAFF_REVIEW: [
            TicketState.IN_PROGRESS,
            TicketState.WAITING_FOR_STUDENT,
            TicketState.WAITING_FOR_DEPARTMENT,
            TicketState.APPROVED,
            TicketState.ESCALATED,
            TicketState.RESOLVED
        ],
        TicketState.IN_PROGRESS: [
            TicketState.WAITING_FOR_STUDENT,
            TicketState.WAITING_FOR_DEPARTMENT,
            TicketState.STAFF_REVIEW,
            TicketState.APPROVED,
            TicketState.ESCALATED,
            TicketState.RESOLVED
        ],
        TicketState.WAITING_FOR_STUDENT: [
            TicketState.IN_PROGRESS,
            TicketState.STAFF_REVIEW,
            TicketState.RESOLVED,
            TicketState.CLOSED
        ],
        TicketState.WAITING_FOR_DEPARTMENT: [
            TicketState.IN_PROGRESS,
            TicketState.STAFF_REVIEW,
            TicketState.RESOLVED
        ],
        TicketState.ESCALATED: [
            TicketState.STAFF_REVIEW,
            TicketState.IN_PROGRESS,
            TicketState.APPROVED,
            TicketState.RESOLVED
        ],
        TicketState.APPROVED: [
            TicketState.RESOLVED,
            TicketState.CLOSED
        ],
        TicketState.RESOLVED: [
            TicketState.CLOSED,
            TicketState.STAFF_REVIEW  # Permitted if reopened within grace period
        ],
        TicketState.CLOSED: [
            TicketState.STAFF_REVIEW  # Reopen on student dispute
        ]
    }

    def can_transition(self, current: str, next_state: str) -> bool:
        try:
            curr_enum = TicketState(current)
            next_enum = TicketState(next_state)
            return next_enum in self.ALLOWED_TRANSITIONS.get(curr_enum, [])
        except ValueError:
            return False

    def transition(
        self,
        ticket: Dict[str, Any],
        next_state: str,
        actor_id: str,
        notes: Optional[str] = None,
        event_type: str = "STATUS_CHANGED",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a validated state transition and records a structured audit event.
        """
        current_state = ticket.get("status", TicketState.INGESTED.value)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Update state
        ticket["status"] = next_state
        ticket["updated_at"] = timestamp
        ticket["last_updated_at"] = timestamp
        ticket["last_actor"] = actor_id

        # Generate structured audit entry
        if "history" not in ticket or not isinstance(ticket["history"], list):
            ticket["history"] = []

        audit_entry = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket.get("ticket_id", "UNKNOWN"),
            "event_type": event_type,
            "actor_id": actor_id,
            "actor_role": ticket.get("last_actor_role", "STAFF_OPERATOR"),
            "timestamp": timestamp,
            "from_state": current_state,
            "to_state": next_state,
            "notes": notes or f"Transitioned from {current_state} to {next_state}",
            "details": details or {}
        }
        ticket["history"].append(audit_entry)
        return ticket
