"""EXP_REP_VALIDITY_V1 Stage 1: frozen model, linear probe, four arms (mission §12-§14).

Order of operations is part of the design, not an implementation detail:

1. extract features for all four arms;
2. run the class-prior and bag-of-words controls;
3. choose the pooling rule on **dev, averaged over the three control arms** -- never on HML,
   and never on any test split (§13);
4. only then train the reported probes and read the test splits.

That order is what makes the HML comparison a prediction rather than a selection. A pooling
rule chosen because it favoured HML would guarantee the result it was meant to test.

The headroom gate runs before any arm comparison is interpreted. Two purpose-built corpora in
this project have already been lost to saturation -- eval001 at mean accuracy 0.961 and the
24-task V1 benchmark at 1.000 against a predicted 0.556 -- and in both cases the saturation
was only visible after the money was spent. Here it is a gate, evaluated on controls, that
stops the run.
"""

from __future__ import annotations

import argparse
import glob
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from .baselines import run_bag_of_words
from .cache import TOKEN_KEY, CacheKey, FeatureCache, verify_precision
from .shortcut_controls import (
    length_only_features,
    minimal_pair_report,
    run_coarse_control,
    structure_count_features,
)
from .extract import POOLINGS, ExtractConfig, extract_arm
from .metrics import (
    LABELS,
    bootstrap_paired_delta,
    class_prior_metrics,
    evaluate,
    mcnemar_counts,
)
from .probe import ProbeConfig, train_probe

EXPERIMENT_ID = "EXP_REP_VALIDITY_V1"

#: Arm order comes from the dataset manifest, not from ``..arms``.
#:
#: Stage 1 consumes rendered text; it never renders or parses anything. Importing the arms
#: package would pull in ``hamiltonian_lang``, whose ``StrEnum`` needs Python 3.11 -- and the
#: A100 image ships 3.10. Reading the manifest also makes the run self-describing: the arms
#: evaluated are exactly the arms the dataset was built with, by construction rather than by
#: two lists agreeing.
DEFAULT_ARMS = ("R_HML", "R_TYPED_AST", "R_LEANLIKE", "R_STRUCTURED_ENGLISH")

#: Control arms. HML is the treatment and is excluded from every calibration decision.
CONTROL_ARMS = ("R_TYPED_AST", "R_LEANLIKE", "R_STRUCTURED_ENGLISH")
TREATMENT_ARM = "R_HML"

#: §13. Below the floor the interface extracts nothing and the task is miscalibrated; above
#: the ceiling the corpus is too easy and no arm difference could be detected.
HEADROOM_FLOOR = 0.40
HEADROOM_CEILING = 0.95

EVAL_SPLITS = (
    "test_iid", "ood_alpha_rename", "ood_binder_depth", "ood_dependency_depth",
    "ood_state_size", "ood_composition", "ood_domain",
)


