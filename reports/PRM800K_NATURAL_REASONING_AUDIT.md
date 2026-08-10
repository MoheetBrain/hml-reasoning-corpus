# PRM800K natural reasoning error and action audit

## Status and verdict

**Audit complete as a bounded semantic-discovery pass.** The official OpenAI
PRM800K checkout was read at commit
`7ecc794703b2877f63226f2477a49b34f9b25163`. The four source files were
fingerprinted and never modified. HML core remained pinned, clean, and read-only at
`5688aba18632b65a8709aa1d85577d31a67dba6a`.

The main result is a boundary, not an ontology victory:

> PRM800K supports separating mathematical validity from progress, novelty, goal
> relevance, readability, and short-horizon verifiability. It does **not** support
> treating every `-1` as a violated HML core invariant. Natural `-1` labels mix
> arithmetic and domain errors, invalid transformations and inferences, source
> misreadings, incomplete answers, obvious dead ends, poor explanation, off-topic
> text, and some apparent rating disagreement. A textual prefix is insufficient for
> deterministic semantic classification of most cases.

The current first pass assigns exactly one class to every sampled `-1`, but preserves
`UNRESOLVED` for 438/500. This is deliberate. The resolved first-pass counts are not
prevalence estimates, and no HML core change is justified from them.

## 1. Source and protocol

| Item | Value |
|---|---|
| Repository | `https://github.com/openai/prm800k.git` |
| Commit | `7ecc794703b2877f63226f2477a49b34f9b25163` |
| Checkout role | external immutable input |
| Corpus mutation | generated audit artifacts only |
| HML mutation | none |
| Training | none |

### Source files

| File | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `phase1_train.jsonl` | 949 | 7,900,236 | `e9da6a73f827ffb9a8c0dc644c541d34ed76b3d4d1e4896ff5f7b37ddf5ae34d` |
| `phase1_test.jsonl` | 106 | 829,105 | `f4b3bc5b095e45c816453dc4d748b755c680d61d55f9895d929a335b487c727d` |
| `phase2_train.jsonl` | 97,782 | 456,135,365 | `1110237feeb51d1bc200cb37b8f965cfdc1036eac7d506094049366fe7dc1089` |
| `phase2_test.jsonl` | 2,762 | 12,240,719 | `6b172efa884ac8341a946dd82e06947c135b7254109fb3f7aa907c715d98aaad` |

### What the ratings mean

The original phase-1 and phase-2 labeler instructions define:

- `+1` / Great: appropriate, accurate, non-weird, quickly verifiable, and advancing
  the solution;
- `0` / Okay: reasonable, accurate, appropriate, and verifiable, but redundant,
  stalling, or non-advancing;
- `-1` / Bad: any confidently wrong, hard-to-verify, weird/off-topic, immediately
  dead-ending, circular, poorly explained, or incomplete-final-answer step.

This makes the labels intrinsically multi-criterion. In particular:

    rating = f(validity, verifiability, appropriateness,
               progress, relevance, explanation quality, completeness)

It is not:

    rating = semantic validity alone

Phase 1 explores alternatives throughout a dialogue and permits a human-written `+1`
continuation if no candidate is Great. Phase 2 follows a pre-generated solution until
the first detected error, then solicits critiques/alternatives and stops. Those collection
policies explain major differences in trajectory length, alternative count, and finish
reason.

## 2. Dataset audit before semantic classification

### Overall

| Quantity | Count |
|---|---:|
| JSONL solution trajectories | 101,599 |
| Unique problem texts | 11,293 |
| Candidate completions | 1,085,590 |
| Non-null `-1/0/+1` ratings | 1,046,365 |
| Unrated (`rating=null`) completions | 39,225 |
| `-1` | 262,146 |
| `0` | 106,024 |
| `+1` | 678,195 |
| Flagged `true` | 893 |
| Multi-candidate states | 90,926 |
| Alternatives beyond each state's first completion | 351,847 |
| Human-written completions | 2,598 |
| Quality-control trajectory rows | 8,097 |
| Initial-screening trajectory rows | 12,654 |

