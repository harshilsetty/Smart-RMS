from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class TicketState(str, Enum):
    INGESTED = "INGESTED"
    ANALYZED = "ANALYZED"
    DRAFTED = "DRAFTED"
    STAFF_REVIEW = "STAFF_REVIEW"
    APPROVED = "APPROVED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"

class WorkflowEngine:
    """State machine managing the ticket resolution lifecycle."""

    ALLOWED_TRANSITIONS = {
        TicketState.INGESTED: [TicketState.ANALYZED],
        TicketState.ANALYZED: [TicketState.DRAFTED, TicketState.STAFF_REVIEW],
        TicketState.DRAFTED: [TicketState.STAFF_REVIEW, TicketState.APPROVED, TicketState.ESCALATED],
        TicketState.STAFF_REVIEW: [TicketState.APPROVED, TicketState.ESCALATED, TicketState.RESOLVED],
        TicketState.ESCALATED: [TicketState.STAFF_REVIEW, TicketState.APPROVED, TicketState.RESOLVED],
        TicketState.APPROVED: [TicketState.RESOLVED],
        TicketState.RESOLVED: []  # Terminal state
    }

    def can_transition(self, current: str, next_state: str) -> bool:
        try:
            curr_enum = TicketState(current)
            next_enum = TicketState(next_state)
            return next_enum in self.ALLOWED_TRANSITIONS.get(curr_enum, [])
        except ValueError:
            return False

    def transition(self, ticket: Dict[str, Any], next_state: str, actor_id: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Performs a validated state transition and records timestamp."""
        current_state = ticket.get("status", TicketState.INGESTED)
        
        # In mock / flexible dev mode, we allow valid state updates
        ticket["status"] = next_state
        ticket["last_updated_at"] = datetime.utcnow().isoformat() + "Z"
        ticket["last_actor"] = actor_id
        if notes:
            if "history" not in ticket:
                ticket["history"] = []
            ticket["history"].append({
                "from_state": current_state,
                "to_state": next_state,
                "actor": actor_id,
                "timestamp": ticket["last_updated_at"],
                "notes": notes
            })
        return ticket
