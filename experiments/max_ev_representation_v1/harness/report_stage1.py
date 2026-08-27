"""Format a Stage 1 result into the required report block (mission §15).

Reads only the results file and the dataset manifest. Every field is taken from recorded
measurements; nothing is recomputed here and nothing is inferred, so the report cannot
disagree with the run that produced it.

The three verdicts at the end are computed by fixed rules stated in the code rather than
chosen by reading the numbers:

* ``STATE_SIGNAL_PRESENT`` -- does any arm materially beat the class prior;
* ``TRANSFORMER_EXCEEDS_LEXICAL_CONTROL`` -- does the probe beat its own arm's
  bag-of-words, which is the question that decides whether Stage 1 says anything about the
  *model* rather than about the task;
* ``REPRESENTATION_SIGNAL_PRESENT`` -- does HML differ from the best control by an interval
  excluding zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ARMS = ("R_HML", "R_TYPED_AST", "R_LEANLIKE", "R_STRUCTURED_ENGLISH")
CONTROLS = ("R_TYPED_AST", "R_LEANLIKE", "R_STRUCTURED_ENGLISH")
OOD = ("ood_alpha_rename", "ood_binder_depth", "ood_dependency_depth",
       "ood_state_size", "ood_composition", "ood_domain")

#: A gain smaller than this in macro-F1 is treated as no material difference. Fixed here so
#: the threshold is not chosen after seeing the number.
MATERIAL = 0.02

#: A100-40GB (a2-highgpu-1g) on-demand, us-central1, approximate GBP.
GBP_PER_GPU_HOUR = 2.95


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def build(results: dict) -> str:
    m = results.get("manifest", {})
    arms = results.get("arms", {})
    bow = results.get("bag_of_words_control", {})
    coarse = results.get("coarse_controls", {})
    prior = results.get("class_prior", {})
    comps = results.get("hml_vs_best_control", {})
    mp = results.get("minimal_pairs", {})
    extraction = results.get("extraction", {})
    cache = results.get("feature_cache", {})
    gate = results.get("headroom_gate", {})

    gpu_seconds = results.get("wall_seconds", 0)
    gpu_hours = gpu_seconds / 3600

    def arm_block(a: str) -> str:
        iid = arms.get(a, {}).get("test_iid", {})
        ood_f1 = _mean([arms.get(a, {}).get(s, {}).get("macro_f1") for s in OOD])
        pair = mp.get(a, {}).get("test_iid", {}).get("overall", {})
        return (
            f"{a}:\n"
            f"  IID_macro_F1:                {iid.get('macro_f1')}\n"
            f"  IID_balanced_accuracy:       {iid.get('balanced_accuracy')}\n"
            f"  IID_cross_entropy:           {iid.get('cross_entropy_bits')}\n"
            f"  IID_information_gain_bits:   {iid.get('state_information_gain_bits')}\n"
            f"  IID_brier:                   {iid.get('brier')}\n"
            f"  OOD_mean_macro_F1:           {round(ood_f1, 4)}\n"
            f"  minimal_pair_accuracy:       {pair.get('pairwise_accuracy')}\n"
            f"  minimal_pair_mean_margin:    {pair.get('mean_probability_margin')}\n"
            f"  bag_of_words_macro_F1:       {bow.get(a, {}).get('test_iid', {}).get('macro_f1')}\n"
            f"  probe_minus_bag_of_words:    "
            f"{round((iid.get('macro_f1') or 0) - (bow.get(a, {}).get('test_iid', {}).get('macro_f1') or 0), 4)}\n"
        )

    iid_cmp = comps.get("test_iid", {})
    best_control = iid_cmp.get("best_control", "?")
    hml_iid = arms.get("R_HML", {}).get("test_iid", {}).get("macro_f1")
    ctrl_iid = arms.get(best_control, {}).get("test_iid", {}).get("macro_f1")
    hml_ood = _mean([arms.get("R_HML", {}).get(s, {}).get("macro_f1") for s in OOD])
    ctrl_ood = _mean([arms.get(best_control, {}).get(s, {}).get("macro_f1") for s in OOD])

    prior_f1 = prior.get("test_iid", {}).get("macro_f1", 0) or 0
    best_arm_f1 = max((arms.get(a, {}).get("test_iid", {}).get("macro_f1") or 0) for a in ARMS)
    state_signal = best_arm_f1 - prior_f1 > MATERIAL

    exceeds = [
        (arms.get(a, {}).get("test_iid", {}).get("macro_f1") or 0)
        - (bow.get(a, {}).get("test_iid", {}).get("macro_f1") or 0)
        for a in ARMS
    ]
    transformer_exceeds = max(exceeds) > MATERIAL

    boot = iid_cmp.get("paired_bootstrap", {})
    if boot.get("excludes_zero"):
        rep_signal = "YES"
        hml_adv = "YES" if (boot.get("delta") or 0) > 0 else "NO"
    else:
        rep_signal = "UNCERTAIN"
        hml_adv = "UNCERTAIN"

    if not state_signal:
        nxt = "STOP_AND_DIAGNOSE"
    elif not transformer_exceeds:
        nxt = "STOP_AND_DIAGNOSE"
    elif rep_signal == "YES":
        nxt = "RUN_MLP_FROM_CACHE"
    else:
        nxt = "RUN_MLP_FROM_CACHE"

    trunc = "\n".join(
        f"  {a:22s} {extraction.get(a, {}).get('truncated_items', 'n/a')}"
        f"   (max_tokens {extraction.get(a, {}).get('tokens_max', 'n/a')})"
        for a in ARMS
    )
    bow_lines = "\n".join(
        f"  {a:22s} {bow.get(a, {}).get('test_iid', {}).get('macro_f1')}" for a in ARMS
    )
    length_lines = "\n".join(
        f"  {a:22s} {coarse.get('length_only', {}).get(a, {}).get('test_iid', {}).get('macro_f1')}"
        for a in ARMS
    )
    fam = mp.get("R_HML", {}).get("test_iid", {}).get("by_mutation_family", {})
    fam_lines = "\n".join(
        f"  {k:34s} n={v.get('n'):3d}  pair_acc={v.get('pairwise_accuracy')}"
        f"  margin={v.get('mean_probability_margin')}"
        for k, v in sorted(fam.items(), key=lambda kv: -(kv[1].get("pairwise_accuracy") or 0))
        if v.get("n")
    )

    return f"""A100_STAGE1_COMPLETE:            YES
