from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class UniversitySystemAdapter(ABC):
    """
    Formal interface for connecting to university administrative systems.
    Defines the stable data contract boundary between Smart RMS core and
    underlying university data sources (Mock adapter in dev, UMS adapter in staging/prod).
    """

    @abstractmethod
    def fetch_tickets(
        self,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetches list of student grievance tickets with optional filters."""
        pass

    @abstractmethod
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single ticket by its unique identifier."""
        pass

    @abstractmethod
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests or creates a new student grievance ticket."""
        pass

    @abstractmethod
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Updates ticket fields (status, department, resolution, etc.)."""
        pass

    @abstractmethod
    def assign_ticket(
        self,
        ticket_id: str,
        department_id: Optional[str],
        staff_id: Optional[str],
        assigned_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """Assigns ticket to a department and/or specific staff member with audit logging."""
        pass

    @abstractmethod
    def add_response(self, ticket_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a staff or student message/response to the ticket communication thread."""
        pass

    @abstractmethod
    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        """Publishes official resolution back to the university system."""
        pass

    @abstractmethod
    def get_audit_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Retrieves the chronological audit history for a ticket."""
        pass

    @abstractmethod
    def list_departments(self) -> List[Dict[str, Any]]:
        """Lists all university departments and their SLA policies."""
        pass

    @abstractmethod
    def get_department(self, department_id: str) -> Optional[Dict[str, Any]]:
        """Gets department details by ID or code."""
        pass

    @abstractmethod
    def list_users(
        self,
        department_id: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists synthetic university staff users."""
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Gets user details by user ID."""
        pass

    @abstractmethod
    def get_student_context(self, student_reference: str) -> Optional[Dict[str, Any]]:
        """Retrieves non-PII academic context for a student."""
        pass
