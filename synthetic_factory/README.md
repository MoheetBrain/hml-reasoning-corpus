# Verifier-certified counterfactual transition factory

This is an independent, representation-neutral synthetic-data track. It takes a
trusted, frozen transition, performs one semantic mutation, and asks the frozen HML
transition verifier for the outcome. It never changes HML and never treats a model,
heuristic, parser success, or an unobserved action as an invalidity label.

The first production-quality checkpoint is deliberately small: Stage 100 uses the
100 records at corpus commit `9d67e54450b9db897ee2ed20ec2e4cbbc16a3780`
that the frozen verifier itself returns `VALID` across DEV and FINAL Semantic
Firewall cases. The 241,265 Lean canonical records are separately pinned and
audited as the future scale source. They are not silently treated as verifier-ready:
their effect-first schema omits dependencies, typed action arguments, evidence,
preconditions, obligations, and scope, and several effect classes need an adapter
the current HML frame condition can truthfully check.

## Authority

- HML tag: `hml-semantic-pre-gemma-v1`
- HML SHA: `84bf9897689b0ed78a2caaefc1db850d49b81260`
- corpus SHA: `9d67e54450b9db897ee2ed20ec2e4cbbc16a3780`
- Lean canonical artifact SHA-256:
  `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`

`authority.py` checks the tag, SHA, tree, clean HML checkout, zero writable HML
files, unchanged corpus source fixtures, Lean artifact hash, and exact 241,265 line
count before and after generation.

## Trust boundary

Originals are frozen externally adjudicated corpus records and are checked through
`verify_replay`. Counterfactuals preserve the original evidence bytes and alter one
semantic field; only counterfactuals that import successfully and are rejected by the
current verifier are retained. Runtime-mode results are recorded as a diagnostic,
but no generated positive is accepted from copied evidence status. Unknown remains
`UNRESOLVED` and is never relabelled `INVALID`.

The independent Stage100 review found 20 semantic-hard certificate-coverage pairs,
60 structural verifier probes, and 20 ambiguous pairs with an additional frame
finding. The tracked Stage100 output is therefore a diagnostic harness artifact, not
a production training set. This transparent failure is the reason scaling is disabled.
The separate alpha-renaming invariance dataset was not started because that work is
downstream of a passing counterfactual-factory quality gate.

## Run

```bash
export HML_FROZEN_PATH=$HOME/HMLTN_CODEX_SYNTH/hml_frozen_readonly
export LEAN_CANONICAL_PATH=$HOME/HMLTN_CODEX_SYNTH/source_artifacts/lean_domino_v2/lean_canonical_records.jsonl
export CORPUS_ROOT=$HOME/HMLTN_CODEX_SYNTH/hml-reasoning-corpus
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$HML_FROZEN_PATH/src:$PWD/synthetic_factory/src"

python -m synthetic_factory.authority --write synthetic_factory/manifests/authority.json
python -m synthetic_factory.generate --stage 100
python -m unittest discover -s synthetic_factory/tests -p 'test_*.py'
python -m synthetic_factory.benchmark --tasks 1000 --workers 4 8 16 20
```

Generated Stage-100 JSONL is small and tracked. Stage 1,000 and Stage 10,000 are
blocked until the prior quality gate is explicitly passed.
