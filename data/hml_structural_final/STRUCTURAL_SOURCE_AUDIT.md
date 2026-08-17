# Structural Source Audit

Date: 2026-08-17. Verdict: **INSUFFICIENT_STRUCTURAL_DATA**.

## Execution environment and authorities

- Host: `moheetc4`, zone `europe-west2-c`, 24 logical CPUs, approximately 88 GiB
  RAM. The canonical scan used 24 mmap byte-range workers.
- Corpus base: `91fdda35851caa0445c1becdb1d7a756d5bcee3d`.
- Corpus source pin: LeanDojo Benchmark 4, Mathlib commit
  `29dcec074de168ac2bf835a77ef68bbe069194c5`.
- Canonical transition export: 241,265 rows, SHA-256
  `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.
- VNext semantic authority: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`;
  inspected from consolidation checkout `73184c5`, whose `src/` is byte-identical to
  the authority. It was mounted read-only under `/tmp`; neither it nor `hml_core`
  was modified.
- Old VNext development parents were loaded from the frozen 10K audit and excluded.

## Fresh formal census

The complete raw LeanDojo traces contain 259,580 transitions. Excluding 42,957
transitions belonging to 3,670 prior-development parent groups leaves **216,623
fresh exact before/action/after transitions** in 57,874 non-empty trajectories.

| Explicit source feature | Fresh count | Headline interpretation |
|---|---:|---|
| explicit Lean goal/context | 216,623 | usable goal state |
| multiple goals before | 1,224 | usable multi-goal state |
| multiple goals after | 15,140 | usable transition signal |
| goal creation | 14,736 | usable transition signal |
| `case` scope before | 92,471 | scope only |
| nested `case` scope before | 42,409 | nested scope only |
| conservative `P`/`¬P` two-case pairs after | 2,242 | branch candidate evidence, not a general branch object |
| action-derived premise lists nonempty | 141,075 | withheld; gold-action-derived |
| claim dependency graph | 0 | absent |
| obligation distinct from goal | 0 | absent |
| candidate lifecycle state | 0 | absent |
| epistemic/status transition | 0 | absent |
| general branch predicate + membership + coverage | 0 | absent |

The older canonical subset excludes goal-creating transitions. Its independent
24-worker scan found 201,887 fresh rows, 198,852 with at least two separated
hypotheses, 86,918 with case labels, 40,037 with nested case labels, and 1,185
multi-goal states. It also exposed a builder defect: the canonical builder looked for
a nonexistent `premises` key, while the raw source stores premises in
`annotated_tactic[1]`. Correcting that census does **not** authorize putting those
action-derived premises into model input.

## Other available sources

Existing whole-corpus acquisition audits were re-read, not counted as newly parsed
formal transitions:

| Source | Rows inventoried | Why it cannot fill the headline gap |
|---|---:|---|
| STP Lean 0320 | 3,262,558 | statement/proof continuation; no before/after states |
| NuminaMath-LEAN | 104,155 | proof text; no proof-state trajectories |
| Herald proofs | 44,553 | theorem/proof text; no states/transitions |
| Pythagoras SFT | 126,113 | solution/proof text; no proof-state trajectories |
| state-tactic pairs | 56,407 | no `state_after`; retrieved block is answer-informative and must be stripped |
| PRM800K trajectories | 101,599 | human process labels and text prefixes, not formal structural state |

These total 3,695,385 inventoried rows. Together with the 259,580 raw LeanDojo
transitions, 3,954,965 records were considered across current and existing audits,
but only the LeanDojo transitions were re-scanned in this mission.

## Existing rich records are not a fresh solution

The prior VNext 10K has 937 dependency-bearing, 318 obligation-bearing, 290
branch-bearing, 251 nontrivial-scope, and 79 candidate-bearing before states. Those
rich fields occur in its 1,000-row synthetic hard tail; the 4,000 LeanDojo rows do
not carry them. The entire 10K is development history. Gold-125 is small,
human-derived, and also development history. Reusing either as FINAL would violate
the freshness contract and make the result synthetic/HML-shaped.

## Decision

The available formal source is excellent for a goal/scope/multi-goal action task.
It is not a source for the conjunctive HML structural-state hypothesis. Filling the
missing relations would require future-action inference, duplicating goals as
obligations, synthetic semantics, or a new annotation/replay source. All are
forbidden. No exporter was therefore allowed past the admission gate.

