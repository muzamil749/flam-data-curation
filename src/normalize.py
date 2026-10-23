# src/normalize.py

import re
import unicodedata

# Invisible Unicode chars frequently found in web data
INVISIBLE_CHARS = re.compile(
    r'[\u200B\u200C\u200D\u2060\uFEFF]'
)

# Multiple whitespace
MULTI_SPACE = re.compile(r'\s+')


def normalize_text(text: str) -> str:
    """
    Normalize Hindi/Hinglish text for
    comparison, deduplication and storage.
    """

    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Remove invisible chars
    text = INVISIBLE_CHARS.sub("", text)

    # Normalize quotes
    text = (
        text.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
    )

    # Normalize dashes
    text = (
        text.replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
    )

    # Remove unwanted control chars
    text = "".join(
        ch
        for ch in text
        if (
            unicodedata.category(ch)[0] != "C"
            or ch in ("\t", "\n", " ")
        )
    )

    # Collapse whitespace
    text = MULTI_SPACE.sub(" ", text)

    return text.strip()
