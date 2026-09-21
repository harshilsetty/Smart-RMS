from app.privacy.pii_detector import PIIDetector
from app.privacy.pii_redactor import PIIRedactor
from app.privacy.policy_validator import PolicyValidator

def test_pii_detection():
    detector = PIIDetector()
    sample_text = (
        "Hello, my registration number is REG-2023-8492 and my phone is +91-9876543210. "
        "Send email to student.mock@lpu.in regarding transaction TXN-892183921."
    )
    detections = detector.detect(sample_text)
    assert "REG_NO" in detections
    assert "PHONE" in detections
    assert "EMAIL" in detections
    assert "TXN_ID" in detections

def test_pii_redaction():
    redactor = PIIRedactor()
    sample_text = "Please contact me at 9876543210 or email test@lpu.ac.in. Registration: 12204918."
    redacted_text, vault = redactor.redact(sample_text)
    
    assert "9876543210" not in redacted_text
    assert "test@lpu.ac.in" not in redacted_text
    assert "12204918" not in redacted_text
    assert "[REDACTED_PHONE]" in redacted_text
    assert "[REDACTED_EMAIL]" in redacted_text
    assert "[REDACTED_REG_NO]" in redacted_text
    assert len(vault) >= 3

def test_policy_validator():
    validator = PolicyValidator()
    safe_text = "Your maintenance ticket has been registered under Hostel SOP Section 4."
    is_safe, violations = validator.validate_response(safe_text)
    assert is_safe
    assert len(violations) == 0

    unsafe_text = "Do not worry, this is a 100% guaranteed pass for your examination."
    is_safe, violations = validator.validate_response(unsafe_text)
    assert not is_safe
    assert len(violations) > 0
