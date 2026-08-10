# AMPS-Khan dataset audit

AMPS-Khan is a second distribution for cross-source falsification of the small-core thesis, not permission to create training data. The Desktop original was not modified.

## Provenance

- Original parquet path: /Users/moheet/Desktop/0000.parquet
- Repository copy: /Users/moheet/Documents/ChatGPT/hmlt-reasoning-corpus/data/raw/amps_khan/0000.parquet
- Original companion CSV: /Users/moheet/Desktop/0000.csv; not used as source of truth
- Byte size: 11125600
- SHA-256: b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41
- Rows: 103059
- Columns: topic_name, problem, hints/solutions

## Distribution audit

- Distinct topics: 721
- Numeric topic IDs: 75302
- Opaque/non-numeric topic IDs: 27757
- Null counts: {"topic_name": 0, "problem": 5, "hints/solutions": 0}
- Empty counts: {"topic_name": 0, "problem": 5, "hints/solutions": 0}
- Empty/malformed proxy rows: 5
- Exact duplicate problem texts: 1666
- Exact duplicate problem+solution pairs: 15
- Visual-dependent marker rows: 3293
- Multiple-choice marker rows: 21094
- LaTeX-heavy marker rows: 102402
- Planning-cue rows: 47530

## Solution length distribution

| Statistic | Characters |
|---|---:|
| min | 5 |
| p25 | 242.0 |
| median | 455 |
| p75 | 799.0 |
| p90 | 1189.0 |
| p95 | 1428.0 |
| p99 | 2023.2 |
| max | 3297 |

## Interpretation

The topics mix numeric identifiers with opaque human-readable families. The distribution contains clean textual/LaTeX mathematics, visual-dependent rows, multiple-choice rows, and duplicate/incomplete material. Any cross-source semantic study must filter and stratify before annotation.

No AMPS trajectory was created in this mission. The future test is new core, meta, library, backend, warrant, and state-field demand relative to ontology-v1.
