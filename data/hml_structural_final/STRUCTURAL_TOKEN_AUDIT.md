# Structural Token Audit

Status: **NOT APPLICABLE — no model-facing views or rungs emitted**.

The Qwen3 tokenizer was not downloaded or invoked because the admission gate failed
before rendering. HML mean/median/p95/max, neutral mean/median/p95/max, ratio,
matched-length subset, `MAXSEQ=6144` truncation count, and systematic-difference flag
are all unavailable. Reporting zero tokens would falsely describe an empty dataset
as efficient.

