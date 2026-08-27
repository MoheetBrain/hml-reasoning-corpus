# Project Status

*Created 2026-08-10 to satisfy the Mandatory Commit Continuity Protocol, which blocks
commits in any repository lacking this file and `PROJECT_LEDGER.md`. This is a **protocol**
document. It is **not** a sixth canonical context document: `docs/00_HML_MASTER.md` through
`docs/04_INTEGRATION_AND_IMPLEMENTATION.md` remain the canonical five and are
integrator-owned.*

## Project Objective

Determine whether a checked intermediate representation helps an AI system reason, and hold
the evidence for that question honestly. Representability is not reasoning superiority.

## Current Stage

**Max-EV representation experiment, CPU preparation complete; A100 Stage 1 pending.**
Branch `claude/max-ev-representation-experiment-v1` adds
`experiments/max_ev_representation_v1/`: a verifier-labelled action-validity probe over four
matched representations of one canonical semantic object. Both blocking gates pass
(representation parity 5,619/5,619; leakage on all four arms). No GPU time has been spent.

The prior forensic reconciliation stage is unchanged and unresolved; this experiment does not
supersede it and does not reuse its results. The 50K HML/Neutral representation result is now
formally recorded as `INVALID_FOR_HML_REPRESENTATION_INFERENCE` — see below.

## Current Branch

`claude/max-ev-representation-experiment-v1`, branched from `codex/reasoning-layer-discovery`.
Additive only: no historical manifest, dataset, audit or result has been modified.

## Current System Architecture

Five canonical context documents (`docs/00`–`docs/04`), the paired HML50K teaching corpus,
a frozen Semantic Firewall
experiment (`experiments/semantic_firewall/`) whose reference checker and 30 acceptance
fixtures are the external acceptance criteria for the production implementation, a PRM800K
natural-error audit, a MiniLang artifact audit, and a project cognition ledger
(`experiments/project_cognition/project_memory.yaml`, 135 entries, twice independently
audited).

## Capabilities Implemented

The frozen reference checker; the 30-fixture acceptance suite; the FINAL 80/80 benchmark;
the neutral transition schema; the cognition ledger; deterministic builders and independent
audits for 56,000 paired HML/Neutral formal-trace teaching transitions.

## Work Completed to Date

See `docs/HML_RESEARCH_LEDGER.md` for the scientific record and `PROJECT_LEDGER.md` for the
chronological change record.

## Important Files and Artifacts

`data/hml_50k_final/CLAUDE_FINAL_QWEN_HANDOFF.md` ·
`data/hml_50k_final/HML50K_MANIFEST.json` · `scripts/hml50k/` ·
`experiments/semantic_firewall/reference_checker.py` · `.../acceptance/fixtures.json` ·
`.../requirements_handoff.json` · `.../freeze_manifest.json` ·
`experiments/project_cognition/project_memory.yaml` · `docs/00`–`docs/04` ·
`docs/HML_RESEARCH_LEDGER.md`.

## Data Sources and Provenance

LeanDojo Benchmark 4 / Mathlib `29dcec0`, Hendrycks MATH, PRM800K, five additional local
Lean/proof-text corpora, and the MiniLang OOPSLA26 v2 artifact
(SHA-256 `1562c845…`). Provenance is recorded per experiment.

## Decisions and Rationale

Recorded in the canonical five and in the cognition ledger. Production-side design decisions
live in the HML repository's `DECISIONS.md`.

## Verification and Test Results

**2026-08-22, HML50K final teaching corpus.** Golden VNext validation passed 20/20 at HML
`68178f0`. The build produced exactly 50,000 TRAIN, 3,000 DEV and 3,000 FINAL records from
16,950 parent theorems. Independent checks passed: 56,000 candidate-order comparisons,
112,000 HML/Neutral state comparisons, 224,000 action-envelope comparisons, all requested
cross-boundary mutations, zero parent/signature overlap, zero old-parent contamination in
FINAL, zero target leaks under the tested detectors, zero JSON Unicode escapes, and zero
Qwen3-8B input+target rows over 6,144. The primary HML view costs 10.2% more tokens than
Neutral. All rows are `FORMAL_TRACE`, not overstated as freshly replay-verified. No Qwen,
Gemma, MLX training, or cloud process was run.

