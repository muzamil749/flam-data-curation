# run.py

import sys

from pipeline import CorpusPipeline


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print(
            "Usage: python run.py <input_jsonl> <output_dir>"
        )

        sys.exit(1)

    raw_file = sys.argv[1]
    out_dir = sys.argv[2]

    pipeline = CorpusPipeline(out_dir)

    pipeline.run(raw_file)