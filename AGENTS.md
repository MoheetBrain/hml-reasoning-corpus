# HML Reasoning Corpus

## ROLE

This repository builds representation-neutral mathematical reasoning
trajectories from worked mathematics and renders them into HML.

## HML AUTHORITY

`./hml_core` is the authoritative pinned Hamiltonian Lang implementation.

## READ-ONLY RULE

Never edit, patch, reformat, commit, or otherwise modify anything inside
`./hml_core`.

You MAY:

- inspect `hml_core`
- search its source
- import its Python modules
- run its parser/compiler/verifier
- execute its tests where useful

You MUST NOT:

- change HML semantics here
- invent new HML syntax because a source cannot be translated
- modify frozen HML experimental artifacts

## SEMANTIC GAP POLICY

If a mathematical reasoning step cannot be represented faithfully with
current HML, create a report under:

    reports/semantic_gaps/

Record:

- source problem
- reasoning step
- required mathematical meaning
- why current HML cannot express it
- relevant HML files/constructs inspected
- proposed capability, WITHOUT implementing it

Claude/the hamiltonian-lang project will decide whether HML itself changes.

## SOURCE OF TRUTH

The master dataset representation is a neutral trajectory:

    S0 -> a0 -> S1 -> a1 -> ... -> Sn

HML is a rendering of that trajectory, not the canonical source.

## INITIAL SCOPE

Do NOT ingest huge datasets yet. Begin with only 10 representative worked
mathematical problems and build the end-to-end reasoning-trajectory pipeline
correctly.

## CONTEXT-LOSS RECOVERY

Chat history is NOT authoritative project memory.

At the beginning of every new Codex thread:

1. Read `AGENTS.md`.
2. Read `RESEARCH_STATE.md`.
3. Read the latest `PROJECT_STATUS.md`.
4. Read the latest `PROJECT_LEDGER.md`.
5. Read `STATUS.json` if present.
6. Inspect Git HEAD/status.
7. Read only the latest relevant experiment report/protocol.
8. Reconstruct project state from repository artifacts.
9. Do not ask the user to reconstruct old conversation history unless repository state is genuinely insufficient.

After every material experiment or scientific decision, persist state to repository
artifacts before relying on chat memory.
