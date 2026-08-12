from __future__ import annotations

import collections
import math
import re
from typing import Any, Callable

from .canonical import canonical_json
from .constants import SENTINELS


def contradiction_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    seen: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for row in rows:
        seen[(row["prediction_contract"], row["learner_input_hash"])].add(row["label"])
    conflicts = {f"{contract}:{key}": sorted(labels) for (contract, key), labels in seen.items() if len(labels) > 1}
    return {"unique_inputs": len(seen), "conflicting_input_count": len(conflicts), "conflicts": conflicts}


def leakage_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_split: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        if row.get("source_theorem_id"):
            by_split[row["source_split"]].add(str(row["source_theorem_id"]))
    pairs = (("TRAIN", "DEV"), ("TRAIN", "FINAL"), ("DEV", "FINAL"))
    overlaps = {f"{a}_INTERSECT_{b}": sorted(by_split[a] & by_split[b]) for a, b in pairs}
    return {"theorems_by_split": {key: len(value) for key, value in sorted(by_split.items())}, "overlap_counts": {key: len(value) for key, value in overlaps.items()}, "overlap_examples": {key: value[:10] for key, value in overlaps.items()}}


def _accuracy(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], str]) -> float:
    return sum(predict(row) == row["label"] for row in rows) / len(rows)


def _majority_by(rows: list[dict[str, Any]], feature: Callable[[dict[str, Any]], str]) -> float:
    counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for row in rows:
        counts[feature(row)][row["label"]] += 1
    return sum(counts[feature(row)].most_common(1)[0][0] == row["label"] for row in rows) / len(rows)


def _length_threshold(rows: list[dict[str, Any]]) -> float:
    values = [(len(canonical_json(row["canonical_source"])), row["label"]) for row in rows]
    best = 0.0
    for threshold in sorted({length for length, _ in values}):
        for low_label in ("APPLICABLE", "NOT_APPLICABLE"):
            other = "NOT_APPLICABLE" if low_label == "APPLICABLE" else "APPLICABLE"
            score = sum((low_label if length <= threshold else other) == label for length, label in values) / len(values)
            best = max(best, score)
    return best


def _lexical_nb(rows: list[dict[str, Any]]) -> float:
    tokenized = [set(re.findall(r"[A-Za-z][A-Za-z0-9_:]*", canonical_json(row["canonical_source"]))) for row in rows]
    groups = [row["neighborhood_id"] for row in rows]
    predictions: list[str] = []
    labels = [row["label"] for row in rows]
    for index, tokens in enumerate(tokenized):
        fold = int(rows[index]["learner_input_hash"][:8], 16) % 5
        train = [i for i, group in enumerate(groups) if int(rows[i]["learner_input_hash"][:8], 16) % 5 != fold and group != groups[index]]
        scores = {}
        vocab = set().union(*(tokenized[i] for i in train)) if train else set()
        for label in ("APPLICABLE", "NOT_APPLICABLE"):
            members = [i for i in train if labels[i] == label]
            score = math.log((len(members) + 1) / (len(train) + 2))
            for token in vocab:
                present = sum(token in tokenized[i] for i in members)
                probability = (present + 1) / (len(members) + 2)
                score += math.log(probability if token in tokens else 1 - probability)
            scores[label] = score
        predictions.append(max(scores, key=scores.get))
    return sum(a == b for a, b in zip(predictions, labels)) / len(labels)


def shortcut_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sentinel_hits = sum(any(token in canonical_json(row["canonical_source"]).lower() for token in SENTINELS) for row in rows)
    majority = collections.Counter(row["label"] for row in rows).most_common(1)[0][1] / len(rows)
    return {
        "sentinel_occurrences": sentinel_hits,
        "sentinel_rule_accuracy": _accuracy(rows, lambda row: "NOT_APPLICABLE" if any(token in canonical_json(row["canonical_source"]).lower() for token in SENTINELS) else "APPLICABLE"),
        "majority_accuracy": majority,
        "mutation_only_accuracy": _majority_by(rows, lambda row: row["applicability_family"]),
        "changed_field_accuracy": _majority_by(rows, lambda row: "domain" if row["applicability_family"] == "DOMAIN_LATTICE" else "scope"),
        "action_family_accuracy": _majority_by(rows, lambda row: row["canonical_source"]["candidate_action"]["operation"]),
        "best_in_sample_length_threshold_accuracy": _length_threshold(rows),
        "lexical_naive_bayes_group_holdout_accuracy": _lexical_nb(rows),
        "full_frozen_semantic_oracle_accuracy": 1.0,
        "note": "Mutation-only excludes audit labels and provenance; only learner-hidden family/change metadata is used.",
    }


def factory_b_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    causal = collections.Counter(row["causal_class"] for row in rows)
    labels = collections.Counter(row["label"] for row in rows)
    neighborhoods: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        neighborhoods[row["neighborhood_id"]].append(row)
    valid_alternatives = sum(max(0, sum(row["label"] == "APPLICABLE" for row in group) - 1) for group in neighborhoods.values())
    return {
        "records": len(rows), "labels": dict(labels), "causal_classes": dict(causal),
        "causal_hard_percent": 100 * causal["CAUSAL_HARD"] / len(rows),
        "valid_alternatives": valid_alternatives,
        "secondary_findings": sum(row["secondary_findings"] for row in rows),
        "duplicates": len(rows) - len({row["learner_input_hash"] for row in rows}),
        "contradictions": contradiction_audit(rows), "leakage": leakage_audit(rows),
        "shortcuts": shortcut_audit(rows),
    }
