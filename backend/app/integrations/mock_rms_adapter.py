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

    # Configurable SLA risk threshold: 25% of window remaining or 4 hours
    SLA_AT_RISK_RATIO = 0.25
    SLA_AT_RISK_MIN_HOURS = 4.0

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
        ticket.setdefault("assignments", [])
        ticket.setdefault("escalations", [])
        ticket.setdefault("history", [])
        ticket.setdefault("metadata", {"environment": "synthetic"})

        # Initialize primary assignment record if absent
        if not ticket["assignments"] and ticket.get("assigned_staff_id"):
            ticket["assignments"].append({
                "assignment_id": f"ASG-{ticket.get('ticket_id', 'TKT')}-01",
                "ticket_id": ticket.get("ticket_id"),
                "department_id": ticket.get("assigned_department_id", "DEPT-GENERAL"),
                "staff_id": ticket.get("assigned_staff_id"),
                "assigned_by": "SYSTEM",
                "assigned_at": ticket.get("created_at", datetime.now(timezone.utc).isoformat()),
                "reason": "Initial routing",
                "active": True
            })

        # Compute dynamic SLA
        self._calculate_sla(ticket)

    def _calculate_sla(self, ticket: Dict[str, Any]):
        """
        Deterministic calculation of due_at, remaining_hours, and SLA breach/risk status.
        Thresholds:
        - RESOLVED: Ticket is already resolved or closed.
        - BREACHED: Remaining time <= 0 for an active ticket.
        - AT_RISK: Remaining time <= 25% of SLA window or <= 4.0 hours.
        - ON_TRACK: Normal operational progression.
        """
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
            c_clean = created_str.replace("Z", "+00:00")
            created_dt = datetime.fromisoformat(c_clean)
        except Exception:
            created_dt = datetime.now(timezone.utc)

        due_dt = created_dt + timedelta(hours=sla_hours)
        now_dt = datetime.now(timezone.utc)
        
        remaining_seconds = (due_dt - now_dt).total_seconds()
        remaining_hours = round(remaining_seconds / 3600.0, 1)

        status_curr = ticket.get("status", "INGESTED")

        if status_curr in ["APPROVED", "RESOLVED", "CLOSED"]:
            sla_status = "RESOLVED"
            is_breached = False
        elif remaining_seconds <= 0:
            sla_status = "BREACHED"
            is_breached = True
        elif remaining_hours <= max(sla_hours * self.SLA_AT_RISK_RATIO, self.SLA_AT_RISK_MIN_HOURS):
            sla_status = "AT_RISK"
            is_breached = False
        else:
            sla_status = "ON_TRACK"
            is_breached = False

        due_iso = due_dt.isoformat().replace("+00:00", "Z")
        ticket["due_at"] = due_iso
        ticket["sla_record"] = {
            "priority": priority,
            "sla_hours": sla_hours,
            "due_at": due_iso,
            "is_breached": is_breached,
            "remaining_hours": remaining_hours,
            "status": sla_status
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
            "event_type": "INGESTED",
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

        if ticket.get("status") == "CLOSED":
            raise ValueError(f"Cannot reassign closed ticket {ticket_id}")

        now_iso = datetime.now(timezone.utc).isoformat()
        is_reassignment = bool(ticket.get("assigned_staff_id") or ticket.get("assigned_department_id"))

        # Deactivate existing active assignments
        for asg in ticket.setdefault("assignments", []):
            asg["active"] = False

        # Validate & assign department
        if department_id:
            dept_obj = self.get_department(department_id)
            if not dept_obj:
                raise ValueError(f"Department '{department_id}' not found.")
            ticket["assigned_department_id"] = dept_obj.get("department_id", department_id)
            ticket["department"] = dept_obj.get("name", ticket["department"])

        # Validate & assign staff
        if staff_id:
            user = self.get_user(staff_id)
            if not user:
                raise ValueError(f"Staff user '{staff_id}' not found.")
            if not user.get("active_status", True):
                raise ValueError(f"Staff user '{staff_id}' is inactive.")
            
            # Verify staff belongs to department when assigned to one
            user_dept = user.get("department_id")
            ticket_dept = ticket.get("assigned_department_id")
            if user_dept and ticket_dept and user_dept != ticket_dept and user.get("role") not in ["SYSTEM_ADMIN", "ADMIN"]:
                raise ValueError(f"Staff user '{staff_id}' belongs to {user_dept}, not {ticket_dept}.")

            ticket["assigned_staff_id"] = staff_id
            ticket["assigned_staff"] = staff_id
            wl = user.setdefault("workload_metadata", {})
            wl["assigned_tickets_count"] = wl.get("assigned_tickets_count", 0) + 1

        ticket["updated_at"] = now_iso
        
        # Create Assignment record
        asg_id = f"ASG-{ticket_id.replace('TKT-', '')}-{len(ticket['assignments']) + 1}"
        assignment_record = {
            "assignment_id": asg_id,
            "ticket_id": ticket_id,
            "department_id": ticket.get("assigned_department_id", "DEPT-GENERAL"),
            "staff_id": ticket.get("assigned_staff_id"),
            "assigned_by": assigned_by,
            "assigned_at": now_iso,
            "reason": reason or ("Staff reassignment" if is_reassignment else "Initial assignment"),
            "active": True
        }
        ticket["assignments"].append(assignment_record)
        self._assignments.append(assignment_record)

        # Audit Event
        event_type = "REASSIGNED" if is_reassignment else "ASSIGNED"
        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": event_type,
            "actor_id": assigned_by,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": ticket.get("status"),
            "notes": f"{event_type.capitalize()} to staff {staff_id} in {ticket.get('department')}: {reason or 'Standard routing'}",
            "details": assignment_record
        }
        ticket.setdefault("history", []).append(audit_event)
        return True

    def redirect_ticket(
        self,
        ticket_id: str,
        new_department: str,
        staff_id: str,
        reason: str
    ) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False

        dept_obj = self.get_department(new_department)
        if not dept_obj:
            raise ValueError(f"Destination department '{new_department}' not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        old_dept = ticket.get("department", "Unknown")
        old_dept_id = ticket.get("assigned_department_id", "DEPT-UNKNOWN")

        # Deactivate existing active assignments
        for asg in ticket.setdefault("assignments", []):
            asg["active"] = False

        # Update department
        ticket["department"] = dept_obj.get("name", new_department)
        ticket["assigned_department_id"] = dept_obj.get("department_id", new_department)
        
        # Reset assigned staff member on cross-department redirect
        prev_staff = ticket.get("assigned_staff_id")
        ticket["assigned_staff_id"] = None
        ticket["assigned_staff"] = None

        # Add new assignment for target department
        asg_id = f"ASG-{ticket_id.replace('TKT-', '')}-{len(ticket['assignments']) + 1}"
        new_asg = {
            "assignment_id": asg_id,
            "ticket_id": ticket_id,
            "department_id": ticket["assigned_department_id"],
            "staff_id": None,
            "assigned_by": staff_id,
            "assigned_at": now_iso,
            "reason": f"Redirected: {reason}",
            "active": True
        }
        ticket["assignments"].append(new_asg)
        ticket["updated_at"] = now_iso

        # Log REDIRECTED audit event
        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "REDIRECTED",
            "actor_id": staff_id,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": ticket.get("status"),
            "notes": f"Redirected from {old_dept} to {ticket['department']}: {reason}",
            "details": {
                "previous_department": old_dept,
                "previous_department_id": old_dept_id,
                "new_department": ticket["department"],
                "new_department_id": ticket["assigned_department_id"],
                "previous_staff_id": prev_staff,
                "reason": reason
            }
        }
        ticket.setdefault("history", []).append(audit_event)
        return True

    def add_response(self, ticket_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        now_iso = datetime.now(timezone.utc).isoformat()
        rsp_id = f"RSP-{ticket_id.replace('TKT-', '')}-{len(ticket.get('responses', [])) + 1}"
        
        response_type = response_data.get("response_type", "STAFF")
        is_internal = response_data.get("is_internal", False)

        # AI drafts remain drafts until explicit human approval
        if response_type == "AI_DRAFT":
            pub_status = "DRAFT"
        else:
            pub_status = response_data.get("status", "PUBLISHED")

        response_data["response_id"] = rsp_id
        response_data["ticket_id"] = ticket_id
        response_data["response_type"] = response_type
        response_data["status"] = pub_status
        response_data["is_internal"] = is_internal
        response_data.setdefault("created_at", now_iso)

        ticket.setdefault("responses", []).append(response_data)
        ticket["updated_at"] = now_iso

        # Select descriptive event type
        if is_internal:
            evt_type = "NOTE_ADDED"
        elif response_type == "AI_DRAFT":
            evt_type = "DRAFT_CREATED"
        else:
            evt_type = "RESPONSE_SENT"

        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": evt_type,
            "actor_id": response_data.get("author_id", "UNKNOWN"),
            "actor_role": response_data.get("author_role", "STAFF_OPERATOR"),
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": ticket.get("status"),
            "notes": f"Communication ({response_type}) added: {response_data.get('content')[:60]}...",
            "details": {
                "response_id": rsp_id,
                "response_type": response_type,
                "is_internal": is_internal,
                "status": pub_status
            }
        }
        ticket.setdefault("history", []).append(audit_event)
        return response_data

    def escalate_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        target_role: str,
        reason: str,
        urgent: bool = False,
        new_level: str = "LEVEL_1"
    ) -> Dict[str, Any]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        now_iso = datetime.now(timezone.utc).isoformat()
        current_level_num = ticket.get("escalation_level", 0)
        previous_level_str = f"LEVEL_{current_level_num}" if current_level_num <= 2 else "HOD"

        escalation_record = {
            "escalation_id": f"ESC-{ticket_id.replace('TKT-', '')}-{len(ticket.get('escalations', [])) + 1}",
            "ticket_id": ticket_id,
            "escalated_by": staff_id,
            "target_role": target_role,
            "previous_level": previous_level_str,
            "new_level": new_level,
            "reason": reason,
            "urgent": urgent,
            "escalated_at": now_iso,
            "status": "PENDING"
        }
        ticket.setdefault("escalations", []).append(escalation_record)
        ticket["escalation_level"] = current_level_num + 1
        ticket["status"] = "ESCALATED"
        ticket["updated_at"] = now_iso

        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "ESCALATED",
            "actor_id": staff_id,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": ticket.get("status"),
            "to_state": "ESCALATED",
            "notes": f"Escalated to {target_role} ({new_level}): {reason}",
            "details": escalation_record
        }
        ticket.setdefault("history", []).append(audit_event)
        return escalation_record

    def post_resolution(self, ticket_id: str, resolution_text: str, staff_id: str) -> bool:
        if ticket_id in self._tickets:
            now_iso = datetime.now(timezone.utc).isoformat()
            self._tickets[ticket_id]["status"] = "APPROVED"
            self._tickets[ticket_id]["resolution_text"] = resolution_text
            self._tickets[ticket_id]["resolved_at"] = now_iso
            self._tickets[ticket_id]["assigned_staff"] = staff_id
            self._tickets[ticket_id]["assigned_staff_id"] = staff_id
            self._tickets[ticket_id]["resolving_actor"] = staff_id
            self._tickets[ticket_id]["updated_at"] = now_iso
            
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

    def resolve_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        resolution_text: str,
        notes: Optional[str] = None
    ) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        if not resolution_text or len(resolution_text.strip()) < 5:
            raise ValueError("Official resolution narrative must be at least 5 characters.")

        now_iso = datetime.now(timezone.utc).isoformat()
        from_state = ticket.get("status", "IN_PROGRESS")

        ticket["status"] = "RESOLVED"
        ticket["resolution_text"] = resolution_text
        ticket["resolved_at"] = now_iso
        ticket["resolving_actor"] = staff_id
        ticket["updated_at"] = now_iso

        self._calculate_sla(ticket)

        # Add official response if not already present
        rsp_id = f"RSP-{ticket_id.replace('TKT-', '')}-{len(ticket.get('responses', [])) + 1}"
        ticket.setdefault("responses", []).append({
            "response_id": rsp_id,
            "ticket_id": ticket_id,
            "author_id": staff_id,
            "author_name": "University Resolution Authority",
            "author_role": "STAFF_OPERATOR",
            "response_type": "STAFF",
            "status": "PUBLISHED",
            "content": resolution_text,
            "is_internal": False,
            "created_at": now_iso
        })

        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "RESOLVED",
            "actor_id": staff_id,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": from_state,
            "to_state": "RESOLVED",
            "notes": notes or "Ticket marked as officially resolved by staff",
            "details": {"resolution_length": len(resolution_text)}
        }
        ticket.setdefault("history", []).append(audit_event)
        return True

    def close_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        notes: Optional[str] = None
    ) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        current_state = ticket.get("status")
        if current_state not in ["RESOLVED", "WAITING_FOR_STUDENT", "APPROVED"]:
            raise ValueError(f"Cannot close ticket in state '{current_state}'. Ticket must be resolved first.")

        now_iso = datetime.now(timezone.utc).isoformat()
        ticket["status"] = "CLOSED"
        ticket["closed_at"] = now_iso
        ticket["closing_actor"] = staff_id
        ticket["updated_at"] = now_iso

        self._calculate_sla(ticket)

        audit_event = {
            "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id": ticket_id,
            "event_type": "CLOSED",
            "actor_id": staff_id,
            "actor_role": "STAFF_OPERATOR",
            "timestamp": now_iso,
            "from_state": current_state,
            "to_state": "CLOSED",
            "notes": notes or "Ticket permanently closed upon verification",
            "details": {"closed_by": staff_id}
        }
        ticket.setdefault("history", []).append(audit_event)
        return True

    def get_audit_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return []
        history = list(ticket.get("history", []))
        # Ensure deterministic chronological ordering
        history.sort(key=lambda x: x.get("timestamp", ""))
        return history

    def list_departments(self) -> List[Dict[str, Any]]:
        seen = set()
        depts = []
        for val in self._departments.values():
            dept_id = val.get("department_id") or val.get("id")
            if dept_id and dept_id not in seen:
                seen.add(dept_id)
                depts.append(val)
        return depts

    def get_department(self, department_id: str) -> Optional[Dict[str, Any]]:
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

    def get_operations_analytics(self) -> Dict[str, Any]:
        """Calculates comprehensive operational metrics directly from active tickets."""
        tickets = list(self._tickets.values())
        for t in tickets:
            self._calculate_sla(t)

        status_counts: Dict[str, int] = {}
        dept_counts: Dict[str, int] = {}
        prio_counts: Dict[str, int] = {}
        sla_counts: Dict[str, int] = {"ON_TRACK": 0, "AT_RISK": 0, "BREACHED": 0, "RESOLVED": 0}

        resolution_durations = []
        closure_durations = []
        escalation_count = 0
        open_backlog = 0
        resolved_count = 0
        closed_count = 0

        for t in tickets:
            st = t.get("status", "INGESTED")
            status_counts[st] = status_counts.get(st, 0) + 1

            dp = t.get("department", "General")
            dept_counts[dp] = dept_counts.get(dp, 0) + 1

            pr = t.get("priority", "Medium")
            prio_counts[pr] = prio_counts.get(pr, 0) + 1

            sla = t.get("sla_record", {})
            sla_st = sla.get("status", "ON_TRACK")
            sla_counts[sla_st] = sla_counts.get(sla_st, 0) + 1

            if t.get("escalation_level", 0) > 0 or st == "ESCALATED":
                escalation_count += 1

            if st in ["RESOLVED", "APPROVED"]:
                resolved_count += 1
            elif st == "CLOSED":
                closed_count += 1
            else:
                open_backlog += 1

            # Duration calculations
            try:
                c_str = t.get("created_at", "").replace("Z", "+00:00")
                c_dt = datetime.fromisoformat(c_str)
                r_str = t.get("resolved_at")
                if r_str:
                    r_dt = datetime.fromisoformat(r_str.replace("Z", "+00:00"))
                    diff = (r_dt - c_dt).total_seconds() / 3600.0
                    if diff >= 0:
                        resolution_durations.append(diff)
                    cl_str = t.get("closed_at")
                    if cl_str:
                        cl_dt = datetime.fromisoformat(cl_str.replace("Z", "+00:00"))
                        cldiff = (cl_dt - r_dt).total_seconds() / 3600.0
                        if cldiff >= 0:
                            closure_durations.append(cldiff)
            except Exception:
                pass

        avg_res = round(sum(resolution_durations) / len(resolution_durations), 1) if resolution_durations else 4.2
        avg_close = round(sum(closure_durations) / len(closure_durations), 1) if closure_durations else 1.5

        return {
            "total_tickets": len(tickets),
            "open_backlog": open_backlog,
            "resolved_count": resolved_count,
            "closed_count": closed_count,
            "escalation_count": escalation_count,
            "avg_resolution_time_hours": avg_res,
            "avg_closure_time_hours": avg_close,
            "tickets_by_status": status_counts,
            "tickets_by_department": dept_counts,
            "tickets_by_priority": prio_counts,
            "tickets_by_sla_status": sla_counts
        }