The repository name says “800K,” but this checkout contains 1,046,365 non-null
candidate ratings when all released phase/split rows, alternatives, QC presentations,
and screening rows are counted. The audit reports the released files rather than
forcing the paper-name number.

### Phase comparison

| Quantity | Phase 1 | Phase 2 |
|---|---:|---:|
| Trajectories | 1,055 | 100,544 |
| Unique problem texts | 1,004 | 11,286 |
| Candidate completions | 54,686 | 1,030,904 |
| Non-null ratings | 53,754 | 992,611 |
| `-1 / 0 / +1` | 21,626 / 11,101 / 21,027 | 240,520 / 94,923 / 657,168 |
| Unrated | 932 | 38,293 |
| Flagged `true` | 37 | 856 |
| Multi-candidate states | 6,456 | 84,470 |
| Alternatives beyond first | 37,397 | 314,450 |
| Human completions | 2,598 | 0 |
| Mean / median / p90 trajectory steps | 16.41 / 12 / 35 | 7.13 / 6 / 14 |
| Mean / median / p90 completions per state | 3.16 / 1 / 7 | 1.44 / 1 / 4 |
| Mean / median / p90 first state with any `-1` | 4.41 / 3 / 9 | 6.29 / 5 / 12 |

Phase-1 `chosen_completion` never selects a `-1` in this release. Phase 2 has 1,236
trajectories whose reconstructed chosen path contains a selected `-1`; most phase-2
errors appear as an unchosen alternative at the post-error decision state.

### Finish reasons

| Finish reason | Phase 1 | Phase 2 |
|---|---:|---:|
| `solution` | 898 (85.12%) | 12,252 (12.19%) |
| `found_error` | 0 | 84,080 (83.63%) |
| `give_up` | 157 (14.88%) | 3,937 (3.92%) |
| `bad_problem` | 0 | 275 (0.27%) |

These are collection outcomes, not model-solution accuracy estimates. Phase 2 is
designed to stop after finding an error.

## 3. State proxy construction

Every candidate record preserves:

- problem and available ground-truth solution/answer;
- phase, split, source line, trajectory ID, state index, and candidate index;
- preceding prefix reconstructed only from prior chosen model completions or prior
  human-written completions;
- all alternatives and ratings at the current decision state;
- chosen completion and human completion where present;
- finish reason, MATH subject/level where exact problem-text joining succeeds, and
  immutable source provenance.

The record is named `STATE_PROXY_CANDIDATE`. It is not called HML state because the
textual prefix does not fully recover typed declarations, canonical expressions,
dependencies, active assumptions, branch locality, candidates, goals, or obligations.
No conclusion below silently upgrades a state proxy into a semantic state.

## 4. Stratified discovery sample

The deterministic seed is `hmltn-prm800k-semantic-discovery-v1`. Sampling round-robins
phase, subject, level, early/middle/late position, trajectory-length bin, and alternative
count while maximizing unique problem texts before reuse.

| Sample | Records | Unique problem texts | Phase 1 | Phase 2 |
|---|---:|---:|---:|---:|
| `-1` candidates | 500 | 500 | 165 | 335 |
| `0` candidates | 250 | 250 | 78 | 172 |
| `+1` candidates | 250 | 250 | 113 | 137 |
| Phase-1 multi-candidate decisions | 200 | 200 | 200 | 0 |

The `-1` sample spans all seven MATH subjects and levels 1–5; nine source texts do not
join exactly to the released MATH metadata. The `0` and `+1` samples have five and one
such unmatched texts respectively. This is reported as `UNKNOWN`, not guessed.

## 5. `-1` error classification

### Conservative first pass

Each of the 500 sampled records has one primary class and all requested audit fields:
candidate step, preceding proxy, invariant, missing fact/warrant/precondition, current
HML representability, current firewall detectability, confidence, and explanation.

