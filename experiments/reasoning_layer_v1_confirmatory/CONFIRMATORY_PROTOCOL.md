# Reasoning-layer V1 — frozen FINAL_A confirmatory protocol

Frozen before unlocking `FRESH_FINAL_A`. The semantic discovery authority is commit
`aea77b0a4197682643337efcc2d61574a5158ca7` (tree
`35971201a0687e75267f9fc60dc8453005a79a96`). Existing HML serialization remains failed;
this protocol tests representation-neutral reasoning semantics, not HML syntax.

## Data and holdouts

- TRAIN begins from the frozen HML50K 10K rung; DEV is its 3,000-row development split.
- Neither old FINAL nor either fresh holdout is used for training or selection.
- `FRESH_FINAL_A` is exactly the 3,000 rows / 757 parents committed by
  `FRESH_HOLDOUT_MANIFEST.json`. Its identifiers are deterministically reconstructed from
  the frozen selection seed after this protocol commit and checked against every recorded
  set hash.
- `FRESH_FINAL_B` stays sealed. Its assignment payload is not opened by this experiment.
- All three arms use identical records, candidates, candidate order and `C0`–`C5` targets.

## Frozen information contract

The shared base is canonical JSON `{"current_lean_state": RAW_STATE_BEFORE}`.

- `BASE_STATE`: shared base only.
- `RAW_HISTORY`: shared base plus `raw_history`, a neutral chronological array of the exact
  last four successful pre-action `(state_before, action, state_after)` events.
- `SEMANTIC_STATE`: shared base plus `reasoning_state`, produced byte-deterministically by
  the frozen V1 extractor from exactly the shared base and those same four events.

V1 fields are unchanged: `active_goal`, `open_goals`, `local_dependencies`,
`active_scope`, `trajectory_position`, `recent_actions`, `recent_deltas`, and
`progress_summary`. No gold/current action, current state-after, future step, proof length,
candidate-derived label, failed route, inferred strategy, lemma role, distinct obligation,
or branch genealogy/coverage is permitted.

`trajectory_position.steps_completed` is a frozen V1 field but cannot be reconstructed
from four unindexed events alone. RAW therefore also receives the source-explicit scalar
`raw_prefix_metadata.successful_events_before_current`. This is neutral source metadata,
not a semantic annotation; it is deterministically renamed to the V1 field. No V1 field or
value changes.

The common user prompt has no system message. Only the bytes inside
`<REASONING_CONTEXT>...</REASONING_CONTEXT>` may differ:

```text
Choose the single most useful next mathematical tactic from the six candidates.

<REASONING_CONTEXT>
{ARM_PAYLOAD}
</REASONING_CONTEXT>

<CANDIDATES>
C0: {RAW_ACTION_0}
C1: {RAW_ACTION_1}
C2: {RAW_ACTION_2}
C3: {RAW_ACTION_3}
C4: {RAW_ACTION_4}
C5: {RAW_ACTION_5}
</CANDIDATES>

Answer with exactly one label:
C0 / C1 / C2 / C3 / C4 / C5
```

Preflight requires zero prefix, suffix, candidate, target, record, parent and ordering
mismatches; exact semantic reconstruction from BASE+RAW for all 16,000 train/dev/FINAL_A
rows; and zero truncation in any arm. Any failure stops before training.

## Frozen preflight resolution

The first preflight (after protocol commit `91b0fad0e1607214f4b844c1f1f30f2dafc9be83`)
correctly stopped: the RAW arm lacked the neutral prefix-count scalar above, and 31 primary
TRAIN rows exceeded the 6,144-token training limit. Sixty-two RAW prompts across all
splits exceeded that training limit, but every DEV/FINAL_A prompt was below the pinned
model's native context limit and the scorer does not truncate evaluation prompts.

Without changing V1 or any row's semantic content, the 31 over-length TRAIN records are
replaced identically in all arms by the first SHA-256-ordered unused HML50K TRAIN records
whose complete prompts fit all arms. The training set remains exactly 10,000 rows. The
64-row validation subset is likewise chosen identically across arms from complete DEV
prompts below 6,144. Full DEV and FINAL_A prompts are audited and scored without truncation
up to the pinned native context limit. Replacement IDs and hashes are frozen in the audit.

## Candidate construction

TRAIN and DEV retain their frozen HML50K six-candidate sets. FINAL_A uses the already
frozen HML50K deterministic hard-negative policy: prefer distinct actions with the same
tactic head and nearby character length, then the same observed effect, then split-wide
near-length actions, excluding the same theorem parent and duplicate action strings. Gold
position and distractor order are SHA-256 deterministic. Alternatives remain
`PLAUSIBLE_UNEXECUTED`; no applicability claim is introduced.

## Model and optimization

- Qwen/Qwen3-8B BF16 revision `b968826d9c46dd6066d109eabc6255188de91218`;
  no quantization.
- LoRA last 8 layers, `q_proj + o_proj`, rank 4, scale 2, dropout 0; Adam; learning rate
  `1e-4`; batch 2; prompt masking; gradient checkpointing; MAXSEQ 6,144.
- One complete 10K epoch: 5,000 optimizer steps. One Metal process at a time, local Mac
  only, no cloud, no arm-specific tuning.
- Thinking disabled. Equal-length `C0`–`C5` labels are scored by mean token log
  probability with the validated shared-prefix prompt-cache scorer.

## Statistics and gate

Seed 1 trains BASE, RAW and SEMANTIC sequentially. FINAL_A is scored only after all three
seed-1 adapters exist and their hashes are frozen. Primary metric is Top-1. Report MRR,
candidate-set NLL, entropy and correct-action margin secondarily.

Primary contrasts are RAW−BASE, SEMANTIC−BASE and SEMANTIC−RAW. Parent-clustered paired
bootstrap uses 4,000 draws and seed `20260824`. Seed 2 is authorized only when seed-1
SEMANTIC−RAW is at least +2pp and its clustered 95% CI lower bound is above zero. A
material signal requires SEMANTIC−RAW at least +5pp with CI above zero. Both seed-2 arms
must directionally favor SEMANTIC over RAW for replicated success.

Mechanical verdicts:

- material positive organization effect: `REASONING_LAYER_SIGNAL_FOUND`;
- credible positive RAW−BASE with negligible SEMANTIC−RAW: `HISTORY_SIGNAL_ONLY`;
- RAW exceeds SEMANTIC: `V1_SEMANTIC_COMPRESSION_FAILED`;
- BASE credibly exceeds both enriched arms: `ENRICHED_STATE_HURTS`;
- otherwise: `NO_REASONING_LAYER_SIGNAL`.

No module retraining or V1 edit is permitted. If organization is non-material, run the
predeclared row-level, module, depth and information-loss diagnostics, keep FINAL_B sealed,
and stop. Any V2 requires separate authorization.
