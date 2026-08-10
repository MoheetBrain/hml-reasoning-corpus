#!/usr/bin/env python3
"""Audit PRM800K and build deterministic state-proxy discovery samples.

The source checkout is an immutable input. This script writes only below the
corpus repository's ``experiments/prm800k_audit`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


SPLITS = (
    ("phase1", "train", "phase1_train.jsonl"),
    ("phase1", "test", "phase1_test.jsonl"),
    ("phase2", "train", "phase2_train.jsonl"),
    ("phase2", "test", "phase2_test.jsonl"),
)
SEED = "hmltn-prm800k-semantic-discovery-v1"
RATINGS = (-1, 0, 1)


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def dump_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")


def iter_jsonl(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open() as stream:
        for line_number, line in enumerate(stream, 1):
            yield line_number, json.loads(line)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(*parts: object) -> str:
    payload = "\x1f".join(str(part) for part in (SEED, *parts))
    return hashlib.sha256(payload.encode()).hexdigest()


def percentile(values: list[int], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] * (upper - rank) + ordered[upper] * (rank - lower)


def describe(values: list[int]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "p90": percentile(values, 0.9),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def load_math_metadata(source_root: Path) -> dict[str, dict[str, Any]]:
    by_problem: dict[str, dict[str, Any]] = {}
    for split in ("train", "test"):
        path = source_root / "prm800k" / "math_splits" / f"{split}.jsonl"
        for _, row in iter_jsonl(path):
            by_problem[row["problem"]] = {
                "math_split": split,
                "math_unique_id": row["unique_id"],
                "subject": row["subject"],
                "level": row["level"],
                "ground_truth_solution": row["solution"],
                "ground_truth_answer": row["answer"],
            }
    return by_problem


def selected_text(step: dict[str, Any]) -> tuple[str | None, str]:
    chosen = step.get("chosen_completion")
    completions = step.get("completions") or []
    if isinstance(chosen, int) and 0 <= chosen < len(completions):
        return completions[chosen].get("text"), "model_completion"
    human = step.get("human_completion")
    if human:
        if isinstance(human, dict):
            return human.get("text"), "human_completion"
        return str(human), "human_completion"
    return None, "none"


def position_bin(index: int, length: int) -> str:
    if length <= 1:
        return "only"
    fraction = index / (length - 1)
    if fraction < 1 / 3:
        return "early"
    if fraction < 2 / 3:
        return "middle"
    return "late"


def length_bin(length: int) -> str:
    if length <= 4:
        return "1-4"
    if length <= 8:
        return "5-8"
    if length <= 16:
        return "9-16"
    return "17+"


def alternative_bin(count: int) -> str:
    if count == 1:
        return "1"
    if count <= 3:
        return "2-3"
    return "4+"


@dataclass
class AuditBucket:
    trajectories: int = 0
    candidates: int = 0
    human_completions: int = 0
    multi_candidate_states: int = 0
    alternative_candidates_beyond_first: int = 0
    quality_control: int = 0
    initial_screening: int = 0

    def __post_init__(self) -> None:
        self.ratings: Counter[str] = Counter()
        self.flags: Counter[str] = Counter()
        self.finish_reasons: Counter[str] = Counter()
        self.step_lengths: list[int] = []
        self.completions_per_state: list[int] = []
        self.first_any_error_positions: list[int] = []
        self.first_chosen_error_positions: list[int] = []
        self.problem_hashes: Counter[str] = Counter()

    def as_dict(self) -> dict[str, Any]:
        return {
            "solution_trajectories": self.trajectories,
            "unique_problem_texts": len(self.problem_hashes),
            "repeated_problem_trajectory_rows": self.trajectories - len(self.problem_hashes),
            "total_candidate_completions": self.candidates,
            "non_null_rated_candidate_steps": self.candidates - self.ratings.get("None", 0),
            "rating_counts": dict(sorted(self.ratings.items())),
            "flag_counts": dict(sorted(self.flags.items())),
            "finish_reason_counts": dict(sorted(self.finish_reasons.items())),
            "finish_reason_percent": {
                key: count / self.trajectories * 100
                for key, count in sorted(self.finish_reasons.items())
            },
            "trajectory_step_count": describe(self.step_lengths),
            "candidate_completions_per_state": describe(self.completions_per_state),
            "multi_candidate_states": self.multi_candidate_states,
            "alternative_candidates_beyond_first": self.alternative_candidates_beyond_first,
            "human_written_completions": self.human_completions,
            "first_any_minus_one_position_1_based": describe(self.first_any_error_positions),
            "first_chosen_minus_one_position_1_based": describe(self.first_chosen_error_positions),
            "quality_control_trajectories": self.quality_control,
            "initial_screening_trajectories": self.initial_screening,
        }


def update_bucket(bucket: AuditBucket, row: dict[str, Any]) -> None:
    steps = row["label"]["steps"]
    bucket.trajectories += 1
    bucket.step_lengths.append(len(steps))
    bucket.finish_reasons[str(row["label"].get("finish_reason"))] += 1
    bucket.problem_hashes[hashlib.sha256(row["question"]["problem"].encode()).hexdigest()] += 1
    bucket.quality_control += int(bool(row.get("is_quality_control_question")))
    bucket.initial_screening += int(bool(row.get("is_initial_screening_question")))
    any_error: int | None = None
    chosen_error: int | None = None
    for step_index, step in enumerate(steps):
        completions = step.get("completions") or []
        bucket.completions_per_state.append(len(completions))
        bucket.multi_candidate_states += int(len(completions) > 1)
        bucket.alternative_candidates_beyond_first += max(0, len(completions) - 1)
        bucket.human_completions += int(bool(step.get("human_completion")))
        for completion_index, completion in enumerate(completions):
            bucket.candidates += 1
            rating = completion.get("rating")
            bucket.ratings[str(rating)] += 1
            flag = completion.get("flagged")
            bucket.flags["null" if flag is None else str(flag).lower()] += 1
            if rating == -1 and any_error is None:
                any_error = step_index + 1
            if rating == -1 and step.get("chosen_completion") == completion_index and chosen_error is None:
                chosen_error = step_index + 1
    if any_error is not None:
        bucket.first_any_error_positions.append(any_error)
    if chosen_error is not None:
        bucket.first_chosen_error_positions.append(chosen_error)


def candidate_records(
    phase: str,
    split: str,
    line_number: int,
    row: dict[str, Any],
    math_meta: dict[str, dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    problem = row["question"]["problem"]
    metadata = math_meta.get(problem, {})
    trajectory_id = f"{phase}-{split}-{line_number:06d}"
    prefix: list[dict[str, Any]] = []
    steps = row["label"]["steps"]
    for step_index, step in enumerate(steps):
        completions = step.get("completions") or []
        for completion_index, completion in enumerate(completions):
            candidate_id = f"{trajectory_id}-s{step_index + 1:03d}-c{completion_index + 1:02d}"
            yield {
                "record_type": "STATE_PROXY_CANDIDATE",
                "candidate_id": candidate_id,
                "trajectory_id": trajectory_id,
                "phase": phase,
                "split": split,
                "source_line": line_number,
                "step_index_0_based": step_index,
                "step_position_1_based": step_index + 1,
                "trajectory_step_count": len(steps),
                "completion_index_0_based": completion_index,
                "alternative_completion_count": len(completions),
                "rating": completion.get("rating"),
                "flagged": completion.get("flagged"),
                "is_chosen_completion": step.get("chosen_completion") == completion_index,
                "human_completion": step.get("human_completion"),
                "candidate_text": completion.get("text", ""),
                "preceding_state_proxy": list(prefix),
                "problem": problem,
                "ground_truth_solution": row["question"].get("ground_truth_solution")
                or metadata.get("ground_truth_solution"),
                "ground_truth_answer": row["question"].get("ground_truth_answer")
                or metadata.get("ground_truth_answer"),
                "subject": metadata.get("subject", "UNKNOWN"),
                "level": metadata.get("level", "UNKNOWN"),
                "math_unique_id": metadata.get("math_unique_id"),
                "finish_reason": row["label"].get("finish_reason"),
                "generation": row.get("generation"),
                "is_quality_control_question": row.get("is_quality_control_question"),
                "is_initial_screening_question": row.get("is_initial_screening_question"),
                "strata": {
                    "phase": phase,
                    "subject": metadata.get("subject", "UNKNOWN"),
                    "level": metadata.get("level", "UNKNOWN"),
                    "error_position": position_bin(step_index, len(steps)),
                    "trajectory_length": length_bin(len(steps)),
                    "alternative_count": alternative_bin(len(completions)),
                },
                "provenance": {
                    "source_split_file": f"{phase}_{split}.jsonl",
                    "source_line": line_number,
                    "source_repository": "https://github.com/openai/prm800k.git",
                },
                "state_proxy_warning": (
                    "The prefix is reconstructed from chosen/human text and is not a canonical "
                    "or complete HML mathematical state."
                ),
            }
        text, origin = selected_text(step)
        if text is not None:
            prefix.append({"step_position_1_based": step_index + 1, "origin": origin, "text": text})


def decision_record(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    first = candidates[0]
    return {
        "record_type": "PHASE1_MULTI_CANDIDATE_DECISION_POINT",
        "decision_id": f"{first['trajectory_id']}-s{first['step_position_1_based']:03d}",
        "trajectory_id": first["trajectory_id"],
        "phase": first["phase"],
        "split": first["split"],
        "source_line": first["source_line"],
        "step_position_1_based": first["step_position_1_based"],
        "problem": first["problem"],
        "ground_truth_solution": first["ground_truth_solution"],
        "ground_truth_answer": first["ground_truth_answer"],
        "subject": first["subject"],
        "level": first["level"],
        "preceding_state_proxy": first["preceding_state_proxy"],
        "candidates": [
            {
                "candidate_id": item["candidate_id"],
                "text": item["candidate_text"],
                "rating": item["rating"],
                "flagged": item["flagged"],
                "is_chosen_completion": item["is_chosen_completion"],
            }
            for item in candidates
        ],
        "human_completion": first["human_completion"],
        "finish_reason": first["finish_reason"],
        "strata": first["strata"],
        "state_proxy_warning": first["state_proxy_warning"],
    }


def stratified_sample(rows: list[dict[str, Any]], target: int, id_key: str) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        strata = row["strata"]
        key = tuple(str(strata[name]) for name in sorted(strata))
        groups[key].append(row)
    for key in groups:
        groups[key].sort(key=lambda row: stable_hash(row[id_key]))
    keys = sorted(groups, key=lambda key: stable_hash(*key))
    selected: list[dict[str, Any]] = []
    used_problems: set[str] = set()
    # First pass maximizes source-problem diversity while round-robining strata.
    while len(selected) < target:
        progress = False
        for key in keys:
            match = next((row for row in groups[key] if row["problem"] not in used_problems), None)
            if match is not None:
                groups[key].remove(match)
                selected.append(match)
                used_problems.add(match["problem"])
                progress = True
                if len(selected) == target:
                    break
        if not progress:
            break
    # Fill only if the target exceeds available unique source problems.
    while len(selected) < target:
        progress = False
        for key in keys:
            if groups[key]:
                selected.append(groups[key].pop(0))
                progress = True
                if len(selected) == target:
                    break
        if not progress:
            raise ValueError(f"Only {len(selected)} rows available for target {target}")
    return sorted(selected, key=lambda row: row[id_key])


def token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z]+|\d+", text.lower()) if len(token) > 1}


def jaccard(a: str, b: str) -> float:
    left, right = token_set(a), token_set(b)
    if not left and not right:
        return 1.0
    return len(left & right) / max(1, len(left | right))


ERROR_META = {
    "PRECONDITION_VIOLATION": ("operation applicability", "required nonzero/sign/domain fact", "PARTIAL", "CONTRACT_DEPENDENT"),
    "DEPENDENCY_VIOLATION": ("dependency ancestry", "supporting premise in active state", "YES", "YES"),
    "SCOPE_LEAK": ("scope locality", "valid discharge or branch-local retention", "PARTIAL", "PARTIAL"),
    "OBLIGATION_DROP": ("persistent proof debt", "named discharge evidence", "PARTIAL", "PARTIAL"),
    "CANDIDATE_PROMOTION": ("candidate/fact separation", "original-constraint verification", "NO", "NO"),
    "INVALID_BRANCH_JOIN": ("branch coverage and join", "coverage/disjointness certificate", "NO", "NO"),
    "WARRANT_MISMATCH": ("warrant identity", "applicable rule and exact premise envelope", "PARTIAL", "CONTRACT_DEPENDENT"),
    "EPISTEMIC_PROMOTION": ("checker-owned status", "trusted evidence before verification", "PARTIAL", "PARTIAL"),
    "FALSE_GOAL_DISCHARGE": ("exact verified goal discharge", "verified exact target and completeness", "YES", "YES_IF_STATE_CANONICALIZED"),
    "TYPE_OR_DOMAIN_MISMATCH": ("type/domain contract", "compatible declared domain evidence", "PARTIAL", "CONTRACT_DEPENDENT"),
    "ARITHMETIC_ERROR": ("numeric correctness", "exact arithmetic certificate", "REPRESENTABLE_WITH_BACKEND", "NO_WITHOUT_BACKEND"),
    "FALSE_FACT": ("claim truth/evidence", "proof, model, or counterexample evidence", "REPRESENTABLE", "NO_OPEN_DOMAIN"),
    "INVALID_TRANSFORMATION": ("relation preservation", "symbolic transformation certificate", "REPRESENTABLE_WITH_BACKEND", "NO_WITHOUT_BACKEND"),
    "WRONG_THEOREM_APPLICATION": ("theorem hypotheses", "library theorem with satisfied hypotheses", "REPRESENTABLE_WITH_LIBRARY", "NO_WITHOUT_LIBRARY"),
    "MISREAD_PROBLEM": ("source/semantic alignment", "correct source reading", "UPSTREAM_INTERPRETATION", "NO"),
    "INVALID_INFERENCE": ("entailment", "licensed inference warrant", "REPRESENTABLE", "NO_OPEN_DOMAIN"),
    "CONTRADICTION_WITH_STATE": ("state consistency", "resolution of conflicting active facts", "REPRESENTABLE", "PARTIAL"),
    "OMISSION": ("solution completeness", "missing required case/part", "REPRESENTABLE_IF_GOAL_DECOMPOSED", "PARTIAL"),
    "OTHER": ("annotation-policy quality", "case-specific evidence", "UNKNOWN", "NO"),
    "UNRESOLVED": ("unresolved", "human mathematical adjudication", "UNKNOWN", "NO"),
}


def classify_error(row: dict[str, Any]) -> dict[str, Any]:
    text = row["candidate_text"]
    low = text.lower()
    prefix = "\n".join(item["text"] for item in row["preceding_state_proxy"])
    answer_marker = bool(re.search(r"#\s*answer|final answer|\banswer\s*[:=]", low))
    class_name = "UNRESOLVED"
    confidence = "LOW"
    rationale = "The human -1 label is preserved, but this bounded lexical pass cannot identify one primary semantic defect safely."
    if answer_marker:
        class_name, confidence = "FALSE_GOAL_DISCHARGE", "MEDIUM"
        rationale = "The candidate attempts to close the task; a -1 final step indicates wrong or incomplete goal discharge under the PRM protocol."
    elif re.search(r"\bcancel(?:ling)?\b|divide both sides by\s+[$\\{(]*[a-zA-Z]", low) and not re.search(r"nonzero|not zero|≠|\\neq", low + prefix.lower()):
        class_name, confidence = "PRECONDITION_VIOLATION", "MEDIUM"
        rationale = "The candidate explicitly cancels a symbolic quantity or divides by a symbolic expression without a nonzero condition in the available state proxy."
    elif len(token_set(text)) < 4 or re.search(r"https?://|as an ai|i cannot|good job|what(?:'s| is) next", low):
        class_name, confidence = "OTHER", "MEDIUM"
        rationale = "The -1 is plausibly driven by the PRM protocol's weird/off-topic/unhelpful or unverifiable-text criteria rather than an HML state invariant."
    invariant, missing, representable, detectable = ERROR_META[class_name]
    return {
        "candidate_id": row["candidate_id"],
        "human_rating": -1,
        "step": text,
        "preceding_state_proxy": row["preceding_state_proxy"],
        "primary_error_class": class_name,
        "violated_invariant": invariant,
        "required_missing_fact_warrant_or_precondition": missing,
        "current_hml_representation": representable,
        "current_semantic_firewall_deterministic_detection": detectable,
        "confidence": confidence,
        "explanation": rationale,
        "adjudication_status": "CONSERVATIVE_RULE_BASED_FIRST_PASS_V2",
        "source_context": {key: row[key] for key in ("trajectory_id", "phase", "split", "subject", "level", "problem", "ground_truth_solution", "finish_reason")},
    }


def classify_zero(row: dict[str, Any]) -> dict[str, Any]:
    text = row["candidate_text"]
    low = text.lower()
    prefix_texts = [item["text"] for item in row["preceding_state_proxy"]]
    problem_similarity = jaccard(text, row["problem"])
    prefix_similarity = max((jaccard(text, prior) for prior in prefix_texts), default=0.0)
    if prefix_similarity >= 0.55:
        reason = "redundant computation" if re.search(r"[=+*/^-]|\\", text) else "restatement"
    elif problem_similarity >= 0.50:
        reason = "restatement"
    elif re.search(r"good job|great|okay|what(?:'s| is) next|this is (?:easy|hard)", low):
        reason = "insufficient progress"
    elif re.search(r"^(?:so )?(?:we|i) (?:need|want|have) to\b|^(?:let us|let's)\b", low) and not re.search(r"=|\\frac|\\sqrt|\d", text):
        reason = "vague plan"
    elif problem_similarity < 0.03 and prefix_similarity < 0.03:
        reason = "semantically valid but goal-irrelevant"
    elif re.search(r"try|approach|perhaps|maybe|could", low):
        reason = "harmless detour"
    else:
        reason = "insufficient progress"
    return {
        "candidate_id": row["candidate_id"],
        "human_rating": 0,
        "step": text,
        "zero_reason": reason,
        "validity_assessment": "LIKELY_VALID_BY_LABEL_BUT_NOT_FORMALLY_REPLAYED",
        "progress_assessment": "NO_CLEAR_PROGRESS_BY_HUMAN_LABEL",
        "novelty_proxy": 1 - prefix_similarity,
        "goal_relevance_proxy": problem_similarity,
        "confidence": "MEDIUM" if reason in {"restatement", "vague plan"} else "LOW",
        "adjudication_status": "CONSERVATIVE_RULE_BASED_FIRST_PASS_V2",
        "source_context": {key: row[key] for key in ("trajectory_id", "phase", "split", "subject", "level", "problem", "finish_reason")},
    }


def classify_positive(row: dict[str, Any]) -> dict[str, Any]:
    text = row["candidate_text"]
    low = text.lower()
    if re.search(r"check|verify|substitute back|confirm", low):
        mode = "VERIFICATION"
    elif re.search(r"let's|we can try|consider|approach|strategy|notice", low):
        mode = "SEARCH_META"
    elif re.search(r"answer|qed|we are done|therefore.*boxed", low):
        mode = "GOAL_MANAGEMENT"
    elif re.search(r"let .* be|denote|define|model", low):
        mode = "MODELING"
    else:
        mode = "EXECUTION"
    return {
        "candidate_id": row["candidate_id"],
        "human_rating": 1,
        "step": text,
        "reasoning_mode_proxy": mode,
        "validity_assessment": "HUMAN_ACCEPTED_NOT_FORMALLY_REPLAYED",
        "progress_assessment": "ADVANCING_BY_HUMAN_LABEL",
        "adjudication_status": "CONSERVATIVE_RULE_BASED_FIRST_PASS_V2",
        "source_context": {key: row[key] for key in ("trajectory_id", "phase", "split", "subject", "level", "problem", "finish_reason")},
    }


def text_features(text: str, problem: str, prefix: list[dict[str, Any]]) -> dict[str, Any]:
    low = text.lower()
    return {
        "characters": len(text),
        "tokens": len(re.findall(r"\S+", text)),
        "has_math_marker": bool(re.search(r"[=<>+*/^]|\\(?:frac|sqrt|boxed|cdot)|\d", text)),
        "has_answer_marker": bool(re.search(r"answer|qed|\\boxed", low)),
        "has_plan_marker": bool(re.search(r"let's|we can|we need|try|consider|notice|approach", low)),
        "problem_jaccard": jaccard(text, problem),
        "prefix_max_jaccard": max((jaccard(text, item["text"]) for item in prefix), default=0.0),
    }


def annotate_decision(row: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for candidate in row["candidates"]:
        candidates.append({
            **candidate,
            "features": text_features(candidate["text"], row["problem"], row["preceding_state_proxy"]),
        })
    return {
        "decision_id": row["decision_id"],
        "rating_set": sorted({candidate["rating"] for candidate in candidates if candidate["rating"] in RATINGS}),
        "same_prefix_comparison": candidates,
        "interpretation": "Feature comparison only; ratings are not reducible to lexical features and no causal claim is made.",
        "source_context": {key: row[key] for key in ("trajectory_id", "split", "subject", "level", "problem", "finish_reason")},
    }


def aggregate_semantics(errors: list[dict[str, Any]], zeros: list[dict[str, Any]], positives: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    error_counts = Counter(row["primary_error_class"] for row in errors)
    confidence_counts = Counter(row["confidence"] for row in errors)
    zero_counts = Counter(row["zero_reason"] for row in zeros)
    positive_modes = Counter(row["reasoning_mode_proxy"] for row in positives)
    feature_by_rating: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for decision in decisions:
        for candidate in decision["same_prefix_comparison"]:
            rating = candidate["rating"]
            if rating not in RATINGS:
                continue
            for name, value in candidate["features"].items():
                feature_by_rating[rating][name].append(float(value))
    return {
        "error_primary_class_counts": dict(sorted(error_counts.items())),
        "error_confidence_counts": dict(sorted(confidence_counts.items())),
        "resolved_error_fraction": sum(count for name, count in error_counts.items() if name != "UNRESOLVED") / len(errors),
        "firewall_ontology_direct_count": sum(error_counts[name] for name in ERROR_META if name in {
            "PRECONDITION_VIOLATION", "DEPENDENCY_VIOLATION", "SCOPE_LEAK", "OBLIGATION_DROP",
            "CANDIDATE_PROMOTION", "INVALID_BRANCH_JOIN", "WARRANT_MISMATCH", "EPISTEMIC_PROMOTION",
            "FALSE_GOAL_DISCHARGE", "TYPE_OR_DOMAIN_MISMATCH",
        }),
        "zero_reason_counts": dict(sorted(zero_counts.items())),
        "positive_reasoning_mode_proxy_counts": dict(sorted(positive_modes.items())),
        "decision_point_feature_means_by_rating": {
            str(rating): {name: statistics.fmean(values) for name, values in sorted(features.items())}
            for rating, features in sorted(feature_by_rating.items())
        },
        "method_warning": (
            "Semantic classes are a deterministic conservative lexical first pass, not human-adjudicated theorem replay. "
            "LOW confidence and UNRESOLVED must not be used as ontology-frequency estimates."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True, help="Official PRM800K checkout root")
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    math_meta = load_math_metadata(source_root)

    buckets = {"phase1": AuditBucket(), "phase2": AuditBucket()}
    overall_bucket = AuditBucket()
    split_buckets: dict[str, AuditBucket] = {}
    all_candidates: list[dict[str, Any]] = []
    source_files = []
    for phase, split, filename in SPLITS:
        path = source_root / "prm800k" / "data" / filename
        split_key = f"{phase}_{split}"
        split_buckets[split_key] = AuditBucket()
        row_count = 0
        for line_number, row in iter_jsonl(path):
            row_count += 1
            update_bucket(overall_bucket, row)
            update_bucket(buckets[phase], row)
            update_bucket(split_buckets[split_key], row)
            all_candidates.extend(candidate_records(phase, split, line_number, row, math_meta))
        source_files.append({
            "path": f"prm800k/data/{filename}",
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "rows": row_count,
        })

    source_manifest = {
        "source_repository": "https://github.com/openai/prm800k.git",
        "source_commit": args.source_commit,
        "source_files": source_files,
        "math_metadata_problem_count": len(math_meta),
        "immutable_input_policy": "The official checkout and source data are read-only inputs and are never modified.",
    }
    dataset_audit = {
        "audit_order": "Raw dataset audit was computed before semantic classification.",
        "overall": overall_bucket.as_dict(),
        "phase1": buckets["phase1"].as_dict(),
        "phase2": buckets["phase2"].as_dict(),
        "by_split": {key: bucket.as_dict() for key, bucket in sorted(split_buckets.items())},
        "definitions": {
            "trajectory": "One JSONL row / labelled solution sample, including repeated QC presentations.",
            "candidate_step": "One item in label.steps[*].completions; alternatives are counted separately.",
            "state_proxy": "Problem plus reconstructed chosen/human textual prefix; not a complete canonical HML state.",
            "first_any_error": "First state containing any -1 candidate, whether chosen or alternative.",
            "first_chosen_error": "First state where the completion selected into the reconstructed trajectory is rated -1.",
        },
    }

    by_rating = {rating: [row for row in all_candidates if row["rating"] == rating] for rating in RATINGS}
    deep_sample = []
    for rating, target in ((-1, 500), (0, 250), (1, 250)):
        deep_sample.extend(stratified_sample(by_rating[rating], target, "candidate_id"))
    deep_sample.sort(key=lambda row: (row["rating"], row["candidate_id"]))

    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in all_candidates:
        if row["phase"] == "phase1" and row["alternative_completion_count"] > 1:
            grouped[(row["trajectory_id"], row["step_position_1_based"])].append(row)
    decisions = [decision_record(rows) for rows in grouped.values()]
    decision_sample = stratified_sample(decisions, 200, "decision_id")

    errors = [classify_error(row) for row in deep_sample if row["rating"] == -1]
    zeros = [classify_zero(row) for row in deep_sample if row["rating"] == 0]
    positives = [classify_positive(row) for row in deep_sample if row["rating"] == 1]
    decision_annotations = [annotate_decision(row) for row in decision_sample]
    semantic_metrics = aggregate_semantics(errors, zeros, positives, decision_annotations)
    sample_profile = {"deep_sample": {}, "phase1_decision_points": {}}
    for rating in RATINGS:
        rows = [row for row in deep_sample if row["rating"] == rating]
        sample_profile["deep_sample"][str(rating)] = {
            "records": len(rows),
            "unique_problem_texts": len({row["problem"] for row in rows}),
            "phase": dict(sorted(Counter(row["phase"] for row in rows).items())),
            "subject": dict(sorted(Counter(str(row["subject"]) for row in rows).items())),
            "level": dict(sorted(Counter(str(row["level"]) for row in rows).items())),
            "position": dict(sorted(Counter(row["strata"]["error_position"] for row in rows).items())),
        }
    sample_profile["phase1_decision_points"] = {
        "records": len(decision_sample),
        "unique_problem_texts": len({row["problem"] for row in decision_sample}),
        "split": dict(sorted(Counter(row["split"] for row in decision_sample).items())),
        "human_completion_present": sum(bool(row["human_completion"]) for row in decision_sample),
    }

    dump_json(output_root / "results" / "source_manifest.json", source_manifest)
    dump_json(output_root / "results" / "dataset_audit.json", dataset_audit)
    dump_jsonl(output_root / "samples" / "deep_sample.jsonl", deep_sample)
    dump_jsonl(output_root / "samples" / "phase1_decision_points.jsonl", decision_sample)
    dump_jsonl(output_root / "annotations" / "minus_one_audit.jsonl", errors)
    dump_jsonl(output_root / "annotations" / "zero_audit.jsonl", zeros)
    dump_jsonl(output_root / "annotations" / "plus_one_audit.jsonl", positives)
    dump_jsonl(output_root / "annotations" / "decision_point_audit.jsonl", decision_annotations)
    dump_json(output_root / "results" / "semantic_metrics.json", semantic_metrics)
    dump_json(output_root / "results" / "sample_profile.json", sample_profile)
    print(json.dumps({
        "source_candidates": len(all_candidates),
        "deep_sample": len(deep_sample),
        "decision_sample": len(decision_sample),
        "outputs": str(output_root),
    }, indent=2))


if __name__ == "__main__":
    main()
