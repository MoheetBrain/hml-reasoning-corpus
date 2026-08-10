# MiniLang artifact audit evidence

This directory is the compact, repository-resident evidence package derived from
Zenodo record 18454706, artifact v2. The audited archive is identified by SHA-256
`1562c84524c0851682e47b32243c0e2dcbfb47daaf6820bcb5c216ae8f12bc82` and MD5
`6f5a1fe82aa182945f6520f7682fa05f`.

The source package is AGPL-3.0-or-later. Exact source/translation snippets retained
in `representative_examples.jsonl` and `translation_failures.json` preserve that
provenance and are redistributed under the source artifact's terms. See
`ARTIFACT_LICENSE_NOTICE.txt`; the full corresponding-source archive remains the
Zenodo artifact identified in `source_manifest.json`.

Files:

- `source_manifest.json`: archive identity, hashes, inventory, licenses, and small
  semantic-source hashes.
- `source_tree.txt.gz`: deterministic compressed copy of all 42,699 archive paths.
- `operation_semantics.json`: forensic reconstruction of the paper's exact ten
  semantic operations and the larger implementation surface.
- `hml_mapping.json`: bidirectional MiniLang/HML and SF-R01…SF-R15 mappings.
- `operation_statistics.json`: corpus, sequence, nesting-proxy, session, and
  evaluation-CSV measurements.
- `translation_failures.json`: exact failure accounting and a diagnostic-stratified
  source sample.
- `representative_examples.jsonl`: ten verified examples covering each public
  command label, with exact Isar source, MiniLang rendering, identity, and hashes.
- `audit_minilang_artifact.py`: standard-library reproduction script.
- `validate_evidence.py`: source-independent integrity and completeness gate for
  the compact evidence package.

Reproduction requires the original archive plus selective extraction of
`results/translation/minilang.jsonl`, `MLML/data/translation/results.db`, and the
top-level result CSVs. It does not require the packaged Python environment.

The exact proof-tree depth and exact backend theorem dependency graph are not
recoverable from the flat JSONL without replay. The statistics label indentation
depth and `WITH` fan-in as proxies; they are not presented as semantic facts.

Run `python3 experiments/minilang_audit/validate_evidence.py` after checkout to
verify the retained manifest, semantic records, mappings, counts, samples, and
reports without restoring the 7 GB archive.
