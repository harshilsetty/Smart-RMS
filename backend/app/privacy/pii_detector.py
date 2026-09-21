import re
from typing import List, Dict, Any

class PIIDetector:
    """Detects student personally identifiable information (PII) using regex patterns and heuristics."""

    PATTERNS = {
        "PHONE": r"(?:\+?91[\-\s]?)?[6-9]\d{9}",
        "REG_NO": r"(?:REG[\-\s]?(?:202\d)[\-\s]?\d{4}|\b122\d{5}\b|\b121\d{5}\b|\b120\d{5}\b)",
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "TXN_ID": r"\bTXN[\-\_]\d{6,12}\b",
        "AADHAAR_MOCK": r"\b\d{4}[\-\s]\d{4}[\-\s]\d{4}\b|\bXXXX[\-\s]XXXX[\-\s]\d{4}\b",
        "MAC_ADDRESS": r"(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})"
    }

    def detect(self, text: str) -> Dict[str, List[str]]:
        """Scans input text and returns a dictionary of detected PII entity types and their raw matches."""
        results: Dict[str, List[str]] = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                results[pii_type] = list(set(matches))
        return results

    def get_detected_tokens(self, text: str) -> List[str]:
        """Returns a list of human-readable redacted token types detected (e.g. ['[REDACTED_PHONE]'])."""
        tokens = []
        detection = self.detect(text)
        token_map = {
            "PHONE": "[REDACTED_PHONE]",
            "REG_NO": "[REDACTED_REG_NO]",
            "EMAIL": "[REDACTED_EMAIL]",
            "TXN_ID": "[REDACTED_TXN_ID]",
            "AADHAAR_MOCK": "[REDACTED_ID]",
            "MAC_ADDRESS": "[REDACTED_MAC]"
        }
        for k in detection:
            if k in token_map:
                tokens.append(token_map[k])
        return sorted(tokens)
