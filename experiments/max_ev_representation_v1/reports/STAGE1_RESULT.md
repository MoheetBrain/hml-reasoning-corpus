A100_STAGE1_COMPLETE:            YES
EXPERIMENT:                      EXP_REP_VALIDITY_V1

CORPUS_COMMIT:                   unavailable
CORPUS_BRANCH:                   unavailable
DATASET_VERSION:                 DATASET_V1-1.0.0
DATASET_SHA (per split):         "dev": "f6896445acc4b7b6e025ff591988ddfc5ed2d55a35fff19caf62bd5de0e3782f",
                                  "ood_alpha_rename": "7b6918565e742520fd467d99fde90ee0e89ceeb623224926e972d30ea99b56d5",
                                  "ood_binder_depth": "3b70a357f8aa2b0ed1a9d3591a351017c211645ae9708a58ef72d5f71f83bc08",
                                  "ood_composition": "609a4b6b6e4cdf332e41e713b38cfca3e02580758a3c5eb25d1d03261c8b0327",
                                  "ood_dependency_depth": "d91b5181bf260ef67ca16ac45f4402c59ab2ef89d87af2378c2c865095a3290a",
                                  "ood_domain": "c50c06403ce5bb837cb89100cf52ce74018fde7b78ab00ad7f8f48bb6e29ee84",
                                  "ood_state_size": "5a63a65c90edea910465983ec54d658f24ba2f8b3bdd51d99c2fd300fb61ce1b",
                                  "test_iid": "bbf84dfa35ae425dccf3502638c29179963a73483699ae313bc129df68f81df8",
                                  "train": "316cf61a371fe7b993caeace868e92ded3d7534cd711565bb72a443447efe8d4"
HML_STANDARD_COMMIT:             5e0fc61d9cf92eae9d3ce7c54299520cd3702f7c
HML_REPRESENTATION_COMMIT:       b011511e72572608eb7836d3b8a1a6bb794c890d
HML_SEMANTIC_COMMIT:             b3d0af9ce5ed8d7c4d87086ceedd7e4fa5e74ad5
EVALUATION_CODE_SHA:             ad1dde17d99ecdc811d480ebf174216ab48ea1cc4466c4f04e426eaca77a2564

MODEL:                           Qwen/Qwen3-8B
MODEL_REVISION_SHA:              b968826d9c46dd6066d109eabc6255188de91218
TOKENIZER_REVISION_SHA:          b968826d9c46dd6066d109eabc6255188de91218 (same repository commit)
DTYPE / CONTEXT:                 bfloat16 / 8192

GPU:                             NVIDIA A100-SXM4-40GB
TORCH / CUDA / PYTHON:           2.9.1+cu129 / 12.9 / 3.10.12
GPU_HOURS:                       0.795
ESTIMATED_COST:                  ~GBP 2.34

FEATURE_CACHE:                   PASS
CACHE_SIZE:                      0.572 GB
FLOAT16_ROUND_TRIP:              {"max_abs_error": 2.9802322387695312e-08, "max_mean_shift": 0.0, "max_std_shift": 0.0, "mean_abs_error": 2.7240257033551984e-13, "mean_relative_error": 6.410002194832953e-13, "storage_dtype": "float16"}

TRUNCATED_ITEMS:
  R_HML                  0   (max_tokens 4101)
  R_TYPED_AST            0   (max_tokens 5132)
  R_LEANLIKE             0   (max_tokens 3386)
  R_STRUCTURED_ENGLISH   0   (max_tokens 3847)

COUNTERFACTUAL_SPLIT_AUDIT:      PASS (0 leaks at all three levels; gated in the driver)

CLASS_PRIOR:
  macro_F1:                      0.1667
  cross_entropy_bits:            1.585

LENGTH_ONLY_CONTROL (test_iid macro_F1):
  R_HML                  0.3379
  R_TYPED_AST            0.3225
  R_LEANLIKE             0.3223
  R_STRUCTURED_ENGLISH   0.3249
STRUCTURE_COUNT_CONTROL:         0.4305

BAG_OF_WORDS (test_iid macro_F1):
  R_HML                  0.7371
  R_TYPED_AST            0.7445
  R_LEANLIKE             0.7213
  R_STRUCTURED_ENGLISH   0.7559

POOLING_SELECTED:                mean_mid
  selected on:                   dev split, control arms only, before any test read
CONTROL_DEV_HEADROOM:            PASS
  control dev macro_F1:          0.7957
  bag-of-words dev macro_F1:     0.6968

