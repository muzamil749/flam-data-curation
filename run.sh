#!/usr/bin/env bash
set -euo pipefail

# Usage: ./run.sh <raw_dir> <out_dir>

if [ "$#" -ne 2 ]; then
    echo "Usage: ./run.sh <raw_dir> <out_dir>"
    echo "Example: ./run.sh data/raw output"
    exit 1
fi

RAW_DIR="$1"
OUT_DIR="$2"

if [ ! -d "$RAW_DIR" ]; then
    echo "Error: Raw data directory does not exist: $RAW_DIR"
    echo "Run ./download.sh first."
    exit 1
fi

if [ ! -f "src/pipeline.py" ]; then
    echo "Error: src/pipeline.py not found."
    echo "Run this script from your project root directory."
    exit 1
fi

mkdir -p "$OUT_DIR"

echo "Starting data curation pipeline..."
echo "Raw data: $RAW_DIR"
echo "Output: $OUT_DIR"

python src/pipeline.py "$RAW_DIR" "$OUT_DIR"

echo "Pipeline finished."

