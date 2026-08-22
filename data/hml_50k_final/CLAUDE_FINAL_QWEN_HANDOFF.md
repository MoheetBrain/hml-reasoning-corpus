# Claude/FABLE final Qwen handoff

This package is executable and data-ready. It contains no model run.

## A–D. Authorities and exact locations

- Corpus repository base before this build:
  `3337217eb2cc9460b91ead15e4a67a420ecdcd8a`.
- Data payload commit: `fb6e28edec0f77753d97486cbae759a59f1d1f38`.
- Branch: `codex/hml-50k-final`.
- HML semantic authority: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`.
- Translation contract: `vnext-translation-contract-1.0.0`; golden validator 20/20 PASS.
- Mathlib: `29dcec074de168ac2bf835a77ef68bbe069194c5`.
- Canonical transition source SHA-256:
  `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869`.
- Prior FABLE result commit: `ccf2a43`; local FABLE checkout observed at handoff:
  `26d114001f5900c0325e8aa576d9adeb868b6f52`.
- Dataset root:
  `/Users/moheet/Documents/ChatGPT/hmlt-reasoning-corpus/data/hml_50k_final`.
- Per-file hashes: `HML50K_MANIFEST.json`, `HML50K_MANIFEST.sha256`, and `SHA256SUMS`.

## E–G. Population, rungs, grouping

- Canonical examples: 56,000 = 50,000 TRAIN + 3,000 DEV + 3,000 FINAL.
- Status: 56,000 FORMAL_TRACE; 0 FORMAL_VERIFIED, 0 HUMAN_PROCESS, 0 synthetic.
- Parents: 16,950 distinct theorems; 14,080 complete source trajectories, of which 5,897
  are multi-step (8,183 are complete single-step trajectories).
- Official LeanDojo train/val/test map to TRAIN/DEV/FINAL; parent overlap is zero.
- All 3,670 old VNext/autopsy parent IDs are excluded; FINAL contamination is zero.
- Nested rung ID hashes:
  - 10K: `1eeb0b2f79d3472b96f72b6b9ee47b12ee9c20b17a9de6e647877169b198bbff`
  - 30K: `255832921459b25dfe29fb86b20e38ab62e3e2e04d2067e359b8c8423cf137b4`
  - 50K: `4777d6e6a2751888473a6eec894da750c2394c1349c8e3be5582862b355f5391`
- `rungs/10k/record_ids.json` is the first 10K of 30K; 30K is the first 30K of 50K.

## H–J. Schema and view formats

Every task row has string-only `input_text` and `target_text`, plus `record_id`,
`parent_id`, `split`, `task`, `representation`, and audit hashes. The canonical audit row
contains source ID, epistemic status, exact neutral transition, trajectory metadata,
premises, complexity, candidates, mechanisms, and view hashes.

- HML: literal-UTF-8 VNext HML state plus the deterministic action/candidate envelope;
  state targets are literal-UTF-8 HML.
- Neutral: canonical JSON, `ensure_ascii=False`, sorted keys, compact separators; state
  targets are canonical Neutral JSON.
- No HML_TREE. No crossed target. Both views derive from the same canonical object.

Primary training files for rung `N`:

`rungs/Nk/NEXT_ACTION_SELECT/{HML_WORKED_UTF8,STRUCTURED_NEUTRAL_WORKED}/train.jsonl.gz`

Fixed evaluation files:

`tasks/NEXT_ACTION_SELECT/<VIEW>/{dev,final}.jsonl.gz`

Delta, judge, continuation, and structural-stress paths follow the same directory names.

## K–L. Token distributions and MAXSEQ

Qwen3-8B tokenizer at `b968826…`, no model loaded. Primary TRAIN input means are 453.384
HML and 411.412 Neutral tokens; p95 is 944 vs 742; max is 3,464 vs 3,373. HML costs
about 10.2% more primary tokens. Raw rows above 6,144 or 8,192: zero.

Use MAXSEQ 6,144 for `NEXT_ACTION_SELECT`. Use 8,192 for delta/continuation because raw
maxima 6,057/6,134 leave insufficient room for a runtime chat template at 6,144.

## M–N. Candidates and leakage

Six candidates per state, same set/order in both views. Mining priority: same tactic head,
same effect class, then split-wide length-nearest fallback; no distractor comes from the
same parent theorem and all tactic texts are distinct. Gold positions are balanced.
Distractors are `PLAUSIBLE_UNEXECUTED`, never fabricated `INVALID` labels.

Leak audit: 0 exact targets in delta inputs, 0 gold actions outside candidate blocks,
0 parent/near-duplicate overlap. Shortest-first 15.786% vs 16.667% chance; randomized-label
lexical baseline 16.661%. Lexical overlap on true labels is 51.836% and must be reported as
an intrinsic task signal.

## O–Q. Complexity, depth, source status

Complexity counts LOW/MEDIUM/HIGH/VERY_HIGH are 14,384 / 14,529 / 13,951 / 13,136.
Depth counts 1 / 2–3 / 4–5 / 6–10 / 11–20 / 21+ are
15,532 / 13,731 / 8,045 / 9,490 / 6,295 / 2,907. Probability/statistics-related rows:
6,639. All 56,000 rows are FORMAL_TRACE; the trace was not freshly replayed in Lean during
this Mac-only mission, so do not relabel it FORMAL_VERIFIED.

## R. Known limitations

The core is Lean-only because exact formal transitions were stronger than padding the mix
with unverified derived natural-language transitions. The semantic wrapper retains the
exact full Lean state as a proposition; it does not create source-unsupported branch,
obligation, or candidate-lifecycle state. Candidate alternatives are plausible and
unexecuted, so validity judging distinguishes FORMAL_TRACE from UNRESOLVED—not valid from
invalid. Lexical overlap is a strong 51.8% baseline. This dataset provides large-scale
teaching exposure, not evidence that HML works.

## S. Recommended Qwen budget and staged experiment

Batch size 2. Exact one-epoch primary input+target token counts:

| rung/view | tokens | iters 0.5 / 1 / 2 epochs | estimated minutes/seed 0.5 / 1 / 2 |
|---|---:|---:|---:|
| 10K HML | 4,564,438 | 2,500 / 5,000 / 10,000 | 30–53 / 61–105 / 122–210 |
| 10K Neutral | 4,145,911 | 2,500 / 5,000 / 10,000 | 24–41 / 47–82 / 95–164 |
| 30K HML | 13,683,806 | 7,500 / 15,000 / 30,000 | 91–158 / 182–315 / 365–630 |
| 30K Neutral | 12,419,080 | 7,500 / 15,000 / 30,000 | 71–122 / 142–245 / 283–490 |
| 50K HML | 22,769,206 | 12,500 / 25,000 / 50,000 | 152–262 / 303–524 / 607–1,048 |
| 50K Neutral | 20,670,614 | 12,500 / 25,000 / 50,000 | 118–204 / 236–408 / 472–815 |

Wall ranges scale the previously observed 335–579 seconds/1K iterations by new/prior mean
prompt length. They are planning estimates, not measurements of this corpus.

Run one seed at 10K first. Compare HML vs Neutral on Top-1, MRR, NLL, entropy, and
correct-action margin, stratified by depth, trajectory length, fact count, complexity,
action family, and source. Stop if HML is clearly flat/worse. Proceed to 30K only if a
material separation appears, and to 50K only if the learning-curve separation continues.
Use the unchanged DEV/FINAL sets for every rung. Do not automatically burn all compute.

THIS IS THE FINAL HML REPRESENTATION SCALING TEST.

If after adequate exposure:

    HML does not materially beat matched Neutral,
    the advantage does not increase with data scale,
    and no strong structural-complexity interaction appears,

then:

    HML_REASONING_REPRESENTATION_PROGRAM_TERMINATED

No:

    HML-V2
    HML-V3
    serializer rescue
    ontology rescue
    another tokenizer rescue
    another representation tweak

The useful pieces may survive as:

    compiler
    IR
    verifier
    mathematical state-machine infrastructure

but the claim of a large HML reasoning advantage ends.