R_HML:
  IID_macro_F1:                0.7701
  IID_balanced_accuracy:       0.7686
  IID_cross_entropy:           0.8645
  IID_information_gain_bits:   0.7206
  IID_brier:                   0.3316
  OOD_mean_macro_F1:           0.6615
  minimal_pair_accuracy:       0.9794
  minimal_pair_mean_margin:    0.4564
  bag_of_words_macro_F1:       0.7371
  probe_minus_bag_of_words:    0.033

R_TYPED_AST:
  IID_macro_F1:                0.7664
  IID_balanced_accuracy:       0.7667
  IID_cross_entropy:           0.8632
  IID_information_gain_bits:   0.7219
  IID_brier:                   0.3393
  OOD_mean_macro_F1:           0.6277
  minimal_pair_accuracy:       0.9647
  minimal_pair_mean_margin:    0.398
  bag_of_words_macro_F1:       0.7445
  probe_minus_bag_of_words:    0.0219

R_LEANLIKE:
  IID_macro_F1:                0.7759
  IID_balanced_accuracy:       0.7745
  IID_cross_entropy:           0.798
  IID_information_gain_bits:   0.7871
  IID_brier:                   0.3028
  OOD_mean_macro_F1:           0.6847
  minimal_pair_accuracy:       0.9706
  minimal_pair_mean_margin:    0.4796
  bag_of_words_macro_F1:       0.7213
  probe_minus_bag_of_words:    0.0546

R_STRUCTURED_ENGLISH:
  IID_macro_F1:                0.7939
  IID_balanced_accuracy:       0.7941
  IID_cross_entropy:           0.7747
  IID_information_gain_bits:   0.8104
  IID_brier:                   0.2916
  OOD_mean_macro_F1:           0.705
  minimal_pair_accuracy:       0.9853
  minimal_pair_mean_margin:    0.5283
  bag_of_words_macro_F1:       0.7559
  probe_minus_bag_of_words:    0.038

BEST_CONTROL:                    R_STRUCTURED_ENGLISH
HML_MINUS_BEST_CONTROL:
  IID_macro_F1:                  -0.0238
  IID_accuracy:                  -0.0255
  OOD_MEAN_macro_F1:             -0.0435
  INFORMATION_GAIN_bits:         -0.0898

PAIRED_BOOTSTRAP_CI:             {"ci95": [-0.0647, 0.0137], "delta": -0.0255, "excludes_zero": false, "iters": 10000, "n_groups": 170}
MCNEMAR:                         {"a_only": 59, "b_only": 72, "discordant": 131, "p_two_sided": 0.294406}

MUTATION_FAMILY_RESULTS (R_HML, test_iid minimal pairs):
  ALTER_BINDER_IDENTITY              n= 23  pair_acc=1.0  margin=0.514
  CLAIM_APPEARS_UNPRODUCED           n= 24  pair_acc=1.0  margin=0.3827
  EPISTEMIC_PROMOTION                n= 16  pair_acc=1.0  margin=0.5027
  EVIDENCE_SUPPORTS_OTHER_RULE       n= 11  pair_acc=1.0  margin=0.3865
  GOAL_VANISHES                      n= 17  pair_acc=1.0  margin=0.4006
  UNKNOWN_EVIDENCE_STATUS            n= 63  pair_acc=1.0  margin=0.5063
  UNKNOWN_PREMISE_STATUS             n= 65  pair_acc=1.0  margin=0.5814
  UNLICENSED_PREMISE_REWRITE         n=  5  pair_acc=1.0  margin=0.4426
  UNKNOWN_GOAL_STATUS                n= 42  pair_acc=0.9524  margin=0.3934
  WARRANT_EVIDENCE_DANGLES           n= 20  pair_acc=0.95  margin=0.482
  FALSE_GOAL_DISCHARGE               n= 19  pair_acc=0.9474  margin=0.2956
  REMOVE_REQUIRED_PREMISE            n= 19  pair_acc=0.9474  margin=0.3431
  DEPENDENCY_ANCESTRY_DRIFT          n= 16  pair_acc=0.875  margin=0.3045

STATE_SIGNAL_PRESENT:                YES
TRANSFORMER_EXCEEDS_LEXICAL_CONTROL: YES
REPRESENTATION_SIGNAL_PRESENT:       UNCERTAIN
HML_ADVANTAGE:                       UNCERTAIN

NEXT_RECOMMENDATION:             RUN_MLP_FROM_CACHE
GPU_NEXT_STAGE_STARTED:          NO


---

# Reading of the result

## Per-split macro-F1

