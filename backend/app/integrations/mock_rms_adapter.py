import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.integrations.base import UniversitySystemAdapter
from app.config import settings

class MockRMSAdapter(UniversitySystemAdapter):
    """Mock RMS adapter serving synthetic tickets from data/mock/rms_requests.json."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (settings.MOCK_DATA_DIR / "rms_requests.json")
        self._tickets: Dict[str, Dict[str, Any]] = {}
        self._load_mock_data()

    def _load_mock_data(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        self._tickets[item["ticket_id"]] = item
            except Exception as e:
                print(f"Error loading mock RMS data: {e}")

    def fetch_tickets(
        self,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = list(self._tickets.values())

        if department:
            results = [t for t in results if t.get("department", "").lower() == department.lower()]
        if priority:
            results = [t for t in results if t.get("priority", "").lower() == priority.lower()]
        if status:
            results = [t for t in results if t.get("status", "").lower() == status.lower()]
        if search:
            s_lower = search.lower()
            results = [
                t for t in results
                if s_lower in t.get("subject", "").lower() or s_lower in t.get("description", "").lower()
            ]

        return results

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        return self._tickets.get(ticket_id)

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        if ticket_id in self._tickets:
            self._tickets[ticket_id].update(updates)
            return True
        return False

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        if ticket_id in self._tickets:
            self._tickets[ticket_id]["status"] = "APPROVED"
            self._tickets[ticket_id]["resolution_text"] = resolution_text
            self._tickets[ticket_id]["resolved_at"] = datetime.utcnow().isoformat() + "Z"
            self._tickets[ticket_id]["assigned_staff"] = staff_id
            return True
        return False