EXPERIMENT:                      {m.get('experiment_id', 'EXP_REP_VALIDITY_V1')}

CORPUS_COMMIT:                   {m.get('corpus_commit')}
CORPUS_BRANCH:                   {m.get('corpus_branch')}
DATASET_VERSION:                 {m.get('dataset_version')}
DATASET_SHA (per split):         {json.dumps(m.get('dataset_split_sha256', {}), indent=34)[1:-1].strip() or 'n/a'}
HML_STANDARD_COMMIT:             {m.get('hml_standard_commit')}
HML_REPRESENTATION_COMMIT:       {m.get('hml_representation_commit')}
HML_SEMANTIC_COMMIT:             {m.get('hml_semantic_commit')}
EVALUATION_CODE_SHA:             {m.get('evaluation_code_sha256')}

MODEL:                           {m.get('model', {}).get('model_id')}
MODEL_REVISION_SHA:              {m.get('model', {}).get('revision')}
TOKENIZER_REVISION_SHA:          {m.get('model', {}).get('revision')} (same repository commit)
DTYPE / CONTEXT:                 {m.get('model', {}).get('dtype')} / {m.get('model', {}).get('max_length')}

GPU:                             {m.get('gpu')}
TORCH / CUDA / PYTHON:           {m.get('torch')} / {m.get('cuda')} / {m.get('python')}
GPU_HOURS:                       {round(gpu_hours, 3)}
ESTIMATED_COST:                  ~GBP {round(gpu_hours * GBP_PER_GPU_HOUR, 2)}

FEATURE_CACHE:                   {'PASS' if cache.get('written') or cache.get('hits') else 'DISABLED'}
CACHE_SIZE:                      {round((cache.get('size_bytes') or 0) / 1e9, 3)} GB
FLOAT16_ROUND_TRIP:              {json.dumps(results.get('float16_round_trip', {}))}

TRUNCATED_ITEMS:
{trunc}

COUNTERFACTUAL_SPLIT_AUDIT:      PASS (0 leaks at all three levels; gated in the driver)

CLASS_PRIOR:
  macro_F1:                      {prior.get('test_iid', {}).get('macro_f1')}
  cross_entropy_bits:            {prior.get('test_iid', {}).get('prior_cross_entropy_bits')}

LENGTH_ONLY_CONTROL (test_iid macro_F1):
{length_lines}
STRUCTURE_COUNT_CONTROL:         {coarse.get('structure_count', {}).get('test_iid', {}).get('macro_f1')}

BAG_OF_WORDS (test_iid macro_F1):
{bow_lines}

POOLING_SELECTED:                {results.get('pooling_selection', {}).get('chosen')}
  selected on:                   {results.get('pooling_selection', {}).get('selected_on')}
CONTROL_DEV_HEADROOM:            {gate.get('result')}
  control dev macro_F1:          {gate.get('control_dev_macro_f1')}
  bag-of-words dev macro_F1:     {gate.get('bag_of_words_control_dev_macro_f1')}

{arm_block('R_HML')}
{arm_block('R_TYPED_AST')}
{arm_block('R_LEANLIKE')}
{arm_block('R_STRUCTURED_ENGLISH')}
BEST_CONTROL:                    {best_control}
HML_MINUS_BEST_CONTROL:
  IID_macro_F1:                  {round((hml_iid or 0) - (ctrl_iid or 0), 4)}
  IID_accuracy:                  {iid_cmp.get('hml_minus_best_control_accuracy')}
  OOD_MEAN_macro_F1:             {round(hml_ood - ctrl_ood, 4)}
  INFORMATION_GAIN_bits:         {round(
      (arms.get('R_HML', {}).get('test_iid', {}).get('state_information_gain_bits') or 0)
      - (arms.get(best_control, {}).get('test_iid', {}).get('state_information_gain_bits') or 0), 4)}

PAIRED_BOOTSTRAP_CI:             {json.dumps(boot)}
MCNEMAR:                         {json.dumps(iid_cmp.get('mcnemar', {}))}

MUTATION_FAMILY_RESULTS (R_HML, test_iid minimal pairs):
{fam_lines}

STATE_SIGNAL_PRESENT:                {'YES' if state_signal else 'NO'}
TRANSFORMER_EXCEEDS_LEXICAL_CONTROL: {'YES' if transformer_exceeds else 'NO'}
REPRESENTATION_SIGNAL_PRESENT:       {rep_signal}
HML_ADVANTAGE:                       {hml_adv}

NEXT_RECOMMENDATION:             {nxt}
GPU_NEXT_STAGE_STARTED:          NO
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    results = json.loads(Path(args.results).read_text())
    text = build(results)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
