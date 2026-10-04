"""
Automated unit tests for Smart RMS Canonical Data Contracts.
Validates Pydantic domain models, enums, aliasing, and SLA calculation policies.
"""

import pytest
from datetime import datetime, timezone
from app.schemas.contracts import (
    TicketStatus,
    PriorityLevel,
    StaffRole,
    SLAStatus,
    AuditEventType,
    StudentReference,
    DepartmentSLAPolicy,
    DepartmentEscalationPolicy,
    Department,
    StaffUser,
    WorkloadMetadata,
    AttachmentMetadata,
    SLARecord,
    AuditEvent,
    RMSResponse,
    Assignment,
    Escalation,
    KnowledgeDocument,
    RMSRequest
)
from app.workflows.workflow_engine import WorkflowEngine, TicketState


def test_student_reference_model():
    student = StudentReference(
        student_id="STU-SYN-8492",
        registration_number="REG-2023-8492",
        name="Harshil Somisetty (Synthetic)",
        program="B.Tech Computer Science & Engineering",
        semester=5,
        hostel_block="BH-4",
        room_number="312"
    )
    assert student.student_id == "STU-SYN-8492"
    assert student.is_synthetic is True
    assert student.semester == 5


def test_department_sla_policy():
    policy = DepartmentSLAPolicy(LOW=72, MEDIUM=48, HIGH=24, CRITICAL=12)
    assert policy.get_hours_for_priority(PriorityLevel.CRITICAL) == 12
    assert policy.get_hours_for_priority("HIGH") == 24
    assert policy.get_hours_for_priority("Medium") == 48
    assert policy.get_hours_for_priority("Low") == 72
    assert policy.get_hours_for_priority("Unknown") == 72


def test_department_model():
    dept = Department(
        department_id="DEPT-HOSTEL",
        department_code="HA",
        name="Hostel Affairs",
        description="Hostel residential operations",
        categories=["Maintenance", "Room Allocation"],
        sla_policy=DepartmentSLAPolicy(LOW=48, MEDIUM=24, HIGH=12, CRITICAL=4),
        staff_ids=["USR-STAFF-01"],
        hod_reference={"name": "Dr. Sandeep Kapoor", "email": "hod.hostels@lpu.ac.in"},
        active_status=True
    )
    assert dept.department_id == "DEPT-HOSTEL"
    assert dept.department_code == "HA"
    assert dept.sla_policy.CRITICAL == 4
    assert dept.active_status is True


def test_staff_user_model():
    user = StaffUser(
        user_id="USR-STAFF-01",
        display_name="Prof. Rajesh Sharma",
        email="rajesh.sharma@lpu.ac.in",
        role=StaffRole.STAFF_OPERATOR,
        department_id="DEPT-HOSTEL",
        department_name="Hostel Affairs",
        permissions=["ticket:read", "ticket:approve"],
        workload_metadata=WorkloadMetadata(
            assigned_tickets_count=3,
            open_tickets_count=2,
            max_capacity=20,
            specialty_categories=["Plumbing"]
        )
    )
    assert user.user_id == "USR-STAFF-01"
    assert user.role == StaffRole.STAFF_OPERATOR
    assert user.workload_metadata.max_capacity == 20
    assert "ticket:approve" in user.permissions


def test_sla_record_model():
    sla = SLARecord(
        priority="High",
        sla_hours=24,
        due_at="2026-09-22T10:00:00Z",
        is_breached=False,
        remaining_hours=18.5,
        status=SLAStatus.ON_TRACK
    )
    assert sla.sla_hours == 24
    assert sla.is_breached is False
    assert sla.status == SLAStatus.ON_TRACK


def test_audit_event_model():
    event = AuditEvent(
        event_id="AUD-001",
        ticket_id="TKT-RMS-1001",
        event_type=AuditEventType.STATUS_CHANGED,
        actor_id="USR-STAFF-01",
        actor_role="STAFF_OPERATOR",
        from_state="INGESTED",
        to_state="STAFF_REVIEW",
        notes="Under evaluation by warden",
        details={"ip": "127.0.0.1"}
    )
    assert event.event_id == "AUD-001"
    assert event.from_state == "INGESTED"
    assert event.to_state == "STAFF_REVIEW"


def test_assignment_model():
    asg = Assignment(
        assignment_id="ASG-001",
        ticket_id="TKT-RMS-1001",
        department_id="DEPT-HOSTEL",
        staff_id="USR-STAFF-01",
        assigned_by="SYSTEM",
        reason="Initial triage routing"
    )
    assert asg.assignment_id == "ASG-001"
    assert asg.active is True


def test_rms_response_model():
    resp = RMSResponse(
        response_id="RSP-001",
        ticket_id="TKT-RMS-1001",
        author_id="USR-STAFF-01",
        author_name="Prof. Rajesh Sharma",
        author_role="STAFF_OPERATOR",
        content="Plumber dispatched to Room 312.",
        is_internal=False
    )
    assert resp.response_id == "RSP-001"
    assert resp.is_internal is False


def test_knowledge_document_model():
    doc = KnowledgeDocument(
        document_id="DOC-2024-HOSTEL-01",
        title="Hostel Code of Conduct",
        department="Hostel Affairs",
        clause="Clause 4.2",
        content="Maintenance requests attended within 24 hours.",
        effective_date="2024-01-01",
        keywords=["hostel", "maintenance"]
    )
    assert doc.document_id == "DOC-2024-HOSTEL-01"
    assert doc.version == "1.0"


def test_rms_request_canonical_model_interop():
    req = RMSRequest(
        ticket_id="TKT-RMS-9999",
        student_reference="STU-SYN-0001",
        subject="Noisy radiator in hostel corridor",
        description="Loud rattling sounds in BH-2 hallway.",
        category="Hostel",
        department="Hostel Affairs",
        priority="Medium",
        status="INGESTED"
    )
    # Validate title / subject interoperability
    assert req.title == "Noisy radiator in hostel corridor"
    assert req.subject == "Noisy radiator in hostel corridor"
    assert req.is_synthetic is True


def test_workflow_engine_lifecycle_transitions():
    engine = WorkflowEngine()

    ticket = {
        "ticket_id": "TKT-TEST-01",
        "status": TicketState.INGESTED.value,
        "history": []
    }

    assert engine.can_transition(TicketState.INGESTED.value, TicketState.ANALYZED.value) is True
    assert engine.can_transition(TicketState.INGESTED.value, TicketState.STAFF_REVIEW.value) is True
    assert engine.can_transition(TicketState.INGESTED.value, TicketState.RESOLVED.value) is False

    # Execute transition
    updated = engine.transition(
        ticket,
        TicketState.STAFF_REVIEW.value,
        actor_id="USR-STAFF-01",
        notes="Reviewed by staff operator"
    )
    assert updated["status"] == TicketState.STAFF_REVIEW.value
    assert len(updated["history"]) == 1
    assert updated["history"][0]["from_state"] == TicketState.INGESTED.value
    assert updated["history"][0]["to_state"] == TicketState.STAFF_REVIEW.value