| split | HML | Typed AST | Lean-like | Structured English | best |
|---|---|---|---|---|---|
| `test_iid` | 0.7701 | 0.7664 | 0.7759 | **0.7939** | STRUCTURED_ENGLISH |
| `ood_alpha_rename` | 0.6976 | 0.6878 | **0.7841** | 0.7374 | LEANLIKE |
| `ood_binder_depth` | 0.7335 | 0.7035 | 0.7312 | **0.7709** | STRUCTURED_ENGLISH |
| `ood_dependency_depth` | 0.6676 | 0.6529 | 0.6931 | **0.7119** | STRUCTURED_ENGLISH |
| `ood_state_size` | 0.6434 | 0.5172 | 0.6591 | **0.7170** | STRUCTURED_ENGLISH |
| `ood_composition` | 0.5300 | 0.5375 | 0.5525 | **0.5732** | STRUCTURED_ENGLISH |
| `ood_domain` | 0.6972 | 0.6672 | 0.6882 | **0.7199** | STRUCTURED_ENGLISH |

## HML against the best control, every split

| split | best control | delta | 95% CI | excludes zero |
|---|---|---|---|---|
| `test_iid` | STRUCTURED_ENGLISH | -0.0255 | [-0.0647, +0.0137] | no |
| `ood_alpha_rename` | LEANLIKE | -0.0852 | [-0.1444, -0.0259] | **YES** |
| `ood_binder_depth` | STRUCTURED_ENGLISH | -0.0333 | [-0.1000, +0.0333] | no |
| `ood_dependency_depth` | STRUCTURED_ENGLISH | -0.0381 | [-0.1143, +0.0381] | no |
| `ood_state_size` | STRUCTURED_ENGLISH | -0.0667 | [-0.1476, +0.0190] | no |
| `ood_composition` | STRUCTURED_ENGLISH | -0.0361 | [-0.0843, +0.0120] | no |
| `ood_domain` | STRUCTURED_ENGLISH | -0.0244 | [-0.0711, +0.0222] | no |

## What this says

**HML is not best on any split, and is never significantly best on any.** It ranks third of
four on the headline IID split. The single interval that excludes zero is
`ood_alpha_rename`, where HML is **worse** than the Lean-like arm by 0.085
(CI [-0.144, -0.026]). Every other split is a negative point estimate with an interval
spanning zero -- that is, unresolvable at this sample size, not equal.

Per §14D this result is preserved as it stands. It is not a reason to redesign the language,
and it is not evidence that HML is *worse* in any general sense: it is one task, one model,
one probe, at n=1,873 parents.

**The frozen transformer barely exceeds the lexical control.** Probe minus its own arm's
bag-of-words is +0.022 to +0.055 macro-F1. Of the ~0.77-0.79 achieved, roughly 0.72-0.76 is
reachable by counting tokens with no language model at all. State-comprehension claims must
therefore stay weak: what Stage 1 demonstrates is mostly that the *task* carries lexical
signal, not that the *model* is reading mathematical state.

**Structured English wins six of seven splits.** If notation helped a pretrained model read
mathematical state, the arm with no notation at all should not be the one in front. The most
economical reading is that explicitness -- not formality -- is what this model uses, and that
prose is the surface its pretraining prepared it best for.

**The Lean-like arm behaves unlike a memoriser.** Its *best* split is `ood_alpha_rename`
(0.7841, above its own IID 0.7759), where every bound name is replaced with one Mathlib never
used. That is the opposite of the retrieval signature the alpha-rename control was built to
detect, so its IID performance is not explained by having seen Mathlib.

**No predefined interaction survives.** Not one of the §19 axes -- binder depth, dependency
depth, state size, premise count, token length, branch presence -- produced an interaction
whose CI excludes zero, on any split. The specific hypothesis that HML's advantage *grows*
with semantic complexity is unsupported here.

**Minimal-pair discrimination is saturated.** All four arms score 0.96-0.99, so the metric
cannot separate them. That is an instrument finding, not a result: a one-edit counterfactual
is evidently easy to detect once the two states sit side by side in the same probe. A future
version needs harder pairs to make this measurement informative.

## Cost

0.79 GPU-hours on one A100-40GB, about GBP 2.34, plus roughly 20 minutes
of failed transfer attempts. The 84-second first attempt bought the torchaudio ABI defect.

## Provenance gap, recorded

`CORPUS_COMMIT` reads `unavailable` in the run manifest because the VM has no git checkout --
the payload ships as a tarball. The code that ran is the working tree at launch, whose
committed base was `4d64500` with the report formatter and driver retarget uncommitted at the
time. Both are committed alongside this report. The dataset is pinned exactly by the nine
per-split SHA-256 digests above, which were verified against the manifest before the GPU
started, so the *data* provenance has no gap.

