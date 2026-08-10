# Semantic Firewall experiment

This directory is an executable research specification in the corpus repository. It
does not implement or modify Hamiltonian Lang.

The benchmark contains 100 matched pairs: 20 DEV pairs and 80 FINAL pairs. Each pair
shares one MATH source row and one neutral semantic neighbourhood; one twin is valid
and one has a single controlled semantic corruption. FINAL excludes all Gold-125 rows
and source hashes. Gold labels and corruption descriptions are sidecars and are never
passed to `reference_checker.py`.

The reference checker tests dependency, scope, precondition, obligation, candidate,
branch/join, warrant, epistemic, goal-discharge, and type/domain invariants. It checks
protocol consistency, not arbitrary theorem truth. The source-presence baseline in
`score_benchmark.py` is an unstructured deterministic control, not an LLM.

The three representation views are generated from the same neutral record. Current
HML cannot losslessly express every candidate and branch/join field, so the HML view
uses a transparent lossless adapter envelope and is explicitly not claimed to be pure
or executable HML. No representation score is reported without a configured external
model runner and a production-grade adapter.

Rebuild and score:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pandas --with pyarrow \
  python experiments/semantic_firewall/build_benchmark.py
PYTHONDONTWRITEBYTECODE=1 python experiments/semantic_firewall/score_benchmark.py
```

The freeze manifest and hash must validate before scoring. Rebuilding FINAL after a
comparative evaluation would create a new benchmark version and is prohibited.

