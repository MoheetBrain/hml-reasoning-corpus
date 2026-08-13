# FABLE VNext 10k Handoff

Use this corpus only when all authorities match:

- Corpus data commit: `09521ae992af5ca583a346da66c93d986e709386`
- HML semantic commit: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`
- Translation contract: `vnext-translation-contract-1.0.0`
- Contract lock: `contracts/hml_vnext/VNEXT_TRANSLATION_LOCK.json`

## Authoritative files

- Manifest: `data/vnext_10k/manifest.json`
- Full audit records: `data/vnext_10k/full_audit_records.jsonl.gz`
- Canonical split projections: `data/vnext_10k/train.jsonl.gz`,
  `data/vnext_10k/dev.jsonl.gz`, `data/vnext_10k/test.jsonl.gz`
- Nested record ordering: `data/vnext_10k/snapshots.json`
- Matched model views:
  `data/vnext_10k/views/{HML_LINEAR,HML_TREE,AST,STRUCTURED_NEUTRAL}/{train,dev,test}.jsonl.gz`

The split recorded on each row is authoritative. Never resplit atomic rows.
All transitions sharing a parent theorem/problem/trajectory remain grouped.
The 100, 250, 1,000, 5,000, and 10,000 snapshots are prefixes of the single
deterministic ordering in `snapshots.json`; each smaller rung is an exact subset
of every larger rung.

## Eligibility

- EXECUTE: use only rows where `task_eligibility.EXECUTE == true` (4,024).
  These are 4,000 formally replay-verified Lean transitions and 24
  deterministic backend-verified transitions.
- JUDGE: use only rows where `task_eligibility.JUDGE == true` (6,000). The
  objective mixes formal proof-step success with PRM human process supervision;
  keep `source_process_label`, `mathematical_verification_status`, and
  `epistemic_status` distinct.
- REPAIR: no rows are eligible (0). Do not manufacture repair pairs from PRM
  negative labels.
- APPLICABILITY: no rows are eligible (0).
- COMPREHENSION: all 10,000 rows are eligible when next-step mathematical truth
  is not being treated as certified.

PRM `{-1,0,+1}` labels are human process labels, not proof certificates. MATH,
AMPS, and unverified hard-tail rows must not be used for truth-sensitive EXECUTE
training.

## Representation experiment

HML_LINEAR, HML_TREE, AST, and STRUCTURED_NEUTRAL are matched deterministic
views of the same canonical transition. Each arm has 10,000 rows and identical
record ids/splits. Do not enrich one arm or independently reconstruct a view
from prose. Run the same model protocol and snapshot membership across all four
arms.

## Safe inputs and forbidden fields

For `(state_before, action) -> state_after`, use the `input` member of a
representation-specific view and its corresponding `target`. Do not expose full
audit transitions as model input.

Forbidden model inputs include:

- `state_after` or any future claim;
- target delta or final answer;
- later source-solution text;
- action summaries or metadata containing the target expression;
- any renamed or deterministically encoded answer-bearing field.

The supplied views passed per-example leakage checks 10,000/10,000. Treat that
projection as part of the data contract.

## Validation before use

Verify manifest hashes, corpus/HML/contract pins, representation counts, and
record-id parity. Expected splits are train 8,132, dev 952, and test 916.
Expected arm count is 10,000 each. The complete scientific interpretation,
coverage deficits, and historical/VNext distinction are in
`reports/VNEXT_CORPUS_MASTER.md`.

## Next atomic task

Run the matched VNext representation/execution learning experiment over
HML_LINEAR vs HML_TREE vs AST vs STRUCTURED_NEUTRAL using the nested
100 -> 250 -> 1k -> 5k -> full snapshots, before proceeding to REPAIR.
