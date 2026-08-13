# FABLE VNext D1/D2 Patch

Status: `FABLE_GATE_REPAIRED`

Data/implementation commit: `a2f992a6d474638814a1f1f7809f4015db3894c5`

## D1 — executed action omitted

Before, EXECUTE projections exposed only an operation class and bookkeeping:

```json
{"dependencies":["p0"],"operation":"LEAN_TACTIC","preconditions":[],"warrant_rule":"LEAN_TACTIC"}
```

That encoded “some Lean tactic,” not the action that produced the transition.

After, the action envelope contains the exact pinned trace action:

```json
{"dependencies":["p0"],"operation":"LEAN_TACTIC","preconditions":[],"tactic_text":"rw [h]","warrant_rule":"LEAN_TACTIC"}
```

All 4,000 Lean rows use exact source `tactic_text`; all 24 deterministic protocol
EXECUTE rows use their canonical `action_text` and typed effects. Explicit
action content changed 0→4,024, with zero still missing. Provenance hashes bind
each action to its source trace and canonical before/after transition.

The full audit classified all 4,024 actions as legitimate action semantics:
zero direct target reveals, ambiguities, or EXECUTE exclusions. Eligibility
therefore remains 4,024.

## D2 — two arms were raw objects

Before:

```json
{"record_id":"…","input":{"state_before":{},"action":{}},"target":{}}
```

AST and STRUCTURED_NEUTRAL required FABLE to choose a serializer. HML_LINEAR and
HML_TREE were already strings.

After:

```json
{"record_id":"…","representation":"STRUCTURED_NEUTRAL","input_text":"{\"action\":{…},\"state_before\":{…}}","target_text":"{…}"}
```

All four arms now expose only canonical `input_text` and `target_text` strings.
AST uses `hmltn-canonical-json-ast@1.0.0`; neutral uses
`hmltn-canonical-json-neutral@1.0.0`. The HML arms use the exact 68178f0 state
renderer plus `canonical-action-envelope@1.0.0`.

FABLE must use these strings directly and make zero serialization decisions.
String/type and semantic-parity gates pass 10,000/10,000 for every arm. A second
build reproduced all 13 regenerated files byte-for-byte.

## Membership unchanged

- Canonical records: 10,000
- Splits: 8,132 / 952 / 916
- EXECUTE splits: 3,254 / 392 / 378
- TRAIN∩EXECUTE snapshots: 29 / 81 / 326 / 1,630 / 3,254

No mathematics, HML semantics, split, snapshot, source status, or task label was
changed.
