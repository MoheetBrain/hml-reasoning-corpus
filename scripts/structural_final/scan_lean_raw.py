#!/usr/bin/env python3
"""Census the complete LeanDojo traces, including goal-creating transitions.

The older canonical export excluded exactly the transitions most likely to expose
multi-goal state.  This read-only pass inspects the pinned raw files and also reads the
actual ``annotated_tactic[1]`` premise list (the old builder looked for a nonexistent
``premises`` key).
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from scan_lean_structure import (
    CASE_RE,
    complementary_case_pair,
    depth_bin,
    old_parent_ids,
    parse_goal_blocks,
)


def n_goals(raw: str) -> int:
    if not raw or raw.strip() == "no goals":
        return 0
    return len(re.findall(r"(?m)^⊢", raw)) or 1


def tactic_head(text: str) -> str:
    match = re.search(r"[A-Za-z_][A-Za-z0-9_!?'.]*", text)
    return match.group(0) if match else "<none>"


def length_bins(values: list[int]) -> dict[str, int]:
    bins = Counter()
    for value in values:
        if value == 1:
            bins["1"] += 1
        elif value <= 3:
            bins["2-3"] += 1
        elif value <= 5:
            bins["4-5"] += 1
        elif value <= 10:
            bins["6-10"] += 1
        elif value <= 20:
            bins["11-20"] += 1
        else:
            bins["21+"] += 1
    return dict(bins)


def scan_file(args: tuple[str, frozenset[str]]) -> dict:
    path, excluded = args
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    counts, tactics, depths = Counter(), Counter(), Counter()
    theorems, lengths, fresh_theorems, fresh_lengths = set(), {}, set(), {}
    samples = {"goal_creation": [], "complementary_branch": []}
    for theorem in rows:
        parent = f"{theorem['file_path']}::{theorem['full_name']}"
        theorems.add(parent)
        trace = theorem.get("traced_tactics") or []
        if trace:
            lengths[parent] = len(trace)
        else:
            counts["theorem_entries_without_traced_transition"] += 1
        is_old = parent in excluded
        if not is_old:
            fresh_theorems.add(parent)
            if trace:
                fresh_lengths[parent] = len(trace)
        for index, step in enumerate(trace):
            counts["transitions"] += 1
            counts["old_history_excluded"] += is_old
            if is_old:
                continue
            counts["fresh_transitions"] += 1
            depths[depth_bin(index)] += 1
            before, after = step.get("state_before", ""), step.get("state_after", "")
            action = step.get("tactic", "")
            counts["exact_before_action_after"] += bool(before and action and after)
            gb, ga = n_goals(before), n_goals(after)
            counts["multi_goal_before"] += gb > 1
            counts["multi_goal_after"] += ga > 1
            counts["goal_creation"] += ga > gb
            counts["goal_close"] += ga < gb
            cb, ca = CASE_RE.findall(before), CASE_RE.findall(after)
            counts["case_scope_before"] += bool(cb)
            counts["case_scope_after"] += bool(ca)
            counts["nested_case_scope_before"] += any("." in label for label in cb)
            counts["nested_case_scope_after"] += any("." in label for label in ca)
            pair = complementary_case_pair(parse_goal_blocks(after))
            counts["complementary_case_pair_after"] += pair
            annotated = step.get("annotated_tactic")
            premises = annotated[1] if isinstance(annotated, list) and len(annotated) > 1 else []
            counts["premises_used_nonempty"] += bool(premises)
            counts["premises_used_total"] += len(premises)
            tactics[tactic_head(action)] += 1
            if ga > gb and len(samples["goal_creation"]) < 6:
                samples["goal_creation"].append({"parent_id": parent, "step_index": index,
                                                  "before_goals": gb, "after_goals": ga,
                                                  "tactic": action[:500], "case_labels": ca})
            if pair and len(samples["complementary_branch"]) < 6:
                samples["complementary_branch"].append({"parent_id": parent,
                                                        "step_index": index,
                                                        "tactic": action[:500],
                                                        "case_labels": ca})
    return {"counts": counts, "tactics": tactics, "depths": depths,
            "theorems": theorems,
            "lengths": lengths, "fresh_theorems": fresh_theorems,
            "fresh_lengths": fresh_lengths, "samples": samples}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", required=True)
    parser.add_argument("--old-audit", required=True,
                        help="VNext full audit used to exclude prior-development parents")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    started = time.monotonic()
    excluded = frozenset(old_parent_ids(args.old_audit))
    paths = [str(Path(args.raw_root) / f"{name}.json") for name in ("train", "val", "test")]
    with ProcessPoolExecutor(max_workers=3) as pool:
        parts = list(pool.map(scan_file, [(path, excluded) for path in paths]))
    counts, tactics, depths, theorems, lengths = Counter(), Counter(), Counter(), set(), {}
    fresh_theorems, fresh_lengths = set(), {}
    samples = {"goal_creation": [], "complementary_branch": []}
    for part in parts:
        counts.update(part["counts"]); tactics.update(part["tactics"])
        depths.update(part["depths"])
        theorems.update(part["theorems"]); lengths.update(part["lengths"])
        fresh_theorems.update(part["fresh_theorems"])
        fresh_lengths.update(part["fresh_lengths"])
        for key in samples:
            samples[key].extend(part["samples"][key])
    vals = sorted(lengths.values())
    fresh_vals = sorted(fresh_lengths.values())
    elapsed = time.monotonic() - started
    report = {
        "artifact": "lean_raw_structural_source_census_v1",
        "raw_root": args.raw_root, "source_splits": paths,
        "workers": 3, "elapsed_seconds": round(elapsed, 3),
        "throughput_records_per_second": round(counts["transitions"] / elapsed, 1),
        "counts": dict(sorted(counts.items())),
        "distinct_parent_theorems": len(theorems),
        "fresh_distinct_parent_theorems": len(fresh_theorems),
        "trajectory_length": {"count": len(vals), "median": statistics.median(vals),
                              "max": max(vals), "complete_ordered_sequence": True,
                              "exact_before_states": True, "exact_source_actions": True,
                              "exact_after_states": True, "replay_executable_now": False},
        "fresh_trajectory_length": {"count": len(fresh_vals),
                                    "median": statistics.median(fresh_vals),
                                    "max": max(fresh_vals),
                                    "multi_step_count": sum(value > 1 for value in fresh_vals),
                                    "bins": length_bins(fresh_vals)},
        "trajectory_length_distribution": length_bins(vals),
        "fresh_proof_depth_distribution": dict(depths),
        "tactic_head_top30": tactics.most_common(30),
        "samples": {key: rows[:12] for key, rows in samples.items()},
        "semantic_availability": {
            "goals": "EXPLICIT", "goal_local_contexts": "EXPLICIT",
            "action_global_premises": "EXPLICIT_BUT_ACTION_DERIVED",
            "claim_dependency_graph": "ABSENT",
            "hml_obligations_distinct_from_goals": "ABSENT",
            "candidate_lifecycle": "ABSENT",
            "general_branch_predicate_and_coverage": "ABSENT",
            "case_scope_labels": "EXPLICIT_BUT_NOT_SUFFICIENT_FOR_BRANCH_OBJECT",
        },
    }
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "workers", "elapsed_seconds", "throughput_records_per_second", "counts",
        "distinct_parent_theorems", "fresh_distinct_parent_theorems",
        "trajectory_length", "fresh_trajectory_length",
        "fresh_proof_depth_distribution", "tactic_head_top30",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
