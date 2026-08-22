# HML50K Qwen token audit

Tokenizer only—no model weights were loaded. Authority:
`Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218`, local-files-only.

Primary TRAIN action-selection input tokens:

| view | mean | p50 | p95 | p99 | max | target mean |
|---|---:|---:|---:|---:|---:|---:|
| HML_WORKED_UTF8 | 453.384 | 385 | 944 | 1,426 | 3,464 | 2 |
| STRUCTURED_NEUTRAL_WORKED | 411.412 | 365 | 742 | 1,109 | 3,373 | 2 |

HML costs 10.2% more input+target tokens on the primary task. For state-delta prediction,
the mean combined cost is about 847.7 HML versus 617.2 Neutral tokens; maxima are 6,057 and
4,574. Continuation's HML maximum is 6,134.

Raw input+target rows exceeding 6,144: 0. Rows exceeding 8,192: 0. Use MAXSEQ 6,144 for
the primary action-selection experiment. Use 8,192 for delta/continuation to reserve room
for chat-template and BOS/EOS tokens; their raw maxima sit too close to 6,144.

Full per-task/split distributions are in `audits/token_length_audit.json`.
