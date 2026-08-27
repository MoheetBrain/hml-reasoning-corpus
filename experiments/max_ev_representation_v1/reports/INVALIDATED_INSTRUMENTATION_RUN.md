# INVALIDATED_INSTRUMENTATION_RUN — the 50K HML representation result

**Status: `INVALID_FOR_HML_REPRESENTATION_INFERENCE`.**
The raw result is preserved. It must not be used as treatment evidence about the frozen HML
representation, in this or any later meta-analysis.

## What was measured

A representation comparison over `data/hml_50k_final`, pairing the view named
`HML_WORKED_UTF8` against `STRUCTURED_NEUTRAL_WORKED`, reported HML at **-3.41pp** of
next-action accuracy.

## Why it is invalid

The HML view carried literal `\uXXXX` escape *text* inside the payload strings the model
read. The matched neutral view did not. The confound is therefore perfectly asymmetric by
arm, and it is large relative to the effect the experiment was trying to detect.

Re-audited at the decoded-payload level on 2026-08-27
(`experiments/max_ev_representation_v1/audit/unicode_payload.py`):

| task | arm | rows | contaminated rows | literal escapes | share of prompt |
|---|---|---:|---:|---:|---:|
| NEXT_ACTION_SELECT | HML_WORKED_UTF8 | 56,000 | 56,000 | 1,583,612 | **15.96%** |
| NEXT_ACTION_SELECT | STRUCTURED_NEUTRAL_WORKED | 56,000 | 0 | 0 | 0.00% |
| STATE_DELTA_PREDICT | HML_WORKED_UTF8 | 56,000 | 56,000 | 4,122,149 | **25.39%** |
| STATE_DELTA_PREDICT | STRUCTURED_NEUTRAL_WORKED | 56,000 | 0 | 0 | 0.00% |
| VALIDITY_JUDGE | HML_WORKED_UTF8 | 112,000 | 112,000 | 3,167,224 | **21.78%** |
| VALIDITY_JUDGE | STRUCTURED_NEUTRAL_WORKED | 112,000 | 0 | 0 | 0.00% |
| WORKED_CONTINUATION | HML_WORKED_UTF8 | 56,000 | 56,000 | 4,122,149 | **23.63%** |
| WORKED_CONTINUATION | STRUCTURED_NEUTRAL_WORKED | 56,000 | 0 | 0 | 0.00% |

**280,000 of 280,000 HML rows are contaminated; 0 of 280,000 neutral rows are.** Total
12,995,134 literal escape sequences. The mission's recorded estimate of 15.2% matches the
primary task (15.96%); the other three tasks are worse.

Evidence: `reports/old_50k_unicode_payload_audit.json`.

## Why the original audit passed it

`HML50K_UNICODE_AUDIT.md` reported `PASS`, and its measurement was correct. It counted JSON
`\uXXXX` escape sequences **in the serialized file** and found zero — which was true, because
every row was written with `ensure_ascii=False`.

The defect was one layer in. An inner serialization had already escaped the mathematics
before the outer writer ever saw it, so the file-level JSON contained no escapes while the
*decoded string the model reads* contained six literal characters where a glyph belonged.
Escaping at the JSON layer and escaping inside the payload are different defects, and only
the second one reaches the model.

`tests/test_unicode_payload.py::test_raw_file_shows_no_json_level_escapes` pins both halves
of that distinction so it cannot be reintroduced silently.

## What was not wrong

The **canonical source is clean.** Scanned across 3,000 canonical records,
`neutral_transition` contains zero literal `\uXXXX` sequences and real non-ASCII glyphs in
every row. The contamination was introduced entirely at render time, which is why
regeneration repairs it and why no mathematical content was ever lost.

The frozen renderer is also already correct: `semantic_state/view.py` at `b011511` passes
`ensure_ascii=False` throughout and documents this exact defect in its module docstring.

## What replaces it

`DATASET_V1` (`dataset/v1`), regenerated from the canonical source through the frozen
renderer, with literal-escape contamination of **0** in all four arms. It does not reproduce
the old experiment: the task, the label source and the arm set are all different, so it is a
replacement instrument, not a re-run. The -3.41pp figure has no successor value and should
not be quoted as one.

## Disposition

- Do not delete the historical artifact or its audits.
- Do not cite -3.41pp as evidence for or against HML.
- Any future meta-analysis must exclude this run or record it under this status.
