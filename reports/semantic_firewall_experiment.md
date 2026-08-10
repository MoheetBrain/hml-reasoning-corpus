# Semantic Firewall experiment and Claude builder handoff

## Status

**Experiment complete.** This is a corpus-side executable specification, not a
production HML implementation. The HML submodule was inspected and executed read-only
at `5688aba18632b65a8709aa1d85577d31a67dba6a`; it was not modified.

The primary deterministic result is:

> On 160 frozen FINAL cases (80 valid, 80 minimally corrupted invalid), the reference
> checker accepted 80/80 valid transitions, detected 80/80 invalid transitions, had
> zero false accepts, and returned the correct primary error class for every invalid.
> A source-presence baseline accepted every superficially plausible twin, giving 50%
> accuracy and a 100% invalid false-accept rate. Relative error reduction was 100%.

This clears the predeclared `>=70%` target **only for the controlled invariant protocol
tested here**. It does not establish open mathematical validity checking, theorem
proving, model reasoning gains, or HML representation superiority.

## 1. Scientific question and answer

Question:

    Given semantic state S_t, proposed action a_t, and proposed state S_{t+1},
    can explicit high-confidence invariants detect invalid mathematical transitions?

Answer: **yes for the ten controlled structural/epistemic corruption families in this
experiment**. The result establishes that these invariants are precise enough to serve
as executable acceptance requirements. It does not establish that the checker can
decide whether an arbitrary mathematical theorem follows from arbitrary premises.

The checker is intentionally small and fail-closed. It reads only the neutral case. It
does not read labels, corruption metadata, MATH answers, or HML syntax.

## 2. Benchmark construction and freeze

| Split | Pairs | Cases | Valid | Invalid | Gold-125 source overlap |
|---|---:|---:|---:|---:|---:|
| DEV | 20 | 40 | 20 | 20 | allowed for development |
| FINAL | 80 | 160 | 80 | 80 | **0** |
| Total | 100 | 200 | 100 | 100 | — |

FINAL uses 80 unique nonvisual MATH Level 4/5 rows: 34 Intermediate Algebra, 26
Number Theory, and 20 Counting & Probability. Every source row and source hash was
excluded if it occurred in Gold-125. Each pair has the same source, semantic focus,
state neighbourhood, and approximately equal serialization size. The invalid twin has
one declared conceptual corruption; labels and corruption paths are held in sidecars.

The ten invalid classes each have two DEV and eight FINAL pairs:

1. `PRECONDITION_VIOLATION`
2. `DEPENDENCY_VIOLATION`
3. `SCOPE_LEAK`
4. `OBLIGATION_DROP`
5. `CANDIDATE_PROMOTION`
6. `INVALID_BRANCH_JOIN`
7. `WARRANT_MISMATCH`
8. `EPISTEMIC_PROMOTION`
9. `FALSE_GOAL_DISCHARGE`
10. `TYPE_OR_DOMAIN_MISMATCH`

The complete protocol—cases, labels, corruptions, prompts, renderings, fixtures,
checker, scoring code, schema, and HML probe—is content-addressed by
`experiments/semantic_firewall/freeze_manifest.json` and its adjacent SHA-256 file.
Scoring refuses changed frozen artifacts.

### Source-grounding boundary

The MATH source provides an exact worked-solution span and mathematical neighbourhood
for every pair. Selection used deterministic semantic-cue patterns and exact source
hashes. The neutral transition then isolates one invariant for controlled mutation.

This is not a full theorem replay of all 100 MATH source steps. Some source spans are
compressed macros or lexical anchors. The checker validates the explicit transition
protocol, not the truth of every arbitrary source assertion. Therefore the 100% result
must be called **controlled semantic-protocol sensitivity**, not MATH solution accuracy.

## 3. Reference semantics

