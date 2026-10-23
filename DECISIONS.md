Flam Data Curation Assignment

1. Sources


Source 1
Name: IndicXParaphrase
URL: <https://huggingface.co/datasets/ai4bharat/IndicXParaphrase/blob/main/data/hi.tsv>
License: N/A
Download Date: 2026-10-22
Documents: 4,000


Source 2
Name: Samanantar
URL: https://huggingface.co/datasets/ai4bharat/samanantar
License: CC BY-NC 4.0
Download Date: 2026-10-22
Documents: 6,000
Total Corpus
Total Raw Documents: 10,000+
Notes
The corpus was assembled from multiple public sources to satisfy the assignment requirement of at least 10,000 documents and multiple data sources.

The corpus contains both:

Hindi (Devanagari)
Hinglish / Romanized Hindi (hi-Latn)
2. Pipeline Overview
The pipeline processes data in the following sequence:

Raw Data

↓

Normalization

↓

Language Detection

↓

Quality Filtering

↓

PII Redaction

↓

Exact Deduplication

↓

Near-Duplicate Detection

↓

Clean Corpus

↓

Eval Set Generation

↓

Contamination Check

↓

Manifest Generation

3. Funnel
Stage	Documents
Raw Input	1000
Malformed Records Removed	0
Quality Filter Removed	0
Exact Duplicates Removed	0
Near Duplicates Removed	4
Final Training Corpus	200
Notes
Counts above are generated automatically from:

ledger.jsonl
manifest.json
The pipeline is deterministic and reproducible.

4. Language Distribution
Language	Count
hi	499
hi-Latn	420
en	77
other	0
Detection Logic
Languages are identified using script-level and lexical heuristics.

Rules:

Devanagari script → hi
Romanized Hindi vocabulary → hi-Latn
English text → en
Non-classifiable text → other
Example:

मेरा नाम राहुल है
↓

hi
Example:

mera naam rahul hai
↓

hi-Latn

5. Quality Filtering
The following records are removed:

Empty text
Extremely short text
Broken markup
Garbled Unicode
Corrupted records
Malformed JSON rows
Malformed records do not stop execution.

The pipeline:

skips bad documents
records statistics
continues processing
This supports large-scale streaming ingestion.

6. PII Redaction
The following entities are redacted:

Type	Replacement
Phone Numbers	<PHONE>
Email Addresses	<EMAIL>
Aadhaar Numbers	<AADHAAR>
PAN Numbers	<PAN>
Validation
Synthetic Hindi and Hinglish test cases were used.

Example:

Input:

Mera phone number 9876543210 hai
Output:

Mera phone number <PHONE> hai
Input:

rahul@gmail.com
Output:

<EMAIL>
7. Exact Deduplication
Method:

Normalized text
Hash-based lookup
Rationale:

Hash-based duplicate detection is:

deterministic
fast
memory efficient
Example:

Text A
equals

Text B
↓

Drop duplicate

Ledger entry:

{
  "stage": "exact_dedup",
  "reason": "exact_duplicate"
}

8. Near-Duplicate Detection
Model
paraphrase-multilingual-MiniLM-L12-v2
Similarity
Cosine Similarity
Threshold Evaluation
Threshold	Observation
0.90	Too aggressive
0.92	Best balance
0.95	Missed obvious paraphrases
Selected Threshold
0.92
Rationale
0.92 removed obvious paraphrases while preserving semantically different statements.

9. Negation Protection
Embedding models sometimes consider:

उन्हें पुरस्कार मिला।
and

उन्हें पुरस्कार नहीं मिला।
very similar.

To avoid dropping contradictory statements, negation-aware logic was added.

Example:

KEEP

मुख्यमंत्री हैं।
मुख्यमंत्री नहीं हैं।
These represent different facts and should remain in the corpus.

10. Eval Set
The evaluation set is generated automatically.

Method:

Random sampling
Fixed random seed
200 documents
Output:

eval.jsonl
Purpose:

The evaluation set is excluded from the training corpus and reserved for downstream benchmarking.

11. Contamination Check
Purpose:

Detect overlap between:

Training Corpus
and

Evaluation Corpus
Method:

Exact text matching
Output:

contamination.jsonl
Current Result:

{
  "contamination_found": false,
  "matches": 0
}
Interpretation:

No evaluation examples were found in the training set.

12. Manifest Generation
The pipeline automatically generates:

manifest.json
The manifest contains:

input documents
output documents
quality removals
exact duplicates
near duplicates
language counts
thresholds used
Purpose:

Provide a reproducible summary of corpus construction.

13. Streaming Design
The pipeline reads JSONL data line-by-line.

Benefits:

Low memory footprint
Handles large datasets
Survives malformed input
Scales better than loading entire corpora in memory
Malformed records are counted and skipped.

14. Scaling Discussion
What breaks first at 2 TB?
Primary bottleneck:

Near-Duplicate Detection
Current implementation stores embeddings in memory.

At larger scales I would replace this with:

FAISS
Approximate Nearest Neighbor Search
Distributed storage
Distributed processing frameworks
Exact duplicate detection would remain inexpensive.

15. Reproducibility
Execution:

bash download.sh
bash run.sh
Outputs:

clean/data.jsonl
ledger.jsonl
eval.jsonl
contamination.jsonl
manifest.json
Every run with identical inputs produces identical results.

16. Summary
The final pipeline performs:

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
The design prioritizes:

Reproducibility
Auditability
Simplicity
Scalability
Data quality
