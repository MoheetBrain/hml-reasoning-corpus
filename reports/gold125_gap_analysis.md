# Gold-125 semantic-gap analysis

The gap registry distinguishes current HML semantic interfaces from theorem/domain libraries, symbolic/numeric backends, and the source-to-trajectory canonicalization boundary. Existing Gold-25 gap IDs are preserved; MATH-GAP-0011–0013 are new recurrence classes observed in the expansion.

| Rank | Gap | Revised class | Recurrence | Domain spread | Severity | Gold-25? | Importance |
|---:|---|---|---:|---:|---|---|---:|
| 1 | MATH-GAP-0003 | CORE_SEMANTIC_MISSING | 204 | 7 | high | yes | 4284 |
| 2 | MATH-GAP-0009 | LIBRARY_MISSING | 179 | 7 | medium | yes | 2506 |
| 3 | MATH-GAP-0004 | CORE_SEMANTIC_MISSING | 107 | 7 | high | yes | 2247 |
| 4 | MATH-GAP-0008 | LIBRARY_MISSING | 121 | 6 | medium | yes | 1452 |
| 5 | MATH-GAP-0002 | CORE_SEMANTIC_MISSING | 47 | 7 | high | yes | 987 |
| 6 | MATH-GAP-0010 | TRAJECTORY_SCHEMA_PROBLEM | 37 | 7 | medium | yes | 518 |
| 7 | MATH-GAP-0007 | LIBRARY_MISSING | 71 | 3 | medium | yes | 426 |
| 8 | MATH-GAP-0001 | CORE_SEMANTIC_MISSING | 22 | 5 | high | yes | 330 |
| 9 | MATH-GAP-0006 | LIBRARY_MISSING | 18 | 6 | medium | yes | 216 |
| 10 | MATH-GAP-0011 | TRANSLATION/CANONICALIZATION_PROBLEM | 7 | 5 | high | no | 105 |
| 11 | MATH-GAP-0012 | CORE_SEMANTIC_MISSING | 7 | 4 | medium | no | 56 |
| 12 | MATH-GAP-0005 | LIBRARY_MISSING | 5 | 3 | medium | yes | 30 |
| 13 | MATH-GAP-0013 | LIBRARY_MISSING | 2 | 2 | medium | no | 8 |

## Gap details

### MATH-GAP-0003: Applicability preconditions

- Class: CORE_SEMANTIC_MISSING
- Layer: CORE_PROOF_OPERATION
- Recurrence: 204 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-002, MATH-GOLD-003, MATH-GOLD-006, MATH-GOLD-018, MATH-GOLD-019, MATH-GOLD-026, MATH-GOLD-028, MATH-GOLD-029, MATH-GOLD-030, MATH-GOLD-031
- Architectural implication: Domain and nonzero conditions are not synthesized uniformly.

### MATH-GAP-0009: Number theory and finite search

- Class: LIBRARY_MISSING
- Layer: DOMAIN_LIBRARY
- Recurrence: 179 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-014, MATH-GOLD-015, MATH-GOLD-017, MATH-GOLD-021, MATH-GOLD-022, MATH-GOLD-027, MATH-GOLD-028, MATH-GOLD-029, MATH-GOLD-036, MATH-GOLD-043
- Architectural implication: Divisibility, congruence, factorization, and minimality certificates are missing.

### MATH-GAP-0004: Persistent proof obligations

- Class: CORE_SEMANTIC_MISSING
- Layer: CORE_PROOF_OPERATION
- Recurrence: 107 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-002, MATH-GOLD-004, MATH-GOLD-012, MATH-GOLD-019, MATH-GOLD-025, MATH-GOLD-027, MATH-GOLD-028, MATH-GOLD-029, MATH-GOLD-030, MATH-GOLD-031
- Architectural implication: Transformation debt is not uniformly attached to source operations.

### MATH-GAP-0008: Counting and probability library

- Class: LIBRARY_MISSING
- Layer: DOMAIN_LIBRARY
- Recurrence: 121 source-granularity step references
- Domains: Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-010, MATH-GOLD-011, MATH-GOLD-012, MATH-GOLD-013, MATH-GOLD-017, MATH-GOLD-028, MATH-GOLD-031, MATH-GOLD-032, MATH-GOLD-035, MATH-GOLD-036
- Architectural implication: Finite sample-space, counting, and probability rules lack trusted evidence.

### MATH-GAP-0002: Candidate generation and verification

- Class: CORE_SEMANTIC_MISSING
- Layer: CORE_PROOF_OPERATION
- Recurrence: 47 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-004, MATH-GOLD-015, MATH-GOLD-025, MATH-GOLD-029, MATH-GOLD-030, MATH-GOLD-031, MATH-GOLD-033, MATH-GOLD-042, MATH-GOLD-043, MATH-GOLD-044
- Architectural implication: Candidate provenance and original-constraint acceptance are not first-class.

