# Authority recovery

## Decision

Both authority gates pass.

| Authority | Verified value |
|---|---|
| HML tag | `hml-semantic-pre-gemma-v1` |
| HML SHA | `84bf9897689b0ed78a2caaefc1db850d49b81260` |
| HML tree | `a81c8f414f0159a7a55dec5ddddbc5a955185d9d` |
| HML commit date | `2026-08-11T12:02:30+01:00` |
| HML checkout | clean; zero writable files |
| corpus SHA | `9d67e54450b9db897ee2ed20ec2e4cbbc16a3780` |
| current isolated branch | `codex/counterfactual-synth-v1` |
| Lean canonical path | `/home/moheet/HMLTN_CODEX_SYNTH/source_artifacts/lean_domino_v2/lean_canonical_records.jsonl` |
| Lean canonical SHA-256 | `8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869` |
| canonical records | 241,265 |
| represented theorems | 61,542 |
| excluded goal creation | 18,315 |
| original Lean transitions | 259,580 |
| source experiment SHA | `81feb32c7e6fbf0b486116a78ea46e6e4ce7713e` |

The arithmetic reconciles exactly: 241,265 +
18,315 = 259,580.

## Stale history

Historical pins `5688aba…` and `164d194…`, Gold-10/25/125, and the MiniLang handoff
were found only as history. None was used as runtime authority. The old corpus
submodule was not imported.

## Isolation

- Claude/FABLE files changed: **0**
- historical Codex handoff files changed: **0**
- frozen HML files changed: **0**

The local FABLE experiment checkout and research artifact store were read only. The
canonical JSONL was exported to the isolated VM workspace and re-hashed before use.
