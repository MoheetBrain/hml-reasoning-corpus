# Project Ledger

Append-only. One chronological entry per change. *Created 2026-08-10 alongside
`PROJECT_STATUS.md` to satisfy the Mandatory Commit Continuity Protocol. Entries before this
date are recorded in `docs/HML_RESEARCH_LEDGER.md` and in the Git history; they are not
back-filled here, because inventing a retrospective ledger is exactly the kind of tidy
fiction this file exists to prevent.*

---

## 2026-08-10 — the project cognition ledger enters version control

**Branch:** `codex/minilang-artifact-audit`, on `fc9b2a3`. **Stage:** corpus-side
reconciliation, with corpus responsibilities temporarily held by the integrator while Codex
is unavailable.

**Objective.** Bring the project cognition ledger under version control after auditing it,
and create the two protocol documents this repository lacked.

**Files and systems changed.** New: `experiments/project_cognition/project_memory.yaml`,
`docs/PROJECT_STATUS.md`, `docs/PROJECT_LEDGER.md`. No canonical document, no frozen
experiment, no fixture and no line of `reference_checker.py` was modified.

**What was completed.** The ledger was written in a first pass, then **independently
re-audited by a second pass that did not take the first on trust** — and the second pass
disagreed with it twice. The reported status breakdown was wrong (rejected 14, not 16, and
the six reported statuses summed to 113 against 128 entries, silently omitting 6 deferred,
5 implemented, 4 superseded, 1 testing, 1 proposed), and `meta` recorded a stale HML head.
Both disagreements are recorded in the file rather than quietly fixed. Seven entries were
corrected for staleness, five appended for audit findings, and two more (X134, X135) added
by the integrator for the post-build audit and the HML_OBF withdrawal.

**Decisions and why.** IDs X1..Xn are permanent and are never renumbered or reused. An entry
whose evidence disappears becomes `status: unresolved` with the loss recorded, never
deleted — X105 was moved from `rejected` to `unresolved` with its original reason preserved
verbatim, because the finding it rested on turned out to be a harness defect rather than an
observation about model cognition. The ledger deliberately does **not** become a sixth
canonical document; the canonical five remain integrator-owned.

**Tests and verification actually executed.** Structural re-verification at commit time:
135 entries, ids X1–X135, **no duplicates, no gaps, no dangling cross-references**. All 83
cited absolute paths resolve on disk; all cited commits resolve. Parsed under a strict YAML
subset reader and cross-validated with Ruby's Psych, since PyYAML is not available in this
environment. The reference checker was **not** run here — that runs in the HML repository.

**Results.** The most consequential content finding: a harness defect had been written up as
a finding about model cognition. `HML_OBF`'s obfuscation map substitutes the ordinary English
words `or` and `not` and is applied to the question text, so the one arm that answered
UNDETERMINED on 6/6 items is the one arm whose third answer option was destroyed. Two ledger
entries had recorded "obfuscation stopped the model engaging" as established. It is not, and
the corresponding withdrawal has now landed in the HML repository at `a21fdb7`.

Second finding: `docs/design/EGRAPH_ADOPTION_GATE.md`, cited as the authority for deferring
e-graphs, **never existed**. Enumerating every path in every commit of every branch across
four repositories and the submodule returns no match. Two of its five conditions survive in
prose; three are unrecoverable and were **not** reconstructed.

**Failures and unresolved uncertainty.** The pinned `hml_core` is `5688aba`, five commits
behind production, so every Gold-125 coverage figure in this repository describes a core that
no longer exists. `schemas/semantic_case.schema.json` is unsatisfiable and rejects all 30 of
its own fixtures. Four unscoped absence-of-evidence statements remain uncorrected. None of
these was repaired in this commit.

**Effect on the overall project.** The material the canonical five deliberately compress away
— things parked, killed, conditionally planned — is now under version control and audited,
and the programme's only positive signature for H2 has been traced to a harness defect rather
than to model behaviour.

**Next intended step.** Correct the four unscoped statements; label Gold-125 coverage
historical; decide on the proposed `FX2-*` probe suite; record the e-graph gate as a broken
historical reference; repin `hml_core` and rerun the 30 fixtures.

---

## 2026-08-10 (second entry) — scope corrections and historical coverage labels

**Branch:** `codex/minilang-artifact-audit`, on `8d1d95f`. **Stage:** corpus-side
reconciliation, integrator holding corpus responsibilities.

**Objective.** Stop this repository's absence-of-evidence statements from being read
programme-wide as though evidence does not exist, and stop stale coverage figures from being
read as current.

**Files changed.** `docs/00_HML_MASTER.md`, `docs/04_INTEGRATION_AND_IMPLEMENTATION.md`,
`docs/HML_RESEARCH_LEDGER.md`, `reports/gold125_hml_coverage.md`. No experiment, fixture or
reference checker touched.

**What was completed.** Four statements were locally true and globally misleading. Each is
now explicitly scoped *"in this repository"* and carries the programme-level result. The
correction is not that the evidence exists — it is that the evidence exists **and is negative
or null for HML**, which is worse for the thesis than the original phrasing implied, not
better. Recovered from raw artifacts, all small-N: implication direction SE 5/12 vs HML 1/12
vs generic AST 0/12; next-action, an apparent HML advantage that did not survive independent
replication (Δ 0.000); quantifier scope won by a generic S-expression; HML-EVAL-001 paired
difference 0.000, CI [0, 0].

