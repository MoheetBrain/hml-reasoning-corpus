# LOSSLESS_HML_OVERLAY representation specification

## Shared information envelope

At every decision, both arms receive exactly the actual current Lean pretty-printed state
and every completed transition on the search path. A completed transition contains the
verbatim state before, verbatim raw Lean tactic including arguments, and verbatim accepted
state after. Rejected candidates are solver events and are supplied equivalently when a
node is revisited. Neither view contains the current gold tactic, future source actions,
future states, or gold-derived annotations.

## RAW_HISTORY

Canonical JSON with:

- `current_lean_state_exact`
- `completed_history_exact`, an ordered array of `state_before_exact`, `tactic_exact`, and
  `state_after_exact`
- `completed_steps`

No exact information is omitted or deliberately made awkward.

## LOSSLESS_HML_OVERLAY

Canonical JSON with the same exact state and history bytes, organized as:

- `current.state_exact`
- `history[i].state_before_exact`, `tactic_exact`, and `state_after_exact`
- `semantic_index`, containing only deterministic surface indexes:
  step number, syntactic tactic family, lexical identifiers appearing in the exact tactic,
  directly printed case labels, SHA-256 transition/state IDs, and chronological ordering

Indexes add pointers; they never replace propositions, goals, contexts, tactics, or tactic
arguments. Hashes identify exact strings and do not carry mathematical judgments. Tactic
families are conservative syntactic heads, not an ontology. Case labels are copied only
when Lean printed them.

Serialization is UTF-8 canonical JSON with sorted keys and compact separators. The common
prompt and exact raw-tactic target are byte-identical outside the representation payload.
