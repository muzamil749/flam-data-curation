import re

HTML_RE = re.compile(r"<[^>]+>")

URL_RE = re.compile(
    r"(https?://\S+|www\.\S+)"
)

REPEATED_CHAR_RE = re.compile(
    r"(.)\1{9,}"
)

GARBLED_RE = re.compile(
    r"[�]{2,}"
)


def quality_check(text: str):
    """
    Returns:
        (True, None) -> keep
        (False, reason) -> drop
    """

    if not text:
        return False, "empty"

    text = text.strip()

    # Empty after stripping
    if len(text) == 0:
        return False, "empty"

    # HTML / XML fragments
    if HTML_RE.search(text):
        return False, "markup"

    # Mostly URLs
    if len(URL_RE.findall(text)) > 3:
        return False, "url_spam"

    # Broken encoding
    if GARBLED_RE.search(text):
        return False, "garbled_encoding"

    # Long repeated chars
    if REPEATED_CHAR_RE.search(text):
        return False, "repeated_characters"

    # Too little alphabetic content
    alpha_chars = sum(
        ch.isalpha()
        for ch in text
    )

    ratio = alpha_chars / max(len(text), 1)

    if len(text) > 20 and ratio < 0.10:
        return False, "mostly_symbols"

    return True, None