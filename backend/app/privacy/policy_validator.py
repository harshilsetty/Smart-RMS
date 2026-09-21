from typing import List, Tuple

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