| Invariant | Legal condition | Invalid condition | Fail-closed/unknown condition |
|---|---|---|---|
| Dependency | Every premise exists before the action, is evidence, and exactly matches output ancestry. | Missing, future, non-evidence, or changed ancestry. | A dependency exists but has unresolved status. |
| Scope | Output remains in the active local frame, or a valid discharge licenses escape. | Local evidence produces a global fact without discharge. | Scope or discharge evidence is unresolved. |
| Preconditions | Every mandatory condition is satisfied by valid evidence or explicitly deferred to persistent debt. | Execution proceeds after failure or undeclared deferral. | Required applicability remains unknown. |
| Obligations | Open debt persists until named valid discharge; new debt appears OPEN. | Existing or newly created debt silently disappears. | Discharge evidence is unresolved. |
| Candidates | Promotion checks candidate identity and every original constraint with independent evidence. | Candidate self-promotes or skips original constraints. | Candidate/check status is unresolved. |
| Branch/join | Required branches are closed, coverage is certified, and each licenses the same conclusion. | Incomplete, uncovered, or inconsistent branches join globally. | Branch completion or coverage is unresolved. |
| Warrant | Rule identity and exact premise envelope match valid evidence. | Evidence supports another rule or premise set. | Evidence checker returns unknown. |
| Epistemic status | `VERIFIED` is checker-owned, trusted, and has no mandatory open debt. | Proposed evidence or unresolved debt is promoted to `VERIFIED`. | Checking evidence is unresolved. |
| Goal discharge | A verified claim is canonically identical to the open goal. | A different or unverified claim closes the goal. | Goal support remains unresolved. |
| Type/domain | Inputs inhabit the operation contract's declared domains. | A definite incompatible type/domain is used. | Input domain is unknown. |

The checker also rejects unrelated mutations to existing claims and unrelated claim
additions in `state_after`.

## 4. Builder acceptance fixtures

There are 30 canonical neutral fixtures: LEGAL, ILLEGAL, and BOUNDARY_UNKNOWN for each
invariant. All 30 pass their expected reference verdict. They are in
`experiments/semantic_firewall/acceptance/fixtures.json` and exercised by
`tests/test_semantic_firewall.py`.

Current-HML fixture assessment at the pinned SHA:

| Assessment | Fixtures | Invariants |
|---|---:|---|
| `CURRENT_HML_PASS` | 6 | dependency, goal discharge |
| `CURRENT_HML_PARTIAL` | 18 | lexical scope, preconditions, obligations, warrant, epistemic status, type/domain |
| `CURRENT_HML_NOT_EXPRESSIBLE` | 6 | candidates, branch/join |
| `CURRENT_HML_FAIL` | 0 | none classified as a demonstrated bug by these fixtures |

`CURRENT_HML_PARTIAL` does not mean “core defect.” It often means the existing core
works for its trusted fragment while a neutral adapter, domain contract, or evidence
library is missing.

## 5. Deterministic results

### FINAL

| Metric | Source-presence baseline | Reference checker |
|---|---:|---:|
| Correct / total | 80 / 160 | 160 / 160 |
| Accuracy | 50.0% | 100.0% |
| Invalid detected | 0 / 80 | 80 / 80 |
| Invalid false accepts | 80 / 80 | 0 / 80 |
| Invalid false-accept rate | 100.0% | 0.0% |
| Macro-F1 over 10 error classes | 0.000 | 1.000 |
| Per-class recall | 0/8 for every class | 8/8 for every class |
| Unresolved | 0 / 160 | 0 / 160 |
| Relative error reduction | — | **100.0%** |

Raw confusion counts for the reference checker are 80 true valid, 0 false reject, 80
true invalid, and 0 false accept. The baseline has 80 true valid, 0 false reject, 0 true
invalid, and 80 false accepts.

Paired McNemar counts are 0 baseline-only correct and 80 checker-only correct; exact
two-sided `p = 1.6543612251060553e-24`. A fixed-seed 10,000-sample paired bootstrap gives
reference accuracy 95% CI `[1.0, 1.0]` and relative error reduction CI `[1.0, 1.0]`.
These intervals describe the frozen constructed cases, not a population of arbitrary
mathematical transitions.

### DEV

DEV also produced 40/40 reference decisions, 0/20 invalid false accepts, 100% relative
error reduction, and McNemar exact `p = 1.9073486328125e-06`.

### Interpretation

The signal is strong as an executable-specification test and weak as a generalization
claim. The negative generator and checker share an invariant ontology by design. FINAL
source holdout prevents Gold-125 source leakage, but it does not remove specification
coupling. A future independent corruption author and external model baseline are needed
before interpreting the result as real-world error reduction.

## 6. Representation experiment

No configured external model runner exists. No representation score was invented.

All three views were prepared from the identical neutral record:

- Structured English: lossless deterministic prose plus canonical JSON fragments.
- Generic typed AST: the neutral record under a `SemanticTransition` root.
- HML: current-HML executable module shell plus a transparent lossless adapter envelope.

The HML view is explicitly **not pure current HML**. Candidates, generic branch joins,
arbitrary neutral state deltas, and arbitrary source propositions cannot all be encoded
losslessly today. The adapter envelope gives HML no hidden information—the identical
neutral record appears in every view—but scoring it as “HML” would confound HML with the
adapter. Representation status is therefore:

