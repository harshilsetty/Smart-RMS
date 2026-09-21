import re
from typing import Tuple, Dict
from app.privacy.pii_detector import PIIDetector

class PIIRedactor:
    """Masks or replaces detected PII tokens in text before LLM or Vector store consumption."""

    def __init__(self):
        self.detector = PIIDetector()

    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redacts sensitive PII from text.
        Returns:
            - redacted_text: string with masked tokens.
            - vault_map: mapping of masked token to original value for session preservation.
        """
        redacted = text
        vault: Dict[str, str] = {}
        counter = 1

        token_tags = {
            "PHONE": "REDACTED_PHONE",
            "REG_NO": "REDACTED_REG_NO",
            "EMAIL": "REDACTED_EMAIL",
            "TXN_ID": "REDACTED_TXN_ID",
            "AADHAAR_MOCK": "REDACTED_ID",
            "MAC_ADDRESS": "REDACTED_MAC"
        }

        detections = self.detector.detect(text)
        for pii_type, matches in detections.items():
            tag_name = token_tags.get(pii_type, "REDACTED_PII")
            for match in matches:
                mask = f"[{tag_name}]"
                redacted = redacted.replace(match, mask)
                vault[f"{tag_name}_{counter}"] = match
                counter += 1

        return redacted, vault
