import json
import re
import unicodedata
from pathlib import Path

from datasets import load_dataset
from aksharamukha import transliterate


# =====================================================
# CONFIGURATION
# =====================================================

OUTPUT_FILE = Path("samanantar_hindi_10000.jsonl")
TEMP_FILE = Path("samanantar_hindi_10000.tmp")

HINDI_COUNT = 9000
HINGLISH_COUNT = 1000
TOTAL_COUNT = HINDI_COUNT + HINGLISH_COUNT

SOURCE_NAME = "Samanantar"


# =====================================================
# HINDI TO READABLE ROMAN HINDI
# =====================================================

def to_hinglish(hindi_text):
    """
    Convert Devanagari Hindi into readable Roman Hindi.

    This uses transliteration, not English translation.
    """

    if not hindi_text:
        return ""

    # Convert Devanagari to IAST transliteration.
    text = transliterate.process(
        "Devanagari",
        "IAST",
        hindi_text
    )

    # Normalize Unicode characters.
    text = unicodedata.normalize("NFC", text)

    # Convert scholarly transliteration into simpler spellings.
    replacements = [
        ("ā", "a"),
        ("ī", "i"),
        ("ū", "u"),
        ("ē", "e"),
        ("ō", "o"),
        ("ṛ", "ri"),
        ("ṝ", "ri"),
        ("ḷ", "li"),
        ("ṅ", "n"),
        ("ñ", "n"),
        ("ṭ", "t"),
        ("ḍ", "d"),
        ("ṇ", "n"),
        ("ś", "sh"),
        ("ṣ", "sh"),
        ("ṃ", "n"),
        ("ṁ", "n"),
        ("ḥ", "h"),
        ("ʼ", ""),
        ("'", ""),
        ("’", ""),
        ("-", " "),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Remove any remaining combining diacritical marks.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    # Remove unwanted formatting characters.
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =====================================================
# VALIDATE RECORDS
# =====================================================

def validate_record(record):
    """Check that every record follows the required schema."""

    return (
        set(record.keys()) == {"id", "text", "source"}
        and isinstance(record["id"], str)
        and isinstance(record["text"], str)
        and isinstance(record["source"], str)
        and bool(record["text"].strip())
    )


# =====================================================
# MAIN DATASET CONVERSION
# =====================================================

def main():

    print("=" * 60)
    print("SAMANANTAR DATASET CURATION")
    print("=" * 60)

    print("\nLoading Hindi dataset...")

    # Load the original dataset from Hugging Face.
    # Cached files will be reused where possible.
    dataset = load_dataset(
        "ai4bharat/samanantar",
        "hi",
        split=f"train[:{TOTAL_COUNT}]"
    )

    print(f"Rows retrieved: {len(dataset)}")

    # Keep only non-empty Hindi target sentences.
    hindi_texts = []

    for row in dataset:
        text = row.get("tgt")

        if isinstance(text, str) and text.strip():
            hindi_texts.append(text.strip())

    # Ensure that enough source records are available.
    if len(hindi_texts) < TOTAL_COUNT:
        raise ValueError(
            f"Expected {TOTAL_COUNT} valid Hindi sentences, "
            f"but found {len(hindi_texts)}."
        )

    records = []

    # -------------------------------------------------
    # PART 1: 9,000 HINDI RECORDS
    # -------------------------------------------------

    print("\nPreparing 9,000 Hindi records...")

    for i in range(HINDI_COUNT):

        record = {
            "id": f"doc_{i}",
            "text": hindi_texts[i],
            "source": SOURCE_NAME
        }

        if not validate_record(record):
            raise ValueError(
                f"Invalid Hindi record at index {i}"
            )

        records.append(record)

    # -------------------------------------------------
    # PART 2: 1,000 ROMANIZED HINDI RECORDS
    # -------------------------------------------------

    print("Preparing 1,000 Hinglish records...")

    for i in range(HINGLISH_COUNT):

        source_index = HINDI_COUNT + i
        record_id = HINDI_COUNT + i

        original_hindi = hindi_texts[source_index]

        hinglish_text = to_hinglish(original_hindi)

        record = {
            "id": f"doc_{record_id}",
            "text": hinglish_text,
            "source": SOURCE_NAME
        }

        if not validate_record(record):
            raise ValueError(
                f"Invalid Hinglish record at index {record_id}"
            )

        records.append(record)

        # Display progress every 100 records.
        if (i + 1) % 100 == 0:
            print(
                f"Converted {i + 1}/{HINGLISH_COUNT} "
                "Hinglish records"
            )

    # -------------------------------------------------
    # PART 3: WRITE A SINGLE JSONL FILE
    # -------------------------------------------------

    print("\nWriting the complete dataset...")

    try:
        with TEMP_FILE.open(
            "w",
            encoding="utf-8",
            newline="\n"
        ) as file:

            for record in records:
                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

        # Verify the temporary file before replacing the output.
        with TEMP_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            saved_records = [
                json.loads(line)
                for line in file
                if line.strip()
            ]

        if len(saved_records) != TOTAL_COUNT:
            raise ValueError(
                f"Expected {TOTAL_COUNT} records, "
                f"found {len(saved_records)}."
            )

        # Verify the record IDs and structure.
        for i, record in enumerate(saved_records):

            if record["id"] != f"doc_{i}":
                raise ValueError(
                    f"Incorrect ID at record {i}"
                )

            if not validate_record(record):
                raise ValueError(
                    f"Invalid schema at record {i}"
                )

        # Replace the previous output only after validation.
        TEMP_FILE.replace(OUTPUT_FILE)

    except Exception:
        if TEMP_FILE.exists():
            TEMP_FILE.unlink()
        raise

    # -------------------------------------------------
    # PART 4: FINAL REPORT
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("DATASET CONVERSION COMPLETED")
    print("=" * 60)

    print(f"Output file: {OUTPUT_FILE.resolve()}")
    print(f"Total records: {len(saved_records)}")
    print(f"Hindi records: {HINDI_COUNT}")
    print(f"Hinglish records: {HINGLISH_COUNT}")
    print(
        f"File size: "
        f"{OUTPUT_FILE.stat().st_size / 1024:.2f} KB"
    )

    print("\nFirst 3 Hindi records:")

    for record in saved_records[:3]:
        print(
            json.dumps(record, ensure_ascii=False)
        )

    print("\nFirst 3 Hinglish records:")

    for record in saved_records[
        HINDI_COUNT:HINDI_COUNT + 3
    ]:
        print(
            json.dumps(record, ensure_ascii=False)
        )

    print("\nLast record:")

    print(
        json.dumps(saved_records[-1], ensure_ascii=False)
    )

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()