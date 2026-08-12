# Semantic and adapter gaps found by the factory

No HML changes were implemented. Detailed candidates are under
`reports/semantic_gap_candidates/`.

1. The 241,265 Lean records are effect-first learning records, not frozen-HML
   verifier transitions. Their compatibility flag is not a verifier result.
2. Lean propositions and tactics are opaque to the semantic-state verifier; arbitrary
   Lean mathematical validity cannot be attested by the current certificate registry.
3. Goal creation is intentionally excluded and fails closed in frozen HML.

These facts block truthful Stage-1,000 scaling from Lean. They do not invalidate the
Stage-100 verifier harness.