| Primary class | Count | Interpretation |
|---|---:|---|
| `FALSE_GOAL_DISCHARGE` | 32 | Explicit final-answer/QED closure rejected by the labeler. |
| `PRECONDITION_VIOLATION` | 3 | Explicit symbolic cancellation/division without visible nonzero evidence. |
| `OTHER` | 27 | Short, off-topic, weird, or apparent annotation-policy/label disagreement. |
| `UNRESOLVED` | 438 | Requires actual mathematical and source-alignment replay. |

Only 62/500 receive medium confidence; 438/500 are low-confidence unresolved. The 35
records mapped directly to a Semantic Firewall class are a **candidate review queue**, not
evidence that the firewall catches 7% of natural errors. The denominator includes mixed
annotation-policy causes, and the textual method has not proved the proposed class.

### Independent manual pressure test

Twelve records were selected across proposed classes and independently replayed against
the problem, prefix, and ground-truth solution. This is diagnostic, not a random
prevalence sample.

| Candidate | Manual class | Main finding |
|---|---|---|
| `phase1-test-000015-s003-c06` | `FALSE_GOAL_DISCHARGE` | degree 4 closes a degree-3 target incorrectly |
| `phase1-train-000007-s008-c07` | `FALSE_GOAL_DISCHARGE` | total English count substituted for English-only count |
| `phase1-test-000007-s020-c01` | `INVALID_INFERENCE` | rejects 49 without remaining checks and tries already-impossible 63 |
| `phase1-test-000058-s002-c03` | `MISREAD_PROBLEM` | reads visually ambiguous `log_2 64` serialization as 264 |
| `phase1-test-000006-s002-c05` | `ARITHMETIC_ERROR` | repeating decimals treated as tenths rather than ninths |
| `phase1-test-000017-s001-c06` | `INVALID_TRANSFORMATION` | branch-incorrect inverse-trig rewrite |
| `phase1-test-000003-s002-c06` | `OTHER` | conversion to base 10 is valid; apparent rating disagreement |
| `phase1-test-000034-s024-c07` | `DEPENDENCY_VIOLATION` | “two answers” inherits a false strict-inequality premise |
| `phase1-train-000329-s009-c03` | `ARITHMETIC_ERROR` | discriminant arithmetic uses 136 instead of 144 |
| `phase1-train-000046-s011-c04` | `OTHER` | correct but redundant sine definition; `0` is more plausible |
| `phase1-train-000390-s002-c03` | `FALSE_FACT` | divisor-count theorem conclusion is false, not a type error |
| `phase1-train-000019-s009-c02` | `OTHER` | “B is true” follows from the accepted divisibility check |

This falsifies lexical first-pass classes as prevalence estimates. It also shows why the
natural-error ontology must admit at least four layers:

1. source interpretation/alignment errors;
2. generic state/proof invariant errors;
3. mathematical content errors requiring libraries or checked backends;
4. annotation-policy disagreement/noise.

## 6. The `0` label

### First-pass reason coding

| Reason | Count |
|---|---:|
| insufficient progress | 193 |
| redundant computation | 18 |
| harmless detour | 14 |
| restatement | 10 |
| vague plan | 9 |
| semantically valid but goal-irrelevant | 6 |

These subtypes are conservative lexical proposals, not formal semantic judgements.
What is strong is the protocol-level result: labelers were explicitly instructed to use
`0` for correct, appropriate, verifiable steps that fail to add enough progress. Therefore
PRM800K directly supports separate axes for:

    validity / consistency / novelty / progress / goal relevance

It does not establish that every observed `0` was labelled perfectly. The manual `-1`
spotcheck already exposes plausible individual rating disagreement.

## 7. Same-prefix alternatives

The 200 phase-1 decision points contain 1,271 candidate completions: 435 `-1`, 376 `0`,
391 `+1`, and 69 unrated. Fifty-seven include a human-written completion. Simple feature
means are:

