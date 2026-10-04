from typing import List, Dict, Any, Optional
from app.integrations.base import UniversitySystemAdapter
from app.integrations.mock_rms_adapter import MockRMSAdapter

class FutureUMSAdapter(UniversitySystemAdapter):
    """
    Adapter skeleton for future live LPU UMS / RMS integration.
    Implements the full UniversitySystemAdapter contract with graceful fallback to MockRMSAdapter.
    """

    def __init__(self, endpoint_url: str = "", auth_token: str = ""):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        self._fallback = MockRMSAdapter()

    def fetch_tickets(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return self._fallback.fetch_tickets(*args, **kwargs)

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_ticket_by_id(ticket_id)

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._fallback.create_ticket(ticket_data)

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        return self._fallback.update_ticket(ticket_id, updates)

    def assign_ticket(
        self,
        ticket_id: str,
        department_id: Optional[str],
        staff_id: Optional[str],
        assigned_by: str,
        reason: Optional[str] = None
    ) -> bool:
        return self._fallback.assign_ticket(ticket_id, department_id, staff_id, assigned_by, reason)

    def add_response(self, ticket_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._fallback.add_response(ticket_id, response_data)

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        return self._fallback.post_resolution(ticket_id, resolution_text, staff_id)

    def get_audit_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        return self._fallback.get_audit_history(ticket_id)

    def list_departments(self) -> List[Dict[str, Any]]:
        return self._fallback.list_departments()

    def get_department(self, department_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_department(department_id)

    def list_users(
        self,
        department_id: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self._fallback.list_users(department_id, role)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_user(user_id)

    def get_student_context(self, student_reference: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_student_context(student_reference)


class FutureLMSAdapter:
    """Stubbed adapter for university LMS (Continuous Assessment / Coursework verification)."""
    async def get_course_evaluations(self, student_id: str, course_code: str) -> Dict[str, Any]:
        return {"status": "MOCK_LMS_ACTIVE", "student_id": student_id, "course_code": course_code}


class FutureERPAdapter:
    """Stubbed adapter for university ERP & Accounts ledger reconciliation."""
    async def get_payment_status(self, transaction_ref: str) -> Dict[str, Any]:
        return {"status": "RECONCILED", "transaction_ref": transaction_ref}
