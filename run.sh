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

# Verify the raw data directory exists.
if [ ! -d "$RAW_DIR" ]; then
    echo "Error: Raw data directory does not exist: $RAW_DIR"
    echo "Please download or place your dataset in this directory."
    exit 1
fi

# Verify that the pipeline exists.
if [ ! -f "src/pipeline.py" ]; then
    echo "Error: src/pipeline.py not found."
    echo "Run this script from your project root directory."
    exit 1
fi

# Verify Python is available.
if ! command -v python >/dev/null 2>&1; then
    echo "Error: Python is not installed or is not available in PATH."
    exit 1
fi

# Ensure the raw directory contains at least one file.
if ! find "$RAW_DIR" -maxdepth 1 -type f -print -quit | grep -q .; then
    echo "Error: No dataset files found in $RAW_DIR"
    exit 1
fi

# Create the output directory.
mkdir -p "$OUT_DIR"

echo "========================================"
echo "Starting Data Curation Pipeline"
echo "========================================"
echo "Raw data: $RAW_DIR"
echo "Output:   $OUT_DIR"
echo "========================================"

# Execute the pipeline.
python src/pipeline.py "$RAW_DIR" "$OUT_DIR"

echo "========================================"
echo "Pipeline finished successfully."
echo "Check the output directory: $OUT_DIR"
echo "========================================"