**2026-08-17, final structural-source census.** On the 24-vCPU `moheetc4` data VM,
259,580 LeanDojo transitions were scanned; 42,957 from old VNext/Qwen development
parents were excluded, leaving 216,623 fresh exact before/action/after transitions in
57,874 complete non-empty trajectories. The source has 1,224 fresh multi-goal before
states, 92,471 scoped before states and 2,242 conservative complementary case-pair
after states, but zero source-supported claim dependency graphs, obligations distinct
from goals, candidate lifecycle states, epistemic transitions, or general branch
objects with predicate and coverage. The frozen population gate failed before
selection; zero headline records and no model views were emitted. Full machine census,
specifications, refusal audits, and manifests are in `data/hml_structural_final/`.

**2026-08-10, cognition ledger, THIRD independent audit.** The file committed at `8d1d95f`
**did not parse** under a real YAML parser: X134 and X135 were indented two spaces deeper
than every other sequence item, making them block content of X133 rather than entries. The
regex-based verification used at commit time could not see it. Repaired by de-indenting 52
lines with no content change. After repair: parses under Ruby Psych, **148 entries, X1-X148
contiguous, 0 duplicates, 0 dangling references**; all 94 cited paths and all 15 cited
commits resolve.

**2026-08-10, cognition ledger, second independent audit.** Executed: 135 entries, ids
X1–X135, no duplicates, no gaps, no dangling cross-references; 83 cited absolute paths all
resolve; all cited commits resolve. Two disagreements with the first pass were recorded
rather than silently corrected — a wrong status breakdown (rejected 14, not 16; the six
reported statuses summed to 113 of 128 entries) and a stale HML head.

**Not run here:** the reference checker against the production implementation. That is run
in the HML repository, which reports 30/30 verdict and error class.

## Known Failures and Limitations

* **The frozen 30 fixtures cannot detect a missing frame condition.** All thirty are
  well-formed records whose delta already matches their action. A production verifier with
  no frame condition passed all thirty while accepting a claim asserting `0 = 1` out of
  nothing. The instrument's blind spot, not only the implementation's.
* ~~`schemas/semantic_case.schema.json` rejects its own fixtures.~~ **REPAIRED 2026-08-11.**
  `$defs/action` was unsatisfiable — `additionalProperties: false`, a 15-name `required`, and
  no `properties` block — and rejected **0/230** of the cases it describes (30 acceptance, 40
  DEV, 160 FINAL). Repaired by adding the `properties` block, which restates `required`
  verbatim, plus the JSON types on which all 230 cases agree. Now **230/230**. It survived
  because *nothing validated against it*: the corpus had no dependency manifest and no
  JSON-Schema test anywhere. Both now exist (`requirements.txt`, `tests/test_schemas.py`),
  including a general guard that fails on any recurrence of the unsatisfiable shape.
