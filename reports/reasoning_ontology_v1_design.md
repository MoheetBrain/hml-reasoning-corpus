# Reasoning ontology v1 design

Ontology-v1 is a derived multi-axis view over frozen Gold-125 annotations. It does not change HML syntax, HML semantics, or canonical trajectories.

## Design decision

A transition may have one generic operation plus independent reasoning mode, warrant, knowledge layer, goal effect, scope effect, epistemic effect, preconditions, obligations, and state delta. The flat-label disagreement is therefore not a single categorical contest.

Examples:

- DISCHARGE versus EVALUATE becomes core_operation=EVALUATE plus goal_effect=DISCHARGE.
- TRIG_IDENTITY versus TRANSFORM becomes core_operation=TRANSFORM plus a trigonometry warrant in DOMAIN_LIBRARY.
- SEARCH_META versus CONSTRUCT becomes reasoning_mode=SEARCH_META plus core_operation=CONSTRUCT.

## Axis contract

| Axis | Question |
|---|---|
| reasoning_mode | Why is this action selected now? |
| core_operation | What reusable state/proof/control effect occurs? |
| warrant | What justifies the effect? |
| knowledge_layer | Where does theorem/domain/backend knowledge live? |
| goal_effect | Does the step create, advance, or discharge a goal? |
| scope_effect | Does it open, close, or join a branch/assumption? |
| epistemic_effect | Does it assert, derive, propose, verify, or reject? |
| preconditions/obligations/state_delta | What must hold and what changes? |

## Quality snapshot

- Derived transitions: 769
- Candidate core operation values: 18
- Adjudicated KEEP_AS_CORE operations: 17
- UNRESOLVED transitions: 136 (17.7%)
- OTHER source labels retained: 125
- Genuine disagreement remainder: 1

The ontology is not declared fully stabilized while UNRESOLVED remains material or the annotation-error review remains open.

## Core boundary

The proposed generic interface contains DECLARE, RECORD, MODEL, CONSTRUCT, TRANSFORM, SUBSTITUTE, APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, COUNT, EVALUATE, BOUND, SELECT, VERIFY, CONTRADICTION, and DISCHARGE. Named trigonometric, modular, probability, sequence, calculus, and counting rules are warrants/libraries rather than bespoke core instructions.
