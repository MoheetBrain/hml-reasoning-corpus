# PRM800K natural reasoning audit

This experiment treats PRM800K prefixes as **state proxies**, not canonical HML
states. It measures the raw annotation structure first, then creates a deterministic
semantic-discovery sample of 500 `-1`, 250 `0`, and 250 `+1` candidate steps plus
200 phase-1 multi-candidate decision points.

The official source checkout is external and immutable. Rebuild with:

```bash
python3 experiments/prm800k_audit/audit_prm800k.py \
  --source-root /absolute/path/to/prm800k \
  --source-commit 7ecc794703b2877f63226f2477a49b34f9b25163
```

The semantic annotation files are explicitly a conservative deterministic first
pass. They preserve `UNRESOLVED` and confidence rather than forcing every human
`-1` into the existing Semantic Firewall ontology. They are suitable for discovery
and human-adjudication planning, not for training or for claiming error prevalence.
