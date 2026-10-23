# src/pipeline.py

import json
import sys
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

        self.clean_docs = []

    def write_clean(self, row):

        self.clean_file.write(
            json.dumps(
                row,
                ensure_ascii=False
            ) + "\n"
        )

    def process_document(self, row):

        # Validate required fields.
        if not isinstance(row, dict):
            raise ValueError("Record must be a JSON object")

        if "id" not in row or "text" not in row:
            raise ValueError("Record must contain 'id' and 'text'")

        doc_id = row["id"]
        text = row["text"]

        if not isinstance(text, str):
            raise ValueError("'text' must be a string")

        source = row.get("source", "unknown")

        # 1. Normalize text.
        text = normalize_text(text)

        # 2. Detect language.
        lang = detect_language(text)

        # 3. Apply quality checks.
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

        # 4. Redact personally identifiable information.
        text = redact_pii(text)

        # 5. Remove exact duplicates.
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

        # 6. Remove near duplicates.
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

        # 7. Save the cleaned record.
        clean_row = {
            "id": doc_id,
            "text": text,
            "lang": lang,
            "source": source
        }

        self.write_clean(clean_row)
        self.clean_docs.append(clean_row)

        self.stats["kept"] += 1

        self.ledger.write(
            doc_id=doc_id,
            status="kept",
            stage="final"
        )

    def process_file(self, input_file):

        print(f"\nProcessing: {input_file}")

        for row, error in stream_jsonl(input_file):

            self.stats["total"] += 1

            if error:
                self.stats["malformed"] += 1
                continue

            try:
                self.process_document(row)

            except Exception as exc:
                self.ledger.write(
                    doc_id=(
                        row.get("id", "unknown")
                        if isinstance(row, dict)
                        else "unknown"
                    ),
                    status="dropped",
                    stage="exception",
                    reason=str(exc)
                )

    def finalize(self):

        # Close output files before generating reports.
        if not self.clean_file.closed:
            self.clean_file.close()

        self.ledger.close()

        # Generate evaluation dataset.
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

        # Check for contamination between training and evaluation data.
        detect_contamination(
            train_docs,
            eval_docs,
            self.out_dir / "contamination.jsonl"
        )

        # Calculate language statistics.
        language_counts = {}

        for doc in self.clean_docs:
            lang = doc["lang"]

            language_counts[lang] = (
                language_counts.get(lang, 0) + 1
            )

        # Generate dataset manifest.
        save_manifest(
            self.out_dir / "manifest.json",
            self.stats,
            language_counts
        )

        # Display final statistics.
        print("\nPipeline Complete")

        print(json.dumps(self.stats, indent=2))

        print("\nGenerated Files:")

        output_files = [
            self.out_dir / "clean" / "data.jsonl",
            self.out_dir / "ledger.jsonl",
            self.out_dir / "eval.jsonl",
            self.out_dir / "contamination.jsonl",
            self.out_dir / "manifest.json"
        ]

        for output_file in output_files:
            print(output_file)


def main():

    if len(sys.argv) != 3:
        print(
            "Usage: python src/pipeline.py "
            "<raw_dir> <out_dir>"
        )
        sys.exit(1)

    raw_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    if not raw_dir.is_dir():
        print(f"Error: Raw data directory not found: {raw_dir}")
        sys.exit(1)

    input_files = sorted(raw_dir.glob("*.jsonl"))

    if not input_files:
        print(f"Error: No JSONL files found in {raw_dir}")
        sys.exit(1)

    pipeline = CorpusPipeline(out_dir)

    try:
        for input_file in input_files:
            pipeline.process_file(input_file)

        pipeline.finalize()

    except Exception as exc:
        print(f"\nPipeline failed: {exc}")
        sys.exit(1)

    print("\nAll input files processed successfully.")


if __name__ == "__main__":
    main()
