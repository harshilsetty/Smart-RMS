import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.integrations.base import UniversitySystemAdapter
from app.config import settings

class MockRMSAdapter(UniversitySystemAdapter):
    """
    High-fidelity Mock University RMS/UMS Adapter.
    Serves synthetic university data adhering to the canonical data contract.
    Enables complete system execution without real university API access.
    """

    def __init__(
        self,
        data_file: Optional[Path] = None,
        departments_file: Optional[Path] = None,
        users_file: Optional[Path] = None
    ):
        self.data_file = data_file or (settings.MOCK_DATA_DIR / "rms_requests.json")
        self.departments_file = departments_file or (settings.MOCK_DATA_DIR / "departments.json")
        self.users_file = users_file or (settings.MOCK_DATA_DIR / "users.json")
        
        self._tickets: Dict[str, Dict[str, Any]] = {}
        self._departments: Dict[str, Dict[str, Any]] = {}
        self._users: Dict[str, Dict[str, Any]] = {}
        self._assignments: List[Dict[str, Any]] = []

        self._load_mock_data()

    def _load_mock_data(self):
        # 1. Load departments
        if self.departments_file.exists():
            try:
                with open(self.departments_file, "r", encoding="utf-8") as f:
                    depts = json.load(f)
                    for d in depts:
                        d_id = d.get("department_id") or d.get("id")
                        self._departments[d_id] = d
                        # Also key by department name for flexible lookups
                        self._departments[d.get("name", "").lower()] = d
            except Exception as e:
                print(f"Error loading departments: {e}")

        # 2. Load users
        if self.users_file.exists():
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    users = json.load(f)
                    for u in users:
                        self._users[u["user_id"]] = u
            except Exception as e:
                print(f"Error loading users: {e}")

        # 3. Load tickets
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        t_id = item["ticket_id"]
                        self._enrich_ticket_defaults(item)
                        self._tickets[t_id] = item
            except Exception as e:
                print(f"Error loading mock RMS data: {e}")

    def _enrich_ticket_defaults(self, ticket: Dict[str, Any]):
        """Ensures all canonical data contract fields exist on ticket dictionary."""
        # Sync title and subject
        if "subject" in ticket and "title" not in ticket:
            ticket["title"] = ticket["subject"]
        elif "title" in ticket and "subject" not in ticket:
            ticket["subject"] = ticket["title"]

        # Sync assigned staff
        if "assigned_staff" in ticket and "assigned_staff_id" not in ticket:
            ticket["assigned_staff_id"] = ticket["assigned_staff"]
        elif "assigned_staff_id" in ticket and "assigned_staff" not in ticket:
            ticket["assigned_staff"] = ticket["assigned_staff_id"]

        # Set synthetic flags and defaults
        ticket.setdefault("is_synthetic", True)
        ticket.setdefault("escalation_level", 0)
        ticket.setdefault("source", "STUDENT_PORTAL")
        ticket.setdefault("tags", [])
        ticket.setdefault("responses", [])
        ticket.setdefault("history", [])
        ticket.setdefault("metadata", {"environment": "synthetic"})

        # Compute dynamic SLA
        self._calculate_sla(ticket)

    def _calculate_sla(self, ticket: Dict[str, Any]):
        """Calculates due_at, remaining_hours, and breach status dynamically."""
        created_str = ticket.get("created_at")
        if not created_str:
            return

        priority = ticket.get("priority", "Medium")
        dept_name = ticket.get("department", "")
        dept = self._departments.get(dept_name.lower()) or {}
        sla_policy = dept.get("sla_policy", {"LOW": 72, "MEDIUM": 48, "HIGH": 24, "CRITICAL": 12})
        
        sla_hours = sla_policy.get(priority.upper(), 48)

        # Parse created_at
        try:
            # Handle ISO string with or without Z
            c_clean = created_str.replace("Z", "+00:00")
            created_dt = datetime.fromisoformat(c_clean)
        except Exception:
            created_dt = datetime.now(timezone.utc)

        due_dt = created_dt + timedelta(hours=sla_hours)
        now_dt = datetime.now(timezone.utc)
        
        # Remaining time
        remaining_seconds = (due_dt - now_dt).total_seconds()
        remaining_hours = round(remaining_seconds / 3600.0, 1)

        is_breached = remaining_seconds < 0 and ticket.get("status") not in ["APPROVED", "RESOLVED", "CLOSED"]
        
        if is_breached:
            status = "BREACHED"
        elif remaining_hours <= 4.0:
            status = "AT_RISK"
        else:
            status = "ON_TRACK"

        due_iso = due_dt.isoformat().replace("+00:00", "Z")
        ticket["due_at"] = due_iso
        ticket["sla_record"] = {
            "priority": priority,
            "sla_hours": sla_hours,
            "due_at": due_iso,
            "is_breached": is_breached,
            "remaining_hours": remaining_hours,
            "status": status
        }

    def fetch_tickets(
        self,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = list(self._tickets.values())

        if department:
            d_lower = department.lower()
            results = [
                t for t in results
                if t.get("department", "").lower() == d_lower or t.get("assigned_department_id", "").lower() == d_lower
            ]
        if priority:
            p_lower = priority.lower()
            results = [t for t in results if t.get("priority", "").lower() == p_lower]
        if status:
            s_lower = status.lower()
            results = [t for t in results if t.get("status", "").lower() == s_lower]
        if search:
            query = search.lower()
            results = [
                t for t in results
                if query in t.get("subject", "").lower()
                or query in t.get("description", "").lower()
                or query in t.get("ticket_id", "").lower()
                or query in t.get("student_reference", "").lower()
            ]

        # Recalculate SLA records on read
        for t in results:
            self._calculate_sla(t)

        return results

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        t = self._tickets.get(ticket_id)
        if t:
            self._calculate_sla(t)
        return t

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests a new synthetic RMS grievance ticket."""
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Generate ID if missing
        if "ticket_id" not in ticket_data or not ticket_data["ticket_id"]:
            next_idx = len(self._tickets) + 1001
            ticket_data["ticket_id"] = f"TKT-RMS-{next_idx}"

        ticket_id = ticket_data["ticket_id"]
        ticket_data.setdefault("external_reference", f"UMS-EXT-{ticket_id.split('-')[-1]}")
        ticket_data.setdefault("status", "INGESTED")
        ticket_data.setdefault("created_at", now_iso)
        ticket_data.setdefault("updated_at", now_iso)

        self._enrich_ticket_defaults(ticket_data)

        # Initial audit record
        initial_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "CREATED",
            "actor_id": ticket_data.get("student_reference", "STUDENT"),
            "actor_role": "STUDENT",
            "timestamp": now_iso,
            "from_state": "NEW",
            "to_state": ticket_data["status"],
            "notes": "Ticket ingested via synthetic university gateway",
            "details": {"source": ticket_data.get("source", "STUDENT_PORTAL")}
        }
        ticket_data["history"].append(initial_event)

        self._tickets[ticket_id] = ticket_data
        return ticket_data

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        if ticket_id in self._tickets:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._tickets[ticket_id].update(updates)
            self._enrich_ticket_defaults(self._tickets[ticket_id])
            return True
        return False

    def assign_ticket(
        self,
        ticket_id: str,
        department_id: Optional[str],
        staff_id: Optional[str],
        assigned_by: str,
        reason: Optional[str] = None
    ) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False

        now_iso = datetime.now(timezone.utc).isoformat()
        asg_id = f"ASG-{ticket_id.replace('TKT-', '')}-{len(self._assignments) + 1}"

        # Update department if given
        if department_id:
            dept_obj = self.get_department(department_id)
            if dept_obj:
                ticket["assigned_department_id"] = dept_obj.get("department_id", department_id)
                ticket["department"] = dept_obj.get("name", ticket["department"])

        # Update staff if given
        if staff_id:
            ticket["assigned_staff_id"] = staff_id
            ticket["assigned_staff"] = staff_id
            user = self.get_user(staff_id)
            if user:
                wl = user.setdefault("workload_metadata", {})
                wl["assigned_tickets_count"] = wl.get("assigned_tickets_count", 0) + 1

        ticket["updated_at"] = now_iso
        
        # Create Assignment record
        assignment_record = {
            "assignment_id": asg_id,
            "ticket_id": ticket_id,
            "department_id": ticket.get("assigned_department_id", "DEPT-GENERAL"),
            "staff_id": ticket.get("assigned_staff_id"),
            "assigned_by": assigned_by,
            "assigned_at": now_iso,
            "reason": reason or "Operational ticket distribution",
            "active": True
        }
        self._assignments.append(assignment_record)

        # Audit Event
        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "ASSIGNED",
            "actor_id": assigned_by,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": ticket.get("status"),
            "notes": f"Assigned to staff {staff_id} in {ticket.get('department')}: {reason or 'Standard routing'}",
            "details": assignment_record
        }
        ticket.setdefault("history", []).append(audit_event)
        return True

    def add_response(self, ticket_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        now_iso = datetime.now(timezone.utc).isoformat()
        rsp_id = f"RSP-{ticket_id.replace('TKT-', '')}-{len(ticket.get('responses', [])) + 1}"
        
        response_data["response_id"] = rsp_id
        response_data["ticket_id"] = ticket_id
        response_data.setdefault("created_at", now_iso)

        ticket.setdefault("responses", []).append(response_data)
        ticket["updated_at"] = now_iso

        # Log audit entry
        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "RESPONSE_ADDED",
            "actor_id": response_data.get("author_id", "UNKNOWN"),
            "actor_role": response_data.get("author_role", "STAFF_OPERATOR"),
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": ticket.get("status"),
            "notes": f"Response added by {response_data.get('author_name', 'Staff')}",
            "details": {"response_id": rsp_id, "is_internal": response_data.get("is_internal", False)}
        }
        ticket.setdefault("history", []).append(audit_event)
        return response_data

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        if ticket_id in self._tickets:
            now_iso = datetime.now(timezone.utc).isoformat()
            self._tickets[ticket_id]["status"] = "APPROVED"
            self._tickets[ticket_id]["resolution_text"] = resolution_text
            self._tickets[ticket_id]["resolved_at"] = now_iso
            self._tickets[ticket_id]["assigned_staff"] = staff_id
            self._tickets[ticket_id]["assigned_staff_id"] = staff_id
            self._tickets[ticket_id]["updated_at"] = now_iso
            
            # Recalculate SLA
            self._calculate_sla(self._tickets[ticket_id])

            audit_event = {
                "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
                "ticket_id": ticket_id,
                "event_type": "APPROVED",
                "actor_id": staff_id,
                "actor_role": "STAFF_OPERATOR",
                "timestamp": now_iso,
                "from_state": "STAFF_REVIEW",
                "to_state": "APPROVED",
                "notes": "Resolution approved by staff operator and dispatched to UMS",
                "details": {"resolution_length": len(resolution_text)}
            }
            self._tickets[ticket_id].setdefault("history", []).append(audit_event)
            return True
        return False

    def get_audit_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return []
        return ticket.get("history", [])

    def list_departments(self) -> List[Dict[str, Any]]:
        # Return unique department objects (ignoring lowercase alias keys)
        seen = set()
        depts = []
        for key, val in self._departments.items():
            dept_id = val.get("department_id") or val.get("id")
            if dept_id and dept_id not in seen:
                seen.add(dept_id)
                depts.append(val)
        return depts

    def get_department(self, department_id: str) -> Optional[Dict[str, Any]]:
        # Check direct ID match or lowercase name/code
        if department_id in self._departments:
            return self._departments[department_id]
        d_lower = department_id.lower()
        if d_lower in self._departments:
            return self._departments[d_lower]
        for val in self._departments.values():
            if val.get("department_code", "").lower() == d_lower or val.get("code", "").lower() == d_lower:
                return val
        return None

    def list_users(
        self,
        department_id: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        users = list(self._users.values())
        if department_id:
            dept_obj = self.get_department(department_id)
            target_id = dept_obj.get("department_id", department_id) if dept_obj else department_id
            users = [u for u in users if u.get("department_id") == target_id]
        if role:
            users = [u for u in users if u.get("role", "").upper() == role.upper()]
        return users

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    def get_student_context(self, student_reference: str) -> Optional[Dict[str, Any]]:
        """Returns non-PII academic context for a synthetic student."""
        return {
            "student_reference": student_reference,
            "program": "B.Tech Computer Science & Engineering",
            "semester": 5,
            "cgpa": 8.42,
            "attendance_aggregate_percentage": 78.5,
            "residential_hostel": "BH-4",
            "room_number": "312",
            "fee_status": "PAID",
            "pending_grievances_count": 1,
            "is_synthetic": True
        }
