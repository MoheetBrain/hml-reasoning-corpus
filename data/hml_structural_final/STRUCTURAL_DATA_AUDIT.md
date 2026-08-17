# Structural Data Audit

Final data verdict: **INSUFFICIENT_STRUCTURAL_DATA**.

## Admission result

| Class | Admitted |
|---|---:|
| `FORMAL_VERIFIED` | 0 |
| `BACKEND_CERTIFIED` | 0 |
| `REPRESENTABLE_UNVERIFIED` | 0 |
| `HUMAN_PROCESS_LABEL` | 0 |
| `SYNTHETIC_STRUCTURAL_STRESS` | 0 |
| **headline total** | **0** |

There are 216,623 fresh exact Lean transitions carrying historical formal trace
evidence, but they were not admitted because the benchmark-level structural
population gate failed. “Source formally traced” is not reported as “admitted
FORMAL_VERIFIED.” Replay was not executable in the current environment.

## Aggregate rejection accounting

The mutually exclusive final-selection accounting is population-level:

| Reason | Rows |
|---|---:|
| old VNext/Qwen development parent | 42,957 |
| missing exact before/action/after | 0 among fresh traced transitions |
| fresh but structural population insufficient | 216,623 |
| **raw Lean transitions** | **259,580** |

The 216,623 fresh rows are not individually declared semantically unrepresentable.
They are withheld as a population because dependencies, distinct obligations,
candidate lifecycle/status, and general covered branch state are absent. Secondary
flags therefore overlap and are not added to the accounting: 215,399 lack multiple
goals before; 124,152 lack an explicit case scope before; all 216,623 lack a claim
dependency graph, distinct obligation, and candidate lifecycle state.

## Rungs and splits

No train/dev/FINAL split and no model-facing HML or neutral file was emitted. All
nested rungs are unavailable: `STRUCT_2K`, `STRUCT_5K`, `STRUCT_10K`,
`STRUCT_30K`, `STRUCT_50K`. No duplicate/padding/synthetic replacement was used.

## Kill-rule status

The representation programme kill rule was **not triggered**, because no matched
model test ran. The data verdict says the final hypothesis cannot be tested fairly
with the currently available sources; it is neither evidence for nor against HML.

