from typing import List, Dict, Any, Optional
from app.integrations.base import UniversitySystemAdapter
from app.integrations.mock_rms_adapter import MockRMSAdapter

class FutureUMSAdapter(UniversitySystemAdapter):
    """Stubbed adapter for future live LPU UMS/RMS integration."""

    def __init__(self, endpoint_url: str = "", auth_token: str = ""):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        # Falls back to mock in sandbox
        self._fallback = MockRMSAdapter()

    def fetch_tickets(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return self._fallback.fetch_tickets(*args, **kwargs)

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_ticket_by_id(ticket_id)

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        return self._fallback.update_ticket(ticket_id, updates)

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        return self._fallback.post_resolution(ticket_id, resolution_text, staff_id)

class FutureLMSAdapter:
    """Stubbed adapter for university LMS (Continuous Assessment / Coursework verification)."""
    async def get_course_evaluations(self, student_id: str, course_code: str) -> Dict[str, Any]:
        return {"status": "MOCK_LMS_ACTIVE", "student_id": student_id, "course_code": course_code}

class FutureERPAdapter:
    """Stubbed adapter for university ERP & Accounts ledger reconciliation."""
    async def get_payment_status(self, transaction_ref: str) -> Dict[str, Any]:
        return {"status": "RECONCILED", "transaction_ref": transaction_ref}
