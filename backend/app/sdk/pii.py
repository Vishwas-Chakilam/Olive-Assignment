import re

EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    """Redact common PII patterns before storing log previews."""
    text = EMAIL.sub("[EMAIL_REDACTED]", text)
    text = PHONE.sub("[PHONE_REDACTED]", text)
    text = SSN.sub("[SSN_REDACTED]", text)
    return text
