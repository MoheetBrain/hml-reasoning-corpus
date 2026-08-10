#!/usr/bin/env python3
"""Verify the freeze and score deterministic Semantic Firewall systems."""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/semantic_firewall"
FREEZE = HERE / "freeze_manifest.json"
FREEZE_SHA = HERE / "freeze_manifest.sha256"
RESULTS = HERE / "results"

sys.path.insert(0, str(ROOT))

from experiments.semantic_firewall.reference_checker import check_case  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze() -> dict[str, Any]:
    expected_line = FREEZE_SHA.read_text(encoding="utf-8").strip().split()[0]
    actual = sha256_file(FREEZE)
    if expected_line != actual:
        raise RuntimeError(f"freeze manifest hash mismatch: {actual} != {expected_line}")
    manifest = json.loads(FREEZE.read_text(encoding="utf-8"))
    for record in manifest["files"]:
        path = ROOT / record["path"]
        if not path.exists() or sha256_file(path) != record["sha256"]:
            raise RuntimeError(f"frozen file changed: {record['path']}")
    return manifest


def source_presence_baseline(case: dict[str, Any]) -> dict[str, Any]:
    """An unstructured/source-presence control, not a mathematical model.

    It can see that a plausible source span and before/after text exist, but it has
    no explicit invariant state and therefore accepts minimally corrupted twins.
    """

    enough_text = bool(case.get("source", {}).get("solution_span")) and bool(case.get("action", {}).get("summary"))
    return {"verdict": "VALID" if enough_text else "UNRESOLVED", "error_class": None}


