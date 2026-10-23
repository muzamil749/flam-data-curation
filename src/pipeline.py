# src/pipeline.py

import json
from pathlib import Path

from normalize import normalize_text
from lang_detect import detect_language
from quality_filter import quality_check
from pii import redact_pii
from dedup import ExactDeduplicator
from near_dedup import NearDeduplicator
from ledger import LedgerWriter
from utils import stream_jsonl

from eval import create_eval_set
from contamination import detect_contamination
from manifest import save_manifest


class CorpusPipeline:

    def __init__(self, out_dir):

        self.out_dir = Path(out_dir)

        (self.out_dir / "clean").mkdir(
            parents=True,
            exist_ok=True
        )

        self.clean_file = open(
            self.out_dir / "clean" / "data.jsonl",
            "w",
            encoding="utf-8"
        )

        self.ledger = LedgerWriter(
            self.out_dir / "ledger.jsonl"
        )

        self.exact_dedup = ExactDeduplicator()

        self.near_dedup = NearDeduplicator(
            threshold=0.92
        )

        self.stats = {
            "total": 0,
            "kept": 0,
            "malformed": 0,
            "quality_dropped": 0,
            "exact_duplicates": 0,
            "near_duplicates": 0,
        }

        # Store kept documents for eval/manifest generation
        self.clean_docs = []

    def write_clean(self, row):

        self.clean_file.write(
            json.dumps(
                row,
                ensure_ascii=False
            )
            + "\n"
        )

    def process_document(self, row):

        doc_id = row["id"]

        text = row["text"]

        source = row.get(
            "source",
            "unknown"
        )

        # ----------------------------------
        # Normalization
        # ----------------------------------

        text = normalize_text(text)

        # ----------------------------------
        # Language Detection
        # ----------------------------------

        lang = detect_language(text)

        # ----------------------------------
        # Quality Filter
        # ----------------------------------

        keep, reason = quality_check(text)

        if not keep:

            self.stats["quality_dropped"] += 1

            self.ledger.write(
                doc_id=doc_id,
                status="dropped",
                stage="quality_filter",
                reason=reason
            )

            return

        # ----------------------------------
        # PII Redaction
        # ----------------------------------

        text = redact_pii(text)

        # ----------------------------------
        # Exact Dedup
        # ----------------------------------

        keep, dup_of = self.exact_dedup.check(
            doc_id,
            text
        )

        if not keep:

            self.stats["exact_duplicates"] += 1

            self.ledger.write(
                doc_id=doc_id,
                status="dropped",
                stage="exact_dedup",
                reason="exact_duplicate",
                dup_of=dup_of
            )

            return

        # ----------------------------------
        # Near Dedup
        # ----------------------------------

        keep, dup_of = self.near_dedup.check(
            doc_id,
            text
        )

        if not keep:

            self.stats["near_duplicates"] += 1

            self.ledger.write(
                doc_id=doc_id,
                status="dropped",
                stage="near_dedup",
                reason="near_duplicate",
                dup_of=dup_of
            )

            return

        # ----------------------------------
        # Final Output
        # ----------------------------------

        clean_row = {
            "id": doc_id,
            "text": text,
            "lang": lang,
            "source": source
        }

        self.write_clean(clean_row)

        self.clean_docs.append(
            clean_row
        )

        self.stats["kept"] += 1

        self.ledger.write(
            doc_id=doc_id,
            status="kept",
            stage="final"
        )

    def run(self, input_file):

        for row, error in stream_jsonl(
            input_file
        ):

            self.stats["total"] += 1

            if error:

                self.stats["malformed"] += 1

                continue

            try:

                self.process_document(row)

            except Exception as e:

                self.ledger.write(
                    doc_id=row.get(
                        "id",
                        "unknown"
                    ),
                    status="dropped",
                    stage="exception",
                    reason=str(e)
                )

        # ----------------------------------
        # Close files first
        # ----------------------------------

        self.clean_file.close()
        self.ledger.close()

        # ----------------------------------
        # Eval Set Generation
        # ----------------------------------

        eval_docs = create_eval_set(
            self.clean_docs,
            self.out_dir / "eval.jsonl"
        )

        eval_ids = {
            doc["id"]
            for doc in eval_docs
        }

        train_docs = [
            doc
            for doc in self.clean_docs
            if doc["id"] not in eval_ids
        ]

        # ----------------------------------
        # Contamination Check
        # ----------------------------------

        detect_contamination(
            train_docs,
            eval_docs,
            self.out_dir / "contamination.jsonl"
        )

        # ----------------------------------
        # Language Statistics
        # ----------------------------------

        language_counts = {}

        for doc in self.clean_docs:

            lang = doc["lang"]

            language_counts[lang] = (
                language_counts.get(
                    lang,
                    0
                )
                + 1
            )

        # ----------------------------------
        # Manifest
        # ----------------------------------

        save_manifest(
            self.out_dir / "manifest.json",
            self.stats,
            language_counts
        )

        print("\nPipeline Complete")

        print(
            json.dumps(
                self.stats,
                indent=2
            )
        )

        print("\nGenerated Files:")

        print(
            self.out_dir / "clean" / "data.jsonl"
        )

        print(
            self.out_dir / "ledger.jsonl"
        )

        print(
            self.out_dir / "eval.jsonl"
        )

        print(
            self.out_dir / "contamination.jsonl"
        )

        print(
            self.out_dir / "manifest.json"
        )