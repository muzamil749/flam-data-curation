# src/dedup.py

import hashlib


def compute_hash(text: str) -> str:
    """
    Generate a deterministic hash for normalized text.
    """
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


class ExactDeduplicator:
    """
    Exact duplicate detector using text hashes.

    Example:
        deduper = ExactDeduplicator()

        keep, dup_of = deduper.check(
            doc_id="doc_1",
            text="मेरा नाम राहुल है"
        )
    """

    def __init__(self):
        self.seen = {}

    def check(self, doc_id: str, text: str):
        """
        Returns:
            (True, None)       -> document should be kept
            (False, first_id)  -> document is duplicate

        Args:
            doc_id: Current document ID
            text: Normalized text
        """

        text_hash = compute_hash(text)

        if text_hash in self.seen:
            return False, self.seen[text_hash]

        self.seen[text_hash] = doc_id

        return True, None

    def total_unique(self):
        """
        Number of unique documents seen so far.
        """
        return len(self.seen)