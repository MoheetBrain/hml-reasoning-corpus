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
* **`schemas/semantic_case.schema.json` rejects its own fixtures.** `$defs/action` declares
  `"additionalProperties": false` with no `properties` block while `required` lists fifteen
  properties — an unsatisfiable subschema. 30/30 frozen fixtures fail validation against it.
* **Coverage figures are historical.** Gold-125 coverage (FULL 11 / PARTIAL 455 /
  REPRESENTABLE_ONLY 303) and every "library-blocked" claim were measured against `hml_core`
  at `5688aba`, before the libraries shipped. Not relabelled yet.
* **Four unscoped absence-of-evidence statements** assert that experiments do not exist when
  they exist in the HML repository. Identified, not yet corrected.
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

## Exact Next Actions

1. Correct the four unscoped absence-of-evidence statements.
2. Label Gold-125 coverage `HISTORICAL COVERAGE AT HML 5688aba` in five identified places.
3. Decide whether to adopt the proposed `FX2-*` probe suite (domain subtyping, warrant
   premise envelope, output domain) as a separately versioned expansion. The frozen 30 are
   immutable.
4. Record the e-graph gate as a broken historical reference.
5. Repin `hml_core` and rerun the 30 fixtures.
