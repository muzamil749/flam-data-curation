Flam Data Curation Assignment
Overview
This project implements a reproducible data curation pipeline for building a high-quality Hindi and Hinglish corpus.

The pipeline performs:

Streaming ingestion
Unicode normalization
Language detection
Quality filtering
PII redaction
Exact deduplication
Near-duplicate detection
Eval set generation
Contamination checking
Manifest generation
Ledger generation
Corpus Sources
Source 1
Dataset: IndicXParaphrase
URL: https://huggingface.co/datasets/ai4bharat/IndicXParaphrase
Documents: 4,000
Source 2
Dataset: Samanantar
URL: https://huggingface.co/datasets/ai4bharat/samanantar
Documents: 6,000
Total
Raw Documents: 10,000+
Languages:

Hindi (hi)
Hinglish / Roman Hindi (hi-Latn)
English (en)
Project Structure
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

├── sample/
│   └── sample_1000.jsonl
Installation
Create a virtual environment:

python -m venv venv
Activate it:

Windows
venv\Scripts\activate
Linux / macOS
source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Download Datasets
bash download.sh
This downloads and prepares the source datasets.

Run Pipeline
bash run.sh
or

python src/run.py data/raw/input.jsonl output
Processing Steps
1. Normalization
Unicode normalization
Invisible character removal
Whitespace cleanup
2. Language Detection
Outputs:

hi
hi-Latn
en
other
3. Quality Filtering
Removes:

Empty records
Corrupted text
Invalid content
Malformed records
4. PII Redaction
Replaces:

Phone Number  -> <PHONE>
Email         -> <EMAIL>
PAN           -> <PAN>
Aadhaar       -> <AADHAAR>
5. Exact Deduplication
Hash-based duplicate removal.

6. Near-Duplicate Detection
Model:

paraphrase-multilingual-MiniLM-L12-v2
Similarity:

Cosine Similarity
Threshold:

0.92
Outputs
The pipeline automatically generates:

output/

├── clean/
│   └── data.jsonl

├── ledger.jsonl

├── eval.jsonl

├── contamination.jsonl

├── manifest.json
Output Descriptions
clean/data.jsonl
Final curated corpus.

Example:

{
  "id": "doc_1",
  "text": "मेरा नाम राहुल है",
  "lang": "hi",
  "source": "IndicXParaphrase"
}
ledger.jsonl
Document-level audit trail.

Example:

{
  "id":"doc_12",
  "status":"dropped",
  "stage":"exact_dedup",
  "reason":"exact_duplicate",
  "dup_of":"doc_3"
}
eval.jsonl
Held-out evaluation set.

Automatically generated
200 documents
Removed from training corpus
contamination.jsonl
Checks for train/eval leakage.

Example:

{
  "contamination_found": false,
  "matches": 0
}
manifest.json
Corpus summary.

Contains:

Input counts
Output counts
Language distribution
Duplicate counts
Quality filter statistics
Reproducibility
All outputs are generated automatically using:

bash run.sh
No manual intervention is required.

The pipeline is deterministic and reproducible.

Scalability
Current bottleneck:

Near-Duplicate Detection
For larger corpora (TB scale), this can be extended using:

FAISS
Approximate Nearest Neighbor Search
Distributed Processing
Distributed Storage
Assignment Deliverables
Included:

Source code
download.sh
run.sh
DECISIONS.md
eval.jsonl
sample_1000.jsonl
contamination.jsonl
manifest.json
Full datasets are intentionally excluded as requested.