* ~~The repaired schema was satisfiable but not discriminating.~~ **HARDENED 2026-08-11
  (amendment 2).** `$defs/source`, `$defs/claim` and `$defs/evidence` carried `required` and
  nothing else; `state.obligations`, `candidates`, `branches`, `goals` and all fifteen
  `action` sub-objects were bare `{"type": "object"}`; array `items` were unconstrained.
  Measured cost: of the malformed shapes it accepted, **thirteen made
  `reference_checker.check_case` raise `TypeError`/`AttributeError` instead of returning a
  verdict**, and `evidence.trusted` spelled as the **string** `"false"` — truthy — turned an
  INVALID epistemic promotion into VALID on `FX-EPI-LEGAL`. Hardened only where the evidence
  reached: `$defs/claim` **closed** (its six fields are agreed by `required`, by the union
  *and* the intersection over all 736 frozen claim instances, by the 76 FX2 claim instances,
  and by `semantic_state.model.Claim`); value schemas added for the four unvalidated state
  regions; JSON types pinned wherever a wrong type crashes or misleads the checker.
  `source`, `evidence`, `obligation`, `candidate`, `branch` and `goal` are **deliberately
  left open**, each with its reason in the schema's own `description`:
  `SEMANTIC_STATE_CONTRACT.md` §4 names `source`, `typing`, `warrant`, the `*_effect` maps
  and the precondition/obligation lists as open dictionaries the corpus may extend at any
  time; `EvidenceRecord` keeps unmodelled keys in an extensible payload; and the canonical
  `Candidate` (9 fields), `Branch` (6) and `Obligation` (7) dataclasses declare strictly more
  fields than the frozen corpus exhibits — FX2 already uses `origin`, `partition_id` and
  `scope`, which proves the frozen union is **not** a complete sample of legitimate formats.
  Still **230/230** frozen and **40/40** FX2 as declared. Freeze manifest amended a second
  time; both superseded hashes preserved.
* **`action.obligations_created` cannot be typed, and that is a known hole.** The reference
  checker raises on a non-object item and `neutral.py::_obligation_specs` refuses one, but the
  frozen fixture `FX2-MAL-UNHASHABLE-REFUSE` carries `obligations_created: [[1], [2]]` and
  declares `schema_valid: true`. Constraining the array would flip a frozen artifact's
  declared flag, so it is left open, documented in the schema, and pinned by a test. That
  fixture is named REFUSE, but the reference checker does not refuse it — it **crashes**.
* **A typo'd extra key still passes in `source` and in an evidence record.** Not an
  oversight: both are declared extensible by the canonical contract, and in an evidence
  record an undeclared key is indistinguishable from a legitimate kind-specific payload key.
  Recorded rather than closed, and asserted by `tests/test_schemas.py` so that closing one
  later fails a test instead of silently discarding the reason.
* **Coverage figures are historical — now labelled as such.** Gold-125 coverage (FULL 11 /
  PARTIAL 455 / REPRESENTABLE_ONLY 303) and every "library-blocked" claim were measured
  against `hml_core` at `5688aba`; `git ls-tree -r 5688aba` contains no `libraries/` path at
  all. Labelled `HISTORICAL COVERAGE AT HML 5688aba` in five places. **No updated coverage
  has been measured, and none was manufactured.**
* **Four unscoped absence-of-evidence statements — now corrected.** They asserted that
  experiments do not exist when they exist in the HML repository. Each is now explicitly
  scoped "in this repository" and carries the programme-level result, which is **negative or
  null for HML** rather than absent.
* **The e-graph adoption gate never existed.** `docs/design/EGRAPH_ADOPTION_GATE.md` is cited
  as authority and no such path appears in any commit of any branch of any of the four
  repositories. Two of five conditions survive in prose; three are unrecoverable.

## Risks and Technical Debt

The pinned `hml_core` is five commits stale, so any coverage or capability claim measured
against it describes a core that no longer exists.

## Current Blockers

There is no data blocker for the staged 10K/30K/50K teaching experiment; it now belongs to
Claude/FABLE. The separate final HML structural hypothesis still cannot be tested fairly
with currently available fresh sources. A suitable source must explicitly expose claim dependencies,
obligations distinct from goals, branch predicate/membership/coverage, and candidate
lifecycle/status while retaining replayable before/action/after state. Existing rich
VNext records are synthetic development history and cannot be used as FINAL.

The trust boundary (HML `DECISIONS.md` D-050): evidence status is read from the imported
record, so a producer that authors a transition authors its verdict. Blocks any use where
transitions are model-authored.

## Fixture Suites

