# Reasoning state semantics V1

V1 is a representation-neutral, canonical-JSON state. It is not HML-V2. Its history horizon is the last 4 successful pre-action transitions.

## Fields

| field | type | meaning and update | provenance | online availability | discovery frequency | expected failure class |
|---|---|---|---|---|---:|---|
| `active_goal` | object/null | First source-ordered open goal; recompute from current Lean state. Includes target, coarse target shape, hypothesis count and content hash. | A/B | current state | 100.00% | GOAL_SELECTION |
| `open_goals` | array | Source order of all open goals with case label, shape, hypothesis count and hash; replace on each state. No parent/child claim. | A/B | current state | 100.00% | GOAL_SELECTION |
| `local_dependencies` | edge array | A declaration points to a later declaration or `@goal` when its exact local name occurs in the dependent type/target; recompute. This is lexical-formal reference, not theorem dependency. | B | current state | 89.67% non-empty | PREMISE_DEPENDENCY |
| `active_scope` | object | The active goal's explicit Lean `case` label, if present. No inferred branch parent, membership or coverage. | A | current state | 43.00% explicit | BRANCH_STATE/SCOPE_CONFUSION |
| `trajectory_position` | object | Count of successful prior events. Never includes total proof length. | A/B | prefix | 70.43% non-zero | TRAJECTORY_MEMORY |
| `recent_actions` | array | Tactic-family heads of the last 4 successful actions, oldest to newest; append after verified/recorded success and truncate left. | A/B | prefix | 70.43% non-empty | TRAJECTORY_MEMORY/STRATEGY_STATE |
| `recent_deltas` | array | Deterministic goal/target/local-declaration changes for the same events; append and truncate with actions. | B | prefix | 70.43% non-empty | TRAJECTORY_MEMORY |
| `progress_summary` | object | Open-goal count, net recent goal delta and immediate repeated-family flag, recomputed from current state/history. | B | current+prefix | 100.00% | TRAJECTORY_MEMORY/STRATEGY_STATE |

## Three-arm information contract

- BASE_STATE: canonical JSON containing the exact current mathematical state only.
- RAW_HISTORY: BASE_STATE plus a neutral chronological array of the exact last 4 pre-action `(state_before, action, state_after)` events.
- SEMANTIC_STATE: BASE_STATE plus exactly the admitted V1 fields derived from that same current state/history.

Instructions, candidates, labels, model, recipe and envelope must otherwise be byte-identical. The semantic renderer must support module removal without recomputation. FINAL_A remains locked until this schema/extractor commit is recorded; FINAL_B remains locked for one evidence-cited V2 revision only.

## Explicit non-semantics

V1 does not represent failed routes, candidate validity, obligations distinct from goals, goal genealogy, branch coverage, theorem-premise use by the next action, inferred strategy, invariant/lemma role, proof length or future success. These omissions are deliberate evidence boundaries.
