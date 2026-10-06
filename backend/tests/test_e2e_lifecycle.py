"""
Complete Deterministic End-to-End Lifecycle Integration Test (Section 30).
Validates the complete 17-step staff operations workflow from ticket creation to final closure.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_end_to_end_rms_lifecycle():
    # -------------------------------------------------------------------------
    # 1. Create RMS Ticket
    # -------------------------------------------------------------------------
    create_payload = {
        "student_reference": "STU-SYN-5582",
        "subject": "Electrical power tripping in BH-3 Room 214",
        "description": "The main circuit breaker trips whenever the table lamp is plugged in. Electrical sparks observed.",
        "category": "Hostel",
        "department": "Hostel Affairs",
        "priority": "High"
    }
    create_res = client.post("/api/v1/rms", json=create_payload)
    assert create_res.status_code == 201
    ticket = create_res.json()
    ticket_id = ticket["ticket_id"]
    assert ticket_id.startswith("TKT-RMS-")

    # -------------------------------------------------------------------------
    # 2. Verify Ingested State & SLA Initialized
    # -------------------------------------------------------------------------
    assert ticket["status"] == "INGESTED"
    assert ticket["sla_record"] is not None
    assert ticket["sla_record"]["sla_hours"] == 12  # High priority for Hostel Affairs is 12h
    assert ticket["sla_record"]["status"] in ["ON_TRACK", "AT_RISK"]

    # -------------------------------------------------------------------------
    # 3. Analyze Ticket via NLP Pipeline
    # -------------------------------------------------------------------------
    analyze_res = client.post(f"/api/v1/rms/{ticket_id}/analyze")
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()
    assert analyze_data["ai_analysis"]["suggested_department"] == "Hostel Affairs"
    
    t_after_analyze = client.get(f"/api/v1/rms/{ticket_id}").json()
    assert t_after_analyze["status"] == "ANALYZED"

    # -------------------------------------------------------------------------
    # 4. Route Ticket
    # -------------------------------------------------------------------------
    patch_route = client.patch(f"/api/v1/rms/{ticket_id}", json={
        "status": "ROUTED",
        "actor_id": "SYSTEM_TRIAGE",
        "reason": "Routed to Hostel Affairs based on electrical maintenance categorization"
    })
    assert patch_route.status_code == 200
    assert patch_route.json()["status"] == "ROUTED"

    # -------------------------------------------------------------------------
    # 5. Assign Department & 6. Assign Staff
    # -------------------------------------------------------------------------
    assign_payload = {
        "department_id": "DEPT-HOSTEL",
        "staff_id": "USR-STAFF-01",
        "assigned_by": "USR-HOD-01",
        "reason": "Assigned to residential maintenance operator"
    }
    assign_res = client.post(f"/api/v1/rms/{ticket_id}/assign", json=assign_payload)
    assert assign_res.status_code == 200

    # -------------------------------------------------------------------------
    # 7. Verify Transition to STAFF_REVIEW
    # -------------------------------------------------------------------------
    t_assigned = client.get(f"/api/v1/rms/{ticket_id}").json()
    assert t_assigned["status"] == "STAFF_REVIEW"
    assert t_assigned["assigned_staff_id"] == "USR-STAFF-01"

    # -------------------------------------------------------------------------
    # 8. Move to IN_PROGRESS
    # -------------------------------------------------------------------------
    progress_res = client.patch(f"/api/v1/rms/{ticket_id}", json={
        "status": "IN_PROGRESS",
        "actor_id": "USR-STAFF-01",
        "reason": "Staff operator commenced physical inspection work order"
    })
    assert progress_res.status_code == 200
    assert progress_res.json()["status"] == "IN_PROGRESS"

    # -------------------------------------------------------------------------
    # 9. Add Internal Note
    # -------------------------------------------------------------------------
    note_payload = {
        "author_id": "USR-STAFF-01",
        "author_name": "Prof. Rajesh Sharma",
        "author_role": "STAFF_OPERATOR",
        "content": "Inspected socket wiring in Room 214: short circuit diagnosed in wall conduit.",
        "is_internal": True
    }
    note_res = client.post(f"/api/v1/rms/{ticket_id}/responses", json=note_payload)
    assert note_res.status_code == 201
    assert note_res.json()["is_internal"] is True

    # -------------------------------------------------------------------------
    # 10. Add Official Response to Student
    # -------------------------------------------------------------------------
    student_msg_payload = {
        "author_id": "USR-STAFF-01",
        "author_name": "Prof. Rajesh Sharma",
        "author_role": "STAFF_OPERATOR",
        "content": "Dear Student, maintenance team has isolated the faulty circuit. Electrician will rewire today.",
        "is_internal": False
    }
    msg_res = client.post(f"/api/v1/rms/{ticket_id}/responses", json=student_msg_payload)
    assert msg_res.status_code == 201
    assert msg_res.json()["is_internal"] is False
    assert msg_res.json()["status"] == "PUBLISHED"

    # -------------------------------------------------------------------------
    # 11. Escalate Ticket to HOD
    # -------------------------------------------------------------------------
    esc_payload = {
        "staff_id": "USR-STAFF-01",
        "target_role": "DEPARTMENT_HOD",
        "reason": "Conduit replacement requires procurement approval over threshold.",
        "urgent": False
    }
    esc_res = client.post(f"/api/v1/rms/{ticket_id}/escalate", json=esc_payload)
    assert esc_res.status_code == 200
    assert esc_res.json()["status"] == "ESCALATED"

    # -------------------------------------------------------------------------
    # 12. Return to IN_PROGRESS (HOD Approved)
    # -------------------------------------------------------------------------
    return_progress = client.patch(f"/api/v1/rms/{ticket_id}", json={
        "status": "IN_PROGRESS",
        "actor_id": "USR-HOD-01",
        "reason": "HOD approved emergency maintenance parts requisition. Resuming work."
    })
    assert return_progress.status_code == 200
    assert return_progress.json()["status"] == "IN_PROGRESS"

    # -------------------------------------------------------------------------
    # 13. Resolve Ticket
    # -------------------------------------------------------------------------
    resolve_payload = {
        "staff_id": "USR-STAFF-01",
        "resolution_text": "Circuit breaker and faulty wall conduit in BH-3 Room 214 fully replaced and safety certified.",
        "notes": "Verified insulation resistance test passed."
    }
    resolve_res = client.post(f"/api/v1/rms/{ticket_id}/resolve", json=resolve_payload)
    assert resolve_res.status_code == 200
    t_resolved = resolve_res.json()
    assert t_resolved["status"] == "RESOLVED"
    assert t_resolved["resolved_at"] is not None
    assert t_resolved["resolving_actor"] == "USR-STAFF-01"

    # -------------------------------------------------------------------------
    # 14. Close Ticket
    # -------------------------------------------------------------------------
    close_payload = {
        "staff_id": "USR-STAFF-01",
        "notes": "Student confirmed full electrical safety and power restored.",
        "satisfaction_score": 5
    }
    close_res = client.post(f"/api/v1/rms/{ticket_id}/close", json=close_payload)
    assert close_res.status_code == 200
    t_closed = close_res.json()
    assert t_closed["status"] == "CLOSED"
    assert t_closed["closed_at"] is not None
    assert t_closed["closing_actor"] == "USR-STAFF-01"

    # -------------------------------------------------------------------------
    # 15. Retrieve Audit History
    # -------------------------------------------------------------------------
    history_res = client.get(f"/api/v1/rms/{ticket_id}/history")
    assert history_res.status_code == 200
    history = history_res.json()

    # -------------------------------------------------------------------------
    # 16. Verify Audit Trail (Who did what, when, why)
    # -------------------------------------------------------------------------
    event_types = [e["event_type"] for e in history]
    assert "INGESTED" in event_types
    assert "ASSIGNED" in event_types
    assert "NOTE_ADDED" in event_types
    assert "RESPONSE_SENT" in event_types
    assert "ESCALATED" in event_types
    assert "RESOLVED" in event_types
    assert "CLOSED" in event_types

    # Verify chronological ascending order
    timestamps = [e["timestamp"] for e in history]
    assert timestamps == sorted(timestamps)

    # -------------------------------------------------------------------------
    # 17. Verify Final SLA State (Resolved before breach)
    # -------------------------------------------------------------------------
    final_ticket = client.get(f"/api/v1/rms/{ticket_id}").json()
    assert final_ticket["sla_record"]["status"] == "RESOLVED"
    assert final_ticket["sla_record"]["is_breached"] is False
