# MiniLang learning experiment reconstruction

## Result

The experiment supports two bounded claims:

1. under fixed base model and ATP condition, the Minilang training/rendering
   condition outperforms the corresponding Isar condition on PISA;
2. under fixed language, Sledgehammer* improves over original Sledgehammer.

It does not isolate operation-count reduction, semantic-boundary clarity, output
length, entropy, translated-data filtering, premise hints, or state recoverability
as individual causes. “Minimal semantics caused the gain” is too strong. The full
condition changes concrete proof representation and how proof obligations are
structured for automation; Minilang and Sledgehammer* are separately compared but
their internal mechanisms are not fully ablated.

## Experimental design

The primary source is [arXiv:2507.18885v4](https://arxiv.org/abs/2507.18885),
Sections 5.1–5.3 and Table 2, checked against the v2 artifact README, datasets,
scripts, and result CSVs.

| Component | Reconstructed setting |
|---|---|
| Task | Whole-proof generation, no iterative proof-agent scaffold |
| Base models | Llemma 7B and DeepSeek-Prover-Base v1.5 7B |
| Languages | Original/Thor-style Isar versus MiniLang |
| ATP levels | none, original Sledgehammer (SH), Sledgehammer* (SH*) |
| Conditions | 2 languages × 3 ATP levels = 6 per base model, 12 fine-tuned models |
| Source | Isabelle2024 HOL + AFP 2025-02-12 |
| Preprocessing | Remove unreachable code, PISA targets, and over-window proofs |
| Preprocessed Isar count | Artifact `fine_tune_data_isar`: 331,767 examples |
| Isar SH* count | Artifact `fine_tune_data_isar-SH*`: 321,963 examples |
| MiniLang SH* count | Artifact `fine_tune_data_minilang`: 284,542 examples |
| MiniLang no-SH count | Artifact `fine_tune_data_minilang-no-SH`: 283,511 examples |
| Paper rounded training source | ~332K proofs before condition-specific conversion |
| Training framework | LLaMA-Factory supervised fine-tuning |
| Epochs | 2 |
| Global batch size | 256 |
| Learning rate | 2×10^-5, linearly decayed to zero |
| Hardware/time | 8 NVIDIA H200 GPUs; approximately 12 h per training run |
| Prompt | preceding declarations/lemmas/proofs in same file + goal |
| Context budget | 4K tokens: 2K prompt and 2K response, distant context truncated |
| Inference | temperature 0 for pass@1; temperature 1.0 for pass@8 |
| Benchmark | PISA updated from 2022-12-06 to AFP 2025-02-12 |
| Test goals | paper: 2,962 available goals; artifact CSVs vary between 2,962 and 2,963 |
| Proof checking | Isabelle checker; proved if any of k samples verifies |
| ATP timeout | 30 seconds per Sledgehammer/SH* invocation |
| Evaluation compute | 3 nodes, 36 Intel i7 cores total; ~20 h per pass@8 language |
| Premise-learning state | reset before each model evaluation |

The artifact README says “12 physical CPU cores and 64 GB memory on each evaluation
server,” consistent with three servers/36 cores in the paper.

## Six corpus conditions

| Language | ATP | Corpus construction |
|---|---|---|
| Isar | none | Preprocessed original Isar |
| Thor-style Isar | SH | Replace tactics with Sledgehammer where it discharges the same obligation |
| Thor-style Isar | SH* | Same with SH* and extracted relevant-lemma hints |
| MiniLang | none | Pre-refinement translation retaining tactics as APPLY escape commands |
| MiniLang | SH | Remove lemma hints from MiniLang+SH* and use original hammer |
| MiniLang | SH* | Full 26-pass translation/refinement with SH* premise hints |

The “MiniLang none” condition is deliberately not pure ten-operation declarative
MiniLang: it retains APPLY tactics. The artifact's file naming uses `no-SH` for this
condition. Conversely, normal MiniLang END/NEXT intrinsically invokes the hammer.

## Paper-reported PISA results

| Base | Language | ATP | pass@1 | pass@4 | pass@8 |
|---|---|---|---:|---:|---:|
| DPSK-PB | MiniLang | SH* | 69.1% | 76.0% | 79.2% |
| DPSK-PB | MiniLang | SH | 59.9% | 68.1% | 72.4% |
| DPSK-PB | Thor-style Isar | SH* | 63.9% | 69.6% | 74.3% |
| DPSK-PB | Thor-style Isar | SH | 45.7% | 54.9% | 59.7% |
| DPSK-PB | MiniLang | none | 35.5% | 40.6% | 44.9% |
| DPSK-PB | Isar | none | 40.2% | 45.8% | 50.5% |
| Llemma | MiniLang | SH* | 68.0% | 74.9% | 78.9% |
| Llemma | MiniLang | SH | 58.7% | 67.9% | 72.2% |
| Llemma | Thor-style Isar | SH* | 63.3% | 66.9% | 72.1% |
| Llemma | Thor-style Isar | SH | 46.1% | 51.9% | 57.5% |
| Llemma | MiniLang | none | 35.2% | 39.8% | 44.6% |
| Llemma | Isar | none | 38.6% | 43.9% | 48.6% |

Controlled comparisons support:

- MiniLang+SH* versus Isar+SH*: +5.2/+4.7 points pass@1 and +4.9/+6.8
  pass@8 for DPSK/Llemma.
- MiniLang+SH versus Isar+SH: +14.2/+12.6 points pass@1 and +12.7/+14.7
  pass@8.
- Within MiniLang, SH* versus SH adds ~9.2–9.3 pass@1 points and 6.7–6.8
  pass@8 points.
- With ATP disabled, MiniLang falls behind Isar by ~3.4–4.7 pass@1 points and
  ~4.0–5.6 pass@8 points.

This interaction matters: MiniLang's advantage is strongest as a declarative
language coupled to automation, not as a generic tactic-script syntax.

## Artifact-result forensic checks

The top-level CSVs reconstruct the principal SH/SH* results closely (small case-count
and run/version differences explain some decimal discrepancies). They also expose
packaging anomalies:

1. All four `minilang-no-SH_*` CSVs are byte-for-byte identical to the corresponding
   `minilang-SH*_*` CSVs. Their measured rates are therefore 69.15/79.17% (DPSK) and
   68.04/78.94% (Llemma), not the paper's no-ATP 35.5/44.9 and 35.2/44.6.
2. The duplicated files are duplicated again under `results/raw/`; this is not only
   a top-level copy mistake.
3. `isar-no-SH_DPSK_pass1_result.db.csv` reports only 2 successes among 2,963 cases,
   inconsistent with Table 2's 40.2%, while its pass@8 file is approximately 50.5%.
4. CSV schemas differ between runs: some record one row per case with list-valued
   attempts/times; others record one row per attempted sample.
5. Result files alternate between 2,962 and 2,963 cases, whereas the paper says the
   updated benchmark has 2,962.

These anomalies do not invalidate the paper table, because multiple independent
CSV conditions match its main results and the official paper is the authoritative
reported analysis. They do mean the v2 artifact is not sufficient to reconstruct
every Table 2 cell from filenames alone. A faithful reproduction must regenerate
the affected conditions or obtain corrected result files from the authors.

Exact CSV hashes and reconstructed case/success counts are retained in
[`operation_statistics.json`](../experiments/minilang_audit/operation_statistics.json).

## Translation and corpus filtering

The translation database begins with 340,267 source goals and verifies 290,185
refined outputs (85.28%). Training generation applies further exclusions and token
limits, yielding 284,542 MiniLang SH* examples. Therefore the model comparison
includes condition-specific corpus cardinality and filtering effects.

The paper argues that losing ~15% does not erase the gain. That is supported as an
existence result, but translated-corpus selection remains a possible contributor:
successful translations are biased toward proofs the normalization and backend can
replay. There is no same-example, equal-token, equal-length training ablation that
isolates the language while controlling this selection.

## Failure analysis reported by the paper

For SH* pass@1, pooled/compared failure categories are reported as:

| Failure category | MiniLang | Thor-style Isar+SH* |
|---|---:|---:|
| Hammer fails | 16.0% | 20.5% |
| Operation fails | 3.4% | 6.4% |
| Term language | 5.3% | 4.2% |
| Undefined lemma | 3.5% | 2.6% |
| Proof language | 1.2% | 1.6% |
| Window overflow | 1.2% | 0.7% |
| Unknown | 0.3% | 0.4% |

The paper notes that reduced proof-language syntax error accounts for no more than
10% of the total performance gain; the larger differences are operation failure and
hammer success. Because error analysis records the first error, category changes are
not independent: resolving one class can expose another.

## What is and is not causally supported

| Proposed explanation | Evidence status |
|---|---|
| Fewer syntax forms help | Supported weakly: proof-language errors decline, but small share of gain |
| Fewer operations help | Not isolated: no vocabulary-size-only ablation |
| Clearer semantic boundaries help | Plausible; operation failures decline, but no boundary-only ablation |
| Shorter outputs help | Paper studies structure/length, but no length-matched causal comparison |
| Lower token entropy helps | Artifact command entropy is low; tokenizer/output entropy was not experimentally isolated |
| Easier state recovery helps | Not tested by whole-proof text generation; later AoA addresses this separately |
| Better Sledgehammer integration helps | Strongly supported by within-language SH→SH* improvements |
| Better obligation shape helps hammer | Plausible and consistent with fewer hammer failures; not mechanistically isolated |
| Translated-corpus filtering helps | Possible confound; no equal-example ablation |
| Representation familiarity helps | Base models should favor familiar Isar, yet MiniLang wins with ATP; does not isolate cause |
| Ten operations encode all reasoning | Not supported; proof work is heavily delegated |

The cleanest statement is: **the combined MiniLang representation/goal-structuring
condition improves declarative NTP under the tested ATPs and base models.**

## Missing reproducibility details

The following requested details are not recoverable exactly from the artifact/paper:

- optimizer type and optimizer hyperparameters beyond learning rate/schedule;
- exact gradient accumulation/microbatch configuration behind batch size 256;
- training step counts and seeds;
- model-token counts for each corpus and condition;
- exact tokenizer versions/config snapshots;
- exact train/dev split (the setup is training corpus plus PISA evaluation; no
  separately described development split was found);
- every condition's corrected raw result database;
- MLML/Isa-Mini Git commit SHA.

The archive supplies generated corpora, so steps/token counts could be recomputed
only after pinning the exact model tokenizers and training configs. Character counts
or whitespace tokens would not be valid substitutes.

## Representation versus semantics and AoA

The later [AoA paper](https://arxiv.org/abs/2607.16372) defines MiniLang's AST as a
recursive algebraic datatype exposed through JSON Schema, interleaves operation nodes
with subgoal-state nodes, and edits the proof tree directly. It reports 2.3–4.7× lower
normalized API cost, 2.9–6.9× fewer tokens, and 3.9–8.9× fewer tool calls versus a
conventional Isabelle text-editing agent on common-success sets.

AoA explicitly says no clean ablation separates Minilang from the tree-edit model.
It therefore strengthens the practical case for AST/state-first interaction but does
not prove that semantic minimality alone caused either study's gains.

## Next decisive experiment

After the current HML Semantic Firewall mechanisms exist, run a four-cell,
equal-example, equal-token-budget Gemma experiment:

| Cell | Canonical semantics | Model-facing representation |
|---|---|---|
| A | same neutral trajectories | natural-language/flat text |
| B | same neutral trajectories | textual HML |
| C | same neutral trajectories | generic syntax AST JSON |
| D | same neutral trajectories | semantic AST + explicit state/evidence deltas |

Hold train examples, tokenizer budget, target proofs, verifier, backend access,
sampling, and context constant. Measure verified success, semantic-firewall failures,
operation/term/syntax errors, token cost, state-recovery tool calls, calibration, and
out-of-distribution transfer. A further ablation can collapse interface labels over
the same kernel to test vocabulary size independently.

That experiment can distinguish text familiarity, syntax structure, semantic state,
and operation-vocabulary effects—the MiniLang/OOPSLA experiment cannot.
