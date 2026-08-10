# Gold-125 HML coverage audit


> **HISTORICAL COVERAGE AT HML `5688aba`.** Measured against the `hml_core` pin in force at the time. The algebra, probability and calculus libraries shipped later at `2af4998`; `git ls-tree -r 5688aba` contains no `libraries/` path at all. These figures, and every "library-blocked" claim resting on them, therefore describe a core that no longer exists. **No updated coverage has been measured** — do not substitute one. Relabelled 2026-08-10.

Coverage uses the unchanged pinned HML implementation. It is a semantic support classification, not a benchmark score and not a claim that REPRESENTABLE_ONLY transitions are executable.

## Step-weighted source-granularity coverage

| Status | Steps | Fraction |
|---|---:|---:|
| FULL | 11 | 1.4% |
| PARTIAL | 455 | 59.2% |
| REPRESENTABLE_ONLY | 303 | 39.4% |
| ABSENT | 0 | 0.0% |
| UNKNOWN | 0 | 0.0% |

## Normalized atomic coverage

| Status | Atomic units | Fraction |
|---|---:|---:|
| FULL | 11 | 1.3% |
| PARTIAL | 514 | 59.3% |
| REPRESENTABLE_ONLY | 342 | 39.4% |
| ABSENT | 0 | 0.0% |
| UNKNOWN | 0 | 0.0% |

## Domain coverage (normalized atomic units)

| Category | FULL | PARTIAL | REPRESENTABLE_ONLY | ABSENT | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Algebra | 6 | 98 | 29 | 0 | 0 |
| Intermediate Algebra | 2 | 87 | 58 | 0 | 0 |
| Counting & Probability | 0 | 58 | 65 | 0 | 0 |
| Number Theory | 1 | 112 | 79 | 0 | 0 |
| Precalculus | 0 | 67 | 47 | 0 | 0 |
| Geometry | 1 | 36 | 33 | 0 | 0 |
| Prealgebra | 1 | 56 | 31 | 0 | 0 |

## Operation-weighted coverage

| Status of operation's majority evidence | Operations |
|---|---:|
| FULL | 4 |
| PARTIAL | 23 |
| REPRESENTABLE_ONLY | 39 |
| ABSENT | 0 |
| UNKNOWN | 0 |

The dominant limitation remains theorem/domain/backend evidence and generic branch/candidate interfaces, not an absence of basic expression syntax. Current HML should not be expanded with one bespoke keyword per mathematical domain.
