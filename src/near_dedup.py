# src/near_dedup.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


NEGATION_WORDS = {
    "नहीं",
    "ना",
    "मत",
    "not",
    "no",
    "never"
}


class NearDeduplicator:
    """
    Semantic near duplicate detector using multilingual embeddings.

    Returns:
        (True, None)      -> keep
        (False, dup_of)   -> drop
    """

    def __init__(self, threshold=0.92):

        self.threshold = threshold

        self.model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        self.embeddings = []
        self.doc_ids = []
        self.texts = []

    def has_negation(self, text):
        """
        Prevent:
            'है'
            'नहीं है'

        from being deduplicated.
        """

        words = set(text.split())

        return any(
            neg_word in words
            for neg_word in NEGATION_WORDS
        )

    def check(
        self,
        doc_id: str,
        text: str
    ):
        """
        Returns:
            keep, dup_of
        """

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        if self.embeddings:

            similarities = cosine_similarity(
                [embedding],
                self.embeddings
            )[0]

            best_idx = np.argmax(
                similarities
            )

            best_score = similarities[
                best_idx
            ]

            candidate_text = self.texts[
                best_idx
            ]

            # ----------------------------------
            # Negation protection
            # ----------------------------------

            current_negation = self.has_negation(
                text
            )

            candidate_negation = self.has_negation(
                candidate_text
            )

            if current_negation != candidate_negation:

                self.embeddings.append(
                    embedding
                )

                self.doc_ids.append(
                    doc_id
                )

                self.texts.append(
                    text
                )

                return True, None

            # ----------------------------------
            # Near duplicate check
            # ----------------------------------

            if best_score >= self.threshold:

                dup_of = self.doc_ids[
                    best_idx
                ]

                return False, dup_of

        self.embeddings.append(
            embedding
        )

        self.doc_ids.append(
            doc_id
        )

        self.texts.append(
            text
        )

        return True, None