The sharpest case was `docs/04` line 267 — a bare unscoped bullet inside the **ontology gate**
fact list, doing decision work ("Do not freeze or implement the semantic kernel while this
gate…"). A gate condition asserting that evidence does not exist, when it exists and is
negative, is the worst placement for this class of error.

Gold-125 coverage was labelled `HISTORICAL COVERAGE AT HML 5688aba` in five places, verified
from the submodule tree rather than from prose: `git ls-tree -r 5688aba` contains no
`libraries/` path, while `2af4998` has algebra, calculus and probability. The highest-value
label is on `reports/gold125_hml_coverage.md`, which named no commit anywhere in the artifact.

**Tests and verification actually executed.** Each edit anchored to a verified string and
applied only on an exact match; every replacement confirmed present afterwards. Rendered
output re-read for the two block-quote insertions, which are the ones that break silently.
No test suite exists in this repository to run.

**Failures and unresolved uncertainty.** **No updated coverage number was measured and none
was manufactured.** The pin is still `5688aba`; repinning and re-measuring is a separate
mission. The `FX2-*` probe suite decision, the e-graph broken-reference record and the
unsatisfiable `semantic_case.schema.json` all remain open.

**Effect on the overall project.** The corpus track can no longer reason from a cleaner
picture than the data supports — which was the cognition audit's most consequential finding.

**Next intended step.** Decide on the `FX2-*` probe suite; repin `hml_core` and rerun the 30
fixtures; repair the unsatisfiable action subschema.

---

## 2026-08-10 (third entry) — the ledger had never parsed; third audit, 14 corrections, X136–X148

**Branch:** `codex/minilang-artifact-audit`, on `d5b5ffa`.

**Objective.** Audit the cognition ledger against the newest evidence and append the
architectural findings from the three-source audit and the Phase-I repairs.

**The defect found first.** The file committed at `8d1d95f` **has never been valid YAML**.
X134 and X135 were written two spaces too deep, so they were block-mapping content of X133
rather than sequence entries; Ruby Psych fails at line 2275. Verified against the committed
object, not merely the working tree. The verification run at commit time was a regex scan
over `- id:` lines, which cannot see indentation structure — **a check that validated the
artefact against itself**, the failure mode X133 records and this repository has now hit
three times. Repaired by de-indenting 52 lines; no content changed.

**What was completed.** 14 existing entries corrected in place, every original `reason:`
preserved verbatim as a prefix. Two are substantive: **X84 is CONTRADICTED** — its
four-dimension evaluation proposal survives as two, because blind adjudication of 260 PRM
candidates collapsed `GOAL_RELEVANCE` and `INFORMATION_GAIN` into `PROGRESS`; **X94 is
partially discharged** — LeanDojo acquired real provenance, so the "no repository
provenance" discrepancy drops from six datasets to five.

Appended **X136–X148** for the frame condition, effect-over-label, in-place transformation,
goal ancestry, `Candidate` ≠ `ActionCandidate`, dynamic-k, validity ≠ quality,
no-acceptable-action, the narration filter, the separable warrant, dormant failure/repair,
the interpretation layer, and the three compression hypotheses kept separate. Three briefed
items already existed and were **reconciled rather than duplicated**.

**Corrections to my own briefing, recorded because they matter.** I briefed "six probes VALID
at `7c9137a`" — **five** were accepted; the sixth was the appended-`UNKNOWN` detection bypass
returning UNRESOLVED, which is a suppression, not an acceptance. All six were repaired at
`8bcd9a5`. `created_by_action` appears nowhere in either repository — it came from the
mission brief, not from an artifact, and was recorded as unsourced rather than adopted.

**Tests and verification actually executed.** Ruby Psych parse (the check that caught this);
148 entries; X1–X148 contiguous; 0 duplicates; 0 dangling cross-references; 0
self-references; `next_free_id: X149`; all 94 cited absolute paths resolve; all 15 cited
commit hashes resolve in their stated repository; all 133 pre-existing `reason:` fields
verified to retain their original text.

**Failures and unresolved uncertainty.** One proposed Gold-125 edit from X131 **did not
land**: `reports/gold125_reasoning_synthesis.md` §K still carries an unlabelled copy of the
coverage table. Recorded, not fixed.

**Next intended step.** Fix the remaining unlabelled coverage table; repair the unsatisfiable
`semantic_case.schema.json`; adopt the second-generation fixture suite.

---

## 2026-08-11 — the frozen schema was unsatisfiable; repaired, and the freeze record amended rather than rewritten

**Branch:** `codex/minilang-artifact-audit`, on `f7d85bc`.

**Objective.** Repair `schemas/semantic_case.schema.json`, which rejected every case it
describes, and add the independent validation whose absence let it survive.

**What was wrong.** `$defs/action` declared `"additionalProperties": false` alongside a
15-name `required` array and **no `properties` block**, so every member key was "additional"
and forbidden. It passes `check_schema` — it is *valid* JSON Schema and *unsatisfiable*, which
is why "the schema is valid" was true and useless. Measured: it rejected **0/230** cases (30
acceptance, 40 DEV, 160 FINAL). A structural walk found `action` is the only subschema in the
corpus with that shape.

**Why it survived.** Nothing validated against it. `grep -rn 'jsonschema|check_schema|validate\('`
over `experiments`, `tests`, `scripts`, `src` returned **zero hits**; the schema's only
appearance in code was being hashed into the freeze manifest. The corpus also had **no
dependency manifest at all**, so a validator could not have been installed even if one had
been written.

**The repair, and why not the cheaper one.** Two candidates: drop `additionalProperties`
(R1), or add the `properties` block (R2). A differential over mutated cases shows R1 **weakens**
the schema — it accepts an action with an extra key, which the original refused. R2 preserves
every constraint the author expressed, and the membership half is a verbatim restatement of
`required`: the 15 names equal both the union *and* the intersection of `action` keys across
all 230 cases. Types were added only where all 230 agree. `output_id` was deliberately left
open: the fixtures show it is always the string `"c1"`, but `reference_checker.py:204,488`
branches on a falsy `output_id` with distinct semantics, so instance evidence and code
evidence conflict and nothing was invented.

**The freeze-manifest question, adjudicated.** Repairing a hashed artifact broke
`test_freeze_manifest_hashes_every_protocol_artifact` — exactly one of 412 entries. The
decisive fact is that **`reference_checker.py` never reads the schema** (zero matches for
"schema"), so it is not on the verdict path and the repair changes no experimental result.
Leaving it broken would preserve the hash of a defect; overwriting the hash silently would
rewrite history. So the manifest was **amended**: the entry now carries the new hash *and* a
`superseded_sha256` with the reason, and `metrics.json` records the superseded manifest hash
alongside the new one. The freeze record still shows what was frozen and what replaced it.

**Tests and verification actually executed.** `pytest tests/` in an isolated venv
(jsonschema 4.26.0): **58 passed, 0 failed** (was 52 passed before the new file; 57 passed /
1 failed at the moment of repair, that one being the manifest hash). New `tests/test_schemas.py`
pins: the schema is valid for its *declared* draft (resolved with `default=None` so an
unrecognised `$schema` fails rather than silently falling back); 30/30 acceptance fixtures
validate; 200/200 DEV+FINAL cases validate; a **general** guard that fails on any subschema
declaring `additionalProperties: false` with a `required` name covered by neither
`properties` nor `patternProperties`; a non-vacuity test proving that guard fires on the
original defect and on a partial one; and a negative control rejecting an extra key, a
missing required key, five wrong-typed values and a bad enum.

**Failures and unresolved uncertainty.** Three further weaknesses found and **not** fixed,
because each changes acceptance behaviour beyond the brief: `$defs/source`, `$defs/claim` and
`$defs/evidence` have `required` but no `additionalProperties`, so a typo'd key passes
silently (`source` and `claim` could be closed with no loss; `evidence` could not — four of
its ten observed keys are genuinely optional). And large regions of every case —
`state.obligations`, `candidates`, `branches`, `goals`, and all 15 `action` sub-objects — are
declared `{"type": "object"}` with no value schema, so they pass because nothing is checked,
not because they were verified.

**Next intended step.** Adopt/freeze the FX2 suite; decide whether to close the three open
`$defs`.

---

## 2026-08-11 (second entry) — FX2: the second-generation acceptance suite

**Branch:** `codex/minilang-artifact-audit`, on `0d82ce6`.

**Objective.** Freeze an additive suite covering the behaviours the frozen thirty cannot
reach, without touching them.

**What was completed.** 40 fixtures across 9 families — domain subtyping, warrant envelope,
frame condition, scope containment, branch/join, unknown masking, trust modes, candidate
rejection, malformed input — plus a schema that `$ref`s the frozen one's structural `$defs`,
a manifest with hashes, a README, and validation on both sides.

**Decisions and why.**

*Expectations are hand-written.* Every expected verdict is stated in `build_fx2.py` from the
semantic contract before any verifier runs. Generating them by execution would record what
the code does rather than what it should do. Production then measured **40/40** against them.

*FX2 gets its own schema rather than widening the frozen one.* The frozen schema is a hashed
artifact describing a frozen experiment; extending its `semantic_focus` enum to cover FRAME,
TRUST and MALFORMED would misrepresent what that experiment tested. The v2 schema `$ref`s
the base's `$defs` so there remains exactly one definition of a case.

*FX2 declares its own `source`.* The frozen source block requires a MATH dataset row, a
source hash and a `gold125_overlap` flag. FX2 cases are constructed to exercise an invariant,
not drawn from a dataset row, and filling those fields would be **fabricating provenance**.

*`domain` is optional on a v2 claim.* The frozen schema requires it, making "this claim
carries no domain" inexpressible — yet D-048 established that absence is semantically
meaningful (`UNRESOLVED`) and distinct from a wrong domain (`INVALID`). A schema that cannot
express the absence cannot describe a case testing it.

**Tests and verification actually executed.**

| check | result |
|---|---|
| FX2 vs production HML (hand-written expectations) | **40/40** |
| FX2 vs the v2 schema | **38/40**; two MAL fixtures deliberately schema-invalid |
| strict RFC 8259 parse, Python + **independent Ruby parser** | both OK |
| frozen thirty byte-unchanged | asserted by test |
| id collision with the frozen thirty | none |
| corpus `pytest tests/` | **63 passed** |
| HML `pytest tests/semantic_state` | **379 passed** |

**Failures and unresolved uncertainty.**

*An earlier build was not valid JSON.* It embedded a `NaN` literal, which RFC 8259 does not
permit; an **independent Ruby parse rejected the entire file**. Caught before commit, by the
independent-validator rule. `NaN` is now carried as a `materialise` instruction and the
generator emits with `allow_nan=False`, so writing a non-standard literal is an error at
build time rather than a file nobody else can read.

*One mutation survives FX2, and is classified rather than papered over.* Removing the
null-branch-conclusion guard fails **0** fixtures, because a non-null published proposition
makes the mismatch check catch a null conclusion anyway — the guard is verdict-equivalent
and exists for its diagnostic, which the HML-side unit test pins. Writing a fixture to
manufacture a kill would have raised a score and taught nothing.

*One fixture is schema-valid and semantically malformed.* `FX2-MAL-UNHASHABLE-REFUSE` passes
the schema because `obligations_created` is typed `array` with no item constraint, and is
still refused by the verifier. It is kept for exactly that contrast: **passing the published
schema is not the same as being a well-formed transition.**

**Next intended step.** The 22 surviving mutations from the earlier census; then
P-01/P-02/P-03; then the semantic freeze, release manifest and tag.

---

## 2026-08-11 (second entry) — schema hardened as far as evidence supports; two FX2 truthfulness defects corrected

**Branch:** `codex/minilang-artifact-audit`, on `a2910c4`.

**Objective.** Harden the case schema only where the evidence supports it, and correct two
places where our own artifacts described reality falsely.

**Schema hardening.** `$defs/claim` **closed** — the one object where four independent
sources agree exactly on six fields (`required`, the frozen union *and* intersection over 736
instances, FX2's 76, and `semantic_state.model.Claim`). `source` **left open**, which
*refutes* the prior recommendation to close it: `SEMANTIC_STATE_CONTRACT.md` §4 names it among
fields "the corpus may extend at any time", and closing on a complete-looking sample against a
contract that declares the field extensible is precisely the trap. `evidence` left open —
four of ten observed keys are genuinely optional, and `EvidenceRecord` models six keys plus an
explicitly kind-specific `payload`. Value schemas were wired for the previously unvalidated
regions; `candidates`, `branches`, `obligations` and `goals` were **not** closed, because
frozen, FX2 and the dataclasses give strictly growing key sets — the corpus is demonstrably
not a complete sample.

**Why it mattered.** Of 28 schema-legal malformed shapes, **13 crashed the reference checker**
and **one flipped a verdict**: `evidence.trusted = "false"` as a *string* is truthy, so a
truthy spelling of falsehood licensed a VERIFIED promotion. Before: 0/28 rejected. After:
26/28. The two survivors are the documented open objects.

**Two FX2 truthfulness defects, corrected.** The `MAL` fixtures recorded the frozen reference
checker's behaviour as `REFUSED`; it **crashes**. Each now carries
`historical_reference_behaviour: CRASH` alongside `hardened_hml_behaviour:
CONTROLLED_REFUSAL`. A hardened implementation may be safer than its historical oracle; that
does not license describing the oracle falsely. And `semantic_case_v2.schema.json`'s
description claimed states, evidence and source were `$ref`'d from the frozen schema — only
`action` is, and `evidence` is **entirely unvalidated**. Corrected to match executable reality.

**Tests and verification actually executed.** `pytest tests/` **68 passed**; frozen **230/230**
validate; FX2 **40/40** match their declared `schema_valid`; HML `tests/semantic_state` **405
passed** against the regenerated suite. Manifest self-check: sidecar matches, **0 mismatches
across 412 entries**. The schema amendment chain now holds **two** superseded hashes —
`786010…` (the original unsatisfiable schema) and `2401eb…` (amendment 1) — as a chronological
list rather than an overwrite.

**Failures and unresolved uncertainty.** `action.obligations_created` could not be constrained:
`FX2-MAL-UNHASHABLE-REFUSE` carries `[[1], [2]]` and declares `schema_valid: true`, so
constraining it would flip a frozen artifact's declared flag. Left open and pinned by a test.
Statuses, `kind`, `supports_rule` and domain names are **not** enumerated anywhere: the
reference checker treats unrecognised values as fail-closed while `neutral.py::_enum` refuses
them, so two admissible sources disagree and the schema stays permissive. And
`build_benchmark.py` would silently erase both amendment records if re-run — pre-existing, not
newly introduced, and not currently runnable.

**Next intended step.** Final post-integration mutation census, then P-02/P-03 Lean witness
audits, then the freeze gate.

---

## 2026-08-17 — final structural-source falsification audit; data gate refused

**Branch:** `codex/structural-final`, begun at `91fdda3`. **Data verdict:**
`INSUFFICIENT_STRUCTURAL_DATA`.

**Objective.** Build up to 50,000 fresh, information-matched HML/neutral action-selection
records for the final conjunctive representation hypothesis, or refuse the build if the
required structural state did not exist. No model training and no semantic-authority edit
were authorized.

**What was inspected.** The raw LeanDojo Benchmark 4 source at Mathlib
`29dcec074de168ac2bf835a77ef68bbe069194c5`, its 241,265-row canonical export (SHA-256
`8ac0ce…869`), the prior VNext 10K and excluded parent history, acquisition audits for five
additional Lean/proof-text sources, and the PRM800K process corpus. The current VNext
authority `68178f0` was inspected from consolidation checkout `73184c5`, whose `src/` is
byte-identical. `hml_core` remained untouched.

**Census.** A 24-worker mmap scan of the canonical export completed at about 39k rows/s.
The complete raw source contains 259,580 transitions; excluding 42,957 old-history rows
leaves 216,623 fresh exact before/action/after transitions in 57,874 non-empty trajectories
(median length 2, maximum 127 fresh). Fresh source structure includes 1,224 multi-goal
before states, 14,736 goal-creating transitions, 92,471 `case`-scoped before states, 42,409
nested scopes and 2,242 conservative complementary case pairs after a transition.

**Why the build was refused.** The same source contains no claim dependency graph, no HML
obligation distinct from a Lean goal, no candidate lifecycle/status state, no epistemic
transition, and no general branch representation with predicate, membership and coverage.
Lean `case` labels are scopes, goals are not obligations, and the global declarations in
`annotated_tactic[1]` are selected by the gold action and would leak if promoted to state
dependencies. The prior VNext rich fields are concentrated in its 1,000-row synthetic hard
tail and are development history. Filling the gap would require invention or synthetic
replacement, both forbidden.

**Artifacts and verification.** Frozen admission and complexity specifications, two machine
censuses, relation/trajectory/data audits, explicit not-applicable parity/leakage/Unicode/
token audits, rejection/rung manifests, and an executable STOP handoff live under
`data/hml_structural_final/`. The package has a deterministic per-file SHA-256 manifest and
tests for census conservation, absence of fake rungs, manifest integrity, and literal UTF-8.
No model-facing rows, empty “passing” views, or synthetic stress records were emitted.

**Effect on the project.** This result neither supports nor falsifies HML: it falsifies the
assumption that the currently acquired natural/formal corpora can instantiate the final
test. The representation kill rule remains untriggered because no fair matched experiment
exists.

**Next intended step.** One data-acquisition experiment only: obtain or instrument a fresh
replayable prover-state source that explicitly emits claim dependencies, obligations
distinct from goals, branch predicate/membership/coverage, and candidate lifecycle/status;
then rerun the frozen gate before any Qwen training.

---

## 2026-08-22 — final 50K paired teaching corpus built; model evaluation handed to FABLE

**Branch:** `codex/hml-50k-final`, begun at
`3337217eb2cc9460b91ead15e4a67a420ecdcd8a`. **Data verdict:** `HML50K_READY`.

**Objective.** Give the final HML representation-scaling test adequate clean teaching
exposure: at least 50,000 worked TRAIN examples in literal-UTF-8 HML and an equally strong
structured-neutral control, with separate parent-disjoint holdouts. No model training,
cloud compute, HML semantic change, or modification of earlier experiment results.

**Source decision.** Ten local source families totaling 4.31M non-deduplicated records were
inventoried. The core uses only exact LeanDojo `(state, tactic, state-after)` traces because
they already exceed the count gate and have the strongest task-native semantics. PRM800K,
MATH, AMPS and proof-text corpora were not mixed in merely to match preferred proportions.
Every core row is labelled `FORMAL_TRACE`, never upgraded to freshly replayed
`FORMAL_VERIFIED`. Premise annotations were recovered exactly from the pinned raw export for
all 56,000 rows and retained only as action-derived audit metadata.

**Build.** Exactly 50,000 TRAIN, 3,000 DEV, and 3,000 FINAL canonical records were emitted
under `data/hml_50k_final/`, with paired `HML_WORKED_UTF8` and
`STRUCTURED_NEUTRAL_WORKED` views for action selection, state-delta prediction, validity
judging, and worked continuation. Six-candidate hard-negative sets are deterministic and
identical across views; alternatives are `PLAUSIBLE_UNEXECUTED`, not invented invalids.
TRAIN rungs are nested 10K ⊂ 30K ⊂ 50K. HML_TREE and crossed targets are absent. A 5,000-row
structural-stress subset preserves the strongest source-supported examples without adding
branch, obligation, or candidate-lifecycle semantics the source does not contain.

**Failed gates that changed the build.** The first candidate audit appeared to show an 80%
shortest-action shortcut; decomposition showed that was mostly equal-length ties, while the
real unique-shortest rate was 1.47% and deterministic shortest-first accuracy 15.79% versus
16.67% chance. Seventy-four rows where the gold tactic naturally occurred verbatim in the
state were nevertheless excluded. The first Qwen tokenizer pass rejected 32 over-length
records; replacements introduced two continuation-only overages. All 34 are now pinned in a
preflight exclusion file and removed intact—none was truncated. The accepted maximum raw
input+target length is 6,134 tokens.

**Independent verification.** HML authority `68178f0` passed 20/20 golden fixtures.
Independent post-build checks passed 56,000 candidate-order comparisons, 112,000 semantic
state comparisons, 224,000 action-envelope comparisons, all requested field mutations,
and five manual FINAL inspections. There are zero duplicate IDs, cross-split parent or
near-signature overlaps, old-parent FINAL contaminations, exact delta-target leaks, gold
actions outside candidate blocks, JSON Unicode escapes, or raw rows over 6,144 tokens.
Fourteen million literal non-ASCII codepoints were observed. The primary HML input is 10.2%
more expensive than Neutral; this is recorded, not normalized away.

**Limits.** This is a Lean-only teaching corpus, not evidence that HML works. The source
still lacks the rich structural families required by the earlier conjunctive structural
hypothesis, so the 2026-08-17 `INSUFFICIENT_STRUCTURAL_DATA` verdict stands. Lexical overlap
alone scores 51.8% on action selection; FABLE must report that baseline. Candidate
alternatives are unexecuted, so the judge task is FORMAL_TRACE versus UNRESOLVED rather than
valid versus invalid.

**Next intended step.** Claude/FABLE runs one-seed Qwen3-8B BF16 HML10K vs Neutral10K using
the unchanged FINAL set and stops if HML is flat/worse. Proceed to 30K and 50K only if the
learning-curve separation continues. This repository does not train the model.

---

## 2026-08-26 — repository checkpoint for context-loss recovery

**Branch:** `codex/reasoning-layer-discovery`, parent HEAD `d6f03ea`.

The external frozen `FINAL_HML_SIGNAL` result at Hamiltonian Lang commit `701f99e` is now
recorded in repository memory: two-seed HML10K mean 85.75%, Neutral mean 50.20%, delta
**+35.55pp**, parent-clustered 95% CI **[+33.53,+37.50]pp**; seed deltas +35.20pp and
+35.90pp. Exact frozen report and protocol copies, with source hashes, were added under
`experiments/final_hml_signal/`.

The headline remains a depth-conditioned one-step action-selection result, not a
free-running or long-horizon theorem-solving claim. A complete forensic validation is
required and 30K is paused. Repository recovery now explicitly requires `AGENTS.md`,
`RESEARCH_STATE.md`, this ledger, `PROJECT_STATUS.md`, `STATUS.json`, and Git state rather
than chat history.

Later evidence is preserved rather than overwritten: the initial forensic audit omitted
two items in the stricter checklist; the frozen common-envelope control subsequently found
HML -2.77pp versus Neutral and attributed the original headline to envelope asymmetry; and
the later free-running solver calibration stopped at RAW 2/48. The next action is forensic
reconciliation of these frozen results, not new training, 30K, semantic redesign, or a new
experiment.

## 2026-08-27 — max-EV representation experiment: instrument built, two defects found, no GPU spent

**Branch:** `claude/max-ev-representation-experiment-v1` (from `codex/reasoning-layer-discovery`).
**Stage:** CPU preparation for `EXP_REP_VALIDITY_V1`; A100 Stage 1 not yet run.

**Objective.** Build an instrument capable of answering whether frozen HML makes mathematical
state easier for a pretrained model to read than matched alternative representations — and
determine, before buying GPU time, whether such an instrument is possible on the existing
corpus.

**Files and systems changed.** New tree `experiments/max_ev_representation_v1/` only
(`canon/`, `arms/`, `mutate/`, `audit/`, `dataset/`, `harness/`, `tests/`, `reports/`,
`run_gpu_experiment.sh`, `README.md`), plus `docs/PROJECT_STATUS.md` and this ledger. No
historical manifest, dataset, audit or result was modified. Nothing in `hamiltonian-lang` or
`hml-standard` was modified; the frozen renderer is called, never re-implemented.

**What was completed.**
- Decoded-payload Unicode audit (`audit/unicode_payload.py`) with 15 regression tests,
  including one that requires the audit to FAIL the historical artifact the old audit passed.
- Canonical builder: decomposes a recorded Lean tactic state into typed claims, a goal, a
  branch and a real dependency graph. 99.9% of 20,000 records decompose cleanly.
- Four representation arms, each with a reader; parity proved by re-parsing the rendered text.
- 16 causal mutation families plus an uncited-distractor stage; all labels from the frozen
  verifier.
- DATASET_V1: 5,619 rows, exactly balanced, nine splits including six OOD axes.
- PyTorch probe harness: linear and MLP probes, class-prior and bag-of-words controls,
  information-gain and calibration metrics, paired bootstrap over parents, McNemar.
- A100 driver that verifies dataset and renderer hashes, starts the instance, smoke-tests,
  runs, retrieves artifacts and stops the instance.

**Decisions made and why.**
- *Checkpoint is `Qwen/Qwen3-8B`, not a Gemma-family model as the mission preferred.* The
  prior evidence this must connect to is Qwen: the 50K corpus was tokenizer-preflighted
  against Qwen3-8B, its token-exclusion file is Qwen-specific, and the invalidated -3.41pp
  result is the Qwen3-8B kill test. Gemma appears three times in the experiment repo and
  nowhere in this corpus's calibration. Recorded as a deliberate deviation.
- *Labels are built by mutation rather than taken from the corpus.* In `vnext_10k` the
  verifier's natural verdict is predicted almost perfectly by the operation name alone
  (LEAN_TACTIC 4000/4000 VALID, SOURCE_DERIVATION 2000/2000 UNRESOLVED, OPEN_BRANCH 61/61
  INVALID). Matched triples drive operation-name and area mutual information to 0.000 bits.
- *The canonical state is decomposed rather than used as wrapped.* Measured over 20,000
  records the 50K canonical state has 1 claim and nothing else, so eight of ten invariants
  are vacuous and the four arms would differ only in how they wrap one opaque string.
- *Propositions are held to a single line.* A printed tactic state contains newlines, and the
  line-oriented HML view would have to escape them while a free-form arm showed them
  literally — reintroducing the §24 asymmetric-escaping confound in miniature.
- *Uncited distractors are injected into every item.* `UNKNOWN` initially carried 0.918 of the
  1.585 available bits. Since the verifier's unknown collection is dependency-scoped (D-049),
  an uncited unknown genuinely does not make a transition UNRESOLVED, so this converts "spot
  the word" into "check which record carries it" — the rule the verifier implements.
- *Record order is excluded from the parity comparison, and nothing else is.* The frozen view
  emits its own order; `SemanticState` maps id to record and the verifier never reads order.
  A dedicated test pins this so the exemption cannot silently widen.

**Tests and verification actually executed.**
- `PYTHONPATH=. .venv/bin/python -m pytest experiments/max_ev_representation_v1/tests -q`
  -> **46 passed** (one earlier failure was a wrong assertion in my own test, corrected).
- Parity gate, all 5,619 rows -> **PASS**. Self-fidelity 5,619/5,619 per arm; cross-arm
  identity 5,619/5,619; label preserved after re-parse 5,619/5,619; 0 failures over 16
  properties.
- Leakage audit, all 5,619 rows -> **PASS** on all four arms. Answer-word MI 0.000,
  operation MI 0.000, area MI 0.000, no mutation-name or source-ID leakage; surface stumps
  0.336-0.348 vs 0.3333 baseline; highest single-token MI 0.082 bits of 1.585.
- Payload escape audit of the historical 50K -> 280,000/280,000 HML rows contaminated,
  0/280,000 neutral rows, 12,995,134 escapes, 15.96%-25.39% of prompt by task.
- Payload escape audit of DATASET_V1 -> 0 in all four arms.
- Full-scale CPU pipeline run with a synthetic encoder -> completes; headroom gate PASS;
  paired bootstrap over 170 parent groups and McNemar both well-formed.
- **GPU: not run.** No Stage 1 result exists.

**Failures and unresolved uncertainty.**
- Residual lexical solvability is real: a bag-of-words model with no LLM reaches macro-F1
  ~0.68. The task is therefore substantially token-solvable, and the meaningful quantity in
  Stage 1 is each arm's margin over its own bag-of-words control, not over the class prior.
  This is a limitation of the benchmark, reported rather than hidden.
- Structural OOD axes are narrow: `max_dependency_depth` spans 0-6 with a top decile of 3, so
  "unseen depth" means train <=2 vs test >=3. `n_claims` (train <=24, test up to 81) is the
  strongest axis.
- Arms differ by up to 2x in length. This is intrinsic to the notations and is recorded and
  analysed (§19/§20) rather than equalised.
- The alpha-rename OOD split doubles as the only control against Mathlib memorisation, which
  matters most for the Lean-like arm. If that arm wins on IID but not on alpha-rename, the
  IID win should be read as retrieval.
- `HML-VER-002` remains untested in the Standard; unrelated to this work and unchanged.

**Effect on the overall project.** The 50K representation result is now formally invalidated
with measured evidence, so the project's only quantitative HML-versus-control datapoint is
withdrawn rather than left ambiguous. A replacement instrument exists and passes its own
blocking gates. The scientific question remains open: no evidence has yet been produced either
way about whether representation is a causal capability variable.

**Next intended step.** Run A100 Stage 1 via `run_gpu_experiment.sh`, read the headroom gate
and the bag-of-words margin before the arm comparison, and follow the §14 decision table. Do
not start Stage 2 automatically.

## 2026-08-27 (later) — pre-flight hardening before the first paid GPU run; GPU still unavailable

**Branch:** `claude/max-ev-representation-experiment-v1`.
**Stage:** `EXP_REP_VALIDITY_V1` pre-flight complete. A100 Stage 1 still not run.

**Objective.** Close the remaining ways the first paid run could produce a number that means
something other than what it appears to, and make Stage 2 nearly GPU-free.

**Files and systems changed.** New: `audit/counterfactual_splits.py`,
`harness/cache.py`, `harness/shortcut_controls.py`, `harness/interactions.py`,
`tests/test_gates_and_cache.py`, `reports/COUNTERFACTUAL_SPLIT_AUDIT.md`,
`reports/PREREGISTERED_ANALYSES.md`, `reports/CPU_PREPARATION_GATE.md`,
`reports/model_pin.json`. Modified: `harness/extract.py`, `harness/stage1.py`,
`run_gpu_experiment.sh`, `docs/PROJECT_STATUS.md`. No historical artifact touched; no change
to `hamiltonian-lang` or `hml-standard`.

**What was completed.**
- Model pinned to `Qwen/Qwen3-8B` @ `b968826d9c46dd6066d109eabc6255188de91218`, resolved from
  the Hugging Face API. Model and tokenizer are the same repository commit.
- Counterfactual split-isolation audit at three levels, wired into the driver as a hard gate.
- Truncation now measured on the pre-clip length; any truncation in any arm aborts the run.
- Length-only and structure-count coarse controls.
- Paired minimal-pair evaluation with per-mutation-family breakdown.
- Frozen-feature cache with full-provenance keying and a measured float16 round-trip cost.
- Predefined §19 interaction analyses, written and committed **before any result exists**.

**Decisions made and why.**
- *Cache disabled for smoke runs.* A capped run holds a prefix of each split, so its tensors
  are not the tensors a full run needs; sharing a key would poison the full run's cache.
- *Structure-count control computed once, not per arm.* The counts describe the semantic
  object, which is identical across arms by the parity gate. Computing it per arm would have
  invented four numbers where there is one fact.
- *Length axis for the interaction test is the HML render's token count.* The question is
  whether HML's advantage changes with how long HML's own render is.
- *Number of obligations recorded as untestable rather than stratified.* It is 0 for every
  item — recorded Lean tactic states carry no proof debt — so §19's obligation-count axis
  cannot be tested on this corpus, and saying so beats binning a constant.

**Tests and verification actually executed.**
- `PYTHONPATH=. python -m pytest experiments/max_ev_representation_v1/tests -q`
  -> **65 passed** (was 46; 19 new tests for the gates, controls and cache).
- Counterfactual split audit over the built dataset -> **PASS**: families_total 1873,
  source_families_total 1873, cross_split_family_leaks 0, cross_split_source_family_leaks 0,
  exact_duplicate_leaks 0, near_duplicate_leaks 0, siblings_per_family {3: 1873}.
- Full-scale CPU control ladder (dev macro-F1): class prior 0.167; length-only 0.3149-0.3349
  by arm; structure-count 0.3947; bag-of-words 0.6701-0.6982 by arm.
- Minimal-pair machinery exercised end to end; per-family breakdown produced.
- Harness re-parsed under `ast.parse(feature_version=(3,10))` -> all GPU-side modules
  compatible with the A100 image's Python 3.10.
- Interaction analysis run end to end on a synthetic-encoder result; produces well-formed
  bootstrap intervals over parent groups.
- **GPU: still not run.** `gcloud compute instances start a100` returns
  `ZONE_RESOURCE_POOL_EXHAUSTED` / STOCKOUT for `a2-ultragpu-1g` in europe-west4-a. Four
  attempts so far; the driver retries every 180s.

**Failures and unresolved uncertainty.**
- The A100 is unavailable. This is a direct consequence of stopping it to avoid idle billing:
  releasing capacity in a constrained zone does not reserve it. Nothing has been spent and
  nothing is lost, but the run cannot proceed until capacity returns or the instance is moved
  to a different machine type or zone — both of which change the user's infrastructure and
  have not been done without asking.
- The synthetic-encoder numbers throughout remain pipeline tests, not evidence about Qwen,
  HML, or representation. They are labelled as such wherever they are recorded.
- Bag-of-words at ~0.69 remains the substantive limitation: the task is materially
  token-solvable, and any state-comprehension claim must be read against that line rather than
  against the class prior.

**Effect on the overall project.** The instrument is now hardened to the point where the first
paid run is worth buying: every gate that could invalidate it is mechanical and passing, and
the feature cache means the money buys hidden states usable for every later probe rather than
one number. No scientific claim has been added or withdrawn.

**Next intended step.** Acquire GPU capacity, then run the driver unchanged: it gates on the
split audit and renderer identity, runs a 32-row real-model smoke, checks truncation, runs
Stage 1 with three seeds and a linear head, retrieves results and cache, and stops the
instance. Stop after Stage 1.

## 2026-08-27 (evening) — EXP_REP_VALIDITY_V1 Stage 1 complete; HML does not lead

**Branch:** `claude/max-ev-representation-experiment-v1`.
**Stage:** Stage 1 complete. Stopped there by instruction; no Stage 2 started.

**Objective.** Run the first paid experiment: does frozen HML make mathematical state easier
for a pretrained model to read than matched alternative representations?

**Files and systems changed.** New: `harness/report_stage1.py`,
`reports/STAGE1_RESULT.md`, `results/stage1/EXP_REP_VALIDITY_V1_linear.json` and its
interactions file, `results/logs/`. Modified: `run_gpu_experiment.sh` (retargeted to
`a100-40`/us-central1-b, batch-tokens 8192, torchaudio removal), `harness/extract.py`,
`harness/stage1.py`, `docs/PROJECT_STATUS.md`, this ledger.

**What was completed.** A full Stage 1: Qwen/Qwen3-8B @ `b968826d9c46dd6066d109eabc6255188de91218`,
frozen, linear probe, seeds 0/1/2, mid-layer mean pooling selected on dev from control arms
only, all seven evaluation splits, on one A100-SXM4-40GB.

**Decisions made and why.**
- *Moved to A100-40GB in us-central1-b.* The 80GB instance became unobtainable after being
  stopped, and the A2 family bundles its accelerator so no in-place conversion exists. 40GB is
  ample: peak VRAM was 20.5 GB of 40.
- *Removed torchaudio/torchvision on the VM.* Upgrading transformers to 5.16.1 pulled
  torchaudio 2.11 against the image's torch 2.9.1, an ABI break failing with
  `undefined symbol: torch_library_impl`. Neither is needed for a text model.
- *Stopped the GPU with the cache unretrieved.* After ~20 minutes of failed transfers ending
  in SSH refusing connections, continuing to hold a paid GPU open for a regenerable artifact
  was the wrong trade. The cache persists on the stopped instance's disk.

**Tests and verification actually executed.**
- Pre-GPU gates on the real run: dataset hashes 9/9 match; counterfactual split isolation
  PASS (0 leaks at all three levels); renderer identity `b011511` confirmed.
- Smoke test on the real model: truncation 0 in all four arms; no NaN/Inf; results written.
- Full Stage 1: **truncation 0 in all four arms** (tokens_max 3386-5132 against 8192 context);
  float16 round trip max abs error 2.98e-08, std shift 0.0 — bf16-derived features are exactly
  representable in fp16, so the cache is lossless rather than merely tolerable.
- Headroom gate PASS: control dev macro-F1 0.7957 against a 0.95 ceiling and 0.40 floor.
- Wall: 2860 s extraction, 0.79 GPU-hours total, ~GBP 2.34.

**Results.** IID macro-F1: Structured English 0.7939, Lean-like 0.7759, **HML 0.7701**,
Typed AST 0.7664. HML minus best control: IID -0.0238 (CI [-0.065, +0.014], McNemar p=0.29),
OOD mean -0.0435, information gain -0.0898 bits. HML is not best on any of seven splits; the
only interval excluding zero has it worse than Lean-like on `ood_alpha_rename` by 0.085.
Probe minus own-arm bag-of-words: +0.022 to +0.055. No predefined §19 interaction has a CI
excluding zero on any axis or split.

**Failures and unresolved uncertainty.**
- **The headline limitation is the lexical control, not the arm ordering.** The frozen
  transformer exceeds bag-of-words by only 2-5.5 points, so Stage 1 mostly demonstrates that
  the task carries lexical signal, not that the model reads mathematical state.
- Minimal-pair discrimination saturated at 0.96-0.99 across all arms; the metric cannot
  separate representations and needs harder pairs to be informative.
- The feature cache (572 MB, 36 shards) was not retrieved. Only 5 shards are local; treat the
  local copy as absent.
- `CORPUS_COMMIT` reads `unavailable` in the run manifest because the VM has no git checkout.
  Data provenance is exact via the nine per-split SHA-256 digests, verified before GPU start;
  code provenance is the working tree at launch, committed here.
- Structural OOD axes remain narrow, as recorded previously.

**Effect on the overall project.** The project now has its first uncontaminated quantitative
comparison of HML against matched controls. It does not support an HML advantage on this task:
HML places third of four, the differences are small and mostly unresolvable, and the arm that
leads is plain structured English. Per §14D the result stands as recorded and is not a reason
to change the language.

**Next intended step.** Decide whether Stage 2 is worth buying, weighing the 2-5.5 point
transformer-over-lexical margin rather than the arm deltas. If it proceeds, retrieve the cache
first so the MLP probe is GPU-free. Do not redesign the language in response to this result.
