from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.nlp.schemas import DepartmentType, DepartmentRoutingResult, IntentType

class BaseDepartmentClassifier(ABC):
    """Abstract interface for Department Routing Classifiers."""

    @abstractmethod
    def route(
        self,
        text: str,
        intent: str,
        entities: Optional[Dict[str, Any]] = None
    ) -> DepartmentRoutingResult:
        """Determines the target department based on text, intent, and entities."""
        pass

class RuleBasedDepartmentRouter(BaseDepartmentClassifier):
    """
    Department routing engine leveraging intent taxonomy, domain entities,
    and contextual vocabulary to route tickets to official university departments.
    """

    # Primary intent to department mapping
    INTENT_TO_DEPT: Dict[str, str] = {
        IntentType.HOSTEL_MAINTENANCE.value: DepartmentType.HOSTEL_AFFAIRS.value,
        IntentType.FEE_PAYMENT.value: DepartmentType.ACCOUNTS_FINANCE.value,
        IntentType.EXAMINATION.value: DepartmentType.EXAMINATION_BRANCH.value,
        IntentType.ACADEMIC.value: DepartmentType.ACADEMIC_AFFAIRS.value,
        IntentType.ATTENDANCE.value: DepartmentType.STUDENT_WELFARE.value,
        IntentType.SCHOLARSHIP.value: DepartmentType.SCHOLARSHIP_SECTION.value,
        IntentType.IT_SUPPORT.value: DepartmentType.IT_SERVICES.value,
        IntentType.STUDENT_SERVICES.value: DepartmentType.ACADEMIC_AFFAIRS.value,
        # Backward-compatible mappings with mock aliases
        "FEE_PAYMENT_RECONCILIATION": DepartmentType.ACCOUNTS_FINANCE.value,
        "FEE_DUPLICATE_PAYMENT_REFUND": DepartmentType.ACCOUNTS_FINANCE.value,
        "GRADE_DISCREPANCY": DepartmentType.ACADEMIC_AFFAIRS.value,
        "ACADEMIC_MARKS_DISCREPANCY": DepartmentType.ACADEMIC_AFFAIRS.value,
        "EXAM_HALL_TICKET_HOLD": DepartmentType.EXAMINATION_BRANCH.value,
        "EXAM_ADMIT_CARD_BLOCKED": DepartmentType.EXAMINATION_BRANCH.value,
        "ATTENDANCE_MEDICAL_CONDONATION": DepartmentType.STUDENT_WELFARE.value,
        "ATTENDANCE_MEDICAL_ADJUSTMENT": DepartmentType.STUDENT_WELFARE.value,
        "SCHOLARSHIP_VERIFICATION": DepartmentType.SCHOLARSHIP_SECTION.value,
        "WIFI_MAC_REGISTRATION": DepartmentType.IT_SERVICES.value,
        "CERTIFICATE_ISSUANCE": DepartmentType.ACADEMIC_AFFAIRS.value
    }

    DEPARTMENT_KEYWORDS: Dict[str, list] = {
        DepartmentType.HOSTEL_AFFAIRS.value: ["warden", "mess", "room", "hostel", "bh", "gh", "geyser"],
        DepartmentType.ACCOUNTS_FINANCE.value: ["finance", "accounts", "tuition", "challan", "bank", "refund", "receipt"],
        DepartmentType.ACADEMIC_AFFAIRS.value: ["academic", "dean", "course", "curriculum", "bonafide", "syllabus", "evaluator"],
        DepartmentType.EXAMINATION_BRANCH.value: ["coe", "exam", "controller", "admit card", "hall ticket", "re-eval"],
        DepartmentType.STUDENT_WELFARE.value: ["dsw", "welfare", "hospital", "medical", "discipline", "condonation"],
        DepartmentType.SCHOLARSHIP_SECTION.value: ["scholarship", "nsp", "freeship", "pms", "state grant"],
        DepartmentType.IT_SERVICES.value: ["helpdesk", "wi-fi", "wifi", "network", "mac address", "ums login"]
    }

    def route(
        self,
        text: str,
        intent: str,
        entities: Optional[Dict[str, Any]] = None
    ) -> DepartmentRoutingResult:
        entities = entities or {}
        lower_text = text.lower()

        # 1. Direct intent overrides for unambiguous domains
        if intent in [IntentType.IT_SUPPORT.value, IntentType.SCHOLARSHIP.value, IntentType.EXAMINATION.value, IntentType.ATTENDANCE.value]:
            dept = self.INTENT_TO_DEPT[intent]
            return DepartmentRoutingResult(
                department=dept,
                confidence=0.95,
                reason=f"Direct domain routing for {intent} request."
            )

        # 2. Check strong entity cues for residential issues
        if ("hostel_block" in entities or "room_number" in entities) and intent in [IntentType.HOSTEL_MAINTENANCE.value, IntentType.GENERAL_INQUIRY.value]:
            return DepartmentRoutingResult(
                department=DepartmentType.HOSTEL_AFFAIRS.value,
                confidence=0.96,
                reason="Direct residential entity matched (Hostel Block / Room Number)."
            )

        if "portal_type" in entities:
            portal = str(entities["portal_type"]).lower()
            if "nsp" in portal or "scholarship" in portal:
                return DepartmentRoutingResult(
                    department=DepartmentType.SCHOLARSHIP_SECTION.value,
                    confidence=0.95,
                    reason="Entity refers to National Scholarship Portal (NSP)."
                )
            if "wifi" in portal or "fortinet" in portal:
                return DepartmentRoutingResult(
                    department=DepartmentType.IT_SERVICES.value,
                    confidence=0.95,
                    reason="Entity refers to Campus Wi-Fi Fortinet Network portal."
                )

        # 2. Check intent-based mapping
        if intent in self.INTENT_TO_DEPT:
            dept = self.INTENT_TO_DEPT[intent]
            # Contextual keyword validation for confidence adjustment
            dept_kws = self.DEPARTMENT_KEYWORDS.get(dept, [])
            kw_hits = sum(1 for kw in dept_kws if kw in lower_text)
            confidence = 0.92 if kw_hits > 0 else 0.88

            return DepartmentRoutingResult(
                department=dept,
                confidence=confidence,
                reason=f"Matched to {dept} via classified intent '{intent}'."
            )

        # 3. Fallback to keyword scanning
        best_dept = DepartmentType.ACADEMIC_AFFAIRS.value
        best_hits = 0
        for dept, kws in self.DEPARTMENT_KEYWORDS.items():
            hits = sum(1 for kw in kws if kw in lower_text)
            if hits > best_hits:
                best_hits = hits
                best_dept = dept

        if best_hits > 0:
            return DepartmentRoutingResult(
                department=best_dept,
                confidence=0.75,
                reason=f"Contextual keyword correlation routed to {best_dept}."
            )

        return DepartmentRoutingResult(
            department=DepartmentType.ACADEMIC_AFFAIRS.value,
            confidence=0.55,
            reason="Default routing applied; no unambiguous departmental signals found."
        )
