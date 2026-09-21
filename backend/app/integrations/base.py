from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class UniversitySystemAdapter(ABC):
    """Abstract contract for connecting to university administrative systems."""

    @abstractmethod
    def fetch_tickets(
        self,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetches list of student grievance tickets."""
        pass

    @abstractmethod
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single ticket by its unique identifier."""
        pass

    @abstractmethod
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Updates ticket fields (status, department, resolution)."""
        pass

    @abstractmethod
    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        """Publishes official resolution back to the source system."""
        pass
