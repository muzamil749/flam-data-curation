#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./download.sh <dataset_url> <filename> <source_name> <license>

if [ "$#" -ne 4 ]; then
    echo "Usage: ./download.sh <dataset_url> <filename> <source_name> <license>"
    echo 'Example: ./download.sh "https://example.org/data.jsonl.gz" "data.jsonl.gz" "Example Dataset" "CC-BY-4.0"'
    exit 1
fi

URL="$1"
FILENAME="$2"
SOURCE_NAME="$3"
LICENSE="$4"

RAW_DIR="data/raw"
mkdir -p "$RAW_DIR"

DEST="$RAW_DIR/$FILENAME"
TEMP="$DEST.part"

echo "Downloading: $SOURCE_NAME"

# Download to a temporary file so incomplete downloads are not treated as complete.
curl --fail --location --retry 3 --output "$TEMP" "$URL"
mv "$TEMP" "$DEST"

# Record provenance. Python handles CSV escaping safely.
python - "$URL" "$FILENAME" "$SOURCE_NAME" "$LICENSE" <<'PY'
import csv
import os
import sys
from datetime import date

url, filename, source_name, license_name = sys.argv[1:]
manifest = "sources.csv"
exists = os.path.exists(manifest) and os.path.getsize(manifest) > 0

with open(manifest, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not exists:
        writer.writerow([
            "source_name",
            "url",
            "license",
            "download_date",
            "filename"
        ])
    writer.writerow([
        source_name,
        url,
        license_name,
        date.today().isoformat(),
        filename
    ])

print(f"Recorded source information in {manifest}")
PY

echo "Download complete: $DEST"
