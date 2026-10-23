# src/contamination.py

import json


def detect_contamination(
    train_docs,
    eval_docs,
    output_file
):

    train_texts = {
        doc["text"]: doc["id"]
        for doc in train_docs
    }

    contamination = []

    for doc in eval_docs:

        text = doc["text"]

        if text in train_texts:

            contamination.append({
                "eval_id": doc["id"],
                "train_ids": [
                    train_texts[text]
                ],
                "method": "exact_match"
            })

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        # No contamination found
        if not contamination:

            f.write(
                json.dumps(
                    {
                        "contamination_found": False,
                        "matches": 0
                    },
                    ensure_ascii=False
                )
                + "\n"
            )

        # Write contamination records
        else:

            for item in contamination:

                f.write(
                    json.dumps(
                        item,
                        ensure_ascii=False
                    )
                    + "\n"
                )

    print(
        f"Contamination check complete. "
        f"Matches found: {len(contamination)}"
    )