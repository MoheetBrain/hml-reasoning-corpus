# Codex translation handoff — the canonical pipeline, and who owns what

**Status: normative for translation. Semantic authority: HML commit `68178f0`**
(`src/` byte-identical through every later experiment/report commit on
`hml/vnext-semantic-coverage`). Machine-readable twin: `CODEX_TRANSLATION_CONTRACT.json`.
Regression oracle: `TRANSLATION_GOLDEN_FIXTURES.jsonl` — **run it green before translating
anything at scale.**

This document exists so that Codex can scale to 10k+ problems without guessing HML
semantics. Everything a translator needs to decide is either stated here, pinned in the JSON
contract, or exercised by a golden fixture. Where none of the three answers a question, the
correct output is a **refusal with a code**, never a guess.

---

## 1. The canonical pipeline

```
SOURCE  (worked mathematics, verbatim)
   │        immutable; hashed; never edited
   ▼
IMMUTABLE SOURCE RECORD
   │        problem block + per-step spans, each with SHA-256
   ▼
REPRESENTATION-NEUTRAL SEMANTIC TRAJECTORY        ← Codex, under this contract
   │        typed states, actions, effects, premises, branch ancestry,
   │        provenance hashes; no HML text anywhere
   ▼
VNEXT CANONICAL STATE / EVENT                     ← frozen semantics, 68178f0
   │        SemanticState + Action + declared effects, imported losslessly
   ▼
VERIFIER                                          ← the only licensing authority
   │        VALID | INVALID(findings) | UNRESOLVED(unknowns)
   ▼
MATCHED RENDERINGS
            HML_LINEAR · HML_TREE · AST · STRUCTURED_NEUTRAL
            deterministic views of the SAME canonical object
            parse(render(S)) == S for every supported state
```

## 2. Ownership — exact boundaries

| Layer | Owner | The rule |
|---|---|---|
| Source / corpus fact | **Codex** | Immutable, hashed. HML never edits, reinterprets, or accommodates a contradictory source role. |
| Neutral semantic trajectory | **Codex, under this contract** | Every state object, effect, premise id, ancestry edge and provenance hash. Where the source under-determines it, refuse with a code. |
| HML core semantics | **Frozen VNext (`68178f0`)** | The state model, effect kinds, verifier rules, trust boundary. Changes require a DECISIONS.md record on the HML side; the translator never works around them. |
| HML_LINEAR / HML_TREE / AST / STRUCTURED_NEUTRAL | Deterministic renderers | Views of the same canonical state. Never semantic authority; a distinction that exists only in a view is a rendering bug. |
| Model-safe training view | Renderer-level policy (§8) | A *projection* of the audit record. Never feeds back into semantics. |

## 3. The state model Codex targets

Object kinds: `Claim` · `Candidate` · `Branch` · `Goal` · `Obligation` · `EvidenceRecord` ·
`Action` · `SemanticState` · `Transition`. The JSON contract pins every field and every
allowed effect kind. The non-negotiables:

* **Status is computed, never asserted.** A candidate is born `PROPOSED`; `VERIFIED`,
  `REJECTED`, `JOINED`, discharge — all verifier-licensed. A translator that writes a
  settled status into a fresh object has forged it.
* **Prose is never authority.** `action.summary` is presentation. The typed declaration is
  `claimed_conclusion`; the typed effects are the semantics. Two actions differing only in
  prose verify identically.
* **`UNKNOWN` is a value.** Unresolvable warrant is honest and expected (an untrusted
  source is exactly that); it yields `UNRESOLVED`, not `VALID`. Structural malformation is
  reported even under unknown warrant — do not rely on unknowns to hide anything.
* **Exactness is a second axis.** Truth (`ClaimStatus`) and precision (`Exactness`) are
  independent. An approximation is a *new* claim with an `Approximation` record; it never
  overwrites its source, and nothing ever travels `APPROXIMATE → EXACT` in place.

## 4. Branch ancestry — the schema that fixed the corpus

The `3bbb425` neutral branch-ancestry structure is **retained permanently**. Per partition:
partition id, parent branch, pre-split premises (objects + ids), join transition; per
branch: branch id, parent branch, label, branch-local assumption, opening transition,
member transitions, `pre_split_premise_ids`, `opening_dependency_ids`,
`rejected_linear_dependency_ids`, source basis, provenance hashes.

**Linear predecessor ≠ semantic dependency.** The single most measured lesson of this
project: sibling cases inherit nothing from each other. A "Case 2" opens from the declared
common pre-split state; the linear edge to Case 1's last step goes in
`rejected_linear_dependency_ids`, never into ancestry. The causal rerun that added only this
structure collapsed branch refusals 24 → 3 with zero semantic changes.

## 5. Corpus-owner requirements (do not implement these in HML)

