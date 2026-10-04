"""
Integration and API tests for the Synthetic University Environment & Stable Adapter.
Tests ticket ingestion, routing, SLA tracking, staff assignments, responses, audit trails,
departments, and staff users.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_synthetic_ticket():
    payload = {
        "student_reference": "STU-SYN-9999",
        "subject": "Room geyser short-circuit in BH-1 Room 104",
        "description": "The geyser sparks when powered on. Urgent inspection needed. Phone: 9876543210.",
        "category": "Hostel",
        "department": "Hostel Affairs",
        "priority": "Critical"
    }
    response = client.post("/api/v1/rms", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "ticket_id" in data
    assert data["student_reference"] == "STU-SYN-9999"
    assert data["status"] == "INGESTED"
    assert data["priority"] == "Critical"
    assert data["is_synthetic"] is True
    assert "sla_record" in data
    assert data["sla_record"]["sla_hours"] == 4  # Critical SLA for Hostel Affairs is 4h


def test_assign_ticket_to_staff():
    # Assign TKT-RMS-1001 to a staff member
    payload = {
        "department_id": "DEPT-HOSTEL",
        "staff_id": "USR-STAFF-01",
        "assigned_by": "USR-HOD-01",
        "reason": "Specialist in residential hostel maintenance"
    }
    response = client.post("/api/v1/rms/TKT-RMS-1001/assign", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "TKT-RMS-1001"
    assert data["assigned_staff_id"] == "USR-STAFF-01"

    # Verify ticket detail reflects assignment
    detail_res = client.get("/api/v1/rms/TKT-RMS-1001")
    assert detail_res.status_code == 200
    ticket_detail = detail_res.json()
    assert ticket_detail["assigned_staff_id"] == "USR-STAFF-01"


def test_add_ticket_communication_response():
    payload = {
        "author_id": "USR-STAFF-01",
        "author_name": "Prof. Rajesh Sharma",
        "author_role": "STAFF_OPERATOR",
        "content": "Maintenance team has been dispatched to inspect Room 312.",
        "is_internal": False
    }
    response = client.post("/api/v1/rms/TKT-RMS-1001/responses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == "TKT-RMS-1001"
    assert data["content"] == payload["content"]
    assert "response_id" in data


def test_get_ticket_audit_history():
    response = client.get("/api/v1/rms/TKT-RMS-1001/history")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0
    # Every audit event should have an event_id and timestamp
    for event in history:
        assert "event_id" in event
        assert "timestamp" in event


def test_list_departments_with_sla():
    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    depts = response.json()
    assert len(depts) >= 7
    dept_names = [d["name"] for d in depts]
    assert "Hostel Affairs" in dept_names
    assert "Accounts & Finance" in dept_names
    assert "Examination Branch" in dept_names

    hostel_dept = next(d for d in depts if d["department_id"] == "DEPT-HOSTEL")
    assert hostel_dept["sla_policy"]["CRITICAL"] == 4
    assert hostel_dept["department_code"] == "HA"
    assert hostel_dept["active_status"] is True


def test_get_department_by_id():
    response = client.get("/api/v1/departments/DEPT-EXAM")
    assert response.status_code == 200
    dept = response.json()
    assert dept["department_id"] == "DEPT-EXAM"
    assert dept["name"] == "Examination Branch"
    assert dept["sla_policy"]["HIGH"] == 12


def test_list_staff_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 4
    roles = [u["role"] for u in users]
    assert "STAFF_OPERATOR" in roles
    assert "DEPARTMENT_HOD" in roles
    assert "SYSTEM_ADMIN" in roles


def test_filter_staff_users_by_role():
    response = client.get("/api/v1/users?role=STAFF_OPERATOR")
    assert response.status_code == 200
    users = response.json()
    for u in users:
        assert u["role"] == "STAFF_OPERATOR"


def test_get_user_by_id():
    response = client.get("/api/v1/users/USR-STAFF-01")
    assert response.status_code == 200
    user = response.json()
    assert user["user_id"] == "USR-STAFF-01"
    assert user["display_name"] == "Prof. Rajesh Sharma"
    assert "ticket:approve" in user["permissions"]
    assert user["workload_metadata"]["max_capacity"] > 0
