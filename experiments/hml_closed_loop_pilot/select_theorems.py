#!/usr/bin/env python3
"""Freeze the 60-parent closed-loop development pilot without opening FINAL_B."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
RAW = Path(
    "/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts/"
    "leandojo_raw/leandojo_benchmark_4"
)
CONFIRMATORY = Path(
    "/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts/"
    "reasoning_layer_v1_confirmatory/records"
)
URL = "https://github.com/leanprover-community/mathlib4"
COMMIT = "29dcec074de168ac2bf835a77ef68bbe069194c5"
SEED = "HML_CLOSED_LOOP_DEV_PILOT_20260826_V1"


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def parent(file_path: str, full_name: str) -> str:
    return f"{file_path}::{full_name}"


def normalized_state(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def gz_rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def exclusions() -> tuple[set[str], set[str]]:
    parents: set[str] = set()
    states: set[str] = set()
    for row in gz_rows(REPO / "data/hml_50k_final/canonical/records.jsonl.gz"):
        parents.add(row["parent_id"])
        state = row["neutral_transition"]["state_before"]["claims"]["p0"]["proposition"]
        states.add(digest(normalized_state(state)))
    for row in gz_rows(REPO / "data/vnext_10k/full_audit_records.jsonl.gz"):
        if row.get("source_family") == "LEAN_DOJO":
            parents.add(row["parent_id"])
            source = row.get("source", {})
            before = source.get("raw_state_before") or row.get("raw_state_before")
            if before:
                states.add(digest(normalized_state(before)))
    for split in ("train", "dev", "final_a"):
        for row in gz_rows(CONFIRMATORY / f"{split}.jsonl.gz"):
            parents.add(row["parent_id"])
            before = row.get("current_state") or row.get("state_before")
            if before:
                states.add(digest(normalized_state(before)))
    return parents, states


def depth_bin(length: int) -> str | None:
    if 6 <= length <= 10:
        return "6-10"
    if 11 <= length <= 20:
        return "11-20"
    if length >= 21:
        return "21+"
    return None


def main() -> None:
    metadata = json.loads((RAW / "metadata.json").read_text())
    if metadata["from_repo"] != {"url": URL, "commit": COMMIT}:
        raise AssertionError(metadata["from_repo"])
    excluded_parents, excluded_states = exclusions()
    source_path = RAW / "random/train.json"
    source = json.loads(source_path.read_text())
    pools: dict[str, list[dict[str, object]]] = {"6-10": [], "11-20": [], "21+": []}
    seen_states = set(excluded_states)
    for theorem in sorted(source, key=lambda x: digest(f"{SEED}|{x['file_path']}|{x['full_name']}")):
        pid = parent(theorem["file_path"], theorem["full_name"])
        trace = theorem.get("traced_tactics") or []
        length = len(trace)
        bucket = depth_bin(length)
        if bucket is None or pid in excluded_parents or not trace:
            continue
        state = trace[0]["state_before"]
        state_hash = digest(normalized_state(state))
        if state_hash in seen_states:
            continue
        seen_states.add(state_hash)
        pools[bucket].append({
            "theorem_id": pid,
            "url": URL,
            "commit": COMMIT,
            "file_path": theorem["file_path"],
            "full_name": theorem["full_name"],
            "start": theorem["start"],
            "end": theorem["end"],
            "source_split": "random/train-unused",
            "source_proof_depth": length,
            "source_depth_bin": bucket,
            "initial_state_sha256": digest(state),
            "normalized_initial_state_sha256": state_hash,
        })
    selected = [item for bucket in ("6-10", "11-20", "21+") for item in pools[bucket][:20]]
    if any(len(pools[bucket]) < 20 for bucket in pools) or len(selected) != 60:
        raise AssertionError({bucket: len(rows) for bucket, rows in pools.items()})
    payload = {
        "schema_version": "hml-closed-loop-pilot-theorems-v1",
        "selection_seed": SEED,
        "source_metadata_sha256": hashlib.sha256((RAW / "metadata.json").read_bytes()).hexdigest(),
        "source_split_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "mathlib_url": URL,
        "mathlib_commit": COMMIT,
        "lean_dojo_version": metadata["leandojo_version"],
        "counts": {"total": 60, "6-10": 20, "11-20": 20, "21+": 20},
        "exclusion_counts": {
            "parents": len(excluded_parents),
            "normalized_initial_states": len(excluded_states),
        },
        "source_actions_included": False,
        "theorems": selected,
    }
    output = Path(__file__).with_name("theorems.json")
    output.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(output)
    print(digest(canonical(payload)))


if __name__ == "__main__":
    main()
