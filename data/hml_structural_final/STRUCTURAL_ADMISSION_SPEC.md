# Structural Admission Specification

Status: **frozen before final selection**, 2026-08-17. Selection seed, if the
population gate had passed: `20260817`. This specification was not weakened after
the source census.

## Scientific question

> Does already-existing HML structural state machinery provide a
> material advantage over a matched neutral representation when
> goals, dependencies, scopes, obligations, branches, and candidate
> state are genuinely populated and state-management complexity is high?

The unit is a source-grounded transition `(S_before, source_action, S_after)`. A
large collection of opaque propositions or ordinary single-goal Lean states does
not answer the question.

## Record gate

A candidate record must satisfy all of the following:

1. Exact before state, source/gold action, and exact after state are present.
2. Source ID, parent theorem/problem, trajectory step, source revision, semantic
   authority, epistemic class, and verification status are retained.
3. The state is representable by the existing VNext authority without changing
   semantics or weakening verification.
4. The input is constructible without the gold action, future state, action-derived
   premise oracle, or any target-bearing retrieval block.
5. At least one explicit goal and at least two independent, source-supported
   structural dimensions beyond the opaque proposition body are present. Eligible
   dimensions are: a claim dependency edge; nested scope; a distinct open
   obligation; multiple goals; an active branch with predicate, membership, and
   coverage; candidate lifecycle/status; epistemic/status transition; or proof
   depth at least five plus a multi-field state delta.

The following substitutions are forbidden:

- a Lean `case` label is scope metadata, not a branch predicate or coverage proof;
- an open Lean goal is not duplicated as an HML obligation;
- the global declarations in `annotated_tactic[1]` are gold-action-derived and are
  not state dependency edges;
- a list of possible next tactics is not candidate lifecycle state;
- lexical mention, tactic name, or future steps may not infer a semantic relation.

## Population readiness gate

The headline release requires a parent-theorem grouped train/dev/FINAL split and a
fresh FINAL holdout with no parent overlap with the VNext/Qwen development history.
Each of these field families must be genuinely populated in FINAL: goals,
dependencies, scopes, obligations distinct from goals, branches with predicate and
coverage, and candidate/status state. Each family must have at least 100 FINAL rows
and at least 2% prevalence in the full admitted population. These are minimums for
an interpretable interaction, not quotas that may be filled synthetically.

Synthetic stress data cannot satisfy this gate. Previous Gold-125 and VNext-10K
records are development history and cannot serve as the fresh final holdout.

## Frozen outcome

The record census found many source-grounded goals and scopes, but zero source-
supported claim dependency graphs, zero obligations distinct from Lean goals, zero
candidate lifecycle states, and no general branch objects with both predicate and
coverage. The population readiness gate therefore failed. Final selection was not
run, no model-facing view was emitted, and the admitted headline count is **0**.

