# Preflight amendment — no training had begun

The first post-protocol preflight stopped as required. Holdout integrity and the common
envelope passed, but two pre-training gates failed:

1. `trajectory_position.steps_completed` used the full successful-prefix count, while RAW
   exposed only the last four unindexed triples. V1 therefore had one scalar unavailable to
   RAW. Resolution: expose that exact source scalar neutrally as
   `raw_prefix_metadata.successful_events_before_current`; V1 itself is unchanged.
2. Complete RAW prompts exceeded the 6,144-token training limit for 31 TRAIN, 23 DEV and 8
   FINAL_A rows (maximums 13,626 / 11,538 / 9,400). Resolution: replace only the 31 TRAIN
   rows by a frozen SHA-256-ordered HML50K reserve that fits all arms. The required neutral
   prefix-count scalar moved one additional TRAIN prompt above the boundary, so the final
   audited replacement count is 32. Select a matched safe
   64-row DEV validation subset. Full DEV/FINAL_A evaluation remains lossless and below the
   pinned model's native context limit; the scorer performs no truncation.

No adapter, prediction or FINAL_A score existed when this amendment was made. The failed
preflight did not inspect model results and FINAL_B remained unopened. The amended protocol
and driver are committed before the second preflight and before any training.