| suite | version | count | status | evidence class |
|---|---|---|---|---|
| `experiments/semantic_firewall/acceptance/fixtures.json` | `semantic-firewall-acceptance-0.1.0` | 30 | **frozen, untouched** | **external** — authored corpus-side against a reference checker before the implementation existed |
| `experiments/semantic_firewall_v2/fixtures_v2.json` | `semantic-firewall-fx2-1.0.0` | 40 | frozen 2026-08-11 | **integrator-authored, weaker** — cannot show the implementation was right, only that a known defect cannot silently return |

FX2 is additive: `FX2-` ids cannot collide, and a test asserts the frozen thirty are
byte-unchanged. **13 of 40 deliberately diverge from the frozen reference checker**, each
with a recorded reason — production is stricter on the frame condition, scope containment
and trust modes, and an undeclared divergence would look like agreement.

## Max-EV representation experiment (2026-08-27)

### The two instrument defects found and repaired

**1. The 50K Unicode audit passed corrupted data.** It counted JSON `\uXXXX` escapes in the
serialized file (correctly: zero, because `ensure_ascii=False`) rather than in the decoded
string the model reads. Re-audited at payload level: **280,000 of 280,000 HML rows are
contaminated and 0 of 280,000 neutral rows are**, 12,995,134 literal escape sequences,
15.96%-25.39% of each HML prompt by task. The confound is perfectly asymmetric by arm, so the
-3.41pp HML result measures the serializer. Recorded as
`reports/INVALIDATED_INSTRUMENTATION_RUN.md`; the raw artifact is preserved and must not be
used as treatment evidence. The canonical source is clean (0 literal escapes across 3,000
records), so the defect was entirely at render time.

**2. The 50K canonical corpus carries almost no HML semantic state.** Measured over 20,000
records: every state has exactly 1 claim, 0 candidates, 0 branches, 0 goals, 0 obligations,
1 scope, operation always `LEAN_TACTIC`. Eight of the verifier's ten invariants have nothing
to check. A representation comparison on it would compare four ways of wrapping one opaque
string. Repaired by decomposing the Lean tactic state into the structure it always contained
(99.9% clean, mean 12.5 typed declarations, 100% with an explicit goal, 42% case-labelled).

A third would-be defect was found before it was built in: in `vnext_10k` the verifier's
natural verdict is predicted almost perfectly by the operation name (LEAN_TACTIC 4000/4000
VALID, SOURCE_DERIVATION 2000/2000 UNRESOLVED, OPEN_BRANCH 61/61 INVALID). The matched-triple
construction was chosen in response, and drives operation-name and Mathlib-area mutual
information to 0.000 bits.

### DATASET_V1

5,619 rows from 1,860 parent theorems; exactly balanced VALID/INVALID/UNRESOLVED; labels from
`semantic_state.verify.verify_replay`, never a judge. Four arms: `R_HML` (the frozen view at
`b011511`), `R_TYPED_AST`, `R_LEANLIKE`, `R_STRUCTURED_ENGLISH`. Splits: train 3,000, dev 510,
test_iid 510, plus six OOD splits (alpha-rename, binder depth, dependency depth, state size,
composition, Mathlib domain). No semantic id appears in two splits; theorems never straddle a
split; training excludes the extreme structural strata the OOD splits test.

16 mutation families, all verified to flip the verdict as intended, spanning 7 error classes
plus UNRESOLVED. Mutation family names never reach a render.

### Verification actually executed

- `pytest experiments/max_ev_representation_v1/tests -q` -> **46 passed**
- representation parity gate over all 5,619 rows -> **PASS**: self-fidelity 5,619/5,619 per
  arm (re-render reproduces stored bytes), cross-arm identity 5,619/5,619, label preserved
  after re-parse 5,619/5,619, 0 failures across 16 §5 properties
- leakage audit -> **PASS** on all four arms: answer-word MI 0.000, operation MI 0.000,
  Mathlib-area MI 0.000, no mutation-name or source-ID leakage, surface-statistic decision
  stumps 0.336-0.348 against a 0.3333 majority baseline
