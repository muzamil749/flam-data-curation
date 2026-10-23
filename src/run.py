# run.py

import sys
from pathlib import Path

from pipeline import CorpusPipeline


def main():

    if len(sys.argv) != 3:
        print("Usage: python run.py <input_jsonl> <output_dir>")
        sys.exit(1)

    raw_file = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    if not raw_file.is_file():
        print(f"Error: Input JSONL file not found: {raw_file}")
        sys.exit(1)

    pipeline = CorpusPipeline(out_dir)

    try:
        pipeline.process_file(raw_file)
        pipeline.finalize()

    except Exception as exc:
        print(f"Pipeline failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
