# Semantic requirements audit

## Admission rule

A field is admitted only when it is prevalent enough to matter, addresses observed failure or ambiguity, is available strictly before the next action, avoids gold/future data, is computable online, and has a precise update rule. Headline data permits provenance A/B/C only; V1 uses A and B.

| module | source status | online | provenance | decision |
|---|---|---:|---|---|
| Goal structure | Lean pretty state exposes ordered open goals, active first goal, hypotheses and targets; no goal genealogy | yes | A/B | KEEP_V1 |
| Local dependencies | declaration-name references in later local types and targets are deterministic | yes | B | KEEP_V1 |
| Branch/scope | `case` identity is explicit; branch parent, coverage and general nested scope are absent | yes, limited | A | KEEP_V1 |
| Successful history | prior exact states/actions and derived deltas exist in complete trace prefixes | yes | A/B | KEEP_V1 |
| Distinct obligations | not distinct from ordinary Lean goals | no supported object | — | DROP_V1 |
| Search memory | no failed attempts in passive successful traces | no | — | DROP_V1 |
| Lemma/invariant/strategy role | would require interpretation not formal evidence | not certified | D only | DROP_V1 |

## Leakage firewall

The extractor accepts only `(current_raw_state, prior_events)`. It does not accept the current tactic, state-after, proof length, future steps, candidate ordering or gold label. `trajectory_position.steps_completed` is the prefix length, not total proof length. The history window is 4; RAW_HISTORY must contain exactly the same bounded pre-action events used by SEMANTIC_STATE.

## Acquisition decision

No Erdős/research-proof acquisition is justified before the formal test. The local source supports a narrow V1 test of successful-history compression plus organization of goals, dependencies and explicit case identity. Genuine discovery traces would be required for rejected conjectures, failed routes, invariant discovery, strategy shifts, uncertainty and branch coverage.