### MATH-GAP-0010: Sequence and exclusion state

- Class: TRAJECTORY_SCHEMA_PROBLEM
- Layer: CORE_STATE_OPERATION
- Recurrence: 37 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-016, MATH-GOLD-023, MATH-GOLD-025, MATH-GOLD-027, MATH-GOLD-033, MATH-GOLD-041, MATH-GOLD-042, MATH-GOLD-043, MATH-GOLD-046, MATH-GOLD-051
- Architectural implication: Sequence generators, excluded values, and index translation need persistent neutral state.

### MATH-GAP-0007: Domain theorem libraries

- Class: LIBRARY_MISSING
- Layer: DOMAIN_LIBRARY
- Recurrence: 71 source-granularity step references
- Domains: Geometry, Intermediate Algebra, Precalculus
- Example trajectories: MATH-GOLD-006, MATH-GOLD-007, MATH-GOLD-008, MATH-GOLD-009, MATH-GOLD-018, MATH-GOLD-019, MATH-GOLD-020, MATH-GOLD-021, MATH-GOLD-022, MATH-GOLD-023
- Architectural implication: Logs, trigonometry, geometry, vectors, complex facts, and related domain knowledge are not broadly checked.

### MATH-GAP-0001: Case coverage and branch joins

- Class: CORE_SEMANTIC_MISSING
- Layer: CORE_PROOF_OPERATION
- Recurrence: 22 source-granularity step references
- Domains: Algebra, Counting & Probability, Intermediate Algebra, Number Theory, Precalculus
- Example trajectories: MATH-GOLD-004, MATH-GOLD-007, MATH-GOLD-010, MATH-GOLD-012, MATH-GOLD-019, MATH-GOLD-027, MATH-GOLD-030, MATH-GOLD-050, MATH-GOLD-106
- Architectural implication: Generic exhaustive/disjoint branch declarations and invariant-only joins are not fully executable.

### MATH-GAP-0006: Open symbolic algebra

- Class: LIBRARY_MISSING
- Layer: SYMBOLIC_BACKEND_OPERATION
- Recurrence: 18 source-granularity step references
- Domains: Algebra, Geometry, Intermediate Algebra, Number Theory, Prealgebra, Precalculus
- Example trajectories: MATH-GOLD-001, MATH-GOLD-002, MATH-GOLD-003, MATH-GOLD-007, MATH-GOLD-015, MATH-GOLD-018, MATH-GOLD-021, MATH-GOLD-022, MATH-GOLD-024, MATH-GOLD-025
- Architectural implication: Open-variable normalization lacks a trusted replayable backend.

### MATH-GAP-0011: Source-supported search/meta reasoning

- Class: TRANSLATION/CANONICALIZATION_PROBLEM
- Layer: SEARCH_META_OPERATION
- Recurrence: 7 source-granularity step references
- Domains: Algebra, Counting & Probability, Geometry, Number Theory, Prealgebra
- Example trajectories: MATH-GOLD-031, MATH-GOLD-032, MATH-GOLD-033, MATH-GOLD-035, MATH-GOLD-036, MATH-GOLD-066, MATH-GOLD-096
- Architectural implication: Successful solutions contain explicit representation and subgoal choices that do not map cleanly to a narrow execution vocabulary.

### MATH-GAP-0012: Induction proof-state protocol

- Class: CORE_SEMANTIC_MISSING
- Layer: CORE_PROOF_OPERATION
- Recurrence: 7 source-granularity step references
- Domains: Algebra, Intermediate Algebra, Number Theory, Precalculus
- Example trajectories: MATH-GOLD-051, MATH-GOLD-061, MATH-GOLD-064, MATH-GOLD-076
- Architectural implication: Base-case and inductive-hypothesis state are not represented as a reusable proof protocol in this corpus.

### MATH-GAP-0005: Theorem and formula evidence

- Class: LIBRARY_MISSING
- Layer: THEOREM_LIBRARY
- Recurrence: 5 source-granularity step references
- Domains: Algebra, Counting & Probability, Number Theory
- Example trajectories: MATH-GOLD-001, MATH-GOLD-028, MATH-GOLD-036
- Architectural implication: Hypothesis-aware theorem evidence is not available as a broad checked library.

### MATH-GAP-0013: Calculus theorem/backend evidence

- Class: LIBRARY_MISSING
- Layer: DOMAIN_LIBRARY
- Recurrence: 2 source-granularity step references
- Domains: Algebra, Counting & Probability
- Example trajectories: MATH-GOLD-035, MATH-GOLD-040
- Architectural implication: Differentiation, integration, and limit claims require domain/library evidence beyond the generic kernel.