- decoded-payload escape audit over DATASET_V1 -> 0 literal escapes in all four arms
- full-scale CPU pipeline run with a synthetic encoder -> headroom gate PASS, paired
  bootstrap and McNemar produce well-formed intervals over 170 parent groups

### The number Stage 1 has to beat

A bag-of-words logistic regression with **no language model** reaches macro-F1 ~0.68 on this
task (per-arm spread 0.021). That, not the 0.333 class prior, is the bar. It is wired into the
harness as a per-arm control and into the headroom gate, and reported as
`probe_minus_own_bag_of_words_macro_f1`. A probe that beats the prior but not bag-of-words has
demonstrated that the task has signal, not that the model reads mathematical state.

### Pre-flight hardening added before the first paid run

Six additions, each closing a way the run could produce a number meaning something other than
it appears to:

- **Model pinned to an immutable commit.** `Qwen/Qwen3-8B` @
  `b968826d9c46dd6066d109eabc6255188de91218` for both model and tokenizer (same repository
  commit). This is also the revision the 50K corpus was tokenizer-preflighted against, so the
  pin preserves continuity as well as blocking an upstream reupload from silently changing the
  experiment.
- **Counterfactual split-isolation gate.** Three levels — semantic family, source theorem,
  canonical fingerprint. **PASS**: 1,873 families = 1,873 source theorems, 3 siblings each,
  0 cross-split leaks at every level, 0 exact and 0 near duplicates.
  `reports/COUNTERFACTUAL_SPLIT_AUDIT.md`.
- **Truncation measured before clipping.** The old check counted
  `len(clipped) >= max_length`, which misclassifies an item exactly at the limit. Now the true
  pre-truncation length is recorded, and any truncation in any arm **aborts the run** rather
  than producing a caveat.
- **Two coarse shortcut controls.** Measured at full scale on CPU (dev macro-F1):
  length-only **0.315–0.335** per arm, structure-count **0.395** shared. Against a 0.333
  majority baseline, neither size/formatting nor coarse record counts is a shortcut — the
  ~0.69 bag-of-words result comes from *which* tokens are present, not from trivial artifacts.
- **Paired minimal-pair evaluation.** Per parent, is `P(VALID | genuine) > P(VALID |
  one-change counterfactual)`, reported per mutation family. Two members of a pair have nearly
  identical lexical statistics, so this is the metric global token statistics cannot fake.
- **Frozen-feature cache.** Keyed on model SHA, tokenizer SHA, dataset hash, renderer commit,
  code hash, max_length, dtype and pooling set; any mismatch is a miss, never a silent reuse.
  float16 on disk, float32 in the probe, with the round-trip cost measured rather than assumed.
  Stage 2's MLP probe, bootstrap re-analysis and diagnostic heads become nearly GPU-free.

### Control ladder measured on CPU (dev macro-F1)

| control | macro-F1 |
|---|---|
| class prior | 0.167 |
| length-only (per arm) | 0.315 – 0.335 |
| structure-count (shared) | 0.395 |
| **bag-of-words (per arm)** | **0.670 – 0.698** |

The gap between structure-count and bag-of-words is where the task's difficulty actually
lives, and it is the interval the frozen transformer has to compete in.

### Stage 1 result (2026-08-27) — EXP_REP_VALIDITY_V1, complete

**Run:** Qwen/Qwen3-8B @ `b968826d9c46dd6066d109eabc6255188de91218`, frozen, linear probe,
three seeds, mid-layer mean pooling (selected on dev from control arms only). One
A100-SXM4-40GB, 0.79 GPU-hours, ~GBP 2.34. Truncation 0 in all four arms.

