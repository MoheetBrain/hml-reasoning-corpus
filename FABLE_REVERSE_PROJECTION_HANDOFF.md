# FABLE Reverse-Projection EXECUTE Handoff

Status: **PASS**. This release adds one model-ready view family,
`HML_IN_JSON_OUT`, for the reverse-projection execution experiment. It is not
newly translated mathematics and it does not invoke a semantic renderer. For
each authoritative EXECUTE `record_id`, it copies:

```text
input_text  := existing HML_LINEAR.input_text
target_text := existing AST.target_text
```

The strings are byte-for-byte identical to their source fields. The existing
AST arm is already the `JSON_IN_JSON_OUT` control. Do not regenerate it, retrain
it, or make any FABLE-side serialization choice.

## Exact authority

- Completed FABLE result: `ccf2a43`
- D1/D2 source export: `a2f992a6d474638814a1f1f7809f4015db3894c5`
- Canonical VNext data: `09521ae992af5ca583a346da66c93d986e709386`
- VNext semantic authority: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`
- Translation contract: `vnext-translation-contract-1.0.0`
- Reverse-projection exporter: `160c2308672a3030b0c0787f5b607f3bbeff35e2`
- Generated data/test commit: `ce5a70032573c0a56ce4513800165f6bf6789c5d`
- Source `data/vnext_10k/manifest.json` SHA-256:
  `77dfee09aaad6616f79057383be6e9c699b95db5e12ddec19dcfb0f9791a9af1`

No canonical records, record ids, task eligibility, snapshots, or split files
changed. No HML semantic file or frozen `hml_core` file changed. No new example
was added and Codex performed no model training.

## Files FABLE should load

Raw joined view:

- `data/vnext_10k/views/HML_IN_JSON_OUT/train.jsonl.gz`
- `data/vnext_10k/views/HML_IN_JSON_OUT/dev.jsonl.gz`
- `data/vnext_10k/views/HML_IN_JSON_OUT/test.jsonl.gz`

Mandatory comparison population:

- `data/vnext_10k/reverse_projection/matched_fit_ids_maxseq6144.json`
  → `comparison_record_ids_by_split`

Use only those comparison ids for the new full-rung train/evaluation so the
population is exactly the population used by the completed AST control. The
list is byte/set-identical to FABLE's existing
`/Users/moheet/hml_research_artifacts/vnext_exec/fit_ids.json`: 4,001/4,001 ids.

Supporting machine artifacts:

- `data/vnext_10k/reverse_projection_manifest.json`
- `data/vnext_10k/reverse_projection/raw_execute_membership.json`
- `data/vnext_10k/reverse_projection/leakage_audit.jsonl.gz`
- `data/vnext_10k/reverse_projection/token_audit.json`
- `data/vnext_10k/reverse_projection/golden_checks.json`

Every emitted view row follows the existing string-only model-view schema.
`input_text` and `target_text` are the only model-bearing fields.

## Membership and MAXSEQ audit

The token audit uses the exact completed-grid assumptions:
`mlx-community/gemma-4-E4B-it-qat-4bit` at
`0f35c6f6d386f7f74e628bd7c6526ce531212300`, the unchanged FABLE training
prompt, and the criterion
`prompted_input_tokens + target_tokens + 16 <= 6144`.

| population | train | dev | test |
|---|---:|---:|---:|
| raw EXECUTE | 3,254 | 392 | 378 |
| HML_IN_JSON_OUT fit | 3,247 | 392 | 378 |
| AST JSON_IN_JSON_OUT fit alone | 3,239 | 391 | 377 |
| new-pair intersection | 3,238 | 391 | 377 |
| reusable completed-control comparison | **3,233** | **391** | **377** |

The joined view excludes seven train records and no dev/test records. Six of
the seven also fail the AST control limit. The sole cross-view-only exclusion
is `VN10K-LEAN-2396`. Exact ids and component lengths for every exclusion are
in `matched_fit_ids_maxseq6144.json`.

The reusable comparison population is intentionally the completed four-arm
control population, not the five-row-larger fresh pair intersection. This
keeps both training exposure and held-out evaluation identical to the already
trained AST control. It is a subset of the joined fit population.

Count clarification: the completed artifact contains 4,001 common-fit records,
namely 3,233 train + 391 dev + 377 test. Thus the old grid excluded 23 records
in total: 21 train, one dev, and one test. Any prose saying "23 train and one
test" is inconsistent with both the arithmetic and FABLE's cached id list.

## Token summary over raw EXECUTE

These are `(mean / median / p90 / p99 / max)` Gemma-token counts. “Input” is
the full prompted input used by FABLE; “total” is input + target before the
16-token reserve.

| arm/component | token summary |
|---|---|
| HML_IN_JSON_OUT input | 446.476 / 363 / 794 / 1,579 / 4,985 |
| HML_IN_JSON_OUT target | 671.881 / 560 / 1,027 / 2,130 / 7,911 |
| HML_IN_JSON_OUT total | 1,118.357 / 937 / 1,797 / 3,610 / 12,874 |
| AST control input | 595.611 / 535 / 777 / 1,359 / 5,688 |
| AST control target | 671.881 / 560 / 1,027 / 2,130 / 7,911 |
| AST control total | 1,267.493 / 1,104 / 1,796 / 3,420 / 12,166 |

Tokenizer and prompt hashes, per-split summaries, and totals including the
16-token reserve are in `token_audit.json`.

## Audit results

- HML/AST/canonical record parity: **PASS**, 10,000/10,000 source rows.
- Raw EXECUTE projection: **PASS**, 4,024/4,024 unique records.
- Split, transition, action, and provenance parity: **PASS**, 4,024/4,024.
- HML input string identity: **PASS**, 4,024/4,024.
- AST target string identity: **PASS**, 4,024/4,024.
- Exact action envelope: **PASS**; 4,000 `tactic_text`, 24 `action_text`.
- Fresh D1 leakage policy: **PASS**; 4,024 checked, zero ambiguous, zero direct
  target-revealing, zero filtered.
- Mechanism coverage preserved: ordinary derivation 4,000; goal close 1,659;
  goal create 292; assumption/nested branch 24 each; weakening 16; branch join
  and obligations 8 each. These overlap and rare mechanisms remain
  underpowered.
- Golden identity checks: **PASS** for ordinary derivation, goal close, goal
  create, and assumption/nested branch.
- Deterministic rebuild: **PASS**, all nine generated files byte-identical on a
  second build.

## SHA-256

Source model-ready views:

| file | SHA-256 |
|---|---|
| `views/HML_LINEAR/train.jsonl.gz` | `e2215950a672bbeba40db6fc881429217e3d305671ab1d17034a6460375e0a70` |
| `views/HML_LINEAR/dev.jsonl.gz` | `b1996172d27a6c97b0d3120633105f90bc76ae5184741a4bd66d8b45a58926c3` |
| `views/HML_LINEAR/test.jsonl.gz` | `4bd9292f6f3b5cb3207a4ed14dcbbec46def87f0f6c7e6e5120b3d33ea09641c` |
| `views/AST/train.jsonl.gz` | `fc9b1dab24dc23c2df8fca5931df0284ee140073b949cbe8732616ee93563571` |
| `views/AST/dev.jsonl.gz` | `4403feb230269d3f95cb83d12abefd4c9373c961d2117b5c201955194abd8d9b` |
| `views/AST/test.jsonl.gz` | `2e18804a3785f756ffc6fd0bf21d3494a915c60a3ac55f399a2b3c7a892e581f` |

New deliverables:

| file | SHA-256 |
|---|---|
| `views/HML_IN_JSON_OUT/train.jsonl.gz` | `a42734aae591433b7da203d8353c065c7c660b66f084e7080af416336d7c6c59` |
| `views/HML_IN_JSON_OUT/dev.jsonl.gz` | `e79315b58a23c8191fbc67c974af78a5d3f6660938ea80c87adbeb454648556f` |
| `views/HML_IN_JSON_OUT/test.jsonl.gz` | `8133e7f216fdb11b2d58370444799b816a9709f425de0468c4c984dec215c35e` |
| `reverse_projection/raw_execute_membership.json` | `fafe3c7366d3c2999bb53a31ac20284511e00be8eebe3abab6ba2ee065de7903` |
| `reverse_projection/matched_fit_ids_maxseq6144.json` | `c5fbc3791f6a63f04dc00b5fd058900cda2b028efa0d910dd427da1f4694a87a` |
| `reverse_projection/leakage_audit.jsonl.gz` | `2a7dde99cc2f721048ded51d800254f9adbbb4748a25993013df45fcbfc4eb62` |
| `reverse_projection/token_audit.json` | `3d1cf87955b68731676b3b3c0599d810e8fc900427d56b0d416866a2493d5bf3` |
| `reverse_projection/golden_checks.json` | `adbfb3f93fcda7ca51dbe517af05074b69722c259abb191092c49af805d14416` |

The machine manifest is the per-file hash authority and also pins the exporter,
source files, tokenizer assets, prompt, and contract.

## FABLE next action

Run only `HML_IN_JSON_OUT`, full rung, seeds 1/2/3, using
`comparison_record_ids_by_split`. Reuse the existing three-seed AST
`JSON_IN_JSON_OUT` control and its evaluations. Do not run 250/1k rungs and do
not retrain the AST control.
