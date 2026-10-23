# src/utils.py

import json
import gzip
from pathlib import Path


def stream_jsonl(file_path):
    """
    Stream JSONL records one at a time.

    Returns:
        (record, None) on success
        (None, error_message) on failure
    """

    with open(file_path, "r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            try:
                yield json.loads(line), None

            except Exception as e:

                yield None, (
                    f"line_{line_number}: "
                    f"{type(e).__name__}"
                )


def write_jsonl(path, row):
    """
    Append a JSON record.
    """

    with open(path, "a", encoding="utf-8") as f:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False
            )
            + "\n"
        )


def write_jsonl_gz(path, row):
    """
    Append a compressed JSONL record.
    """

    with gzip.open(
        path,
        "at",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False
            )
            + "\n"
        )


def ensure_dir(path):
    """
    Create directory if missing.
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )


def count_jsonl(path):
    """
    Count rows in a JSONL file.
    """

    count = 0

    with open(path, "r", encoding="utf-8") as f:

        for _ in f:
            count += 1

    return count