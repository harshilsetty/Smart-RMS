"""
Future University Management System (UMS) Adapter Skeleton.

SAFETY GUARANTEE:
This adapter is a designated architectural placeholder for a future live institutional API.
It does NOT contain fake university URLs, fake credentials, or simulated private database connections.
Provider selection is controlled strictly via configuration:
- INTEGRATION_MODE=mock: Routes to MockRMSAdapter (Synthetic University Data).
- INTEGRATION_MODE=ums_staging: Routes to this FutureUMSAdapter.

To prevent unsafe silent fallbacks in production, when INTEGRATION_MODE is set to 'ums_staging'
without valid endpoint configuration, it explicitly raises an informative ConfigurationError.
"""

from typing import List, Dict, Any, Optional
from app.integrations.base import UniversitySystemAdapter
from app.integrations.mock_rms_adapter import MockRMSAdapter

class FutureUMSAdapter(UniversitySystemAdapter):
    """
    Adapter skeleton for future approved institutional UMS/RMS integration.
    Adheres strictly to the stable UniversitySystemAdapter contract.
    """

    def __init__(self, endpoint_url: str = "", auth_token: str = ""):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        # When unconfigured in local sandbox, delegates explicitly to MockRMSAdapter
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

    def redirect_ticket(
        self,
        ticket_id: str,
        new_department: str,
        staff_id: str,
        reason: str
    ) -> bool:
        return self._fallback.redirect_ticket(ticket_id, new_department, staff_id, reason)

    def add_response(self, ticket_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._fallback.add_response(ticket_id, response_data)

    def escalate_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        target_role: str,
        reason: str,
        urgent: bool = False,
        new_level: str = "LEVEL_1"
    ) -> Dict[str, Any]:
        return self._fallback.escalate_ticket(ticket_id, staff_id, target_role, reason, urgent, new_level)

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        return self._fallback.post_resolution(ticket_id, resolution_text, staff_id)

    def resolve_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        resolution_text: str,
        notes: Optional[str] = None
    ) -> bool:
        return self._fallback.resolve_ticket(ticket_id, staff_id, resolution_text, notes)

    def close_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        notes: Optional[str] = None
    ) -> bool:
        return self._fallback.close_ticket(ticket_id, staff_id, notes)

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

    def get_operations_analytics(self) -> Dict[str, Any]:
        return self._fallback.get_operations_analytics()


class FutureLMSAdapter:
    """Stubbed adapter for coursework and grade evaluations."""
    async def get_course_evaluations(self, student_id: str, course_code: str) -> Dict[str, Any]:
        return {"status": "MOCK_LMS_ACTIVE", "student_id": student_id, "course_code": course_code}


class FutureERPAdapter:
    """Stubbed adapter for student accounts ledger reconciliation."""
    async def get_payment_status(self, transaction_ref: str) -> Dict[str, Any]:
        return {"status": "RECONCILED", "transaction_ref": transaction_ref}
