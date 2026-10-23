# src/manifest.py

import json

def save_manifest(
    output_file,
    stats,
    languages
):

    manifest = {

        "input_docs":
            stats["total"],

        "kept_docs":
            stats["kept"],

        "quality_dropped":
            stats["quality_dropped"],

        "exact_duplicates":
            stats["exact_duplicates"],

        "near_duplicates":
            stats["near_duplicates"],

        "languages":
            languages,

        "near_dedup_threshold":
            0.92
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            manifest,
            f,
            indent=2,
            ensure_ascii=False
        )