def _load_split(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _code_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unavailable"


def build_manifest(data_dir: Path, config: ExtractConfig, root: Path, repo: Path,
                   arm_names: tuple) -> dict:
    """§25: every run records what it was, exactly, or it is a notebook experiment."""
    import torch

    manifest = json.loads((data_dir / "MANIFEST.json").read_text())
    return {
        "experiment_id": EXPERIMENT_ID,
        "corpus_commit": _git(repo, "rev-parse", "HEAD"),
        "corpus_branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "corpus_dirty": bool(_git(repo, "status", "--porcelain")),
        "hml_semantic_commit": "b3d0af9ce5ed8d7c4d87086ceedd7e4fa5e74ad5",
        "hml_representation_commit": "b011511e72572608eb7836d3b8a1a6bb794c890d",
        "hml_standard_version": "1.0",
        "hml_standard_commit": "5e0fc61d9cf92eae9d3ce7c54299520cd3702f7c",
        "hml_standard_tag": "hml-standard-v1.0-2026-08-27",
        "dataset_version": manifest["dataset_version"],
        "dataset_split_sha256": {k: v["sha256"] for k, v in manifest["splits"].items()},
        "label_source": manifest["label_source"],
        "arms": list(arm_names),
        "task": "ACTION_VALIDITY",
        "model": config.to_dict(),
        "evaluation_code_sha256": _code_hash(root),
        "torch": torch.__version__,
        "cuda": getattr(torch.version, "cuda", None),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="experiments/max_ev_representation_v1/dataset/v1")
    ap.add_argument("--out", default="experiments/max_ev_representation_v1/results/stage1")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    #: Immutable Hugging Face commit. Never run science on a floating ``main``: an upstream
    #: reupload would silently change the experiment. This is also the revision the 50K
    #: corpus was tokenizer-preflighted against, so the pin preserves continuity too.
    ap.add_argument("--revision", default="b968826d9c46dd6066d109eabc6255188de91218")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--max-length", type=int, default=8192)
    ap.add_argument("--batch-tokens", type=int, default=16384)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--probe", default="linear", choices=["linear", "mlp"])
    ap.add_argument("--smoke", type=int, default=0, help="cap items per split for a smoke run")
    ap.add_argument("--cache", default="experiments/max_ev_representation_v1/cache")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--synthetic-encoder", action="store_true",
                    help="CPU pipeline check: deterministic hashed features, no model")
    args = ap.parse_args()

    data_dir = Path(args.data)
    dataset_manifest = json.loads((data_dir / "MANIFEST.json").read_text())
    ARM_NAMES = tuple(dataset_manifest["arms"])
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    repo = root.parents[1]
    started = time.time()

    splits = {}
    for name in ("train", "dev", *EVAL_SPLITS):
        path = data_dir / f"{name}.jsonl.gz"
        rows = _load_split(path)
        if args.smoke:
            rows = rows[: args.smoke]
        splits[name] = rows
        print(f"  {name:22s} {len(rows):5d} rows", flush=True)

    label_index = {lab: i for i, lab in enumerate(LABELS)}
    y = {k: np.array([label_index[r["label"]] for r in v]) for k, v in splits.items()}
    groups = {k: np.array([r["semantic_id"] for r in v]) for k, v in splits.items()}

    config = ExtractConfig(
        model_id=args.model, revision=args.revision, dtype=args.dtype,
        max_length=args.max_length, batch_tokens=args.batch_tokens, device=args.device,
    )

    # ---- 1. features ---------------------------------------------------------------
    features: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    extract_stats: dict[str, dict] = {}
    tok = model = None
    if not args.synthetic_encoder:
        from .extract import _load

        print(f"loading {args.model} ...", flush=True)
        tok, model = _load(config)

    cache = None
    if not args.synthetic_encoder and not args.no_cache:
        cache = FeatureCache(
            args.cache,
            CacheKey(
                model_sha=args.revision or "unpinned",
                tokenizer_sha=args.revision or "unpinned",
                dataset_sha=hashlib.sha256(
                    json.dumps(dataset_manifest["splits"], sort_keys=True).encode()
                ).hexdigest(),
                renderer_commit="b011511e72572608eb7836d3b8a1a6bb794c890d",
                code_sha=_code_hash(root),
                max_length=args.max_length,
                dtype=args.dtype,
                poolings=tuple(POOLINGS),
            ),
        )
        if args.smoke:
            # A capped run holds a prefix of each split, so its tensors are not the tensors
            # a full run needs. Sharing a key would poison the full run's cache.
            cache = None
            print("  cache disabled for smoke run (row subset would poison the full key)",
                  flush=True)

    for arm in ARM_NAMES:
        print(f"extracting {arm} ...", flush=True)
        features[arm] = {}
        arm_started = time.time()
        for split, rows in splits.items():
            texts = [r["renders"][arm] for r in rows]
            if args.synthetic_encoder:
                features[arm][split] = _synthetic(texts)
                continue
            cached = cache.load(arm, split) if cache else None
            if cached is not None and len(cached["mean_last"]) == len(texts):
                features[arm][split] = cached
                print(f"    {split}: cache hit", flush=True)
                continue
            features[arm][split] = extract_arm(texts, config, tok, model)
            if cache:
                cache.store(arm, split, features[arm][split], dict(config.stats))
        extract_stats[arm] = dict(config.stats)
        extract_stats[arm]["arm_wall_seconds"] = round(time.time() - arm_started, 2)
        print(f"  {arm} done in {extract_stats[arm]['arm_wall_seconds']}s"
              + (f"  tokens_max={config.stats.get('tokens_max')}"
                 f" truncated={config.stats.get('truncated_items')}"
                 if config.stats else ""), flush=True)

    # Hard gate: a clipped arm compared against unclipped controls measures verbosity, not
    # readability. Refuse rather than record a caveat nobody will read.
    truncating = {
        a: st.get("truncated_items", 0) for a, st in extract_stats.items()
        if st.get("truncated_items", 0)
    }
    if truncating:
        print(f"\nTRUNCATION_GATE: FAIL -- {truncating}. Raise --max-length and re-run.",
              flush=True)
        return 4

    if model is not None:
        del model
        import torch

        torch.cuda.empty_cache()

    eval_names = list(EVAL_SPLITS)

    # ---- 2. controls ---------------------------------------------------------------
    print("class-prior baseline ...", flush=True)
    prior = {s: class_prior_metrics(y["train"], y[s]) for s in ("dev", *eval_names)}

    print("bag-of-words control ...", flush=True)
    bow: dict[str, dict] = {}
    for arm in ARM_NAMES:
        res = run_bag_of_words(
            [r["renders"][arm] for r in splits["train"]], y["train"],
            [r["renders"][arm] for r in splits["dev"]], y["dev"],
            {s: [r["renders"][arm] for r in splits[s]] for s in ("dev", *eval_names)},
            seed=args.seeds[0],
        )
        bow[arm] = {
            s: evaluate(res["probs"][s], y[s], prior=np.array(prior["dev"]["prior"]))
            for s in ("dev", *eval_names)
        }
        bow[arm]["_vocabulary_size"] = res["vocabulary_size"]
        print(f"  {arm:24s} dev macroF1 {bow[arm]['dev']['macro_f1']:.4f}", flush=True)

    # ---- 2b. coarse shortcut controls (§4) -----------------------------------------
    # Neither is a blocker. They answer a question the leakage audit cannot: single-token
    # mutual information says nothing about what a *combination* of coarse features can do,
    # and a linear probe on pooled embeddings is exactly the model that would exploit one.
    print("coarse shortcut controls ...", flush=True)
    coarse: dict = {}

    for arm in ARM_NAMES:
        res = run_coarse_control(
            length_only_features([r["renders"][arm] for r in splits["train"]]), y["train"],
            length_only_features([r["renders"][arm] for r in splits["dev"]]), y["dev"],
            {s: length_only_features([r["renders"][arm] for r in splits[s]])
             for s in ("dev", *eval_names)},
            seed=args.seeds[0],
        )
        coarse.setdefault("length_only", {})[arm] = {
            s: evaluate(res["probs"][s], y[s], prior=np.array(prior["dev"]["prior"]))
            for s in ("dev", *eval_names)
        }
        print(f"  length-only  {arm:24s} dev macroF1 "
              f"{coarse['length_only'][arm]['dev']['macro_f1']:.4f}", flush=True)

    # Structure counts describe the semantic object, which is identical across arms, so this
    # control is computed once from the uniformly tagged AST render rather than per arm.
    ast_arm = "R_TYPED_AST"
    struct_res = run_coarse_control(
        structure_count_features([r["renders"][ast_arm] for r in splits["train"]]), y["train"],
        structure_count_features([r["renders"][ast_arm] for r in splits["dev"]]), y["dev"],
        {s: structure_count_features([r["renders"][ast_arm] for r in splits[s]])
         for s in ("dev", *eval_names)},
        seed=args.seeds[0],
    )
    coarse["structure_count"] = {
        s: evaluate(struct_res["probs"][s], y[s], prior=np.array(prior["dev"]["prior"]))
        for s in ("dev", *eval_names)
    }
    print(f"  structure-count (shared)          dev macroF1 "
          f"{coarse['structure_count']['dev']['macro_f1']:.4f}", flush=True)

    # ---- 2c. what float16 caching costs, measured not assumed (§6) ------------------
    precision_check = (
        verify_precision(features[ARM_NAMES[0]]["dev"]["mean_last"])
        if not args.synthetic_encoder else {}
    )
    if precision_check:
        print(f"  float16 round trip: mean rel err "
              f"{precision_check['mean_relative_error']:.2e}, "
              f"max std shift {precision_check['max_std_shift']:.2e}", flush=True)

    # ---- 3. pooling chosen on dev, control arms only (§13) -------------------------
    probe_device = "cuda" if args.device == "cuda" else "cpu"
    pooling_scores = {}
    for pooling in POOLINGS:  # POOLINGS never includes __token_lengths__
        scores = []
        for arm in CONTROL_ARMS:
            res = train_probe(
                features[arm]["train"][pooling], y["train"],
                features[arm]["dev"][pooling], y["dev"],
                {"dev": features[arm]["dev"][pooling]},
                ProbeConfig(kind=args.probe, seed=args.seeds[0]),
                device=probe_device,
            )
            scores.append(evaluate(res["probs"]["dev"], y["dev"])["macro_f1"])
        pooling_scores[pooling] = round(float(np.mean(scores)), 4)
        print(f"  pooling {pooling:18s} control dev macroF1 {pooling_scores[pooling]:.4f}",
              flush=True)
    chosen = max(pooling_scores, key=pooling_scores.get)
    print(f"chosen pooling (controls only): {chosen}", flush=True)

    # ---- 4. headroom gate on controls, dev only (§13) -------------------------------
    # Two ways a benchmark can be worthless, and both are checked before any arm comparison
    # is read. The second is the one this project keeps hitting: a task can be unsaturated
    # for the *model* and still be solved by counting tokens, in which case the probe's
    # margin over bag-of-words -- not over the class prior -- is the whole result.
    control_dev = pooling_scores[chosen]
    bow_control_dev = float(np.mean([bow[a]["dev"]["macro_f1"] for a in CONTROL_ARMS]))
    bow_spread = round(
        max(bow[a]["dev"]["macro_f1"] for a in ARM_NAMES)
        - min(bow[a]["dev"]["macro_f1"] for a in ARM_NAMES),
        4,
    )
    gate = "PASS"
    if control_dev >= HEADROOM_CEILING:
        gate = "INSUFFICIENT_CEILING"
    elif control_dev <= HEADROOM_FLOOR:
        gate = "INSUFFICIENT_FLOOR"
    elif bow_control_dev >= HEADROOM_CEILING:
        gate = "INSUFFICIENT_LEXICALLY_SATURATED"
    print(f"headroom gate: {gate} (control dev macro-F1 {control_dev:.4f}, "
          f"bag-of-words {bow_control_dev:.4f}, arm spread {bow_spread}; "
          f"floor {HEADROOM_FLOOR}, ceiling {HEADROOM_CEILING})", flush=True)

    # ---- 5. reported probes ---------------------------------------------------------
    results: dict[str, dict] = {}
    per_seed_correct: dict[str, dict[str, np.ndarray]] = {}
    predictions: dict[str, dict[str, list]] = {}
    probabilities: dict[str, dict[str, list]] = {}
    minimal_pairs: dict[str, dict[str, dict]] = {}
    for arm in ARM_NAMES:
        per_split: dict[str, list] = {s: [] for s in eval_names}
        dev_scores = []
        correct_acc: dict[str, np.ndarray] = {}
        for seed in args.seeds:
            res = train_probe(
                features[arm]["train"][chosen], y["train"],
                features[arm]["dev"][chosen], y["dev"],
                {s: features[arm][s][chosen] for s in ("dev", *eval_names)},
                ProbeConfig(kind=args.probe, seed=seed),
                device=probe_device,
            )
            dev_scores.append(evaluate(res["probs"]["dev"], y["dev"])["macro_f1"])
            for s in eval_names:
                per_split[s].append(res["probs"][s])
        arm_out = {"dev_macro_f1_by_seed": [round(v, 4) for v in dev_scores]}
        predictions[arm] = {}
        probabilities[arm] = {}
        minimal_pairs[arm] = {}
        for s in eval_names:
            mean_probs = np.mean(per_split[s], axis=0)
            arm_out[s] = evaluate(mean_probs, y[s], prior=np.array(prior["dev"]["prior"]))
            correct_acc[s] = (mean_probs.argmax(axis=1) == y[s]).astype(int)
            # Stored so the §19 interaction analyses can run afterwards from this file
            # alone. Without them every predefined breakdown would need the GPU again,
            # which is how predefined analyses quietly become post-hoc ones.
            predictions[arm][s] = [int(v) for v in mean_probs.argmax(axis=1)]
            probabilities[arm][s] = [[round(float(x), 5) for x in row] for row in mean_probs]
            minimal_pairs[arm][s] = minimal_pair_report(mean_probs, splits[s], label_index)
        results[arm] = arm_out
        per_seed_correct[arm] = correct_acc
        print(f"  {arm:24s} test_iid macroF1 {arm_out['test_iid']['macro_f1']:.4f} "
              f"gain {arm_out['test_iid']['state_information_gain_bits']:.4f} bits", flush=True)

    # ---- 6. paired comparison, HML vs best control (§18) ----------------------------
    comparisons = {}
    for split in eval_names:
        best_control = max(CONTROL_ARMS, key=lambda a: results[a][split]["macro_f1"])
        a = per_seed_correct[TREATMENT_ARM][split]
        b = per_seed_correct[best_control][split]
        comparisons[split] = {
            "best_control": best_control,
            # The margin that matters: each arm against *its own* lexical control, which
            # normalises out how token-solvable that particular surface happens to be.
            "probe_minus_own_bag_of_words_macro_f1": {
                arm: round(
                    results[arm][split]["macro_f1"] - bow[arm][split]["macro_f1"], 4
                )
                for arm in ARM_NAMES
            },
            "bag_of_words_macro_f1": {
                arm: bow[arm][split]["macro_f1"] for arm in ARM_NAMES
            },
            "hml_macro_f1": results[TREATMENT_ARM][split]["macro_f1"],
            "best_control_macro_f1": results[best_control][split]["macro_f1"],
            "hml_minus_best_control_accuracy": round(float(a.mean() - b.mean()), 4),
            "paired_bootstrap": bootstrap_paired_delta(a, b, groups[split]),
            "mcnemar": mcnemar_counts(a, b),
            "per_arm_macro_f1": {arm: results[arm][split]["macro_f1"] for arm in ARM_NAMES},
            "per_arm_information_gain_bits": {
                arm: results[arm][split]["state_information_gain_bits"] for arm in ARM_NAMES
            },
        }

    payload = {
        "manifest": (
            build_manifest(data_dir, config, root, repo, ARM_NAMES)
            if not args.synthetic_encoder
            else {"synthetic_encoder": True, "dataset": str(data_dir)}
        ),
        "probe_kind": args.probe,
        "seeds": args.seeds,
        "pooling_selection": {
            "scores_control_dev": pooling_scores,
            "chosen": chosen,
            "selected_on": "dev split, control arms only, before any test read",
        },
        "headroom_gate": {
            "result": gate,
            "control_dev_macro_f1": round(control_dev, 4),
            "bag_of_words_control_dev_macro_f1": round(bow_control_dev, 4),
            "bag_of_words_arm_spread": bow_spread,
            "class_prior_dev_macro_f1": prior["dev"]["macro_f1"],
            "floor": HEADROOM_FLOOR,
            "ceiling": HEADROOM_CEILING,
        },
        "extraction": extract_stats,
        "token_lengths": {
            arm: {
                split: [int(v) for v in features[arm][split]["__token_lengths__"]]
                for split in ("dev", *eval_names)
            }
            for arm in ARM_NAMES
        } if not args.synthetic_encoder else {},
        "class_prior": prior,
        "bag_of_words_control": bow,
        "arms": results,
        "minimal_pairs": minimal_pairs,
        "coarse_controls": coarse,
        "feature_cache": cache.report() if cache else {"enabled": False},
        "float16_round_trip": precision_check,
        "hml_vs_best_control": comparisons,
        "per_item": {
            "labels": {s: [int(v) for v in y[s]] for s in eval_names},
            "item_ids": {s: [r["item_id"] for r in splits[s]] for s in eval_names},
            "semantic_ids": {s: [r["semantic_id"] for r in splits[s]] for s in eval_names},
            "predictions": predictions,
            "probabilities": probabilities,
            "class_order": list(LABELS),
        },
        "wall_seconds": round(time.time() - started, 2),
    }
    out = out_dir / (f"{EXPERIMENT_ID}_{args.probe}"
                     + ("_smoke" if args.smoke or args.synthetic_encoder else "") + ".json")
    out.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


def _synthetic(texts: list[str]) -> dict[str, np.ndarray]:
    """A deterministic hashed encoder, for exercising the pipeline without a model.

    Not a model and not a baseline: it exists so the probe, metrics, split handling and
    reporting can be validated on CPU before any GPU time is bought. It carries real lexical
    signal (hashed token counts) so the probe has something to fit, which is what makes the
    smoke test able to fail.
    """
    import zlib

    from .baselines import TOKEN

    # zlib.crc32 rather than ``hash``: str hashing is salted per process, so a run would not
    # reproduce and a smoke test that cannot reproduce cannot verify anything.
    dim = 256
    out = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for tok in TOKEN.findall(text):
            out[i, zlib.crc32(tok.encode()) % dim] += 1.0
    out = np.log1p(out)
    return {p: out for p in POOLINGS}


if __name__ == "__main__":
    sys.exit(main())
