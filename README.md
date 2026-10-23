# Flam Data Curation Assignment

## Overview

This project implements a reproducible data curation pipeline for building a high-quality Hindi and Hinglish corpus.

The pipeline performs:

* Streaming ingestion
* Unicode normalization
* Language detection
* Quality filtering
* PII redaction
* Exact deduplication
* Near-duplicate detection
* Evaluation set generation
* Contamination checking
* Manifest generation
* Audit ledger generation

## Corpus Sources

### Source 1: IndicXParaphrase

* **Dataset:** IndicXParaphrase
* **URL:** https://huggingface.co/datasets/ai4bharat/IndicXParaphrase
* **Target documents:** 4,000

### Source 2: Samanantar

* **Dataset:** Samanantar
* **URL:** https://huggingface.co/datasets/ai4bharat/samanantar
* **Target documents:** 6,000

### Dataset Summary

* **Target raw documents:** 10,000+
* **Languages:** Hindi, Romanized Hindi (Hinglish), and English
* **Language codes:** `hi`, `hi-Latn`, `en`

Actual document counts and language distributions are reported by the pipeline outputs.

## Project Structure

```text
flam-data-curation/
├── download.sh
├── run.sh
├── requirements.txt
├── README.md
├── DECISIONS.md
├── src/
│   ├── run.py
│   ├── pipeline.py
│   ├── utils.py
│   ├── normalize.py
│   ├── lang_detect.py
│   ├── quality_filter.py
│   ├── pii.py
│   ├── dedup.py
│   ├── near_dedup.py
│   ├── ledger.py
│   ├── eval.py
│   ├── contamination.py
│   └── manifest.py
├── eval/
│   └── eval.jsonl
└── sample/
    └── sample_1000.jsonl
```

*The structure above describes the intended project layout. File availability depends on the current implementation.*

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the environment

**Windows — Command Prompt:**

```cmd
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Download Datasets

Run the download script from the project root:

```bash
bash download.sh
```

This script should download and prepare the configured source datasets.

On Windows, use Git Bash or another Bash-compatible environment if Bash is unavailable in Command Prompt.

## Run the Pipeline

Run the pipeline using:

```bash
bash run.sh
```

Alternatively, invoke the Python entry point directly:

```bash
python src/run.py data/raw/input.jsonl output
```

Use the input path and output path expected by your implementation. The example above assumes that the pipeline accepts an input JSONL file and an output directory.

## Processing Steps

### 1. Text Normalization

* Unicode normalization
* Invisible character removal
* Whitespace cleanup

### 2. Language Detection

The pipeline is designed to identify:

* `hi` — Hindi
* `hi-Latn` — Romanized Hindi/Hinglish
* `en` — English
* `other` — Other or unclassified languages

### 3. Quality Filtering

The quality filter is intended to handle:

* Empty records
* Corrupted text
* Invalid content
* Malformed records

### 4. Personally Identifiable Information (PII) Redaction

The pipeline is intended to redact sensitive information using placeholders such as:

| Information    | Placeholder |
| -------------- | ----------- |
| Phone number   | `<PHONE>`   |
| Email address  | `<EMAIL>`   |
| PAN            | `<PAN>`     |
| Aadhaar number | `<AADHAAR>` |

Redaction coverage depends on the implemented detection rules.

### 5. Exact Deduplication

Exact duplicate records are identified using content hashing so that duplicate text can be removed reproducibly.

### 6. Near-Duplicate Detection

Near-duplicate detection is designed to identify highly similar records.

* **Proposed model:** `paraphrase-multilingual-MiniLM-L12-v2`
* **Similarity measure:** Cosine similarity
* **Proposed threshold:** `0.92`

The threshold should be validated against representative Hindi and Hinglish samples.

## Expected Outputs

The pipeline is intended to generate the following outputs:

```text
output/
├── clean/
│   └── data.jsonl
├── ledger.jsonl
├── eval.jsonl
├── contamination.jsonl
└── manifest.json
```

The actual output paths depend on the pipeline configuration.

### 1. `clean/data.jsonl`

Contains the final curated corpus.

Example:

```json
{
  "id": "doc_1",
  "text": "मेरा नाम राहुल है",
  "lang": "hi",
  "source": "IndicXParaphrase"
}
```

### 2. `ledger.jsonl`

Provides a document-level audit trail of processing decisions.

Example:

```json
{
  "id": "doc_12",
  "status": "dropped",
  "stage": "exact_dedup",
  "reason": "exact_duplicate",
  "dup_of": "doc_3"
}
```

The exact fields depend on the ledger schema implemented in the pipeline.

### 3. `eval.jsonl`

Contains records reserved for evaluation and held out from the training corpus.

The target evaluation set size is 200 records, subject to the implemented selection logic and available data.

### 4. `contamination.jsonl`

Records the results of contamination checks between the training corpus and evaluation set.

Example:

```json
{
  "contamination_found": false,
  "matches": 0
}
```

The actual schema depends on the implementation.

### 5. `manifest.json`

Provides a summary of the curated corpus, including:

* Input and output counts
* Language distribution
* Duplicate statistics
* Quality-filtering statistics
* Processing configuration

The manifest should reflect actual pipeline results rather than predefined counts.

## Reproducibility

The pipeline is designed to support reproducible data processing through:

* Consistent normalization and filtering rules
* Deterministic deduplication
* Document-level processing records
* Evaluation-set separation
* Dataset and output statistics

Reproducibility depends on the implementation, dependency versions, configuration, and dataset versions.

## Scalability

Near-duplicate detection can become a computational bottleneck as corpus size increases.

Potential improvements include:

* FAISS for vector similarity search
* Approximate nearest-neighbor search
* Batch processing
* Distributed processing
* Distributed storage

These are potential extensions and should not be considered implemented unless they are present in the source code.

## Assignment Deliverables

The project is intended to include:

* Source code
* `download.sh`
* `run.sh`
* `DECISIONS.md`
* Curated corpus
* `ledger.jsonl`
* `eval.jsonl`
* `contamination.jsonl`
* `manifest.json`
* `sample_1000.jsonl`

Large source datasets are excluded from version control where appropriate.

**Note:** Deliverable availability and successful generation should be verified against the actual repository and pipeline outputs.
