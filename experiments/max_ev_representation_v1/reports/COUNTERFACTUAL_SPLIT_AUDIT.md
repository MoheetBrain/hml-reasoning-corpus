# COUNTERFACTUAL_SPLIT_AUDIT

**Verdict: PASS.** Required for GPU spend: `cross_split_family_leaks = 0`.

```
families_total                    1873
source_families_total             1873
rows                              5619
cross_split_family_leaks          0
cross_split_source_family_leaks   0
exact_duplicate_leaks             0
near_duplicate_leaks              0
within_split_duplicate_groups     0
verdict                           PASS
```

## Why three levels, not one

Row-level deduplication cannot catch this failure, because the counterfactual siblings **are**
different rows. They share the entire mathematical state and differ in one edit, so a parent
in train and a sibling in test would make the test item a near-copy of a training item and the
reported generalisation fiction.

| level | what it catches | result |
|---|---|---|
| semantic family (`semantic_id`) | a parent and its own mutations straddling a split | 0 leaks |
| source theorem (`provenance.parent_id`) | two steps of one Mathlib proof landing in different splits | 0 leaks |
| canonical fingerprint | two *different* theorems that produce the same state — ids would never reveal it | 0 exact, 0 near |

The third level matters because Mathlib genuinely repeats tactic states across files. The
fingerprint is a whitespace-normalised hash of the HML render, deliberately blunt: for a leak
audit a false positive costs one inspection and a false negative costs the experiment.

## Family structure

`siblings_per_family = {'3': 1873}` — every one of the 1873 families
contributes exactly three items (VALID, INVALID, UNRESOLVED). `families_total` equals
`source_families_total`, so each Mathlib theorem contributes exactly one parent; no two items
in the dataset descend from the same proof.

## Rows per split

```
dev                        510
ood_alpha_rename           270
ood_binder_depth           210
ood_composition            249
ood_dependency_depth       210
ood_domain                 450
ood_state_size             210
test_iid                   510
train                     3000
```

## Recorded identity (§1, §2)

```
CORPUS_COMMIT              223c4e938e4e7f542605a70cb9a4e84a09d72c97
DATASET_HASH               e1e42f037571d54b5136ed8770f7f5ef01146e2af320add1f39e916005cd6a87
HARNESS_HASH               35f8e7dff5a9a35eb8c2bec89ad4280183d95ce9375a46f865052c2d40cfe84d
HML_STANDARD_COMMIT        5e0fc61d9cf92eae9d3ce7c54299520cd3702f7c
HML_REPRESENTATION_COMMIT  b011511e72572608eb7836d3b8a1a6bb794c890d
HML_SEMANTIC_COMMIT        b3d0af9ce5ed8d7c4d87086ceedd7e4fa5e74ad5
MODEL_ID                   Qwen/Qwen3-8B
MODEL_REVISION_SHA         b968826d9c46dd6066d109eabc6255188de91218
TOKENIZER_REVISION_SHA     b968826d9c46dd6066d109eabc6255188de91218  (same repository commit)
```

The model revision is the same commit the 50K corpus was tokenizer-preflighted against, so
pinning it preserves continuity with the corpus's own token-budget calibration as well as
protecting the run from an upstream reupload.

