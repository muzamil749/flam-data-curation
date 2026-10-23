# src/ledger.py

import json
from pathlib import Path


class LedgerWriter:
    """
    Tracks every document through the pipeline.
    """

    def __init__(self, output_path):
        self.output_path = Path(output_path)

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file = open(
            self.output_path,
            "w",
            encoding="utf-8"
        )

    def write(
        self,
        doc_id,
        status,
        stage,
        reason="",
        dup_of=""
    ):
        row = {
            "id": doc_id,
            "status": status,
            "stage": stage,
            "reason": reason,
            "dup_of": dup_of,
        }

        self.file.write(
            json.dumps(
                row,
                ensure_ascii=False
            )
            + "\n"
        )

    def close(self):
        self.file.close()