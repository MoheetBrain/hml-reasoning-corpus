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
