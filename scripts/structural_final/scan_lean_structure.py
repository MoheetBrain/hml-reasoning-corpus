#!/usr/bin/env python3
"""Parallel, read-only structural census of the pinned LeanDojo transition export.

This script deliberately reports only structure that is explicit in the source.  In
particular, a Lean ``case`` label is counted as scope metadata, not promoted to a HML
``Branch`` (the source does not always expose the corresponding predicate), and open Lean
goals are not duplicated as HML obligations.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import statistics
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


CASE_RE = re.compile(r"(?m)^case ([^\n]+)$")
HYP_RE = re.compile(r"^([^\s⊢][^:⊢]*?)\s*:\s*(.+)$")


def depth_bin(depth: int) -> str:
    step = depth + 1
    if step == 1:
        return "1"
    if step <= 3:
        return "2-3"
    if step <= 5:
        return "4-5"
    if step <= 10:
        return "6-10"
    if step <= 20:
        return "11-20"
    return "21+"


def parse_goal_blocks(raw: str) -> list[dict]:
    """Parse only explicit pretty-printer boundaries; never infer semantic ancestry."""
    blocks = []
    for piece in re.split(r"\n\s*\n", raw.strip()):
        lines = piece.splitlines()
        turnstiles = [i for i, line in enumerate(lines) if line.startswith("⊢")]
        if not turnstiles:
            continue
        cut = turnstiles[0]
        header = lines[0][5:].strip() if lines and lines[0].startswith("case ") else None
        hypotheses = []
        for line in lines[1 if header else 0 : cut]:
            match = HYP_RE.match(line)
            if match:
                hypotheses.append((match.group(1).strip(), match.group(2).strip()))
        target_lines = [lines[cut][1:].strip()]
        target_lines.extend(line.strip() for line in lines[cut + 1 :] if line.strip())
        blocks.append({"header": header, "hypotheses": hypotheses,
                       "target": " ".join(target_lines)})
    return blocks


def complementary_case_pair(blocks: list[dict]) -> bool:
    """Conservative evidence only: explicit two-case scopes with P / not-P locals."""
    if len(blocks) != 2 or not all(block["header"] for block in blocks):
        return False
    left = {typ for _, typ in blocks[0]["hypotheses"]}
    right = {typ for _, typ in blocks[1]["hypotheses"]}
    left_only, right_only = left - right, right - left
    for value in left_only:
        compact = re.sub(r"\s+", "", value)
        for other in right_only:
            other_compact = re.sub(r"\s+", "", other)
            if other_compact in {f"¬{compact}", f"Not{compact}"}:
                return True
            if compact in {f"¬{other_compact}", f"Not{other_compact}"}:
                return True
    return False


def old_parent_ids(path: str | None) -> set[str]:
    if not path:
        return set()
    parents = set()
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("source_family") == "LEAN_DOJO":
                parents.add(row["parent_id"])
    return parents


def ranges(path: Path, workers: int) -> list[tuple[int, int]]:
    size = path.stat().st_size
    return [(size * index // workers, size * (index + 1) // workers)
            for index in range(workers)]


def scan_chunk(args: tuple[str, int, int, frozenset[str]]) -> dict:
    path, start, end, excluded = args
    counts = Counter()
    depth = Counter()
    dimensions = Counter()
    proof_lengths = {}
    theorem_ids = set()
    examples = {"multi_goal": [], "case_scope": [], "complementary_case": [],
                "high_dimension": []}
    with open(path, "rb") as stream:
        if start:
            stream.seek(start - 1)
            if stream.read(1) != b"\n":
                stream.readline()
        else:
            stream.seek(0)
        while stream.tell() < end:
            line = stream.readline()
            if not line:
                break
            row = json.loads(line)
            counts["records"] += 1
            theorem = row["theorem_id"]
            parent = f"{row['source_file']}::{theorem}"
            theorem_ids.add(parent)
            proof_lengths[parent] = row["proof_length"]
            if parent in excluded:
                counts["old_history_excluded"] += 1
                continue
            counts["fresh_records"] += 1
            raw = row["lean"]["raw_state_before"]
            blocks = parse_goal_blocks(raw)
            goal_count = row["state_before"]["n_goals"]
            hypothesis_count = len(row["state_before"]["hypotheses"])
            case_labels = CASE_RE.findall(raw)
            scope_depth = max((label.count(".") + 1 for label in case_labels), default=1)
            effect = row["observed_action"]
            changed = sum([
                bool(effect.get("target_changed")),
                bool(effect.get("delta_goals")),
                bool(effect.get("names_added")),
                bool(effect.get("names_removed")),
                bool(effect.get("names_rebound")),
            ])
            dims = {
                "explicit_goal": goal_count >= 1,
                "separated_hypothesis_context": hypothesis_count >= 2,
                "multiple_goals": goal_count >= 2,
                "explicit_case_scope_label": bool(case_labels),
                "nested_scope_label": scope_depth >= 2,
                "long_trajectory_context": row["proof_depth"] >= 4,
                "multi_field_state_delta": changed >= 2,
            }
            for name, present in dims.items():
                if present:
                    dimensions[name] += 1
            depth[depth_bin(row["proof_depth"])] += 1
            counts["has_goal"] += goal_count >= 1
            counts["has_hypotheses"] += hypothesis_count > 0
            counts["has_2plus_hypotheses"] += hypothesis_count >= 2
            counts["multiple_goals"] += goal_count >= 2
            counts["case_scope_labels"] += bool(case_labels)
            counts["nested_case_scope_labels"] += scope_depth >= 2
            counts["premises_used_nonempty"] += bool(effect.get("premises_used"))
            counts["complementary_case_pair_source_derivable"] += complementary_case_pair(blocks)
            counts["exact_before_action_after"] += bool(
                row["state_before"] and row["lean"]["raw_tactic"] and row["state_after"]
            )
            # Three means an explicit goal plus at least two additional independent
            # external-state dimensions.  This is a census candidate, not final admission.
            dim_count = sum(dims.values())
            counts["candidate_gate_3_dimensions"] += dim_count >= 3
            for key, condition in (
                ("multi_goal", goal_count >= 2),
                ("case_scope", bool(case_labels)),
                ("complementary_case", complementary_case_pair(blocks)),
                ("high_dimension", dim_count >= 5),
            ):
                if condition and len(examples[key]) < 3:
                    examples[key].append({
                        "example_id": row["example_id"], "parent_id": parent,
                        "goals": goal_count, "hypotheses_focused": hypothesis_count,
                        "case_labels": case_labels, "proof_depth": row["proof_depth"],
                        "dimensions": sorted(name for name, present in dims.items() if present),
                    })
    return {
        "counts": counts, "depth": depth, "dimensions": dimensions,
        "theorem_ids": theorem_ids, "proof_lengths": proof_lengths, "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--old-audit")
    parser.add_argument("--workers", type=int, default=min(24, os.cpu_count() or 1))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.records)
    started = time.monotonic()
    excluded = frozenset(old_parent_ids(args.old_audit))
    jobs = [(str(source), start, end, excluded) for start, end in ranges(source, args.workers)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        partial = list(pool.map(scan_chunk, jobs))
    counts, depth, dimensions = Counter(), Counter(), Counter()
    theorem_ids, proof_lengths = set(), {}
    examples = {key: [] for key in partial[0]["examples"]}
    for item in partial:
        counts.update(item["counts"])
        depth.update(item["depth"])
        dimensions.update(item["dimensions"])
        theorem_ids.update(item["theorem_ids"])
        proof_lengths.update(item["proof_lengths"])
        for key, rows in item["examples"].items():
            examples[key].extend(rows)
    for key in examples:
        examples[key] = sorted(examples[key], key=lambda row: row["example_id"])[:8]
    lengths = sorted(proof_lengths.values())
    hasher = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            hasher.update(block)
    digest = hasher.hexdigest()
    report = {
        "artifact": "lean_structural_source_census_v1",
        "source_path": str(source), "source_sha256": digest,
        "workers": args.workers, "elapsed_seconds": round(time.monotonic() - started, 3),
        "throughput_records_per_second": round(counts["records"] / max(time.monotonic() - started, 1e-9), 1),
        "old_vnext_parent_groups_excluded": len(excluded),
        "counts": dict(sorted(counts.items())),
        "distinct_parent_theorems": len(theorem_ids),
        "trajectory_length": {
            "count": len(lengths), "median": statistics.median(lengths),
            "max": max(lengths), "complete_in_raw_source": True,
            "complete_in_canonical_subset": False,
        },
        "proof_depth_distribution_fresh": dict(depth),
        "structural_dimensions_fresh": dict(sorted(dimensions.items())),
        "source_explicit_but_not_state_dependencies": {
            "premises_used": "global declarations used by the gold tactic; withheld from model state because they are action-derived and can leak the answer",
        },
        "not_source_supported": {
            "claim_dependency_edges": 0,
            "hml_obligations_distinct_from_lean_goals": 0,
            "candidate_lifecycle_states": 0,
            "epistemic_status_transitions": 0,
            "general_branch_objects_with_predicate_and_coverage": 0,
        },
        "examples": examples,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "workers", "elapsed_seconds", "throughput_records_per_second",
        "old_vnext_parent_groups_excluded", "counts", "distinct_parent_theorems",
        "trajectory_length", "proof_depth_distribution_fresh", "structural_dimensions_fresh",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
