#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./download.sh <dataset_url> <filename> <source_name> <license>

if [ "$#" -ne 4 ]; then
    echo "Usage: ./download.sh <dataset_url> <filename> <source_name> <license>"
    echo 'Example: ./download.sh "https://example.org/data.jsonl" "data.jsonl" "Example Dataset" "CC-BY-4.0"'
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

# Remove any leftover incomplete download.
rm -f "$TEMP"

echo "Downloading: $SOURCE_NAME"

# Download the dataset safely.
if ! curl --fail --location --retry 3 --output "$TEMP" "$URL"; then
    rm -f "$TEMP"
    echo "Error: Dataset download failed."
    exit 1
fi

# Ensure the downloaded file is not empty.
if [ ! -s "$TEMP" ]; then
    rm -f "$TEMP"
    echo "Error: Downloaded file is empty."
    exit 1
fi

# Save the completed download.
mv "$TEMP" "$DEST"

# Record dataset provenance in sources.csv.
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

print(f"Source information recorded in {manifest}")
PY

echo "Download complete: $DEST"
echo "File size: $(wc -c < "$DEST") bytes"
