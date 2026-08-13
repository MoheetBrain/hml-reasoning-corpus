#!/usr/bin/env python3
"""Build the 1,000-record PRM800K cross-source semantic-gap pilot.

This is a deterministic forensic annotator, not an automatic mathematical judge. It
validates every selected record against the immutable official source, preserves PRM's
process labels separately, and classifies only the state distinction demanded by the
candidate action. No HML file is written or imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator


SOURCE_COMMIT = "7ecc794703b2877f63226f2477a49b34f9b25163"
FROZEN_HML_SHA = "84bf9897689b0ed78a2caaefc1db850d49b81260"
EXPECTED_FILES = {
    "phase1_train.jsonl": "e9da6a73f827ffb9a8c0dc644c541d34ed76b3d4d1e4896ff5f7b37ddf5ae34d",
    "phase1_test.jsonl": "f4b3bc5b095e45c816453dc4d748b755c680d61d55f9895d929a335b487c727d",
    "phase2_train.jsonl": "1110237feeb51d1bc200cb37b8f965cfdc1036eac7d506094049366fe7dc1089",
    "phase2_test.jsonl": "6b172efa884ac8341a946dd82e06947c135b7254109fb3f7aa907c715d98aaad",
}

CATEGORIES = {
    "EXISTING_SEMANTICS",
    "LIBRARY_GAP",
    "BACKEND/VERIFIER_GAP",
    "CURRENT_KNOWN_CORE_GAP",
    "NEW_CORE_SEMANTIC_CANDIDATE",
    "SOURCE_AMBIGUITY",
    "UNRESOLVED",
}

TARGET_PATTERNS = {
    "branch_create": re.compile(
        r"\b(?:case\s*(?:1|2|3|i|ii|one|two)\s*:|(?:start|begin) with (?:the )?case|"
        r"(?:need|have|want|going) to consider (?:both|all|the|two) cases|"
        r"(?:consider|try) (?:both|all|the|two) cases|split into (?:two )?cases|"
        r"without loss of generality)\b",
        re.I,
    ),
    "branch_join": re.compile(
        r"\b(?:in either case|in both cases(?:,| we (?:have|see|obtain|find))|"
        r"combining (?:the )?cases|the result is the same in both cases|"
        r"add up the results for all cases|these cases (?:give|yield))\b",
        re.I,
    ),
    "exact_approximate_status": re.compile(
        r"\\approx|approximately|approximation|rounded? (?:to|off)|decimal approximation|numerical estimate",
        re.I,
    ),
    "domain_or_sign_precondition": re.compile(
        r"\bdomain\b|nonzero|non-zero|denominator|must be positive|must be negative|defined only|restriction",
        re.I,
    ),
    "theorem_or_domain_library": re.compile(
        r"\b(?:theorem|lemma|identity|formula|criterion|derivative|differentiat|integrat|antiderivative|"
        r"bayes|binomial|probability|expected value|variance|standard deviation|eigenvalue|determinant)\b|"
        r"\\(?:int|lim|sum|prod)\b|\\frac\s*\{d",
        re.I,
    ),
}
TARGET_MINIMUMS = {
    "branch_create": 25,
    "branch_join": 20,
    "exact_approximate_status": 30,
    "domain_or_sign_precondition": 40,
    "theorem_or_domain_library": 80,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


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


def iter_selected_source_rows(
    source_root: Path,
    wanted: dict[str, set[int]],
) -> Iterator[tuple[str, int, dict[str, Any]]]:
    for filename in sorted(wanted):
        path = source_root / "prm800k" / "data" / filename
        actual = sha256_file(path)
        if actual != EXPECTED_FILES[filename]:
            raise ValueError(f"immutable source hash mismatch for {filename}: {actual}")
        remaining = wanted[filename]
        with path.open() as stream:
            for line_number, line in enumerate(stream, 1):
                if line_number in remaining:
                    yield filename, line_number, json.loads(line)


def validate_source(sample: list[dict[str, Any]], source_root: Path) -> None:
    by_location = {(row["provenance"]["source_split_file"], row["source_line"]): row for row in sample}
    wanted: dict[str, set[int]] = defaultdict(set)
    for filename, line_number in by_location:
        wanted[filename].add(line_number)
    source_rows = {(filename, line_number): row for filename, line_number, row in iter_selected_source_rows(source_root, wanted)}
    if source_rows.keys() != by_location.keys():
        missing = sorted(by_location.keys() - source_rows.keys())
        raise ValueError(f"source rows missing: {missing[:5]}")

    for item in sample:
        filename = item["provenance"]["source_split_file"]
        row = source_rows[(filename, item["source_line"])]
        step_index = item["step_index_0_based"]
        completion_index = item["completion_index_0_based"]
        step = row["label"]["steps"][step_index]
        completion = step["completions"][completion_index]
        checks = {
            "problem": row["question"]["problem"] == item["problem"],
            "candidate_text": completion.get("text", "") == item["candidate_text"],
            "rating": completion.get("rating") == item["rating"],
            "flagged": completion.get("flagged") == item["flagged"],
            "chosen": (step.get("chosen_completion") == completion_index) == item["is_chosen_completion"],
        }
        prefix = []
        for prior_index, prior in enumerate(row["label"]["steps"][:step_index]):
            text, origin = selected_text(prior)
            if text is not None:
                prefix.append({"step_position_1_based": prior_index + 1, "origin": origin, "text": text})
        checks["prefix"] = prefix == item["preceding_state_proxy"]
        if not all(checks.values()):
            failed = sorted(key for key, passed in checks.items() if not passed)
            raise ValueError(f"{item['candidate_id']}: source validation failed: {failed}")


def targeted_sample(sample: list[dict[str, Any]], source_root: Path) -> list[dict[str, Any]]:
    """Replace ordinary rows with same-rating targeted rows while keeping n=1,000.

    The original sample already stratifies rating, phase, subject, difficulty, position,
    trajectory length, and alternative count. This second deterministic pass guarantees
    enough case/approximation/domain/theorem examples for semantic discovery without
    changing the 500/250/250 source-rating balance.
    """
    from experiments.prm800k_audit.audit_prm800k import candidate_records, load_math_metadata

    selected = {row["candidate_id"]: row for row in sample}
    counts = Counter(name for row in sample for name, pattern in TARGET_PATTERNS.items() if pattern.search(row["candidate_text"]))
    deficits = {name: max(0, target - counts[name]) for name, target in TARGET_MINIMUMS.items()}
    if not any(deficits.values()):
        return sample

    math_meta = load_math_metadata(source_root)
    candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for filename in sorted(EXPECTED_FILES):
        phase, split = filename.removesuffix(".jsonl").split("_", 1)
        path = source_root / "prm800k" / "data" / filename
        with path.open() as stream:
            for line_number, line in enumerate(stream, 1):
                source_row = json.loads(line)
                if not any(
                    pattern.search(completion.get("text", ""))
                    for step in source_row["label"]["steps"]
                    for completion in (step.get("completions") or [])
                    for pattern in TARGET_PATTERNS.values()
                ):
                    continue
                for item in candidate_records(phase, split, line_number, source_row, math_meta):
                    if item["candidate_id"] in selected:
                        continue
                    if item["rating"] not in {-1, 0, 1}:
                        continue
                    for name, pattern in TARGET_PATTERNS.items():
                        if deficits[name] and pattern.search(item["candidate_text"]) and len(candidates[name]) < 400:
                            candidates[name].append(item)
        if all(len(candidates[name]) >= min(400, max(1, deficits[name] * 4)) for name in deficits if deficits[name]):
            break

    additions: list[dict[str, Any]] = []
    added_ids: set[str] = set()
    running = Counter(counts)
    for name in TARGET_MINIMUMS:
        pool = sorted(candidates[name], key=lambda row: hashlib.sha256(row["candidate_id"].encode()).hexdigest())
        for item in pool:
            if running[name] >= TARGET_MINIMUMS[name]:
                break
            if item["candidate_id"] in added_ids:
                continue
            additions.append(item)
            added_ids.add(item["candidate_id"])
            for matched, pattern in TARGET_PATTERNS.items():
                if pattern.search(item["candidate_text"]):
                    running[matched] += 1

    removable: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in sample:
        if not any(pattern.search(item["candidate_text"]) for pattern in TARGET_PATTERNS.values()):
            removable[item["rating"]].append(item)
    for rating in removable:
        removable[rating].sort(key=lambda row: hashlib.sha256(("remove:" + row["candidate_id"]).encode()).hexdigest())
    removed_ids: set[str] = set()
    accepted_additions: list[dict[str, Any]] = []
    for item in additions:
        pool = removable[item["rating"]]
        replacement = next((row for row in pool if row["candidate_id"] not in removed_ids), None)
        if replacement is None:
            continue
        removed_ids.add(replacement["candidate_id"])
        accepted_additions.append(item)

    result = [row for row in sample if row["candidate_id"] not in removed_ids] + accepted_additions
    result.sort(key=lambda row: row["candidate_id"])
    if len(result) != 1000 or Counter(row["rating"] for row in result) != Counter(row["rating"] for row in sample):
        raise AssertionError("targeted replacement changed pilot size or source-rating balance")
    final_counts = Counter(name for row in result for name, pattern in TARGET_PATTERNS.items() if pattern.search(row["candidate_text"]))
    missing = {name: target - final_counts[name] for name, target in TARGET_MINIMUMS.items() if final_counts[name] < target}
    if missing:
        raise ValueError(f"could not satisfy targeted pilot minima: {missing}")
    return result


def mechanisms(row: dict[str, Any]) -> list[str]:
    text = row["candidate_text"]
    low = text.lower()
    found: list[str] = []
    # An unchosen completion is necessarily a proposed action, not a committed state
    # update. This source-process fact is stronger than lexical use of "candidate".
    if not row["is_chosen_completion"]:
        found.append("candidate_lifecycle_action_creation")
    if re.search(
        r"\b(?:candidate|potential)\s+(?:root|solution)|extraneous (?:root|solution)|"
        r"(?:root|solution) candidate(?:s)?\b",
        low,
    ):
        found.append("candidate_lifecycle_mathematical_object")
    if TARGET_PATTERNS["branch_create"].search(text):
        found.append("branch_create")
    if TARGET_PATTERNS["branch_join"].search(text):
        found.append("branch_join")
    if TARGET_PATTERNS["exact_approximate_status"].search(text):
        found.append("exact_approximate_status")
    if TARGET_PATTERNS["domain_or_sign_precondition"].search(text):
        found.append("domain_or_sign_precondition")
    if TARGET_PATTERNS["theorem_or_domain_library"].search(text):
        found.append("theorem_or_domain_library")
    if row["rating"] == -1:
        found.append("source_process_error_label")
    elif row["rating"] == 0:
        found.append("source_process_neutral_label")
    else:
        found.append("source_process_progress_label")
    if re.search(r"\b(?:try|work backwards|guess|notice|consider|perhaps|maybe|strategy|approach)\b", low):
        found.append("planner_or_search_heuristic")
    return sorted(set(found))


def classify(row: dict[str, Any], found: list[str]) -> tuple[str, str, str, str]:
    text = row["candidate_text"].strip()
    tokens = re.findall(r"\w+", text)
    if not text or len(tokens) < 2:
        return (
            "SOURCE_AMBIGUITY",
            "the candidate text is too incomplete to recover a mathematical state effect",
            "NOT_ATTEMPTED_SOURCE_AMBIGUITY",
            "No neutral/HML transition is asserted.",
        )
    known = {
        "candidate_lifecycle_action_creation",
        "candidate_lifecycle_mathematical_object",
        "branch_create",
        "branch_join",
        "exact_approximate_status",
    } & set(found)
    if known:
        ordered = sorted(known)
        return (
            "CURRENT_KNOWN_CORE_GAP",
            f"requires already-recorded frozen-HML state effect(s): {', '.join(ordered)}",
            "REFUSED_CURRENT_FROZEN_HML",
            "The neutral state preserves the proposal/branch/epistemic effect; HML rendering is withheld.",
        )
    if "theorem_or_domain_library" in found:
        return (
            "LIBRARY_GAP",
            "the generic operation/state update is representable but its mathematical authority is a theorem or domain library",
            "STRUCTURALLY_REPRESENTABLE_UNATTESTED",
            "Render as a generic action with an UNKNOWN theorem/library warrant; do not claim truth.",
        )
    if "planner_or_search_heuristic" in found and not re.search(r"[=$<>]|\\(?:frac|sqrt)", text):
        return (
            "EXISTING_SEMANTICS",
            "planner/search prose has no demonstrated mathematical state effect and needs no new execution primitive",
            "REPRESENTABLE_AS_NO_MATHEMATICAL_STATE_CHANGE",
            "Preserve as source-process metadata, not as a new core operation.",
        )
    if re.search(r"[=$<>]|\\(?:frac|sqrt|cdot|begin)", text):
        return (
            "BACKEND/VERIFIER_GAP",
            "the claim/effect shape is representable, but this natural-language transition lacks a complete trusted mathematical replay certificate",
            "STRUCTURALLY_REPRESENTABLE_UNATTESTED",
            "Render with source evidence UNKNOWN; a local arithmetic check cannot certify contextual validity.",
        )
    return (
        "EXISTING_SEMANTICS",
        "a generic claim/no-op/control-neutral action suffices; no distinct state effect is evidenced",
        "STRUCTURALLY_REPRESENTABLE_UNATTESTED",
        "Preserve the source label externally and use generic operation plus warrant/state effect.",
    )


def record(row: dict[str, Any]) -> dict[str, Any]:
    found = mechanisms(row)
    category, rationale, attempt, rendering_policy = classify(row, found)
    assert category in CATEGORIES
    before_hash = hashlib.sha256(canonical_json(row["preceding_state_proxy"]).encode()).hexdigest()
    action_hash = hashlib.sha256(row["candidate_text"].encode()).hexdigest()
    neutral_after = (
        "PROPOSED_ACTION_CANDIDATE_NOT_COMMITTED"
        if "candidate_lifecycle_action_creation" in found
        else "SOURCE_RATED_ERROR_NOT_ACCEPTED_AS_TRUTH"
        if row["rating"] == -1
        else "COMMIT_GENERIC_DERIVED_CLAIM"
    )
    return {
        "pilot_record_id": f"PRM-PILOT-{row['candidate_id']}",
        "source": {
            "repository": "https://github.com/openai/prm800k.git",
            "commit": SOURCE_COMMIT,
            "file": row["provenance"]["source_split_file"],
            "line": row["source_line"],
            "candidate_id": row["candidate_id"],
            "subject": row["subject"],
            "level": row["level"],
            "problem": row["problem"],
        },
        "source_process_labels": {
            "rating": row["rating"],
            "flagged": row["flagged"],
            "is_chosen_completion": row["is_chosen_completion"],
            "alternative_completion_count": row["alternative_completion_count"],
            "finish_reason": row["finish_reason"],
        },
        "source_prefix_state_proxy": row["preceding_state_proxy"],
        "candidate_reasoning_step": row["candidate_text"],
        "neutral_trajectory": {
            "state_before_sha256": before_hash,
            "action_sha256": action_hash,
            "operation": "GENERIC_REASONING_ACTION",
            "warrant": "PRM800K_SOURCE_LABEL_IS_PROCESS_METADATA_NOT_MATHEMATICAL_AUTHORITY",
            "state_after_policy": neutral_after,
            "mechanisms": found,
        },
        "frozen_hml_attempt": {
            "hml_commit": FROZEN_HML_SHA,
            "status": attempt,
            "rendering_policy": rendering_policy,
            "relevant_constructs": [
                "semantic_state/model.py:Action,SemanticState,Candidate,Branch,ClaimStatus",
                "semantic_state/verify.py:_check_candidates,_check_branch,_check_epistemic",
            ],
        },
        "backend": {
            "status": "NO_COMPLETE_CONTEXTUAL_CERTIFICATE",
            "detail": "No source-process rating is treated as a proof certificate; this pilot does not promote local expression truth to transition validity.",
        },
        "hml_judgment": category,
        "judgment_rationale": rationale,
        "new_core_semantic_candidate": None,
        "source_validated_exactly": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    sample = [json.loads(line) for line in args.sample.read_text().splitlines() if line.strip()]
    if len(sample) != 1000 or len({row["candidate_id"] for row in sample}) != 1000:
        raise ValueError("pilot requires exactly 1,000 unique candidate records")
    sample = targeted_sample(sample, args.source_root)
    validate_source(sample, args.source_root)
    records = [record(row) for row in sample]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(canonical_json(row) + "\n" for row in records))
    category_counts = Counter(row["hml_judgment"] for row in records)
    mechanism_counts = Counter(
        mechanism for row in records for mechanism in row["neutral_trajectory"]["mechanisms"]
    )
    summary = {
        "pilot_schema": "prm800k-cross-source-gap-pilot-0.1.0",
        "records": len(records),
        "unique_source_problems": len({row["problem"] for row in sample}),
        "unique_source_trajectories": len({row["trajectory_id"] for row in sample}),
        "source_commit": SOURCE_COMMIT,
        "frozen_hml_commit": FROZEN_HML_SHA,
        "source_validation": "1000/1000 exact",
        "rating_counts": dict(sorted(Counter(str(row["rating"]) for row in sample).items())),
        "subject_counts": dict(sorted(Counter(str(row["subject"]) for row in sample).items())),
        "level_counts": dict(sorted(Counter(str(row["level"]) for row in sample).items())),
        "judgment_counts": dict(sorted(category_counts.items())),
        "mechanism_counts": dict(sorted(mechanism_counts.items())),
        "known_gap_recurrence": {
            name: mechanism_counts[name]
            for name in (
                "candidate_lifecycle_action_creation",
                "candidate_lifecycle_mathematical_object",
                "branch_create",
                "branch_join",
                "exact_approximate_status",
            )
        },
        "new_core_semantic_candidates": 0,
        "marginal_new_semantic_rate": 0.0,
        "method_warning": (
            "The pilot is a conservative representability audit. PRM ratings remain source-process labels, "
            "lexical routing is not mathematical proof, and no local expression check is promoted to full transition validity."
        ),
        "output_sha256": sha256_file(args.output),
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