| View | Status |
|---|---|
| Structured English | prepared, unscored |
| Generic typed AST | prepared, unscored |
| HML | prepared as HML + transparent adapter, unscored |

**Conclusion:** HML-vs-AST-vs-Structured-English remains untested.

## 7. Current HML audit, read-only

Thirteen executable probes passed their expected outcomes without modifying HML. The
machine record is `experiments/semantic_firewall/results/current_hml_probe.json`.

| Requirement | Existing HML capability | Exact gap | Minimal builder direction |
|---|---|---|---|
| Dependency | Ordered premise resolution, explicit `EvidenceGraph`, cycle checks, weakest-evidence closure, transitive obligations. | Neutral transition import is absent. | Keep core; add corpus adapter. |
| Scope | `ScopeStmt`, lexical frames, capture-aware binding, local contradiction containment. | No generic case partition or branch join. | Reuse frames; add one proof protocol, not a new domain keyword. |
| Preconditions | Term-level `CONTRACTS` for division, powers, tangent; guarded `log`/`sqrt`; fail-closed side conditions. | Coverage is not uniform across observed domains. | Extend verifier contracts and domain libraries. |
| Obligations | Generated `ReasoningObligation`, OPEN/DISCHARGED/FAILED, inheritance through dependencies. | Neutral adapter/renderer does not expose the whole lifecycle. | Adapter change; preserve current semantics. |
| Candidates | No first-class candidate lifecycle. | Candidate and fact cannot be separated in core state. | Minimal core-state object plus verifier-owned promotion. |
| Branch/join | Lexical scopes exist. | No exhaustive/disjoint partition evidence or safe global join. | Minimal core-proof protocol reusing scopes/evidence. |
| Warrant | Trusted kernel and static `CertificateEnvelope` registry bind claim/context/premises. | Broad external theorem/domain evidence path is absent. | Narrow evidence adapter and libraries. |
| Epistemic | Source cannot set `VERIFIED`; derivation/evidence/goal statuses are checker-computed. | Candidate/branch outcomes are unavailable. | Extend existing status ownership; do not redesign it. |
| Goal | `proved` requires a VERIFIED derivation with canonically identical target. | No defect found. | No change. |
| Type/domain | Rich types, guarded calls, side-condition domain checks, fail-closed unknowns. | Broader domain applicability and adapter type propagation are partial. | Verifier/library work. |

Relevant pinned files include:

- `src/hamiltonian_lang/ast/nodes.py`
- `src/hamiltonian_lang/reasoning/check.py`
- `src/hamiltonian_lang/reasoning/evidence.py`
- `src/hamiltonian_lang/reasoning/refinement.py`
- `src/hamiltonian_lang/reasoning/partiality.py`
- `src/hamiltonian_lang/reasoning/side_conditions.py`
- `src/hamiltonian_lang/reasoning/kernel.py`
- `src/hamiltonian_lang/reasoning/certificates/__init__.py`
- `src/hamiltonian_lang/reasoning/certificates/builtin.py`
- `src/hamiltonian_lang/types.py`
- `src/hamiltonian_lang/type_system/__init__.py`
- `src/hamiltonian_lang/verification/obligations/records.py`
- `src/hamiltonian_lang/verification/obligations/checkers.py`

## 8. Exact builder requirements and classification

The machine-readable source is
`experiments/semantic_firewall/requirements_handoff.json`. Every proposed change has
exactly one classification.

| ID | Requirement summary | Classification | Minimal change |
|---|---|---|---|
| SF-R01 | Dependency legality and ancestry | `NO_CHANGE_ALREADY_SUPPORTED` | retain existing graph checks |
| SF-R02 | Lexical scope locality | `NO_CHANGE_ALREADY_SUPPORTED` | retain scopes/refinement frames |
| SF-R03 | Neutral transition import | `CORPUS_ADAPTER` | versioned lossless importer |
| SF-R04 | Uniform partial-operation preconditions | `VERIFIER_CHANGE` | extend fail-closed contract registry |
| SF-R05 | Neutral obligation round-trip | `CORPUS_ADAPTER` | expose existing lifecycle |
| SF-R06 | Candidate state/lifecycle | `CORE_STATE_CHANGE` | one generic candidate object |
| SF-R07 | Candidate promotion check | `VERIFIER_CHANGE` | check all original constraints |
| SF-R08 | Certified branch join | `CORE_PROOF_CHANGE` | partition/branch/join protocol |
| SF-R09 | External evidence envelope adapter | `EVIDENCE_ADAPTER` | narrow trusted adapter API |
| SF-R10 | Theorem/domain evidence | `LIBRARY_CHANGE` | minimal replayable library path |
| SF-R11 | Checker-owned epistemic status | `NO_CHANGE_ALREADY_SUPPORTED` | extend, do not redesign |
| SF-R12 | Exact goal discharge | `NO_CHANGE_ALREADY_SUPPORTED` | retain current adjudication |
| SF-R13 | Type/domain propagation | `VERIFIER_CHANGE` | propagate declared types fail-closed |
| SF-R14 | Domain applicability knowledge | `LIBRARY_CHANGE` | typed versioned checkers |
| SF-R15 | Lossless HML rendering | `RENDERER_CHANGE` | renderer after semantic objects land |

