"""
Comprehensive Operational Workflow Unit & Integration Tests.
Covers state machine enforcement, ingestion, assignments, redirections, communication threads,
SLA risk, escalations, resolution, closure, audit trail, roles, and analytics.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.workflows.workflow_engine import WorkflowEngine, TicketState
from app.schemas.contracts import InvalidStateTransitionError

client = TestClient(app)

# ============================================================================
# 1. State Machine Tests
# ============================================================================

def test_workflow_valid_transitions():
    engine = WorkflowEngine()
    ticket = {"ticket_id": "TKT-TEST-001", "status": "INGESTED", "history": []}

    # INGESTED -> ROUTED
    t1 = engine.transition(ticket, TicketState.ROUTED.value, actor_id="USR-STAFF-01")
    assert t1["status"] == "ROUTED"

    # ROUTED -> STAFF_REVIEW
    t2 = engine.transition(ticket, TicketState.STAFF_REVIEW.value, actor_id="USR-STAFF-01")
    assert t2["status"] == "STAFF_REVIEW"

    # STAFF_REVIEW -> IN_PROGRESS
    t3 = engine.transition(ticket, TicketState.IN_PROGRESS.value, actor_id="USR-STAFF-01")
    assert t3["status"] == "IN_PROGRESS"

    # IN_PROGRESS -> WAITING_FOR_STUDENT
    t4 = engine.transition(ticket, TicketState.WAITING_FOR_STUDENT.value, actor_id="USR-STAFF-01")
    assert t4["status"] == "WAITING_FOR_STUDENT"

    # WAITING_FOR_STUDENT -> IN_PROGRESS
    t5 = engine.transition(ticket, TicketState.IN_PROGRESS.value, actor_id="USR-STAFF-01")
    assert t5["status"] == "IN_PROGRESS"

    # IN_PROGRESS -> RESOLVED
    t6 = engine.transition(ticket, TicketState.RESOLVED.value, actor_id="USR-STAFF-01")
    assert t6["status"] == "RESOLVED"

    # RESOLVED -> CLOSED
    t7 = engine.transition(ticket, TicketState.CLOSED.value, actor_id="USR-STAFF-01")
    assert t7["status"] == "CLOSED"


def test_workflow_invalid_transitions_raise_error():
    engine = WorkflowEngine()
    ticket = {"ticket_id": "TKT-TEST-002", "status": "INGESTED", "history": []}

    # INGESTED cannot jump directly to RESOLVED or CLOSED
    with pytest.raises(InvalidStateTransitionError):
        engine.transition(ticket, TicketState.RESOLVED.value, actor_id="USR-STAFF-01")

    with pytest.raises(InvalidStateTransitionError):
        engine.transition(ticket, TicketState.CLOSED.value, actor_id="USR-STAFF-01")


def test_api_patch_invalid_transition_returns_400():
    # TKT-RMS-1007 is currently in STAFF_REVIEW
    payload = {
        "status": "CLOSED",
        "actor_id": "USR-STAFF-01",
        "reason": "Illegal direct closure attempt"
    }
    response = client.patch("/api/v1/rms/TKT-RMS-1007", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Illegal state transition" in detail or "CLOSED" in detail


# ============================================================================
# 2. Assignment & Reassignment Tests
# ============================================================================

def test_assignment_valid_department_and_staff():
    payload = {
        "department_id": "DEPT-ACADEMICS",
        "staff_id": "USR-STAFF-02",
        "assigned_by": "USR-HOD-03",
        "reason": "Assigning to Academic course coordinator"
    }
    response = client.post("/api/v1/rms/TKT-RMS-1003/assign", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_staff_id"] == "USR-STAFF-02"


def test_assignment_invalid_staff_fails():
    payload = {
        "department_id": "DEPT-HOSTEL",
        "staff_id": "USR-NONEXISTENT-999",
        "assigned_by": "USR-ADMIN-01"
    }
    response = client.post("/api/v1/rms/TKT-RMS-1001/assign", json=payload)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


def test_reassignment_preserves_history():
    # Reassign TKT-RMS-1001 to a different staff member
    payload = {
        "department_id": "DEPT-HOSTEL",
        "staff_id": "USR-HOD-01",
        "assigned_by": "USR-ADMIN-01",
        "reason": "Reassigned for supervisory review"
    }
    response = client.post("/api/v1/rms/TKT-RMS-1001/assign", json=payload)
    assert response.status_code == 200

    # Fetch detail and inspect assignments array
    detail = client.get("/api/v1/rms/TKT-RMS-1001").json()
    assert len(detail.get("assignments", [])) >= 2
    # Active assignment should be USR-HOD-01
    active_asg = next(a for a in detail["assignments"] if a["active"])
    assert active_asg["staff_id"] == "USR-HOD-01"
    # Previously active assignment should now be deactivated
    inactive_asg = [a for a in detail["assignments"] if not a["active"]]
    assert len(inactive_asg) >= 1


# ============================================================================
# 3. Redirection Workflow Tests
# ============================================================================

def test_redirection_workflow():
    payload = {
        "staff_id": "USR-STAFF-02",
        "new_department": "DEPT-EXAM",
        "reason": "Grievance requires examination branch records"
    }
    response = client.post("/api/v1/rms/TKT-RMS-1008/redirect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["new_department"] == "Examination Branch"

    # Verify history logs REDIRECTED
    history = client.get("/api/v1/rms/TKT-RMS-1008/history").json()
    redirect_events = [e for e in history if e["event_type"] == "REDIRECTED"]
    assert len(redirect_events) >= 1
    assert "examination branch records" in redirect_events[-1]["notes"]


# ============================================================================
# 4. Response & Communication Thread Tests
# ============================================================================

def test_internal_note_vs_official_response():
    # Add internal note
    note_payload = {
        "author_id": "USR-STAFF-01",
        "author_name": "Prof. Rajesh Sharma",
        "author_role": "STAFF_OPERATOR",
        "content": "Checked maintenance schedule: team is available at 3 PM.",
        "is_internal": True
    }
    res1 = client.post("/api/v1/rms/TKT-RMS-1001/responses", json=note_payload)
    assert res1.status_code == 201
    assert res1.json()["is_internal"] is True

    # Add official student response
    resp_payload = {
        "author_id": "USR-STAFF-01",
        "author_name": "Prof. Rajesh Sharma",
        "author_role": "STAFF_OPERATOR",
        "content": "Dear Student, the maintenance electrician has been assigned to inspect BH-4 Room 312.",
        "is_internal": False
    }
    res2 = client.post("/api/v1/rms/TKT-RMS-1001/responses", json=resp_payload)
    assert res2.status_code == 201
    assert res2.json()["is_internal"] is False
    assert res2.json()["status"] == "PUBLISHED"


def test_ai_draft_remains_draft():
    # Triggering draft generation stores an AI_DRAFT in communication thread
    draft_res = client.get("/api/v1/rms/TKT-RMS-1002/draft")
    assert draft_res.status_code == 200

    ticket = client.get("/api/v1/rms/TKT-RMS-1002").json()
    ai_drafts = [r for r in ticket.get("responses", []) if r.get("response_type") == "AI_DRAFT"]
    assert len(ai_drafts) >= 1
    # AI draft MUST have status DRAFT and is_internal True
    assert ai_drafts[-1]["status"] == "DRAFT"
    assert ai_drafts[-1]["is_internal"] is True


# ============================================================================
# 5. SLA Tracking & Risk Tests
# ============================================================================

def test_sla_deterministic_risk():
    ticket = client.get("/api/v1/rms/TKT-RMS-1004").json()
    sla = ticket.get("sla_record")
    assert sla is not None
    assert sla["priority"] == "Critical"
    assert sla["sla_hours"] == 4
    assert sla["status"] in ["ON_TRACK", "AT_RISK", "BREACHED", "RESOLVED"]


# ============================================================================
# 6. Escalation Workflow Tests
# ============================================================================

def test_manual_escalation():
    payload = {
        "staff_id": "USR-STAFF-01",
        "target_role": "DEPARTMENT_HOD",
        "reason": "Appliance motor replacement requires financial approval of HOD.",
        "urgent": True
    }
    res = client.post("/api/v1/rms/TKT-RMS-1001/escalate", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ESCALATED"

    # Detail reflects escalation
    detail = client.get("/api/v1/rms/TKT-RMS-1001").json()
    assert detail["status"] == "ESCALATED"
    assert detail["escalation_level"] >= 1


# ============================================================================
# 7. Resolution & Closure Workflow Tests
# ============================================================================

def test_resolution_workflow():
    payload = {
        "staff_id": "USR-STAFF-01",
        "resolution_text": "Electrician has replaced the split AC drain line in BH-4 Room 312. Verified operational.",
        "notes": "Work order signed by resident student."
    }
    res = client.post("/api/v1/rms/TKT-RMS-1001/resolve", json=payload)
    assert res.status_code == 200
    ticket = res.json()
    assert ticket["status"] == "RESOLVED"
    assert ticket["resolved_at"] is not None
    assert ticket["resolving_actor"] == "USR-STAFF-01"


def test_resolution_with_short_text_fails():
    payload = {
        "staff_id": "USR-STAFF-01",
        "resolution_text": "Done",  # Less than 5 chars
        "notes": "Insufficient text"
    }
    res = client.post("/api/v1/rms/TKT-RMS-1001/resolve", json=payload)
    assert res.status_code == 422 or res.status_code == 400


def test_closure_workflow():
    # TKT-RMS-1001 is now RESOLVED, so closing it is valid
    payload = {
        "staff_id": "USR-STAFF-01",
        "notes": "Student confirmed issue resolved via portal satisfaction rating.",
        "satisfaction_score": 5
    }
    res = client.post("/api/v1/rms/TKT-RMS-1001/close", json=payload)
    assert res.status_code == 200
    ticket = res.json()
    assert ticket["status"] == "CLOSED"
    assert ticket["closed_at"] is not None
    assert ticket["closing_actor"] == "USR-STAFF-01"


def test_closure_unresolved_ticket_fails():
    # TKT-RMS-1007 is in STAFF_REVIEW, not resolved
    payload = {
        "staff_id": "USR-STAFF-07",
        "notes": "Attempting early closure without resolution"
    }
    res = client.post("/api/v1/rms/TKT-RMS-1007/close", json=payload)
    assert res.status_code == 400
    assert "must be resolved first" in res.json()["detail"].lower() or "cannot transition" in res.json()["detail"].lower() or "illegal state transition" in res.json()["detail"].lower()


# ============================================================================
# 8. Operations Analytics Tests
# ============================================================================

def test_operations_analytics_endpoint():
    res = client.get("/api/v1/analytics/operations")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tickets"] > 0
    assert "tickets_by_status" in data
    assert "tickets_by_department" in data
    assert "tickets_by_priority" in data
    assert "tickets_by_sla_status" in data
    assert "open_backlog" in data
    assert "resolved_count" in data
    assert "closed_count" in data
    assert data["avg_resolution_time_hours"] >= 0
