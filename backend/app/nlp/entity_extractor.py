import re
from typing import Dict, Any, List, Optional
from app.nlp.preprocessing import clean_text

class EntityExtractor:
    """
    Extracts university domain entities from RMS request text.
    Operates safely on both raw and PII-redacted text.
    """

    PATTERNS = {
        "course_code": r"\b(?!(?:ROOM|FLAT|TERM|YEAR|SECS|SEPT|POST)\b)([A-Z]{2,4}\s?[\-_]?\s?\d{3})\b",
        "hostel_block": r"\b(BH[\-\s]?[0-9]{1,2}|GH[\-\s]?[0-9]{1,2}|Boys Hostel[\-\s]?[0-9]{1,2}|Girls Hostel[\-\s]?[0-9]{1,2})\b",
        "room_number": r"\b(?:Room|Rm|Flat|Cabin)[\s\-\#]*([0-9]{2,4}[A-Z]?)\b",
        "currency_amount": r"\b(?:INR|Rs\.?|₹)\s?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+)\b",
        "bank_name": r"\b(HDFC(?:\sBank)?|SBI|State Bank of India|ICICI(?:\sBank)?|Axis(?:\sBank)?|PNB|Punjab National Bank|Canara Bank)\b",
        "portal_type": r"\b(NSP|National Scholarship Portal|UMS(?:\sPortal)?|Fortinet(?:\sWi[\-\s]?Fi)?|Payment Gateway|Grade Management System)\b",
        "certificate_type": r"\b(Bonafide(?:\sCertificate)?|Medium of Instruction(?:\sLetter)?|MOI|Migration(?:\sCertificate)?|Character(?:\sCertificate)?)\b",
        "date_reference": r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{4})?)\b",
        "time_window": r"\b(\d{1,2}\s*(?:hours?|hrs?|days?|weeks?))\b"
    }

    ISSUE_KEYWORDS = {
        "Water Leakage": ["leak", "leaking", "water drip", "pipe burst", "seepage"],
        "Appliance Malfunction": ["ac unit", "air conditioner", "fan", "geyser", "refrigerator", "cooler"],
        "Duplicate Payment": ["deducted twice", "double payment", "debited twice", "duplicate debit", "transaction timeout"],
        "Marks Discrepancy": ["marks discrepancy", "rubric", "ca marks", "continuous assessment", "grade error", "ca-1", "ca-2", "ca-3"],
        "Admit Card Hold": ["admit card blocked", "hall ticket", "clearance hold", "library hold", "blocked from exam"],
        "Medical Condonation": ["medical leave", "hospitalization", "dengue", "severe illness", "discharge summary", "attendance drop"],
        "Scholarship Delay": ["scholarship pending", "institute verification", "nsp verification", "post-matric"],
        "Network Connectivity": ["wi-fi", "mac address", "radius", "device limit", "registration failure"]
    }

    def extract(self, text: str) -> Dict[str, Any]:
        """Extracts domain entities and returns a structured dictionary."""
        cleaned = clean_text(text)
        entities: Dict[str, Any] = {}

        # Regex-based pattern extractions
        for key, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                # Deduplicate while preserving order
                unique_matches = list(dict.fromkeys([m.strip() for m in matches if m.strip()]))
                if len(unique_matches) == 1:
                    entities[key] = unique_matches[0]
                elif len(unique_matches) > 1:
                    entities[key] = unique_matches

        # Normalize hostel block representation
        if "hostel_block" in entities:
            raw_hb = entities["hostel_block"]
            if isinstance(raw_hb, list):
                raw_hb = raw_hb[0]
            norm_hb = re.sub(r"Boys Hostel[\-\s]?", "BH-", raw_hb, flags=re.IGNORECASE)
            norm_hb = re.sub(r"Girls Hostel[\-\s]?", "GH-", norm_hb, flags=re.IGNORECASE)
            norm_hb = norm_hb.replace(" ", "-").upper()
            entities["hostel_block"] = norm_hb

        # Detect primary issue types
        lower = cleaned.lower()
        detected_issues = []
        for issue_name, kws in self.ISSUE_KEYWORDS.items():
            for kw in kws:
                if kw in lower:
                    detected_issues.append(issue_name)
                    break
        if detected_issues:
            entities["detected_issues"] = detected_issues if len(detected_issues) > 1 else detected_issues[0]

        return entities