Classification totals: four no-change, two corpus-adapter, one renderer, one evidence
adapter, two library, three verifier, one core-state, and one core-proof requirement.
There is no backend change and no unknown classification required by this experiment.

## 9. Minimal dependency order

1. Preserve and regression-test SF-R01, SF-R02, SF-R11, and SF-R12 unchanged.
2. Implement SF-R03 neutral import and SF-R09 evidence adapter so later state objects
   enter one trusted boundary.
3. Implement SF-R06 candidate state.
4. Implement SF-R07 candidate verification on top of SF-R06 and SF-R09.
5. Implement SF-R08 branch/join on top of existing scope plus SF-R09.
6. Extend SF-R04 and SF-R13 fail-closed verifier contracts; add only fixture-demanded
   SF-R10/SF-R14 library evidence.
7. Wire SF-R05 obligation round-tripping through the adapter.
8. Implement SF-R15 renderer only after the semantic objects stabilize.
9. Run all 30 fixtures against production HML and rerun the same frozen FINAL set.

## 10. What Claude should implement first

1. Versioned neutral transition and evidence adapters (SF-R03, SF-R09).
2. Generic candidate lifecycle and original-constraint promotion protocol (SF-R06,
   SF-R07).
3. Generic exhaustive/disjoint case and safe join protocol (SF-R08).
4. Uniform fail-closed precondition/type/domain checking over the existing contract
   architecture (SF-R04, SF-R13), with minimal libraries only where fixtures require.
5. Lossless obligation and rendering paths, then execute the acceptance fixtures
   unchanged (SF-R05, SF-R15).

## 11. What Claude must not implement yet

- No `REFRAME`, `WORK_BACKWARDS`, `STRENGTHEN_HYPOTHESIS`, `PRUNE`, `REPAIR_LEMMA`,
  `REVISE_CONJECTURE`, `INDUCT`, or concept-formation keywords.
- No open proof-search policy.
- No domain-specific core keywords for probability, number theory, calculus, or
  combinatorics.
- No broad theorem-library ingestion to make the benchmark look complete.
- No user-registerable trusted checker.
- No source-writable `VERIFIED` status.
- No pure-HML representation claim while the adapter envelope carries unsupported
  fields.
- No benchmark mutation after comparative evaluation; version any future change.
- No training and no Gold expansion.

## 12. What the experiment established

- The ten invariant contracts are executable and mutually separable enough to classify
  one controlled corruption per invalid case.
- A fail-closed three-way outcome supports legal, illegal, and unknown boundaries.
- Exact source presence alone cannot distinguish matched semantic corruptions.
- Current HML already supplies much of the dependency/scope/obligation/status/goal/type
  foundation.
- The smallest genuinely absent semantic objects are candidate lifecycle and generic
  certified branch join.

## 13. What it did not establish

- That the source span's full mathematics was formally replayed.
- That the reference checker recognizes naturally occurring or adversarially authored
  errors outside its ten contracts.
- That a learned model benefits from the explicit record.
- That HML beats generic AST or Structured English.
- That 100% controlled-fixture accuracy will transfer to production HML.
- That theorem/domain libraries or symbolic backends are complete.
- That open mathematical search should be encoded in HML.

## 14. Transfer index

Claude can reconstruct the required build from the repository alone using:

1. `docs/00_HML_MASTER.md`
2. `docs/04_INTEGRATION_AND_IMPLEMENTATION.md`
3. this report
4. `experiments/semantic_firewall/requirements_handoff.json`
5. `experiments/semantic_firewall/acceptance/fixtures.json`
6. `tests/test_semantic_firewall.py`
7. `experiments/semantic_firewall/reference_checker.py`
8. `experiments/semantic_firewall/results/current_hml_probe.json`
9. `experiments/semantic_firewall/freeze_manifest.json`
10. the experiment commit/diff

No undocumented chat reasoning is required.

