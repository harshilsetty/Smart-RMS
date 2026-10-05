from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.config import settings
from app.integrations.base import UniversitySystemAdapter
from app.integrations.mock_rms_adapter import MockRMSAdapter
from app.integrations.future_adapters import FutureUMSAdapter
from app.ai.provider import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.rag.retriever import PolicyRetriever
from app.privacy.pii_redactor import PIIRedactor
from app.privacy.policy_validator import PolicyValidator
from app.workflows.workflow_engine import WorkflowEngine, TicketState
from app.schemas.rms import (
    Ticket,
    TicketListResponse,
    AIAnalysis,
    DraftResponse,
    RAGSource,
    AnalyzeResponse,
    ApprovalResponse,
    EscalateResponse,
    RedirectResponse,
    AnalyticsOverviewResponse,
    RMSCreateRequest,
    AssignmentRequest,
    RMSResponseCreateRequest,
    RMSResponse,
    Department,
    StaffUser,
    AuditEvent,
    ResolveRequest,
    CloseRequest,
    TicketPatchRequest,
    OperationsAnalytics,
    InvalidStateTransitionError
)

class RMSService:
    """
    Central orchestration service coordinating AI, Privacy, RAG, Workflow,
    SLA calculation, and synthetic university operations via stable contracts.
    """

    def __init__(self):
        # Initialize adapter based on configuration
        if settings.INTEGRATION_MODE == "ums_staging":
            self.adapter: UniversitySystemAdapter = FutureUMSAdapter()
        else:
            self.adapter: UniversitySystemAdapter = MockRMSAdapter()

        # Initialize AI Provider
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            self.ai_provider: AIProvider = GeminiProvider(api_key=settings.GEMINI_API_KEY)
        else:
            self.ai_provider: AIProvider = MockAIProvider()

        # Initialize Core Subsystems
        self.privacy_redactor = PIIRedactor()
        self.policy_retriever = PolicyRetriever()
        self.policy_validator = PolicyValidator()
        self.workflow = WorkflowEngine()

    def get_tickets(
        self,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> TicketListResponse:
        raw_tickets = self.adapter.fetch_tickets(
            department=department,
            priority=priority,
            status=status,
            search=search
        )
        parsed_tickets: List[Ticket] = []
        for t in raw_tickets:
            # Mask PII for presentation
            redacted_desc, _ = self.privacy_redactor.redact(t.get("description", ""))
            t_copy = dict(t)
            t_copy["redacted_description"] = redacted_desc
            parsed_tickets.append(Ticket(**t_copy))

        return TicketListResponse(
            total=len(parsed_tickets),
            count=len(parsed_tickets),
            tickets=parsed_tickets
        )

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        raw = self.adapter.get_ticket_by_id(ticket_id)
        if not raw:
            return None
        redacted_desc, _ = self.privacy_redactor.redact(raw.get("description", ""))
        raw_copy = dict(raw)
        raw_copy["redacted_description"] = redacted_desc
        return Ticket(**raw_copy)

    def create_ticket(self, request: RMSCreateRequest) -> Ticket:
        """Ingests or creates a new RMS ticket in the synthetic environment."""
        redacted_desc, _ = self.privacy_redactor.redact(request.description)
        
        ticket_data = {
            "student_reference": request.student_reference,
            "subject": request.subject,
            "title": request.subject,
            "description": request.description,
            "redacted_description": redacted_desc,
            "category": request.category,
            "subcategory": request.subcategory,
            "department": request.department,
            "priority": request.priority,
            "status": TicketState.INGESTED.value,
            "source": request.source,
            "attachments": request.attachments,
            "metadata": request.metadata
        }
        
        created = self.adapter.create_ticket(ticket_data)
        return Ticket(**created)

    def patch_ticket(self, ticket_id: str, request: TicketPatchRequest) -> Ticket:
        """Applies selective updates to a ticket, validating lifecycle transitions."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        updates: Dict[str, Any] = {}

        # If a state transition is requested, validate through WorkflowEngine
        if request.status and request.status != ticket.get("status"):
            self.workflow.transition(
                ticket,
                request.status,
                actor_id=request.actor_id,
                notes=request.reason or f"Status changed to {request.status}"
            )
            updates["status"] = request.status

        if request.priority:
            updates["priority"] = request.priority
        if request.category:
            updates["category"] = request.category
        if request.subcategory:
            updates["subcategory"] = request.subcategory
        if request.tags is not None:
            updates["tags"] = request.tags

        # Update assignment if specified
        if request.assigned_staff_id or request.assigned_department_id:
            self.adapter.assign_ticket(
                ticket_id=ticket_id,
                department_id=request.assigned_department_id,
                staff_id=request.assigned_staff_id,
                assigned_by=request.actor_id,
                reason=request.reason
            )

        if updates:
            self.adapter.update_ticket(ticket_id, updates)

        updated = self.adapter.get_ticket_by_id(ticket_id)
        return Ticket(**updated)

    def assign_ticket(self, ticket_id: str, request: AssignmentRequest) -> Dict[str, Any]:
        """Assigns or reassigns ticket to department or staff with validation and audit tracking."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        success = self.adapter.assign_ticket(
            ticket_id=ticket_id,
            department_id=request.department_id,
            staff_id=request.staff_id,
            assigned_by=request.assigned_by,
            reason=request.reason
        )
        if not success:
            raise ValueError(f"Could not assign ticket {ticket_id}")

        # If currently INGESTED or ROUTED, transition to STAFF_REVIEW
        if ticket.get("status") in [TicketState.INGESTED.value, TicketState.ROUTED.value, TicketState.NEW.value]:
            self.workflow.transition(
                ticket,
                TicketState.STAFF_REVIEW.value,
                actor_id=request.assigned_by,
                notes=f"Assigned for staff review: {request.reason or 'Assigned to staff'}"
            )
            self.adapter.update_ticket(ticket_id, {"status": TicketState.STAFF_REVIEW.value})

        updated = self.adapter.get_ticket_by_id(ticket_id)
        return {
            "ticket_id": ticket_id,
            "department_id": updated.get("assigned_department_id"),
            "department": updated.get("department"),
            "assigned_staff_id": updated.get("assigned_staff_id"),
            "status": updated.get("status"),
            "message": "Ticket successfully assigned."
        }

    def redirect_ticket(self, ticket_id: str, staff_id: str, new_department: str, reason: str) -> RedirectResponse:
        """Redirects ticket to another department, deactivating existing assignments."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        old_dept = ticket.get("department", "Unknown")

        # Execute adapter redirection
        self.adapter.redirect_ticket(
            ticket_id=ticket_id,
            new_department=new_department,
            staff_id=staff_id,
            reason=reason
        )

        # Transition state to STAFF_REVIEW or ROUTED
        target_state = TicketState.STAFF_REVIEW.value if self.workflow.can_transition(ticket.get("status"), TicketState.STAFF_REVIEW.value) else ticket.get("status")
        self.workflow.transition(
            ticket,
            target_state,
            actor_id=staff_id,
            notes=f"Redirected from {old_dept} to {new_department}: {reason}",
            event_type="REDIRECTED"
        )
        self.adapter.update_ticket(ticket_id, {"status": target_state})

        return RedirectResponse(
            ticket_id=ticket_id,
            previous_department=old_dept,
            new_department=new_department,
            status=target_state,
            message=f"Ticket redirected to {new_department}."
        )

    def add_response(self, ticket_id: str, request: RMSResponseCreateRequest) -> RMSResponse:
        """Appends a communication message or internal note to the ticket."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        rsp_dict = self.adapter.add_response(ticket_id, request.model_dump())
        return RMSResponse(**rsp_dict)

    def get_ticket_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological audit events for a ticket."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        return self.adapter.get_audit_history(ticket_id)

    async def analyze_ticket(self, ticket_id: str, override_text: Optional[str] = None) -> AnalyzeResponse:
        raw = self.adapter.get_ticket_by_id(ticket_id)
        if not raw:
            raise ValueError(f"Ticket {ticket_id} not found")

        text_to_analyze = override_text or raw.get("description", "")
        subject = raw.get("subject", raw.get("title", ""))

        # 1. PII Redaction
        redacted_text, _ = self.privacy_redactor.redact(text_to_analyze)

        # 2. AI NLP Triage
        analysis = await self.ai_provider.analyze_ticket(subject, redacted_text)

        # 3. RAG Retrieval
        sources = self.policy_retriever.retrieve(
            query=f"{subject} {redacted_text}",
            department=analysis.suggested_department
        )

        # 4. State transition to ANALYZED if valid
        target_status = TicketState.ANALYZED.value
        if self.workflow.can_transition(raw.get("status"), target_status):
            self.workflow.transition(
                raw,
                target_status,
                actor_id="SYSTEM",
                notes="AI analysis pipeline executed"
            )

        # 5. Update ticket metadata
        self.adapter.update_ticket(ticket_id, {
            "ai_analysis": analysis.model_dump(),
            "confidence": analysis.confidence,
            "status": target_status
        })

        return AnalyzeResponse(
            ticket_id=ticket_id,
            ai_analysis=analysis,
            redacted_description=redacted_text,
            sources=sources
        )

    async def get_draft_response(self, ticket_id: str) -> DraftResponse:
        raw = self.adapter.get_ticket_by_id(ticket_id)
        if not raw:
            raise ValueError(f"Ticket {ticket_id} not found")

        subject = raw.get("subject", raw.get("title", ""))
        description = raw.get("description", "")
        department = raw.get("department", "University")

        # 1. Redact description
        redacted_text, _ = self.privacy_redactor.redact(description)

        # 2. Retrieve sources
        sources = self.policy_retriever.retrieve(
            query=f"{subject} {redacted_text}",
            department=department
        )

        # 3. Generate grounded draft
        draft = await self.ai_provider.generate_draft(
            ticket_subject=subject,
            ticket_description=redacted_text,
            sources=sources,
            department=department
        )
        draft.ticket_id = ticket_id

        # 4. Validate output safety
        is_safe, _ = self.policy_validator.validate_response(draft.draft_response)
        draft.policy_compliance_passed = is_safe
        if not is_safe:
            draft.requires_staff_edit = True

        # 5. Record AI draft response in ticket communication thread (status: DRAFT, not official)
        self.adapter.add_response(ticket_id, {
            "author_id": "SYSTEM_AI",
            "author_name": "Smart RMS AI Assistant",
            "author_role": "AI",
            "response_type": "AI_DRAFT",
            "status": "DRAFT",
            "content": draft.draft_response,
            "is_internal": True
        })

        return draft

    def approve_ticket(self, ticket_id: str, staff_id: str, approved_text: str, notes: Optional[str] = None) -> ApprovalResponse:
        """Staff approval workflow: marks approved and publishes official response."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # Validate transition to APPROVED
        self.workflow.transition(ticket, TicketState.APPROVED.value, actor_id=staff_id, notes=notes)
        self.adapter.post_resolution(ticket_id, approved_text, staff_id)

        resolved_ts = datetime.now(timezone.utc).isoformat()
        return ApprovalResponse(
            ticket_id=ticket_id,
            status=TicketState.APPROVED.value,
            approved_by=staff_id,
            resolved_at=resolved_ts,
            message="Ticket successfully approved by staff and queued for resolution dispatch."
        )

    def escalate_ticket(
        self,
        ticket_id: str,
        staff_id: str,
        target_role: str,
        reason: str,
        urgent: bool = False,
        new_level: str = "LEVEL_1"
    ) -> EscalateResponse:
        """Escalates ticket to Department HOD or higher tier."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # Validate state transition
        self.workflow.transition(ticket, TicketState.ESCALATED.value, actor_id=staff_id, notes=f"Escalated: {reason}")
        
        self.adapter.escalate_ticket(
            ticket_id=ticket_id,
            staff_id=staff_id,
            target_role=target_role,
            reason=reason,
            urgent=urgent,
            new_level=new_level
        )

        return EscalateResponse(
            ticket_id=ticket_id,
            status=TicketState.ESCALATED.value,
            escalated_to=target_role,
            message=f"Ticket escalated to {target_role} for review: {reason}"
        )

    def resolve_ticket(self, ticket_id: str, request: ResolveRequest) -> Ticket:
        """Controlled official resolution of an RMS request."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # Validate transition to RESOLVED
        self.workflow.transition(ticket, TicketState.RESOLVED.value, actor_id=request.staff_id, notes=request.notes)
        self.adapter.resolve_ticket(
            ticket_id=ticket_id,
            staff_id=request.staff_id,
            resolution_text=request.resolution_text,
            notes=request.notes
        )

        updated = self.adapter.get_ticket_by_id(ticket_id)
        return Ticket(**updated)

    def close_ticket(self, ticket_id: str, request: CloseRequest) -> Ticket:
        """Final administrative closure of a resolved RMS request."""
        ticket = self.adapter.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # Validate transition to CLOSED
        self.workflow.transition(ticket, TicketState.CLOSED.value, actor_id=request.staff_id, notes=request.notes)
        self.adapter.close_ticket(
            ticket_id=ticket_id,
            staff_id=request.staff_id,
            notes=request.notes
        )

        updated = self.adapter.get_ticket_by_id(ticket_id)
        return Ticket(**updated)

    def get_analytics_overview(self) -> AnalyticsOverviewResponse:
        tickets = self.adapter.fetch_tickets()
        dept_dist: Dict[str, int] = {}
        prio_dist: Dict[str, int] = {}
        open_count = 0
        approved_count = 0
        escalated_count = 0

        for t in tickets:
            dept = t.get("department", "Other")
            dept_dist[dept] = dept_dist.get(dept, 0) + 1

            prio = t.get("priority", "Medium")
            prio_dist[prio] = prio_dist.get(prio, 0) + 1

            status = t.get("status", "INGESTED")
            if status in ["APPROVED", "RESOLVED", "CLOSED"]:
                approved_count += 1
            elif status == "ESCALATED":
                escalated_count += 1
            else:
                open_count += 1

        return AnalyticsOverviewResponse(
            total_tickets=len(tickets),
            open_tickets=open_count,
            approved_today=approved_count,
            escalated_tickets=escalated_count,
            avg_resolution_time_hours=4.2,
            ai_acceptance_rate=88.5,
            department_distribution=dept_dist,
            priority_distribution=prio_dist
        )

    def get_operations_analytics(self) -> OperationsAnalytics:
        """Returns detailed operational metrics calculated directly from the live dataset."""
        data = self.adapter.get_operations_analytics()
        return OperationsAnalytics(**data)

    def list_departments(self) -> List[Department]:
        depts = self.adapter.list_departments()
        return [Department(**d) for d in depts]

    def get_department(self, department_id: str) -> Optional[Department]:
        d = self.adapter.get_department(department_id)
        return Department(**d) if d else None

    def list_users(self, department_id: Optional[str] = None, role: Optional[str] = None) -> List[StaffUser]:
        users = self.adapter.list_users(department_id=department_id, role=role)
        return [StaffUser(**u) for u in users]

    def get_user(self, user_id: str) -> Optional[StaffUser]:
        u = self.adapter.get_user(user_id)
        return StaffUser(**u) if u else None