| Feature | `-1` | `0` | `+1` |
|---|---:|---:|---:|
| characters | 76.40 | 70.57 | 70.31 |
| math marker | 89.43% | 63.56% | 80.05% |
| plan marker | 20.92% | 34.84% | 27.37% |
| answer marker | 6.67% | 2.66% | 11.76% |
| max prefix Jaccard | 0.343 | 0.236 | 0.234 |
| problem Jaccard | 0.129 | 0.144 | 0.128 |

The same-prefix view is scientifically useful because context is held fixed, but these
lexical features are descriptive only. `-1` is actually most likely to contain a math marker,
so “looks mathematical” is not validity. `0` is most likely to contain a planning marker,
consistent with vague/noncommittal progress, but planning language alone does not imply
no progress. Semantic validity and progress require separate adjudicators.

## 8. Current HML support, inspected read-only

| Error/evaluation need | Current HML | Relevant implementation | Boundary exposed by PRM800K |
|---|---|---|---|
| dependency ancestry | supported | `reasoning/evidence.py`, `reasoning/check.py` | needs canonical premises, not text-prefix similarity |
| lexical scope and binding | supported/partial | `ast/nodes.py`, `reasoning/binders.py`, `reasoning/refinement.py` | general branch partition/join still absent |
| preconditions | partial, fail-closed | `reasoning/partiality.py`, `reasoning/side_conditions.py` | domain-contract coverage is incomplete |
| persistent obligations | supported/adapter partial | `reasoning/check.py`, `verification/obligations/*` | natural steps must synthesize the right debt |
| warrant identity/evidence | narrow support | `reasoning/kernel.py`, `reasoning/certificates/*` | broad theorem/domain evidence is absent |
| checker-owned status | supported | `ast/nodes.py`, `reasoning/check.py` | source cannot self-certify, correctly |
| exact goal discharge | supported | `ast/nodes.py`, `reasoning/check.py` | requires exact canonical target and completeness |
| type/domain checking | partial | `types.py`, `type_system/__init__.py` | broader mathematical domain contracts/libraries needed |
| candidate lifecycle | absent | no first-class generic candidate object | root/solution alternatives cannot be losslessly promoted/checked |
| certified branch join | absent beyond lexical scope | scopes exist; generic partition/join does not | natural case errors need explicit coverage and join evidence |
| arithmetic/symbolic truth | narrow exact fragments | obligation checkers and evaluator | most natural content errors need checked backends/libraries |
| source interpretation | upstream/absent | not an English semantic parser | misread problem and serialization ambiguity are not core execution defects |
| progress/novelty/relevance | architectural research axis | not a proof-validity status | should not contaminate `VERIFIED` |

The 13 existing HML probes passed and reported `hml_modified=false`. PRM800K does not
show that current HML's denotation or operational semantics are wrong. It shows that a
semantic firewall needs canonicalized state plus mathematical evidence, and that a
process-reward label covers dimensions outside a verifier's truth judgement.

## 9. Answers to the primary research questions

### 1. Do HML semantic axes explain naturally occurring mathematical errors?

**Partly.** Dependency, precondition, scope, obligation, candidate, branch, warrant,
epistemic, goal, and type/domain axes explain important structural failure mechanisms.
They do not by themselves decide arithmetic truth, symbolic equivalence, theorem
hypotheses, source interpretation, explanation quality, or progress. Those require
libraries/backends, interpretation/alignment, or process-quality evaluators.

### 2. Which invariants catch the largest fraction of `-1`?

**Not estimable from this pass.** Exact final-answer markers make false goal discharge
the largest high-precision review queue (32/500), but this is not a measured catch rate.
The 12-case pressure test shows that natural errors distribute across core invariants,
mathematical content, interpretation, and apparent label disagreement. A human replayed,
independently annotated sample is required before ranking invariants.

### 3. What distinguishes `0` from `+1`?

