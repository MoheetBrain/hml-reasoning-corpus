# Gold-125 reasoning-state sufficiency profile

The profile compares the frozen Gold-25 state fields with the new trajectory schema. New fields are added to the Gold-125 schema without changing old files.

| State field | Trajectories using field | Classification |
|---|---:|---|
| assumptions | 0/125 | NOT_TESTED_ENOUGH |
| branch_state | 5/125 | OCCASIONAL |
| candidates | 25/125 | OCCASIONAL |
| constraints | 1/125 | NOT_TESTED_ENOUGH |
| declarations | 24/125 | OCCASIONAL |
| definitions | 0/125 | NOT_TESTED_ENOUGH |
| dependencies | 125/125 | ESSENTIAL |
| discharged_obligations | 82/125 | FREQUENTLY_USEFUL |
| epistemic_status | 125/125 | ESSENTIAL |
| facts | 125/125 | ESSENTIAL |
| goals | 125/125 | ESSENTIAL |
| id | 125/125 | POSSIBLY_REDUNDANT |
| objects | 125/125 | ESSENTIAL |
| open_obligations | 69/125 | FREQUENTLY_USEFUL |
| scope | 125/125 | FREQUENTLY_USEFUL |
| subgoals | 0/125 | NOT_TESTED_ENOUGH |
| types_domains | 73/125 | ESSENTIAL |

## New or strengthened dimensions

- candidates: explicit candidate/selection state is used by the new schema even when the source solution does not fully verify every candidate.
- branch_state: branch declarations, active branch-local facts, and join context are separated from lexical scope.
- epistemic_status: source-grounded, inferred, verified, and goal-discharged claims are not collapsed into one fact status.
- macro_components and reasoning_mode: provenance metadata records atomicity and search/execution distinction without changing mathematical denotation.
- obligation lifetime: created_at_step, discharged_at_step, and lifetime_steps make proof debt measurable.

No state dimension is removed. The evidence supports a typed S_t with facts, provenance, scope/branch state, candidate state, obligations, goals, and epistemic status. The new meta-reasoning fields are primarily trajectory metadata unless later evidence shows they must affect proof-state denotation.
