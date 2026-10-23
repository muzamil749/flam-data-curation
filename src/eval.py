# src/eval.py

import random
import json

def create_eval_set(
    docs,
    output_file,
    size=200
):

    random.seed(42)

    eval_docs = random.sample(
        docs,
        min(size, len(docs))
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        for row in eval_docs:

            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                )
                + "\n"
            )

    return eval_docs