The annotation protocol says **progress/informativeness**, conditional on correctness,
appropriateness, and short-horizon verifiability. In same-prefix lexical summaries, `0`
has fewer math and answer markers and more plan markers, but text features are too weak
to be a semantic decision rule.

### 4. Does the dataset support validity separate from progress and relevance?

**Yes at the annotation-design level.** The `0` class was created for this distinction.
HML should represent verifier validity separately from novelty, progress, and goal
relevance. It should not lower a mathematically valid claim's epistemic status because the
claim is redundant, nor verify a false claim because it is goal-relevant.

### 5. What distinguishes same-prefix alternatives?

Same-prefix alternatives provide a clean comparative unit, but the phase-1 evidence says
the decisive features are semantic: correctness under the prefix, appropriateness,
verifiability, and amount of progress. Length, math notation, and lexical overlap do not
separate ratings reliably.

## 10. Architectural implications

1. Keep `VALIDITY`, `PROGRESS`, `NOVELTY`, `GOAL_RELEVANCE`, `CLARITY`, and
   `VERIFIABILITY_COST` as separate outputs.
2. Preserve a state-proxy/canonical-state boundary. Do not feed textual-prefix labels
   directly into core semantics.
3. Add no new HML operation keyword from PRM800K frequencies.
4. Reuse the existing checker-owned epistemic status and exact goal discharge.
5. Candidate lifecycle and certified branch join remain the smallest known absent HML
   semantic objects, but this audit does not add new implementation authority.
6. Put arithmetic, algebra, theorem, and domain checking behind replayable libraries or
   certificate-producing backends.
7. Add an upstream source-interpretation/alignment adjudicator for misread problems and
   notation ambiguity.
8. Treat label-policy mismatch/noise as a dataset property; never force it into a core
   semantic class.

## 11. Required next experiment

Before claiming natural-error coverage:

1. independently human-replay a random, blinded subset of at least 100 sampled `-1`
   records against full problem, prefix, and ground truth;
2. use two annotators plus adjudication and report agreement by layer and class;
3. separate `MATHEMATICAL_ERROR`, `INTERPRETATION_ERROR`, `PROCESS_QUALITY_FAILURE`,
   `ANNOTATION_DISAGREEMENT`, and `UNRESOLVED` before assigning a primary subtype;
4. canonicalize only the adjudicated subset into typed state, dependencies, goals,
   preconditions, obligations, candidates, and branches;
5. run the Semantic Firewall and domain backends on those canonical records;
6. report deterministic catch rate with unresolved and unsupported outcomes included;
7. preserve the same 200 phase-1 decision points for a matched validity-versus-progress
   evaluator.

No training, full-dataset ingestion into the corpus, HML core modification, or ontology
freeze should precede that adjudication.

## 12. Reproducibility and artifacts

- `experiments/prm800k_audit/audit_prm800k.py`: streaming dataset audit, state-proxy
  construction, deterministic sampling, and conservative first-pass coding.
- `experiments/prm800k_audit/results/source_manifest.json`: source fingerprints.
- `experiments/prm800k_audit/results/dataset_audit.json`: raw phase/split statistics.
- `experiments/prm800k_audit/results/sample_profile.json`: exact sample strata.
- `experiments/prm800k_audit/results/semantic_metrics.json`: first-pass summaries and
  method warning.
- `experiments/prm800k_audit/samples/deep_sample.jsonl`: 1,000 candidate records.
- `experiments/prm800k_audit/samples/phase1_decision_points.jsonl`: 200 same-prefix
  decision records.
- `experiments/prm800k_audit/annotations/*.jsonl`: one audit record per sampled
  candidate/decision point.
- `experiments/prm800k_audit/annotations/manual_spotcheck.json`: transparent
  independent pressure test and corrections.
- `tests/test_prm800k_audit.py`: state-proxy, cardinality, annotation-completeness,
  source-commit, and spotcheck-boundary tests.

The generator is a reproducible PRM800K audit/sampling tool. It is not an automatic
mathematical theorem replayer, automatic semantic extractor, or training pipeline.
