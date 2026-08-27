"""Metrics for the action-validity probe (mission §12, §18).

Accuracy is reported but is not the primary quantity. The mission asks what a representation
makes *available*, which is an information question, so the headline number is

    StateInformationGain(R) = H(Y) - H(Y | R)

estimated as ``prior_cross_entropy - model_cross_entropy`` in bits per example. That has a
property accuracy does not: it is on a scale where the class-prior baseline is exactly 0 and
a perfect deterministic predictor is exactly H(Y), so "how much of the answer does this
representation carry" has a numerical answer rather than a comparison.

Calibration is reported alongside, because a probe can gain accuracy while becoming
overconfident, and an overconfident probe is a worse instrument for every downstream decision
this project would make.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np

__all__ = [
    "LABELS",
    "evaluate",
    "class_prior_metrics",
    "bootstrap_paired_delta",
    "mcnemar_counts",
]

LABELS = ("VALID", "INVALID", "UNRESOLVED")
EPS = 1e-12


def _one_hot(y: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros((len(y), k))
    out[np.arange(len(y)), y] = 1.0
    return out


def evaluate(probs: np.ndarray, y: np.ndarray, prior: np.ndarray | None = None) -> dict:
    """Full metric block for one arm on one split.

    ``probs`` is (n, 3) predicted probability; ``y`` is (n,) integer label; ``prior`` is the
    class distribution the baseline predicts, taken from **training** so the comparison is
    against a predictor that saw no test data.
    """
    n, k = probs.shape
    probs = np.clip(probs, EPS, 1.0)
    probs = probs / probs.sum(axis=1, keepdims=True)
    pred = probs.argmax(axis=1)

    correct = pred == y
    accuracy = float(correct.mean())

    per_class = {}
    f1s = []
    recalls = []
    for c in range(k):
        tp = float(((pred == c) & (y == c)).sum())
        fp = float(((pred == c) & (y != c)).sum())
        fn = float(((pred != c) & (y == c)).sum())
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[LABELS[c]] = {
            "precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4), "support": int((y == c).sum()),
        }
        f1s.append(f1)
        recalls.append(recall)

    cross_entropy = float(-np.log2(probs[np.arange(n), y]).mean())
    brier = float(((probs - _one_hot(y, k)) ** 2).sum(axis=1).mean())

    if prior is None:
        counts = np.bincount(y, minlength=k).astype(float)
        prior = counts / counts.sum()
    prior = np.clip(np.asarray(prior, dtype=float), EPS, 1.0)
    prior_ce = float(-np.log2(prior[y]).mean())

    confusion = [[int(((y == a) & (pred == b)).sum()) for b in range(k)] for a in range(k)]

    return {
        "n": int(n),
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(float(np.mean(recalls)), 4),
        "macro_f1": round(float(np.mean(f1s)), 4),
        "cross_entropy_bits": round(cross_entropy, 4),
        "prior_cross_entropy_bits": round(prior_ce, 4),
        "state_information_gain_bits": round(prior_ce - cross_entropy, 4),
        "brier": round(brier, 4),
        "per_class": per_class,
        "confusion_rows_true_cols_pred": confusion,
        "labels": list(LABELS),
        "correct_mask_sum": int(correct.sum()),
    }


def class_prior_metrics(y_train: np.ndarray, y_eval: np.ndarray) -> dict:
    """The baseline every arm must beat before any arm comparison is meaningful (§14A)."""
    k = len(LABELS)
    counts = np.bincount(y_train, minlength=k).astype(float)
    prior = counts / counts.sum()
    probs = np.repeat(prior[None, :], len(y_eval), axis=0)
    out = evaluate(probs, y_eval, prior=prior)
    out["prior"] = [round(float(p), 4) for p in prior]
    return out


def bootstrap_paired_delta(
    a_correct: np.ndarray,
    b_correct: np.ndarray,
    groups: np.ndarray,
    iters: int = 10000,
    seed: int = 0,
) -> dict:
    """Paired bootstrap over *semantic ids*, not rows (§18).

    The three items derived from one parent are not independent -- they share the whole state
    and differ in one mutation. Resampling rows would treat them as three observations and
    understate the interval. Resampling parents keeps siblings together.
    """
    rng = np.random.default_rng(seed)
    uniq, inverse = np.unique(groups, return_inverse=True)
    by_group = [np.flatnonzero(inverse == i) for i in range(len(uniq))]
    diff = a_correct.astype(float) - b_correct.astype(float)
    observed = float(diff.mean())
    draws = np.empty(iters)
    for i in range(iters):
        pick = rng.integers(0, len(by_group), len(by_group))
        idx = np.concatenate([by_group[p] for p in pick])
        draws[i] = diff[idx].mean()
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "delta": round(observed, 4),
        "ci95": [round(float(lo), 4), round(float(hi), 4)],
        "excludes_zero": bool(lo > 0 or hi < 0),
        "n_groups": int(len(uniq)),
        "iters": iters,
    }


def mcnemar_counts(a_correct: np.ndarray, b_correct: np.ndarray) -> dict:
    """Discordant pairs -- the only items that carry any information about which arm is better."""
    a_only = int(((a_correct == 1) & (b_correct == 0)).sum())
    b_only = int(((a_correct == 0) & (b_correct == 1)).sum())
    n = a_only + b_only
    if n == 0:
        return {"a_only": 0, "b_only": 0, "discordant": 0, "p_two_sided": 1.0}
    # Exact binomial two-sided test at p=0.5 over the discordant pairs.
    k = min(a_only, b_only)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return {
        "a_only": a_only, "b_only": b_only, "discordant": n,
        "p_two_sided": round(min(1.0, 2 * tail), 6),
    }
