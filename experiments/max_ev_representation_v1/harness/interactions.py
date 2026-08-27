"""Predefined complexity-interaction analyses (mission §19).

Written and committed **before any Stage 1 result exists**, which is the only thing that
makes the word "predefined" mean anything. The axes, the binning rule, the statistic and the
direction of the hypothesis are all fixed here; running this module on a results file
performs the analysis and cannot choose it.

The hypothesis being tested is not "HML wins". §19 states it precisely: the interesting
prediction is not a constant advantage but an advantage that **grows with semantic
complexity**. So the reported statistic per axis is the difference-of-differences

    (HML - best control) in the top bin  -  (HML - best control) in the bottom bin

with a paired bootstrap over parent theorems. A positive interval that excludes zero is the
predicted result; a negative one is evidence against; an interval spanning zero is the
honest answer that this dataset cannot resolve it.

Axes that are degenerate in this corpus are reported as degenerate rather than binned into
meaningless strata. Obligation count is 0 for every item -- recorded Lean tactic states carry
no proof debt -- so "number of obligations" from §19's list cannot be tested here, and saying
so is more useful than inventing a stratification of a constant.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from .metrics import bootstrap_paired_delta

#: Feature -> how to bin it. Fixed in advance; nothing here may be chosen after seeing results.
ORDINAL_AXES = (
    "binder_depth",
    "max_dependency_depth",
    "n_claims",
    "n_cited",
    "n_dependency_edges",
    "goal_chars",
    "state_chars",
    "quantifiers",
)
BINARY_AXES = ("has_branch", "discharges_goal")
CATEGORICAL_AXES = ("domain_area",)

#: Also predefined: token length, which is not a dataset feature but an extraction output and
#: differs per arm. Handled separately because the axis value depends on the arm.
TOKEN_LENGTH_AXIS = "token_length"

#: An axis with fewer than this many items in a tail bin is reported but not tested; a
#: bootstrap over a handful of parents produces an interval wide enough to be uninformative
#: and narrow enough to look like a finding.
MIN_BIN = 30

CONTROL_ARMS = ("R_TYPED_AST", "R_LEANLIKE", "R_STRUCTURED_ENGLISH")
TREATMENT_ARM = "R_HML"


def _load_features(data_dir: Path, splits) -> dict[str, dict]:
    """item_id -> features, for every split under analysis."""
    out: dict[str, dict] = {}
    for split in splits:
        with gzip.open(data_dir / f"{split}.jsonl.gz", "rt", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                out[row["item_id"]] = row["features"]
    return out


def _terciles(values: np.ndarray):
    """Bottom and top third by value. Ties go to the lower bin, so bins never overlap.

    A heavily skewed axis can put its 67th percentile *at* the maximum -- ``quantifiers`` is
    0 for most items here -- which leaves the top bin empty. Both bins are checked for
    occupancy rather than only the percentile pair, so such an axis is reported as
    untestable instead of raising on an empty reduction.
    """
    if len(np.unique(values)) < 3:
        return None
    lo, hi = np.percentile(values, [33.333, 66.667])
    if lo == hi:
        return None
    low, high = values <= lo, values > hi
    if not low.any() or not high.any():
        return None
    return low, high


def _delta(correct_h: np.ndarray, correct_c: np.ndarray, mask: np.ndarray) -> float:
    if not mask.any():
        return float("nan")
    return float(correct_h[mask].mean() - correct_c[mask].mean())


def analyse(results: dict, data_dir: Path) -> dict:
    per_item = results["per_item"]
    splits = list(per_item["labels"])
    features = _load_features(data_dir, splits)
    token_lengths = results.get("token_lengths") or {}

    report: dict = {
        "hypothesis": (
            "The representation advantage grows with semantic complexity: "
            "(HML - best control) is larger in the top bin than the bottom bin."
        ),
        "statistic": "difference-of-differences in accuracy, paired bootstrap over parents",
        "min_bin_size": MIN_BIN,
        "splits": {},
    }

    for split in splits:
        labels = np.array(per_item["labels"][split])
        ids = per_item["item_ids"][split]
        parents = np.array(per_item["semantic_ids"][split])
        preds = {a: np.array(per_item["predictions"][a][split]) for a in per_item["predictions"]}
        correct = {a: (p == labels).astype(int) for a, p in preds.items()}

        best_control = max(CONTROL_ARMS, key=lambda a: correct[a].mean())
        ch, cc = correct[TREATMENT_ARM], correct[best_control]

        axes: dict[str, dict] = {}

        def record(name: str, low: np.ndarray, high: np.ndarray, detail: dict) -> None:
            entry = {
                "n_low": int(low.sum()), "n_high": int(high.sum()),
                "delta_low_bin": round(_delta(ch, cc, low), 4),
                "delta_high_bin": round(_delta(ch, cc, high), 4),
                **detail,
            }
            if low.sum() >= MIN_BIN and high.sum() >= MIN_BIN:
                dod = entry["delta_high_bin"] - entry["delta_low_bin"]
                entry["difference_of_differences"] = round(dod, 4)
                # Bootstrap the interaction directly: resample parents, recompute both bin
                # deltas on the resample, take the difference.
                diff_h = ch.astype(float) - cc.astype(float)
                entry["interaction_bootstrap"] = _interaction_ci(diff_h, low, high, parents)
                entry["tested"] = True
            else:
                entry["tested"] = False
                entry["reason"] = f"a tail bin has fewer than {MIN_BIN} items"
            axes[name] = entry

        for axis in ORDINAL_AXES:
            values = np.array([features[i].get(axis, 0) for i in ids], dtype=float)
            if len(np.unique(values)) < 2:
                axes[axis] = {
                    "tested": False,
                    "reason": f"degenerate in this corpus (constant value {values[0]:g})",
                }
                continue
            bins = _terciles(values)
            if bins is None:
                axes[axis] = {"tested": False, "reason": "too few distinct values to tercile"}
                continue
            low, high = bins
            record(axis, low, high, {
                "bin_rule": "terciles", "low_max": float(values[low].max()),
                "high_min": float(values[high].min()),
            })

        for axis in BINARY_AXES:
            values = np.array([bool(features[i].get(axis)) for i in ids])
            if len(np.unique(values)) < 2:
                axes[axis] = {"tested": False, "reason": "constant in this split"}
                continue
            record(axis, ~values, values, {"bin_rule": "false vs true"})

        for axis in CATEGORICAL_AXES:
            values = [str(features[i].get(axis)) for i in ids]
            by_group = defaultdict(list)
            for idx, v in enumerate(values):
                by_group[v].append(idx)
            axes[axis] = {
                "tested": False,
                "reason": "categorical: reported per group, no ordering to interact with",
                "per_group_delta": {
                    g: {
                        "n": len(idxs),
                        "delta": round(
                            float(ch[idxs].mean() - cc[idxs].mean()), 4
                        ),
                    }
                    for g, idxs in sorted(by_group.items())
                    if len(idxs) >= MIN_BIN
                },
            }

        if token_lengths:
            # Token length is per arm. The axis is the *treatment arm's* length, because the
            # question is whether HML's advantage changes with how long HML's own render is.
            hml_lengths = np.array(token_lengths.get(TREATMENT_ARM, {}).get(split, []), dtype=float)
            if hml_lengths.size == len(ids):
                bins = _terciles(hml_lengths)
                if bins is not None:
                    low, high = bins
                    record(TOKEN_LENGTH_AXIS, low, high, {
                        "bin_rule": "terciles of HML token count",
                        "low_max": float(hml_lengths[low].max()),
                        "high_min": float(hml_lengths[high].min()),
                    })

        report["splits"][split] = {
            "best_control": best_control,
            "overall_delta": round(float(ch.mean() - cc.mean()), 4),
            "axes": axes,
        }
    return report


def _interaction_ci(diff: np.ndarray, low: np.ndarray, high: np.ndarray,
                    parents: np.ndarray, iters: int = 5000, seed: int = 0) -> dict:
    """Bootstrap the difference-of-differences, resampling parent theorems."""
    rng = np.random.default_rng(seed)
    uniq, inverse = np.unique(parents, return_inverse=True)
    by_group = [np.flatnonzero(inverse == i) for i in range(len(uniq))]
    draws = []
    for _ in range(iters):
        pick = rng.integers(0, len(by_group), len(by_group))
        idx = np.concatenate([by_group[p] for p in pick])
        lo_mask, hi_mask = low[idx], high[idx]
        if not lo_mask.any() or not hi_mask.any():
            continue
        draws.append(diff[idx][hi_mask].mean() - diff[idx][lo_mask].mean())
    if not draws:
        return {"ci95": None, "excludes_zero": False, "iters": 0}
    lo_v, hi_v = np.percentile(draws, [2.5, 97.5])
    return {
        "ci95": [round(float(lo_v), 4), round(float(hi_v), 4)],
        "excludes_zero": bool(lo_v > 0 or hi_v < 0),
        "iters": len(draws),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results")
    ap.add_argument("--data", default="experiments/max_ev_representation_v1/dataset/v1")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    results = json.loads(Path(args.results).read_text())
    report = analyse(results, Path(args.data))
    out = Path(args.out or Path(args.results).with_name(
        Path(args.results).stem + "_interactions.json"))
    out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    for split, block in report["splits"].items():
        tested = [
            (name, a["difference_of_differences"], a["interaction_bootstrap"]["ci95"])
            for name, a in block["axes"].items() if a.get("tested")
        ]
        print(f"\n{split}: overall HML - {block['best_control']} = {block['overall_delta']:+.4f}")
        for name, dod, ci in sorted(tested, key=lambda t: -abs(t[1])):
            print(f"   {name:24s} interaction {dod:+.4f}  95% CI {ci}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
