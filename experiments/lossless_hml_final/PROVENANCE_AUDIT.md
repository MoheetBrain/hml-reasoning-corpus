# Lossless overlay provenance audit

The matched 10K views were rebuilt from the pinned canonical Lean transition export with
SHA-256 `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.
Both views contain the same 10,000 ordered source IDs, 7,125 parent theorems, and exact raw
tactic target for each row.

An exhaustive paired audit over all 10,000 rows found:

- ordered record mismatches: 0
- target tactic mismatches: 0
- exact current-state/history envelope mismatches: 0
- lossless overlay reconstruction mismatches: 0
- forbidden explicit future/gold fields: 0
- truncations: 0

For every row, the overlay was reconstructed from only the RAW current state and completed
pre-action history and matched the stored overlay byte-canonically. Its added fields are
limited to chronological step numbers, conservative syntactic tactic heads, lexical tokens
copied from completed tactics, directly printed case labels, and hashes of exact available
strings. It does not inspect the target action while constructing the input.

The common fit gate requires the complete assistant chat for both views to be no longer
than 3,072 tokens. This selects rows identically across arms and applies no truncation.
The common prompt text and action language are identical outside the representation JSON.
FINAL_B was not opened.