**A. `SOURCE_INITIAL_STATE` corpus-wide.** Every source premise any later transition cites
must receive a stable neutral id, its proposition, an origin
(`SOURCE_PROBLEM` / `SOURCE_INITIAL_STATE` / `EARLIER_SOURCE_TRANSITION` /
`EXPLICIT_SOURCE_STATE_OMITTED_BY_OLD_SEGMENTER`) and a provenance hash — for **all**
problems, not only partition-bearing ones. The `i00N` family currently blocks 11 root
trajectories (196 downstream rows) solely because these premises are declared only where
partitions needed them. Never reconstruct an initial premise from linear adjacency.

**B. MIXED-039.** The ancestry declares `c008` a pre-split *premise*; the master classifier
codes the same step as *candidate creation*. One interpretation must become canonical from
the original source. HML will not accommodate contradictory roles for one object — until
resolved, the translator must refuse that problem with `SOURCE_ROLE_CONTRADICTION`.

**C. Branch ancestry** stays as in §4, unchanged.

**D. Implicit logical weakening** (from D-063). Where exhaustive branches establish unequal
conclusions and the source publishes their union, the neutral trajectory **must insert the
weakening transitions the source skipped**, one per branch, under all of these constraints:

* origin-marked `IMPLICIT_LOGICAL_STEP` with provenance naming the union step's span hash;
* rule drawn from the closed whitelist — initially exactly `DISJUNCTION_INTRODUCTION` —
  extended only by amending this contract, never by translator judgment;
* the inserted step's content is **uniquely determined** by declared structure: premise = the
  branch's own established conclusion; conclusion = the source's own union proposition (or,
  for inner levels of a nested analysis, the deterministic disjunction of the sibling
  conclusions in declared branch order);
* never arithmetic, never creative, never reading ahead to anything but the union step the
  source itself contains;
* each branch then closes on the common union and the **existing** join publishes it,
  discharging coverage. No disjunctive-join primitive exists or is coming (D-063).

## 6. Refusal, never guess

Refusal codes are pinned in the JSON contract: `MISSING_SOURCE_PREMISE`,
`AMBIGUOUS_BRANCH_PARENT`, `MISSING_BRANCH_COVERAGE`, `UNSUPPORTED_CANDIDATE_TRANSITION`,
`UNREPRESENTABLE_APPROXIMATION`, `SOURCE_ROLE_CONTRADICTION`, `BACKEND_REQUIRED`,
`LIBRARY_REQUIRED`, `SOURCE_AMBIGUITY`.

The translator must refuse rather than: infer an unstated premise; use the previous linear
transition as a semantic parent; turn human process labels into mathematical proof; promote
a candidate; invent branch coverage; invent an approximation error bound; or read the final
answer ahead into any earlier state. A faithful refusal is a **good** output: it is how the
corpus learns what to repair, and every category above has already produced a measured
defect when guessed.

## 7. What the verifier will do with honest output

Source-warranted steps carry `UNKNOWN` evidence and verify `UNRESOLVED` — correct and
expected. Structural soundness (lifecycle, frames, coverage, exactness, the frame condition)
is checked regardless. `VALID` appears where real evidence is carried (replayable
certificates); `INVALID` means the state delta itself is malformed — a translation bug, not
a source property. Do not tune output to chase `VALID`; tune it to be *refusable or
faithful*.

## 8. Model-training safe view policy (FABLE lessons, as rendering policy)

Semantics stores the full audit record. Training views are **projections**, and the policy
is a renderer contract, never a semantic one:

A model input `(S_before, action)` **must never include**: `state_after`; any claim,
candidate, branch conclusion or goal status that first exists after the action; an
answer-bearing `action.summary` (summaries are dropped or neutralised in training views —
they are already semantically inert); `claimed_conclusion` when it states the step's output;
the target delta; the final answer; later source-solution text (including via `source` /
provenance payloads); or any derived field whose value trivially reveals the target.

Required mechanics: the training renderer emits from an explicit **allowlist** of fields;
every emitted example passes an automated per-example leakage assertion (no token of the
held-out target present in the input projection, no post-action id cited); the full
semantic/audit record is preserved separately and linked by id. Leakage checks are part of
dataset CI, not a one-off audit.

## 9. Before translating 10k

1. Pin HML `68178f0` and this contract's version; mismatch = stop.
2. Run `TRANSLATION_GOLDEN_FIXTURES.jsonl` through the fixture validator — all green,
   including the refusal fixtures refusing.
3. Repair §5.A and §5.B in the corpus; rerun the 600-problem rederivation and the PRM-1k
   pilot; gates: no new mechanism family, no verifier regressions, root-cause refusals only
   in declared corpus/backend/source categories.
4. Only then scale.
