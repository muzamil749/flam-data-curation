import re


PHONE_RE = re.compile(
    r'(?<!\d)(?:\+91[\-\s]?)?[6-9]\d{9}(?!\d)'
)

EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

AADHAAR_RE = re.compile(
    r'(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)'
)

PAN_RE = re.compile(
    r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
)


def redact_pii(text: str) -> str:
    """
    Redact sensitive Indian PII.
    """

    text = EMAIL_RE.sub("<EMAIL>", text)

    text = PHONE_RE.sub("<PHONE>", text)

    text = AADHAAR_RE.sub("<AADHAAR>", text)

    text = PAN_RE.sub("<PAN>", text)

    return text