from typing import List, Tuple, Any

class PolicyValidator:
    """Validates that generated or suggested response text conforms to university communication policies."""

    FORBIDDEN_PROMISES = [
        "100% guaranteed pass",
        "waive all fees completely without approval",
        "immediate automatic degree award",
        "unconditional attendance 100% without documentation",
        "bypassing university disciplinary committee"
    ]

    def validate_response(self, text: str) -> Tuple[bool, List[str]]:
        """
        Ensures response does not contain unsafe autonomous commitments or banned phrasing.
        Returns (is_valid, violation_reasons).
        """
        violations = []
        lower_text = text.lower()
        for forbidden in self.FORBIDDEN_PROMISES:
            if forbidden in lower_text:
                violations.append(f"Forbidden commitment detected: '{forbidden}'")

        return len(violations) == 0, violations

    def validate_source(self, source: Any) -> Tuple[bool, List[str]]:
        """
        Validates an authoritative policy source before it is used in response generation.
        Checks:
        - Source exists
        - Source is approved
        - Excerpt is non-empty
        - Document ID is well-formed
        """
        reasons = []
        if not source:
            return False, ["Source is empty or null"]

        # Support both RAGSource object and dict
        doc_id = getattr(source, "document_id", None) or (source.get("document_id") if isinstance(source, dict) else None)
        excerpt = getattr(source, "excerpt", None) or (source.get("excerpt") if isinstance(source, dict) else None)
        status = getattr(source, "approval_status", None) or (source.get("approval_status") if isinstance(source, dict) else "APPROVED")

        if not doc_id:
            reasons.append("Missing document_id in policy source")
        if not excerpt or not excerpt.strip():
            reasons.append("Empty policy excerpt in source")
        if status and status != "APPROVED":
            reasons.append(f"Policy status '{status}' is not approved")

        return len(reasons) == 0, reasons


