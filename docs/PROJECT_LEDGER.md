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
