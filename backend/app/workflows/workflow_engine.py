from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from app.schemas.contracts import InvalidStateTransitionError, TicketStatus

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
    Enforces deterministic transitions and rejects illegal jumps with InvalidStateTransitionError.
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
            TicketState.RESOLVED,
            TicketState.ROUTED
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
            TicketState.ESCALATED,
            TicketState.RESOLVED
        ],
        TicketState.ESCALATED: [
            TicketState.IN_PROGRESS,
            TicketState.STAFF_REVIEW,
            TicketState.APPROVED,
            TicketState.RESOLVED
        ],
        TicketState.APPROVED: [
            TicketState.RESOLVED,
            TicketState.CLOSED
        ],
        TicketState.RESOLVED: [
            TicketState.CLOSED,
            TicketState.STAFF_REVIEW  # Permitted on student reopening / dispute
        ],
        TicketState.CLOSED: [
            TicketState.STAFF_REVIEW  # Formal administrative reopening
        ]
    }

    def can_transition(self, current: str, next_state: str) -> bool:
        """Evaluates whether transitioning from current to next_state is legally allowed."""
        if current == next_state:
            return True  # Idempotent state transition or note update
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
        details: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Executes a validated state transition and records a structured audit event.
        Raises InvalidStateTransitionError if the requested transition is illegal.
        """
        current_state = ticket.get("status", TicketState.INGESTED.value)

        # Enforce validation unless explicitly forced
        if not force and not self.can_transition(current_state, next_state):
            raise InvalidStateTransitionError(
                f"Illegal state transition from '{current_state}' to '{next_state}' "
                f"for ticket {ticket.get('ticket_id', 'UNKNOWN')}."
            )

        timestamp = datetime.now(timezone.utc).isoformat()

        # Update ticket state
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
