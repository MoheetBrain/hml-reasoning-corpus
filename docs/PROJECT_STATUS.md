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

Corpus-side reconciliation. Codex, who owns this repository, is unavailable; corpus and
research-integration responsibilities are temporarily held by the integrator.

## Current Branch

`codex/minilang-artifact-audit` at `fc9b2a3`, matching `origin`. Submodule `hml_core` pinned
at `5688aba` — **stale**: the production HML repository has since shipped the algebra,
probability and calculus libraries at `2af4998` and four further commits, most recently
`a21fdb7`.

## Current System Architecture

Five canonical context documents (`docs/00`–`docs/04`), a frozen Semantic Firewall
experiment (`experiments/semantic_firewall/`) whose reference checker and 30 acceptance
fixtures are the external acceptance criteria for the production implementation, a PRM800K
natural-error audit, a MiniLang artifact audit, and a project cognition ledger
(`experiments/project_cognition/project_memory.yaml`, 135 entries, twice independently
audited).

## Capabilities Implemented

The frozen reference checker; the 30-fixture acceptance suite; the FINAL 80/80 benchmark;
the neutral transition schema; the cognition ledger.

## Work Completed to Date

See `docs/HML_RESEARCH_LEDGER.md` for the scientific record and `PROJECT_LEDGER.md` for the
chronological change record.

## Important Files and Artifacts

`experiments/semantic_firewall/reference_checker.py` · `.../acceptance/fixtures.json` ·
`.../requirements_handoff.json` · `.../freeze_manifest.json` ·
`experiments/project_cognition/project_memory.yaml` · `docs/00`–`docs/04` ·
`docs/HML_RESEARCH_LEDGER.md`.

## Data Sources and Provenance

Hendrycks MATH (levels 4–5), PRM800K, the MiniLang OOPSLA26 v2 artifact
(SHA-256 `1562c845…`). Provenance is recorded per experiment.

## Decisions and Rationale

Recorded in the canonical five and in the cognition ledger. Production-side design decisions
live in the HML repository's `DECISIONS.md`.

## Verification and Test Results

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

## Exact Next Actions

1. ~~Correct the four unscoped absence-of-evidence statements.~~ **Done 2026-08-10.**
2. ~~Label Gold-125 coverage historical.~~ **Done 2026-08-10, five places.**
3. Decide whether to adopt the proposed `FX2-*` probe suite (domain subtyping, warrant
   premise envelope, output domain) as a separately versioned expansion. The frozen 30 are
   immutable.
4. Record the e-graph gate as a broken historical reference.
5. Repin `hml_core` and rerun the 30 fixtures.