def load_split(split: str) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    base = HERE / "data" / split.lower()
    labels = json.loads((base / "labels.json").read_text(encoding="utf-8"))
    records = []
    for path in sorted((base / "cases").glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        records.append((case, labels[case["case_id"]]))
    return records


def confusion(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for record in records:
        gold_invalid = record["gold"] == "INVALID"
        pred_invalid = record["prediction"] == "INVALID"
        if gold_invalid and pred_invalid:
            counts["true_invalid"] += 1
        elif gold_invalid and not pred_invalid:
            counts["false_accept"] += 1
        elif not gold_invalid and pred_invalid:
            counts["false_reject"] += 1
        else:
            counts["true_valid"] += 1
    return {key: counts[key] for key in ("true_valid", "false_reject", "true_invalid", "false_accept")}


def class_metrics(records: list[dict[str, Any]]) -> tuple[dict[str, Any], float]:
    classes = sorted({record["gold_class"] for record in records if record["gold_class"]})
    output = {}
    f1s = []
    for error_class in classes:
        tp = sum(record["gold_class"] == error_class and record["predicted_class"] == error_class for record in records)
        fn = sum(record["gold_class"] == error_class and record["predicted_class"] != error_class for record in records)
        fp = sum(record["gold_class"] != error_class and record["predicted_class"] == error_class for record in records)
        recall = tp / (tp + fn) if tp + fn else 0.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        output[error_class] = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
        f1s.append(f1)
    return output, sum(f1s) / len(f1s)


def score_system(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    runner: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = []
    for case, label in pairs:
        result = runner(case)
        records.append(
            {
                "case_id": case["case_id"],
                "pair_id": case["pair_id"],
                "gold": label["expected"],
                "gold_class": label["error_class"],
                "prediction": result["verdict"],
                "predicted_class": result.get("error_class"),
                "correct": result["verdict"] == label["expected"]
                and (label["expected"] != "INVALID" or result.get("error_class") == label["error_class"]),
                "checker_result": result,
            }
        )
    binary_correct = sum(record["prediction"] == record["gold"] for record in records)
    invalid_count = sum(record["gold"] == "INVALID" for record in records)
    false_accept = sum(record["gold"] == "INVALID" and record["prediction"] != "INVALID" for record in records)
    unresolved = sum(record["prediction"] == "UNRESOLVED" for record in records)
    per_class, macro_f1 = class_metrics(records)
    return records, {
        "cases": len(records),
        "binary_correct": binary_correct,
        "binary_errors": len(records) - binary_correct,
        "accuracy": binary_correct / len(records),
        "invalid_cases": invalid_count,
        "false_accepts": false_accept,
        "invalid_false_accept_rate": false_accept / invalid_count if invalid_count else 0.0,
        "unresolved": unresolved,
        "unresolved_rate": unresolved / len(records),
        "confusion": confusion(records),
        "per_error_class": per_class,
        "macro_f1_error_classes": macro_f1,
    }


def exact_mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2**n)
    return min(1.0, 2 * tail)


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        return float("nan")
    position = (len(values) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return values[low]
    return values[low] * (high - position) + values[high] * (position - low)


def paired_bootstrap(
    baseline: list[dict[str, Any]],
    system: list[dict[str, Any]],
    *,
    samples: int = 10_000,
    seed: int = 20260810,
) -> dict[str, list[float]]:
    rng = random.Random(seed)
    n = len(system)
    base_acc, sys_acc, rer = [], [], []
    for _ in range(samples):
        indices = [rng.randrange(n) for _ in range(n)]
        b_error = sum(baseline[index]["prediction"] != baseline[index]["gold"] for index in indices) / n
        s_error = sum(system[index]["prediction"] != system[index]["gold"] for index in indices) / n
        base_acc.append(1 - b_error)
        sys_acc.append(1 - s_error)
        if b_error:
            rer.append((b_error - s_error) / b_error)
    return {
        "baseline_accuracy_95ci": [percentile(base_acc, 0.025), percentile(base_acc, 0.975)],
        "system_accuracy_95ci": [percentile(sys_acc, 0.025), percentile(sys_acc, 0.975)],
        "relative_error_reduction_95ci": [percentile(rer, 0.025), percentile(rer, 0.975)],
        "samples": samples,
        "seed": seed,
    }


def evaluate_split(split: str) -> tuple[dict[str, Any], dict[str, Any]]:
    pairs = load_split(split)
    baseline_records, baseline_metrics = score_system(pairs, source_presence_baseline)
    system_records, system_metrics = score_system(pairs, check_case)
    baseline_error = 1 - baseline_metrics["accuracy"]
    system_error = 1 - system_metrics["accuracy"]
    rer = (baseline_error - system_error) / baseline_error if baseline_error else None
    b = sum(base["prediction"] == base["gold"] and sys["prediction"] != sys["gold"] for base, sys in zip(baseline_records, system_records))
    c = sum(base["prediction"] != base["gold"] and sys["prediction"] == sys["gold"] for base, sys in zip(baseline_records, system_records))
    comparison = {
        "baseline": baseline_metrics,
        "reference_checker": system_metrics,
        "relative_error_reduction": rer,
        "target_relative_error_reduction": 0.70,
        "target_met": rer is not None and rer >= 0.70,
        "mcnemar": {"baseline_only_correct": b, "reference_only_correct": c, "exact_two_sided_p": exact_mcnemar(b, c)},
        "paired_bootstrap": paired_bootstrap(baseline_records, system_records),
        "interpretation_boundary": "The source-presence control is deliberately unstructured and the negatives are controlled invariant mutations. This estimates deterministic firewall sensitivity, not open mathematical reasoning accuracy.",
    }
    raw = {"baseline": baseline_records, "reference_checker": system_records}
    return comparison, raw


def main() -> None:
    manifest = verify_freeze()
    metrics = {
        "result_version": "semantic-firewall-results-0.1.0",
        "freeze_manifest_sha256": sha256_file(FREEZE),
        "benchmark_counts": manifest["counts"],
        "DEV": None,
        "FINAL": None,
        "representation_experiment": {
            "status": "NOT_RUN_NO_CONFIGURED_MODEL_RUNNER",
            "structured_english": "PREPARED_UNSCORED",
            "generic_typed_ast": "PREPARED_UNSCORED",
            "hml": "PREPARED_AS_HML_PLUS_LOSSLESS_ADAPTER_UNSCORED",
            "warning": "Pure current-HML parity is blocked by candidate, branch/join, and arbitrary neutral-state fields. No comparative score is invented.",
        },
    }
    raw_results = {}
    for split in ("DEV", "FINAL"):
        comparison, raw = evaluate_split(split)
        metrics[split] = comparison
        raw_results[split] = raw
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (RESULTS / "predictions.json").write_text(json.dumps(raw_results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics["FINAL"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
