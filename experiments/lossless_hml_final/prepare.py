#!/usr/bin/env python3
"""Build matched 10K generative views and model-blind theorem candidate pools."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from transformers import AutoTokenizer


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from representation import canonical, digest, prompt  # noqa: E402


MODEL_REV = "b968826d9c46dd6066d109eabc6255188de91218"
MAX_TOKENS = 3072
TRAIN_N = 10_000
TRAIN_SEED = "LOSSLESS_HML_GENERATIVE_10K_20260826_V1"
DEV_SEED = "LOSSLESS_HML_SOLVER_DEV_20260826_V1"
EVAL_SEED = "LOSSLESS_HML_FINAL_EVAL_20260826_V1"
URL = "https://github.com/leanprover-community/mathlib4"
COMMIT = "29dcec074de168ac2bf835a77ef68bbe069194c5"
ARTIFACTS = Path("/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts")
SOURCE = ARTIFACTS / "lean_domino_v2/lean_canonical_records.jsonl"
BENCHMARK = ARTIFACTS / "leandojo_raw/leandojo_benchmark_4"
FINAL_A = ARTIFACTS / "reasoning_layer_v1_confirmatory/records/final_a.jsonl.gz"


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def gz_rows(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def parent(row: dict[str, Any]) -> str:
    return f"{row['source_file']}::{row['theorem_id']}"


def chat_lengths(tokenizer: Any, user_prompt: str, completion: str) -> tuple[int, int, int]:
    user = [{"role": "user", "content": user_prompt}]
    prompt_ids = tokenizer.apply_chat_template(
        user, add_generation_prompt=True, tokenize=True, enable_thinking=False, return_dict=False,
    )
    full_ids = tokenizer.apply_chat_template(
        user + [{"role": "assistant", "content": completion}],
        tokenize=True, enable_thinking=False, return_dict=False,
    )
    return len(prompt_ids), len(full_ids) - len(prompt_ids), len(full_ids)


def training_authority() -> tuple[dict[str, dict[str, Any]], set[str], set[str]]:
    rung_ids = set(json.loads((REPO / "data/hml_50k_final/rungs/10k/record_ids.json").read_text()))
    candidates: dict[str, dict[str, Any]] = {}
    all_parents: set[str] = set()
    all_states: set[str] = set()
    priority: list[tuple[str, dict[str, Any]]] = []
    for row in gz_rows(REPO / "data/hml_50k_final/canonical/records.jsonl.gz"):
        all_parents.add(row["parent_id"])
        state = row["neutral_transition"]["state_before"]["claims"]["p0"]["proposition"]
        all_states.add(digest(re.sub(r"\s+", " ", state).strip()))
        if row["split"] != "train":
            continue
        key = digest(f"{TRAIN_SEED}|{row['canonical_source_example_id']}")
        # Preserve the old 10K authority at the front, then deterministic common reserves.
        tier = "0" if row["record_id"] in rung_ids else "1"
        priority.append((tier + key, {
            "record_id": row["record_id"],
            "parent_id": row["parent_id"],
            "source_example_id": row["canonical_source_example_id"],
            "depth": row["depth"],
            "priority_tier": tier,
        }))
    for _, item in sorted(priority):
        candidates[item["source_example_id"]] = item
    return candidates, all_parents, all_states


def build_training(tokenizer: Any, output: Path) -> tuple[set[str], dict[str, Any]]:
    candidates, prior_parents, prior_states = training_authority()
    parent_targets: dict[str, set[str]] = collections.defaultdict(set)
    for example, item in candidates.items():
        parent_targets[item["parent_id"]].add(example)
    fits: list[dict[str, Any]] = []
    current_parent: str | None = None
    group: list[dict[str, Any]] = []

    def consume(rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        pid = parent(rows[0])
        targets = parent_targets.get(pid)
        if not targets:
            return
        ordered = sorted(rows, key=lambda row: row["transition_index"])
        events: list[dict[str, str]] = []
        for row in ordered:
            example = row["example_id"]
            if example in targets:
                raw_prompt = prompt("raw", row["lean"]["raw_state_before"], events)
                hml_prompt = prompt("lossless_hml", row["lean"]["raw_state_before"], events)
                tactic = row["lean"]["raw_tactic"]
                raw_lengths = chat_lengths(tokenizer, raw_prompt, tactic)
                hml_lengths = chat_lengths(tokenizer, hml_prompt, tactic)
                if max(raw_lengths[2], hml_lengths[2]) <= MAX_TOKENS:
                    meta = candidates[example]
                    fits.append({
                        **meta,
                        "current_state": row["lean"]["raw_state_before"],
                        "history": list(events),
                        "completion": tactic,
                        "raw_prompt": raw_prompt,
                        "lossless_hml_prompt": hml_prompt,
                        "raw_lengths": raw_lengths,
                        "lossless_hml_lengths": hml_lengths,
                    })
            events.append({
                "state_before": row["lean"]["raw_state_before"],
                "action": row["lean"]["raw_tactic"],
                "state_after": row["lean"]["raw_state_after"],
            })

    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            pid = parent(row)
            if current_parent is None:
                current_parent = pid
            if pid != current_parent:
                consume(group)
                group = []
                current_parent = pid
            if pid in parent_targets:
                group.append(row)
        consume(group)
    selected = sorted(
        fits,
        key=lambda item: (
            item["priority_tier"],
            digest(f"{TRAIN_SEED}|{item['source_example_id']}"),
        ),
    )[:TRAIN_N]
    if len(selected) != TRAIN_N:
        raise AssertionError((len(fits), len(selected)))
    output.mkdir(parents=True, exist_ok=True)
    paths = {arm: output / f"{arm}_train.jsonl" for arm in ("raw", "lossless_hml")}
    handles = {arm: path.open("w", encoding="utf-8") for arm, path in paths.items()}
    try:
        for item in selected:
            common = {
                "record_id": item["record_id"],
                "parent_id": item["parent_id"],
                "source_example_id": item["source_example_id"],
                "depth": item["depth"],
                "completion": item["completion"],
            }
            for arm in handles:
                row = {
                    **common,
                    "prompt": item[f"{arm}_prompt"],
                    "prompt_tokens": item[f"{arm}_lengths"][0],
                    "completion_tokens": item[f"{arm}_lengths"][1],
                    "full_tokens": item[f"{arm}_lengths"][2],
                }
                handles[arm].write(canonical(row) + "\n")
    finally:
        for handle in handles.values():
            handle.close()
    ids = [item["source_example_id"] for item in selected]
    parents = {item["parent_id"] for item in selected}
    manifest = {
        "schema_version": "lossless-hml-generative-10k-v1",
        "model_revision": MODEL_REV,
        "selection_seed": TRAIN_SEED,
        "rows": TRAIN_N,
        "parents": len(parents),
        "max_full_tokens": MAX_TOKENS,
        "ordered_source_ids_sha256": digest(canonical(ids)),
        "source_sha256": sha(SOURCE),
        "views": {},
    }
    for arm, path in paths.items():
        lengths = [item[f"{arm}_lengths"][2] for item in selected]
        prompts = [item[f"{arm}_lengths"][0] for item in selected]
        manifest["views"][arm] = {
            "sha256": sha(path),
            "total_full_tokens": sum(lengths),
            "mean_full_tokens": sum(lengths) / len(lengths),
            "max_full_tokens": max(lengths),
            "mean_prompt_tokens": sum(prompts) / len(prompts),
        }
    write_json(output / "dataset_manifest.json", manifest)
    write_json(output / "train_parents.json", sorted(parents))
    return parents, {"manifest": manifest, "prior_parents": prior_parents, "prior_states": prior_states}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def exclusion_parents(prior: set[str], train: set[str]) -> set[str]:
    result = set(prior) | set(train)
    for row in gz_rows(REPO / "data/vnext_10k/full_audit_records.jsonl.gz"):
        if row.get("source_family") == "LEAN_DOJO":
            result.add(row["parent_id"])
    for row in gz_rows(FINAL_A):
        result.add(row["parent_id"])
    old = REPO / "experiments/hml_closed_loop_pilot/theorems.json"
    if old.exists():
        result.update(item["theorem_id"] for item in json.loads(old.read_text())["theorems"])
    return result


def theorem_pool(excluded: set[str], excluded_states: set[str], output: Path) -> None:
    metadata = json.loads((BENCHMARK / "metadata.json").read_text())
    if metadata["from_repo"] != {"url": URL, "commit": COMMIT}:
        raise AssertionError(metadata)
    source = json.loads((BENCHMARK / "random/train.json").read_text())
    pools: dict[str, list[dict[str, Any]]] = {"2-5": [], "6-10": [], "11-20": []}
    seen = set(excluded_states)
    for theorem in source:
        pid = f"{theorem['file_path']}::{theorem['full_name']}"
        trace = theorem.get("traced_tactics") or []
        length = len(trace)
        bucket = "2-5" if 2 <= length <= 5 else "6-10" if 6 <= length <= 10 else "11-20" if 11 <= length <= 20 else None
        if bucket is None or pid in excluded or not trace:
            continue
        normalized = digest(re.sub(r"\s+", " ", trace[0]["state_before"]).strip())
        if normalized in seen:
            continue
        seen.add(normalized)
        base = {
            "theorem_id": pid,
            "url": URL,
            "commit": COMMIT,
            "file_path": theorem["file_path"],
            "full_name": theorem["full_name"],
            "source_proof_length": length,
            "source_length_bin": bucket,
            "source_split": "random/train-unused",
            "initial_state_sha256": digest(trace[0]["state_before"]),
            "normalized_initial_state_sha256": normalized,
        }
        for kind, seed in (("dev", DEV_SEED), ("eval", EVAL_SEED)):
            item = dict(base)
            item["selection_key"] = digest(f"{seed}|{pid}")
            pools[bucket].append((kind, item))
    payload: dict[str, Any] = {
        "schema_version": "lossless-hml-model-blind-theorem-pools-v1",
        "mathlib_commit": COMMIT,
        "source_actions_included": False,
        "dev": {},
        "eval": {},
    }
    for kind in ("dev", "eval"):
        for bucket, values in pools.items():
            ordered = sorted((item for item_kind, item in values if item_kind == kind), key=lambda x: x["selection_key"])
            payload[kind][bucket] = ordered[:240]
    write_json(output / "theorem_candidates.json", payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True, trust_remote_code=False)
    train_parents, authority = build_training(tokenizer, args.output)
    excluded = exclusion_parents(authority["prior_parents"], train_parents)
    theorem_pool(excluded, authority["prior_states"], args.output)
    print(canonical({"output": str(args.output), "manifest": authority["manifest"]}))


if __name__ == "__main__":
    main()