| arm | IID macro-F1 | info gain (bits) | OOD mean | bag-of-words | probe − BoW |
|---|---|---|---|---|---|
| R_HML | 0.7701 | 0.7206 | 0.6615 | 0.7371 | +0.033 |
| R_TYPED_AST | 0.7664 | 0.7219 | 0.6277 | 0.7445 | +0.022 |
| R_LEANLIKE | 0.7759 | 0.7871 | 0.6847 | 0.7213 | +0.055 |
| **R_STRUCTURED_ENGLISH** | **0.7939** | **0.8104** | **0.7050** | 0.7559 | +0.038 |

**HML minus best control:** IID −0.0238 (CI [−0.065, +0.014], spans zero; McNemar p=0.29),
OOD mean −0.0435, information gain −0.0898 bits.

**Findings, in order of how much they should change the project's beliefs.**

1. **The frozen transformer barely exceeds the lexical control** — +0.022 to +0.055 macro-F1
   over its own arm's bag-of-words. Of the ~0.78 achieved, roughly 0.74 is reachable by
   counting tokens with no model at all. State-comprehension claims must stay weak.
2. **HML is not best on any of the seven splits** and is third of four on IID. The one
   interval excluding zero has HML *worse* than Lean-like on `ood_alpha_rename` by 0.085.
   Every other split is a negative point estimate with an interval spanning zero.
3. **Structured English wins six of seven splits.** If notation helped a pretrained model read
   mathematical state, the arm with no notation should not lead.
4. **No predefined §19 interaction survives** on any axis or split. The hypothesis that HML's
   advantage grows with semantic complexity is unsupported here.
5. **The Lean-like arm is not a memoriser** — its best split is `ood_alpha_rename` (0.784,
   above its own IID), the opposite of the retrieval signature that control was built to catch.
6. **Minimal-pair discrimination is saturated** at 0.96–0.99 for all arms and cannot separate
   them. An instrument finding: one-edit counterfactuals are too easy side by side.

Per §14D the result is preserved as it stands. It is not a reason to redesign the language,
and it is not evidence that HML is worse in general: one task, one model, one probe,
n=1,873 parents.

### GPU status and the capacity move

The original `a100` (`a2-ultragpu-1g`, A100 80GB, europe-west4-a) was stopped to avoid idle
billing during CPU preparation and could not be restarted:
`ZONE_RESOURCE_POOL_EXHAUSTED` on every attempt. Releasing capacity in a constrained zone
does not reserve it, and that is the cost of the stop decision. The A2 family bundles its
accelerator, so `set-machine-type` cannot cross from 80GB to 40GB. Quota was never the
constraint (`NVIDIA_A100_GPUS` limit 16, usage 0 in every region checked); capacity was.

Stage 1 ran on `a100-40` (`a2-highgpu-1g`, A100-SXM4-40GB, us-central1-b). **Both instances
are now TERMINATED.**

The 572 MB feature cache was written on the VM but **could not be retrieved** — repeated scp
failures, ending in SSH refusing connections. It remains on the stopped instance's disk. It is
regenerable for roughly GBP 2.30 if a Stage 2 probe is wanted; the local copy has 5 of 36
shards and should be treated as absent.

### Not yet done

No Stage 2. No MLP probe, no LoRA, no scaling to 20K/50K, per the standing instruction to stop
after Stage 1 and reason over the result first.

## Exact Next Actions

1. **Decide whether Stage 2 is worth buying at all.** The frozen probe exceeds bag-of-words by
   only 2–5.5 points, which is the number that should drive the decision — not the HML-versus-
   control delta, which is small, negative and mostly unresolvable.
2. If Stage 2 proceeds, restart `a100-40` and retrieve the 572 MB feature cache **first**; an
   MLP probe from cache is then GPU-free. Regenerating it costs ~GBP 2.30.
3. Do not redesign the language in response to this result (§14D).
4. If the benchmark is revisited, the two instrument defects to fix are: minimal-pair
   saturation (0.96–0.99, cannot separate arms) and residual lexical solvability
   (bag-of-words ~0.74 on test).
