#!/usr/bin/env python3
"""Frozen three-arm reasoning-layer V1 FINAL_A experiment."""

from __future__ import annotations

import argparse
import bisect
import collections
import gzip
import hashlib
import io
import json
import math
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache
from safetensors import safe_open
from transformers import AutoTokenizer


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "scripts/reasoning_layer_discovery"))
from semantic_extractor import (  # noqa: E402
    HISTORY_WINDOW,
    SCHEMA_VERSION,
    canonical,
    digest_text,
    extract_reasoning_state,
    parse_lean_state,
    raw_history_payload,
    tactic_family,
)


CORPUS = REPO / "data/hml_50k_final"
VNEXT = REPO / "data/vnext_10k/full_audit_records.jsonl.gz"
SOURCE = Path("/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts/lean_domino_v2/lean_canonical_records.jsonl")
DISCOVERY = REPO / "experiments/reasoning_layer_discovery"
HOLDOUT_MANIFEST = DISCOVERY / "FRESH_HOLDOUT_MANIFEST.json"
ART = Path("/Users/moheet/Projects/Hamiltonian-Labs/hml_research_artifacts/reasoning_layer_v1_confirmatory")
MODEL_REV = "b968826d9c46dd6066d109eabc6255188de91218"
MODEL = Path("/Users/moheet/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots") / MODEL_REV
PYTHON = Path("/Users/moheet/Projects/Hamiltonian-Labs/hml-model-experiments/.venv/bin/python")
RECIPE = HERE / "lora_config.yaml"
MAXSEQ = 6144
ARMS = ("base", "raw", "semantic")
N_TRAIN = 10_000
N_DEV = 3_000
N_FINAL = 3_000
BOOTSTRAPS = 4_000
BOOTSTRAP_SEED = 20_260_824
MICROBATCH_SIZE = 1
GRAD_ACCUMULATION_STEPS = 2
MICROSTEPS = 10_000
OPTIMIZER_UPDATES = MICROSTEPS // GRAD_ACCUMULATION_STEPS
SELECTION_SEED = "REASONING_LAYER_FRESH_HOLDOUTS_20260824_V1"
HML_CANDIDATE_SEED = "hml-50k-final-20260822"
DEPTH_ORDER = ("1", "2-3", "4-5", "6-10", "11-20", "21+")

PREFIX = (
    "Choose the single most useful next mathematical tactic from the six candidates.\n\n"
    "<REASONING_CONTEXT>\n"
)
SUFFIX_HEAD = "\n</REASONING_CONTEXT>\n\n<CANDIDATES>\n"
SUFFIX_TAIL = (
    "\n</CANDIDATES>\n\n"
    "Answer with exactly one label:\n"
    "C0 / C1 / C2 / C3 / C4 / C5"
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical(row) + "\n")


def deterministic_gzip(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                for row in rows:
                    text.write(canonical(row) + "\n")


def read_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def protocol_commit() -> str:
    return git("log", "-1", "--format=%H", "--", str((HERE / "CONFIRMATORY_PROTOCOL.md").relative_to(REPO)))


def stable_int(seed: str, *parts: str) -> int:
    return int(digest_text("\0".join((seed, *parts))), 16)


def depth_bin(value: int) -> str:
    if value <= 1:
        return "1"
    if value <= 3:
        return "2-3"
    if value <= 5:
        return "4-5"
    if value <= 10:
        return "6-10"
    if value <= 20:
        return "11-20"
    return "21+"


def count_bin(value: int) -> str:
    if value == 0:
        return "0"
    if value == 1:
        return "1"
    if value <= 3:
        return "2-3"
    if value <= 7:
        return "4-7"
    if value <= 15:
        return "8-15"
    return "16+"


def action_head(tactic: str) -> str:
    text = re.sub(r"^(?:by\s+)+", "", tactic.strip())
    match = re.search(r"[A-Za-z_][A-Za-z0-9_'.!?]*|[<>=:+*/-]+", text)
    return match.group(0).lower() if match else "<symbolic>"


def parent_id(row: dict[str, Any]) -> str:
    return f"{row['source_file']}::{row['theorem_id']}"


def percentile(values: list[int | float], q: float) -> float:
    return float(np.quantile(np.asarray(values), q))


def stats(values: list[int | float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values), "median": statistics.median(values),
        "p95": percentile(values, .95), "max": max(values), "total": sum(values),
    }


def state_hash_from_hml_record(row: dict[str, Any]) -> str:
    return digest_text(row["neutral_transition"]["state_before"]["claims"]["p0"]["proposition"])


def load_hml_authority() -> tuple[dict[str, dict[str, Any]], set[str], set[str], set[str], set[str], set[str]]:
    train_ids = set(json.loads((CORPUS / "rungs/10k/record_ids.json").read_text(encoding="utf-8")))
    selected: dict[str, dict[str, Any]] = {}
    parents: set[str] = set()
    states: set[str] = set()
    train_examples: set[str] = set()
    reserve_candidates: list[tuple[str, str]] = []
    dev_examples: set[str] = set()
    for row in read_gzip(CORPUS / "canonical/records.jsonl.gz"):
        parents.add(row["parent_id"])
        states.add(state_hash_from_hml_record(row))
        if row["record_id"] in train_ids:
            selected[row["canonical_source_example_id"]] = row
            train_examples.add(row["canonical_source_example_id"])
        elif row["split"] == "dev":
            selected[row["canonical_source_example_id"]] = row
            dev_examples.add(row["canonical_source_example_id"])
        elif row["split"] == "train":
            reserve_candidates.append((
                digest_text("RLV1_MAXSEQ_RESERVE|" + row["record_id"]),
                row["canonical_source_example_id"],
            ))
    reserve_examples = {example for _, example in sorted(reserve_candidates)[:512]}
    if reserve_examples & train_examples:
        raise AssertionError("reserve overlaps primary 10K rung")
    for row in read_gzip(CORPUS / "canonical/records.jsonl.gz"):
        if row["canonical_source_example_id"] in reserve_examples:
            selected[row["canonical_source_example_id"]] = row
    if len(train_examples) != N_TRAIN or len(dev_examples) != N_DEV:
        raise AssertionError((len(train_examples), len(dev_examples)))
    return selected, parents, states, train_examples, reserve_examples, dev_examples


def load_vnext_parents() -> set[str]:
    return {row["parent_id"] for row in read_gzip(VNEXT) if row.get("source_family") == "LEAN_DOJO"}


def reconstruct_final_a(hml_parents: set[str], vnext_parents: set[str], prior_states: set[str]) -> tuple[set[str], set[str], dict[str, Any]]:
    frozen = json.loads(HOLDOUT_MANIFEST.read_text(encoding="utf-8"))
    expected = frozen["holdouts"]["FRESH_FINAL_A"]
    previous = hml_parents | vnext_parents
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    bad_parent: set[str] = set()
    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            parent = parent_id(row)
            if parent in previous:
                continue
            state_hash = digest_text(row["lean"]["raw_state_before"])
            if state_hash in prior_states:
                bad_parent.add(parent)
            groups[parent].append({
                "example_id": row["example_id"], "parent_id": parent,
                "step_index": row["transition_index"], "official_split": row["lean_official_split"],
                "state_hash": state_hash,
                "transition_hash": digest_text(canonical({
                    "example_id": row["example_id"], "state_before": row["lean"]["raw_state_before"],
                    "action": row["lean"]["raw_tactic"], "state_after": row["lean"]["raw_state_after"],
                })),
            })
    for parent in bad_parent:
        groups.pop(parent, None)
    ordered = sorted(groups, key=lambda p: digest_text(f"{SELECTION_SEED}|FRESH_FINAL_A|{p}"))
    chosen: list[dict[str, Any]] = []
    chosen_parents: set[str] = set()
    for parent in ordered:
        if len(chosen) + len(groups[parent]) <= N_FINAL:
            chosen.extend(groups[parent]); chosen_parents.add(parent)
        if len(chosen) == N_FINAL:
            break
    if len(chosen) != N_FINAL:
        raise AssertionError("could not reconstruct FINAL_A")
    ids = {row["example_id"] for row in chosen}
    checks = {
        "records": len(ids), "parents": len(chosen_parents),
        "record_id_set_sha256": digest_text("\n".join(sorted(ids)) + "\n"),
        "parent_id_set_sha256": digest_text("\n".join(sorted(chosen_parents)) + "\n"),
        "current_state_hash_set_sha256": digest_text("\n".join(sorted(row["state_hash"] for row in chosen)) + "\n"),
        "transition_commitment_set_sha256": digest_text("\n".join(sorted(row["transition_hash"] for row in chosen)) + "\n"),
    }
    for key in checks:
        if checks[key] != expected[key]:
            raise AssertionError(f"FINAL_A frozen hash mismatch {key}: {checks[key]} != {expected[key]}")
    return ids, chosen_parents, checks


def candidate_sets(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lite = []
    for row in rows:
        observed = row.get("observed_action") or {}
        tactic = row["lean"]["raw_tactic"]
        lite.append({
            "example_id": row["example_id"], "parent_id": parent_id(row), "tactic": tactic,
            "tactic_head": action_head(tactic), "effect_class": observed.get("effect_class") or "UNKNOWN",
            "selection_rank": stable_int(HML_CANDIDATE_SEED, "select", row["example_id"]),
        })
    by_head: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    by_effect: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in lite:
        by_head[row["tactic_head"]].append(row); by_effect[row["effect_class"]].append(row)
    for pool in (*by_head.values(), *by_effect.values()):
        pool.sort(key=lambda x: (len(x["tactic"]), x["selection_rank"]))
    global_pool = sorted(lite, key=lambda x: (len(x["tactic"]), x["selection_rank"]))

    def nearby(pool: list[dict[str, Any]], row: dict[str, Any]) -> list[dict[str, Any]]:
        lengths = [len(x["tactic"]) for x in pool]
        middle = bisect.bisect_left(lengths, len(row["tactic"]))
        window = pool[max(0, middle - 80): min(len(pool), middle + 81)]
        return sorted(window, key=lambda x: (
            abs(len(x["tactic"]) - len(row["tactic"])),
            stable_int(HML_CANDIDATE_SEED, "distractor", row["example_id"], x["example_id"]),
        ))

    output = {}
    for row in lite:
        chosen = []
        seen = {row["tactic"]}
        for pool in (by_head[row["tactic_head"]], by_effect[row["effect_class"]], global_pool):
            for candidate in nearby(pool, row):
                if candidate["parent_id"] == row["parent_id"] or candidate["tactic"] in seen:
                    continue
                chosen.append(candidate); seen.add(candidate["tactic"])
                if len(chosen) == 5:
                    break
            if len(chosen) == 5:
                break
        if len(chosen) < 5:
            start = stable_int(HML_CANDIDATE_SEED, "global-fallback", row["example_id"]) % len(global_pool)
            for offset in range(min(len(global_pool), 5000)):
                candidate = global_pool[(start + offset) % len(global_pool)]
                if candidate["parent_id"] == row["parent_id"] or candidate["tactic"] in seen:
                    continue
                chosen.append(candidate); seen.add(candidate["tactic"])
                if len(chosen) == 5:
                    break
        if len(chosen) != 5:
            raise AssertionError(f"candidate failure {row['example_id']}")
        gold_pos = stable_int(HML_CANDIDATE_SEED, "gold-position", row["example_id"]) % 6
        distractors = sorted(chosen, key=lambda x: stable_int(HML_CANDIDATE_SEED, "candidate-order", row["example_id"], x["example_id"]))
        candidates = []
        for position in range(6):
            source = row if position == gold_pos else distractors.pop(0)
            candidates.append({
                "candidate_id": f"C{position}", "tactic_text": source["tactic"],
                "source_example_id": source["example_id"],
                "epistemic_status": "GOLD_SOURCE_ACTION" if position == gold_pos else "PLAUSIBLE_UNEXECUTED",
                "same_tactic_head_as_gold": source["tactic_head"] == row["tactic_head"],
            })
        output[row["example_id"]] = {"gold_candidate_id": f"C{gold_pos}", "candidates": candidates}
    return output


def build_records() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    selected_hml, hml_parents, prior_states, train_examples, reserve_examples, dev_examples = load_hml_authority()
    vnext_parents = load_vnext_parents()
    final_examples, final_parents, final_checks = reconstruct_final_a(hml_parents, vnext_parents, prior_states)
    wanted_examples = train_examples | reserve_examples | dev_examples | final_examples
    wanted_parents = {
        selected_hml[x]["parent_id"] for x in train_examples | reserve_examples | dev_examples
    } | final_parents
    source_rows: dict[str, dict[str, Any]] = {}
    parent_rows: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            parent = parent_id(row)
            if parent in wanted_parents:
                parent_rows[parent].append(row)
            if row["example_id"] in wanted_examples:
                source_rows[row["example_id"]] = row
    if set(source_rows) != wanted_examples:
        raise AssertionError(f"missing source rows {len(wanted_examples-set(source_rows))}")
    final_candidates = candidate_sets([source_rows[x] for x in final_examples])

    histories: dict[str, list[dict[str, str]]] = {}
    for parent, rows in parent_rows.items():
        rows.sort(key=lambda x: (x["transition_index"], x["example_id"]))
        prior = []
        for row in rows:
            if row["example_id"] in wanted_examples:
                histories[row["example_id"]] = list(prior)
            prior.append({
                "state_before": row["lean"]["raw_state_before"], "action": row["lean"]["raw_tactic"],
                "state_after": row["lean"]["raw_state_after"],
            })

    output = {"train": [], "reserve": [], "dev": [], "final_a": []}
    split_examples = (
        ("train", train_examples), ("reserve", reserve_examples),
        ("dev", dev_examples), ("final_a", final_examples),
    )
    for split, examples in split_examples:
        for example in examples:
            source = source_rows[example]
            frozen = selected_hml.get(example)
            candidates = frozen["candidate_audit"] if frozen else final_candidates[example]
            target = candidates["gold_candidate_id"]
            raw = source["lean"]["raw_state_before"]
            parsed = parse_lean_state(raw)
            semantic = extract_reasoning_state(raw, histories.get(example, []))
            dependencies = semantic["local_dependencies"]
            history = histories.get(example, [])[-HISTORY_WINDOW:]
            record = {
                "record_id": frozen["record_id"] if frozen else "RLV1-A-" + digest_text(example)[:16],
                "source_example_id": example, "parent_id": parent_id(source),
                "split": "train" if split == "reserve" else split,
                "current_state": raw, "history": history, "semantic_state": semantic,
                "candidates": [{"candidate_id": x["candidate_id"], "tactic_text": x["tactic_text"]} for x in candidates["candidates"]],
                "target": target,
                "metadata": {
                    "depth": int(source["transition_index"]) + 1,
                    "depth_bin": depth_bin(int(source["transition_index"]) + 1),
                    "trajectory_position": len(histories.get(example, [])),
                    "history_length": len(history),
                    "open_goal_count": parsed["open_goal_count"],
                    "dependency_edge_count": len(dependencies),
                    "case_label_present": semantic["active_scope"]["source_explicit"],
                    "module_presence": {
                        "goals": bool(semantic["open_goals"]), "dependencies": bool(dependencies),
                        "branch_scope": semantic["active_scope"]["source_explicit"], "history": bool(history),
                    },
                    "gold_action_verbatim_in_current_state": source["lean"]["raw_tactic"].strip() in raw,
                },
            }
            output[split].append(record)
        output[split].sort(key=lambda x: x["record_id"])
    audit = {
        "final_a_reconstruction": final_checks,
        "final_b": {
            "status": "SEALED_NOT_OPENED", "records": 3000,
            "integrity_relied_on": "frozen discovery commit and FRESH_HOLDOUT_MANIFEST hashes",
        },
        "counts_before_maxseq_resolution": {key: len(value) for key, value in output.items()},
        "parents": {key: len({x["parent_id"] for x in value}) for key, value in output.items()},
        "cross_split_parent_overlap": {
            "train_dev": len({x["parent_id"] for x in output["train"]} & {x["parent_id"] for x in output["dev"]}),
            "train_final_a": len({x["parent_id"] for x in output["train"]} & {x["parent_id"] for x in output["final_a"]}),
            "dev_final_a": len({x["parent_id"] for x in output["dev"]} & {x["parent_id"] for x in output["final_a"]}),
        },
        "gold_action_verbatim_in_current_state": {
            key: sum(x["metadata"]["gold_action_verbatim_in_current_state"] for x in value) for key, value in output.items()
        },
    }
    return output, audit


def payload(record: dict[str, Any], arm: str) -> str:
    base = {"current_lean_state": record["current_state"]}
    if arm == "base":
        value = base
    elif arm == "raw":
        value = {
            **base,
            "raw_prefix_metadata": {
                "successful_events_before_current": record["metadata"]["trajectory_position"],
            },
            "raw_history": raw_history_payload(record["history"]),
        }
    elif arm == "semantic":
        value = {**base, "reasoning_state": record["semantic_state"]}
    else:
        raise ValueError(arm)
    return canonical(value)


def reconstruct_semantic_from_raw(record: dict[str, Any]) -> dict[str, Any]:
    value = extract_reasoning_state(record["current_state"], record["history"])
    value["trajectory_position"]["steps_completed"] = record["metadata"]["trajectory_position"]
    return value


def candidate_block(candidates: list[dict[str, str]]) -> str:
    if [x["candidate_id"] for x in candidates] != [f"C{i}" for i in range(6)]:
        raise AssertionError("candidate ids/order")
    return "\n".join(f"{x['candidate_id']}: {x['tactic_text']}" for x in candidates)


def project(record: dict[str, Any], arm: str) -> dict[str, Any]:
    context = payload(record, arm)
    suffix = SUFFIX_HEAD + candidate_block(record["candidates"]) + SUFFIX_TAIL
    return {"context": context, "prompt": PREFIX + context + suffix, "suffix": suffix}


def audit_and_prepare() -> None:
    if any((HERE / "train").glob("*_seed*.json")):
        raise SystemExit("refusing preflight after training exists")
    records, holdout = build_records()
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, trust_remote_code=False)

    def full_length(record: dict[str, Any], arm: str) -> int:
        prompt = project(record, arm)["prompt"]
        return len(tokenizer.apply_chat_template([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": record["target"]},
        ], return_dict=False))

    primary_bad = [record for record in records["train"] if full_length(record, "raw") > MAXSEQ]
    safe_reserve = [record for record in records["reserve"] if max(full_length(record, arm) for arm in ARMS) <= MAXSEQ]
    if len(safe_reserve) < len(primary_bad):
        raise SystemExit(f"insufficient deterministic MAXSEQ reserve: {len(safe_reserve)} < {len(primary_bad)}")
    bad_ids = {record["record_id"] for record in primary_bad}
    replacements = safe_reserve[:len(primary_bad)]
    records["train"] = sorted(
        [record for record in records["train"] if record["record_id"] not in bad_ids] + replacements,
        key=lambda record: record["record_id"],
    )
    records.pop("reserve")
    if len(records["train"]) != N_TRAIN:
        raise AssertionError(len(records["train"]))
    replacement_audit = {
        "policy": "replace primary-rung RAW rows above training MAXSEQ with the first SHA256-ordered unused HML50K TRAIN rows that fit all arms",
        "primary_overflow_rows": len(primary_bad), "replacement_rows": len(replacements),
        "removed_record_id_set_sha256": digest_text("\n".join(sorted(bad_ids)) + "\n"),
        "replacement_record_id_set_sha256": digest_text("\n".join(sorted(x["record_id"] for x in replacements)) + "\n"),
        "semantic_content_changed": False, "same_records_all_arms": True,
    }
    holdout["counts"] = {key: len(value) for key, value in records.items()}
    holdout["parents"] = {key: len({x["parent_id"] for x in value}) for key, value in records.items()}
    holdout["gold_action_verbatim_in_current_state"] = {
        key: sum(x["metadata"]["gold_action_verbatim_in_current_state"] for x in value)
        for key, value in records.items()
    }
    holdout["maxseq_training_resolution"] = replacement_audit

    validation_ids = []
    for record in records["dev"]:
        if max(full_length(record, arm) for arm in ARMS) <= MAXSEQ:
            validation_ids.append(record["record_id"])
        if len(validation_ids) == 64:
            break
    if len(validation_ids) != 64:
        raise SystemExit("could not select 64 matched non-truncated DEV validation rows")
    validation_id_set = set(validation_ids)
    common = collections.Counter()
    info_failures = []
    token_values = {arm: {"chat_prompt_tokens": [], "full_tokens": []} for arm in ARMS}
    above_training_maxseq = {split: {arm: 0 for arm in ARMS} for split in records}
    coverage = {}
    for split, values in records.items():
        coverage[split] = {
            "rows": len(values), "history_present": sum(x["metadata"]["module_presence"]["history"] for x in values),
            "history_absent": sum(not x["metadata"]["module_presence"]["history"] for x in values),
            "dependencies_present": sum(x["metadata"]["module_presence"]["dependencies"] for x in values),
            "branch_scope_present": sum(x["metadata"]["module_presence"]["branch_scope"] for x in values),
            "multi_goal": sum(x["metadata"]["open_goal_count"] > 1 for x in values),
            "depth": dict(sorted(collections.Counter(x["metadata"]["depth_bin"] for x in values).items())),
        }
        for record in values:
            projections = {arm: project(record, arm) for arm in ARMS}
            common["rows"] += 1
            common["prefix_mismatch"] += len({value["prompt"][:len(PREFIX)] for value in projections.values()}) != 1
            common["suffix_mismatch"] += len({value["suffix"] for value in projections.values()}) != 1
            common["candidate_mismatch"] += any(candidate_block(record["candidates"]) not in value["prompt"] for value in projections.values())
            common["target_mismatch"] += record["target"] not in [f"C{i}" for i in range(6)]
            reconstructed = reconstruct_semantic_from_raw(record)
            if canonical(reconstructed) != canonical(record["semantic_state"]):
                info_failures.append(record["record_id"])
            forbidden = ("proof_length", "gold_candidate", "current_action", "future_trajectory")
            if any(key in projections["semantic"]["context"] for key in forbidden):
                info_failures.append(record["record_id"] + ":forbidden")
            for arm in ARMS:
                prompt = projections[arm]["prompt"]
                chat = tokenizer.apply_chat_template(
                    [{"role": "user", "content": prompt}], add_generation_prompt=True,
                    tokenize=False, enable_thinking=False,
                )
                full = tokenizer.apply_chat_template([
                    {"role": "user", "content": prompt}, {"role": "assistant", "content": record["target"]},
                ], return_dict=False)
                token_values[arm]["chat_prompt_tokens"].append(len(tokenizer.encode(chat)))
                token_values[arm]["full_tokens"].append(len(full))
                above_training_maxseq[split][arm] += len(full) > MAXSEQ

    common_result = {
        **dict(common), "expected_rows": N_TRAIN + N_DEV + N_FINAL,
        "result": "PASS" if all(common[key] == 0 for key in ("prefix_mismatch", "suffix_mismatch", "candidate_mismatch", "target_mismatch")) else "FAIL",
        "template_sha256": digest_text(PREFIX + "{REASONING_CONTEXT}" + SUFFIX_HEAD + "{CANDIDATES}" + SUFFIX_TAIL),
    }
    info_result = {
        "result": "PASS" if not info_failures else "FAIL", "rows": common["rows"],
        "semantic_reconstructed_exactly_from_base_plus_raw": not info_failures,
        "failures": info_failures[:100], "history_window": HISTORY_WINDOW,
        "field_provenance": {
            "active_goal": "A/B current state", "open_goals": "A/B current state",
            "local_dependencies": "B deterministic current-state name references",
            "active_scope": "A source-explicit current-state case label",
            "trajectory_position": "A source-explicit prefix length, copied neutrally into RAW raw_prefix_metadata and deterministically renamed in V1",
            "recent_actions": "A/B exact prior successful action -> deterministic family",
            "recent_deltas": "B deterministic prior state-before/state-after diff",
            "progress_summary": "B deterministic current state + recent deltas",
        },
    }
    model_context = int(json.loads((MODEL / "config.json").read_text()).get("max_position_embeddings", 0))
    context_overflows = {arm: sum(value > model_context for value in token_values[arm]["full_tokens"]) for arm in ARMS}
    training_overflows = above_training_maxseq["train"]
    token_result = {
        "result": "PASS" if not any(training_overflows.values()) and not any(context_overflows.values()) else "FAIL",
        "training_maxseq": MAXSEQ, "model_context_limit": model_context,
        "arms": {arm: {key: stats(values) for key, values in fields.items()} for arm, fields in token_values.items()},
        "training_overflows": training_overflows,
        "model_context_overflows": context_overflows,
        "rows_above_training_maxseq_by_split": above_training_maxseq,
        "zero_differential_truncation": not any(training_overflows.values()) and not any(context_overflows.values()),
        "evaluation_policy": "full prompts are scored without truncation up to the pinned model context limit; training and 64-row validation remain <=6144",
        "maxseq_resolution": replacement_audit,
        "validation_record_id_set_sha256": digest_text("\n".join(sorted(validation_ids)) + "\n"),
    }
    means = {arm: token_result["arms"][arm]["chat_prompt_tokens"]["mean"] for arm in ARMS}
    token_result["ratios"] = {
        "raw_over_base": means["raw"] / means["base"],
        "semantic_over_base": means["semantic"] / means["base"],
        "semantic_over_raw": means["semantic"] / means["raw"],
    }
    holdout["result"] = "PASS" if not any(holdout["cross_split_parent_overlap"].values()) and holdout["final_a_reconstruction"]["records"] == N_FINAL else "FAIL"

    audits = HERE / "audits"
    write_json(audits / "holdout_integrity.json", holdout)
    write_json(audits / "common_envelope.json", common_result)
    write_json(audits / "information_contract.json", info_result)
    write_json(audits / "token_audit.json", token_result)
    write_json(audits / "training_coverage.json", coverage)
    if {holdout["result"], common_result["result"], info_result["result"], token_result["result"]} != {"PASS"}:
        raise SystemExit("PREFLIGHT_FAILED; inspect audits; no training authorized")

    record_root = ART / "records"
    if record_root.exists():
        shutil.rmtree(record_root)
    for split, values in records.items():
        deterministic_gzip(record_root / f"{split}.jsonl.gz", values)
    prepared = ART / "prepared"
    if prepared.exists():
        shutil.rmtree(prepared)
    for arm in ARMS:
        destination = prepared / arm
        destination.mkdir(parents=True)
        arm_stats = {}
        for split, output_name in (("train", "train"), ("dev", "valid")):
            converted = []
            for record in records[split]:
                if split == "dev" and record["record_id"] not in validation_id_set:
                    continue
                prompt = project(record, arm)["prompt"]
                messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": record["target"]}]
                full = tokenizer.apply_chat_template(messages, return_dict=False)
                offset = len(tokenizer.apply_chat_template(messages[:-1], add_generation_prompt=True, return_dict=False))
                converted.append({"record_id": record["record_id"], "prompt": prompt, "completion": record["target"], "full": len(full), "supervised": len(full)-offset})
            converted.sort(key=lambda x: x["record_id"])
            with (destination / f"{output_name}.jsonl").open("w", encoding="utf-8") as handle:
                for item in converted:
                    handle.write(json.dumps({"prompt": item["prompt"], "completion": item["completion"]}, ensure_ascii=False) + "\n")
            arm_stats[output_name] = {
                "rows": len(converted), "max_full_tokens": max(x["full"] for x in converted),
                "full_tokens": sum(x["full"] for x in converted),
                "supervised_tokens": sum(x["supervised"] for x in converted),
                "sha256": sha(destination / f"{output_name}.jsonl"),
            }
        write_json(destination / "dataset_manifest.json", {"arm": arm, **arm_stats})

    inventory = collections.Counter(); params = 0
    for shard in sorted(MODEL.glob("model-*.safetensors")):
        with safe_open(shard, framework="numpy") as source:
            for key in source.keys():
                tensor = source.get_slice(key); params += math.prod(tensor.get_shape()); inventory[str(tensor.get_dtype())] += 1
    run_manifest = {
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "protocol_commit": protocol_commit(),
        "discovery_commit": "aea77b0a4197682643337efcc2d61574a5158ca7",
        "model_id": "Qwen/Qwen3-8B", "model_revision": MODEL_REV,
        "model_inventory": {"parameters": params, "dtypes": dict(inventory), "quantization": json.loads((MODEL / "config.json").read_text()).get("quantization_config")},
        "recipe_sha256": sha(RECIPE), "driver_sha256": sha(Path(__file__)),
        "protocol_sha256": sha(HERE / "CONFIRMATORY_PROTOCOL.md"),
        "source_sha256": sha(SOURCE), "holdout_manifest_sha256": sha(HOLDOUT_MANIFEST),
        "prepared": {arm: json.loads((prepared / arm / "dataset_manifest.json").read_text()) for arm in ARMS},
        "audits": {path.name: sha(path) for path in sorted(audits.glob("*.json"))},
        "stack": subprocess.check_output([str(PYTHON), "-c", "import importlib.metadata as m; print('mlx='+m.version('mlx')); print('mlx-lm='+m.version('mlx-lm')); print('transformers='+m.version('transformers'))"], text=True).splitlines(),
        "hardware": {"platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count()},
    }
    if inventory != {"BF16": 399} or run_manifest["model_inventory"]["quantization"] is not None:
        raise AssertionError(run_manifest["model_inventory"])
    write_json(HERE / "RUN_MANIFEST.json", run_manifest)
    print(canonical({"result": "PASS", "audits": str(audits), "prepared": str(prepared)}))


def swap_mb() -> float:
    text = subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True)
    match = re.search(r"used = ([0-9.]+)([MG])", text)
    if not match:
        return math.nan
    return float(match.group(1)) * (1024 if match.group(2) == "G" else 1)


def memory_snapshot() -> dict[str, Any]:
    vm = subprocess.check_output(["vm_stat"], text=True)
    page_match = re.search(r"page size of (\d+) bytes", vm)
    page = int(page_match.group(1)) if page_match else 16384
    values = {key: int(value.replace(".", "")) for key, value in re.findall(r"^([^:]+):\s+(\d+\.)$", vm, re.M)}
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "swap_used_mb": swap_mb(),
        "free_gib": values.get("Pages free", 0) * page / 2**30,
        "compressed_gib": values.get("Pages occupied by compressor", 0) * page / 2**30,
    }


def train(arm: str, seed: int) -> None:
    if json.loads((HERE / "audits/token_audit.json").read_text())["result"] != "PASS":
        raise SystemExit("token audit not PASS")
    result_path = HERE / "train" / f"{arm}_seed{seed}.json"
    if result_path.exists():
        print(result_path); return
    cell = ART / "train" / arm / f"seed_{seed}"
    adapter = cell / "adapter"
    log_path = HERE / "train" / f"{arm}_seed{seed}.log"
    telemetry_path = HERE / "train" / f"{arm}_seed{seed}_telemetry.jsonl"
    if adapter.exists() or log_path.exists() or telemetry_path.exists():
        raise SystemExit(f"partial training artifacts exist for {arm} seed {seed}")
    cell.mkdir(parents=True, exist_ok=True); result_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "caffeinate", "-dimsu", str(PYTHON), "-m", "mlx_lm", "lora", "--model", str(MODEL), "--train",
        "--data", str(ART / "prepared" / arm), "-c", str(RECIPE),
        "--batch-size", str(MICROBATCH_SIZE), "--grad-accumulation-steps", str(GRAD_ACCUMULATION_STEPS),
        "--iters", str(MICROSTEPS),
        "--learning-rate", "1e-4", "--max-seq-length", str(MAXSEQ), "--grad-checkpoint",
        "--steps-per-report", "200", "--steps-per-eval", "200000", "--val-batches", "1",
        "--adapter-path", str(adapter), "--save-every", "200", "--seed", str(seed),
    ]
    started = time.time(); swap_start = swap_mb()
    with log_path.open("x", encoding="utf-8") as log, telemetry_path.open("x", encoding="utf-8") as telemetry:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, text=True)
        while process.poll() is None:
            telemetry.write(canonical(memory_snapshot()) + "\n"); telemetry.flush()
            try:
                process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                pass
        returncode = process.returncode
        telemetry.write(canonical(memory_snapshot()) + "\n")
    text = log_path.read_text(errors="replace")
    losses = [float(x) for x in re.findall(r"Train loss ([0-9.]+)", text)]
    iterations = [int(x) for x in re.findall(r"Iter ([0-9]+): Train loss", text)]
    rates = [float(x) for x in re.findall(r"Tokens/sec ([0-9.]+)", text)]
    peaks = [float(x) for x in re.findall(r"Peak mem ([0-9.]+) GB", text)]
    trained = [int(x) for x in re.findall(r"Trained Tokens ([0-9]+)", text)]
    telemetry = [json.loads(line) for line in telemetry_path.read_text().splitlines()]
    passed = returncode == 0 and iterations and iterations[-1] == MICROSTEPS and len(losses) == 50 and (adapter / "adapters.safetensors").exists()
    result = {
        "result": "PASS" if passed else "FAIL", "arm": arm, "seed": seed,
        "protocol_commit": json.loads((HERE / "RUN_MANIFEST.json").read_text())["protocol_commit"],
        "model_revision": MODEL_REV, "recipe_sha256": sha(RECIPE),
        "dataset_manifest_sha256": sha(ART / "prepared" / arm / "dataset_manifest.json"),
        "microbatch_size": MICROBATCH_SIZE, "gradient_accumulation_steps": GRAD_ACCUMULATION_STEPS,
        "microsteps": MICROSTEPS, "optimizer_updates": OPTIMIZER_UPDATES,
        "first_loss": losses[0] if losses else None, "final_loss": losses[-1] if losses else None,
        "loss_checkpoints": losses, "iterations": iterations[-1] if iterations else None,
        "examples_seen": N_TRAIN, "reported_tokens_seen": trained[-1] if trained else None,
        "mean_tokens_per_second": statistics.fmean(rates) if rates else None,
        "peak_mlx_gb": max(peaks) if peaks else None, "swap_start_mb": swap_start, "swap_end_mb": swap_mb(),
        "minimum_free_gib": min(x["free_gib"] for x in telemetry),
        "maximum_compressed_gib": max(x["compressed_gib"] for x in telemetry),
        "wall_seconds": time.time() - started, "adapter_path": str(adapter),
        "adapter_sha256": sha(adapter / "adapters.safetensors") if (adapter / "adapters.safetensors").exists() else None,
        "returncode": returncode, "command": command,
    }
    write_json(result_path, result)
    if not passed:
        raise SystemExit(f"training failed: {log_path}")


def load_records(split: str) -> list[dict[str, Any]]:
    return list(read_gzip(ART / "records" / f"{split}.jsonl.gz"))


def score(arm: str, seed: int) -> None:
    for required_arm in ARMS:
        path = HERE / "train" / f"{required_arm}_seed{seed}.json"
        if not path.exists() or json.loads(path.read_text())["result"] != "PASS":
            raise SystemExit(f"all three adapters must be frozen before scoring; missing {path}")
    output = HERE / "raw" / f"{arm}_seed{seed}_predictions.jsonl"
    summary = HERE / "train" / f"{arm}_seed{seed}_score.json"
    if output.exists() and summary.exists():
        print(output); return
    train_result = json.loads((HERE / "train" / f"{arm}_seed{seed}.json").read_text())
    model, tokenizer = load(str(MODEL), adapter_path=train_result["adapter_path"]); model.eval()
    label_tokens = [tokenizer.encode(f"C{i}", add_special_tokens=False) for i in range(6)]
    if not all(len(x) == 2 for x in label_tokens) or len({x[0] for x in label_tokens}) != 1:
        raise AssertionError(label_tokens)
    shared = label_tokens[0][0]
    records = load_records("final_a")
    partial = output.with_suffix(".jsonl.partial")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or partial.exists():
        raise SystemExit(f"score output exists {output}")
    totals = collections.Counter(); prompt_lengths = []; started = time.time()
    with partial.open("x", encoding="utf-8") as handle:
        for record in records:
            projection = project(record, arm)
            chat = tokenizer.apply_chat_template(
                [{"role": "user", "content": projection["prompt"]}], add_generation_prompt=True,
                tokenize=False, enable_thinking=False,
            )
            prompt_ids = tokenizer.encode(chat)
            cache = make_prompt_cache(model)
            logits = model(mx.array([prompt_ids]), cache=cache)
            first = nn.log_softmax(logits[:, -1, :].astype(mx.float32), axis=-1)[0, shared]
            digits = model(mx.array([[shared]]), cache=cache)
            digit_lp = nn.log_softmax(digits[:, -1, :].astype(mx.float32), axis=-1)[0]
            sums = [float(first + digit_lp[item[1]]) for item in label_tokens]
            means = [value / 2 for value in sums]
            order = sorted(range(6), key=lambda x: (-means[x], x))
            gold = int(record["target"][1:])
            probs = np.exp(np.asarray(means) - max(means)); probs /= probs.sum()
            best_other = max(means[i] for i in range(6) if i != gold)
            item = {
                "record_id": record["record_id"], "parent_id": record["parent_id"],
                "answer_index": gold, "scores_sum": sums, "scores_mean": means,
                "candidate_probabilities": probs.tolist(), "pred_index": order[0],
                "rank": order.index(gold) + 1, "correct": order[0] == gold,
                "nll": -math.log(max(float(probs[gold]), 1e-12)),
                "entropy": -sum(float(p) * math.log(max(float(p), 1e-12)) for p in probs),
                "gold_margin": means[gold] - best_other,
                "prompt_tokens": len(prompt_ids), "prompt_sha256": digest_text(projection["prompt"]),
                "context_sha256": digest_text(projection["context"]),
                "candidate_sha256": [digest_text(x["tactic_text"]) for x in record["candidates"]],
                **record["metadata"],
            }
            handle.write(canonical(item) + "\n")
            totals["correct"] += item["correct"]; totals["mrr"] += 1/item["rank"]
            totals["nll"] += item["nll"]; totals["entropy"] += item["entropy"]; totals["margin"] += item["gold_margin"]
            prompt_lengths.append(len(prompt_ids))
            del cache, logits, digits
            mx.clear_cache()
    partial.rename(output)
    write_json(summary, {
        "arm": arm, "seed": seed, "n": len(records), "top1": totals["correct"]/len(records),
        "mrr": totals["mrr"]/len(records), "nll": totals["nll"]/len(records),
        "entropy": totals["entropy"]/len(records), "gold_margin": totals["margin"]/len(records),
        "prompt_tokens": stats(prompt_lengths), "wall_seconds": time.time()-started,
        "peak_mlx_gib": mx.get_peak_memory()/2**30, "adapter_sha256": train_result["adapter_sha256"],
        "raw_sha256": sha(output), "thinking_enabled": False,
    })


def load_scores(arm: str, seed: int) -> dict[str, dict[str, Any]]:
    path = HERE / "raw" / f"{arm}_seed{seed}_predictions.jsonl"
    return {row["record_id"]: row for row in (json.loads(line) for line in path.read_text().splitlines())}


def bootstrap(values: list[float], parents: list[str], offset: int) -> dict[str, Any]:
    groups: dict[str, list[int]] = collections.defaultdict(list)
    for index, parent in enumerate(parents):
        groups[parent].append(index)
    arrays = [np.asarray(groups[key], dtype=int) for key in sorted(groups)]
    data = np.asarray(values, dtype=float); rng = np.random.default_rng(BOOTSTRAP_SEED + offset)
    draws = np.empty(BOOTSTRAPS)
    for draw in range(BOOTSTRAPS):
        selected = rng.integers(0, len(arrays), len(arrays))
        indices = np.concatenate([arrays[x] for x in selected])
        draws[draw] = data[indices].mean()
    return {
        "value": float(data.mean()), "ci95": [float(x) for x in np.percentile(draws, (2.5, 97.5))],
        "p_gt_zero": float(np.mean(draws > 0)), "n": len(values), "parents": len(arrays),
    }


def metric_values(rows: dict[str, dict[str, Any]], ids: list[str], metric: str) -> list[float]:
    if metric == "top1":
        return [float(rows[x]["correct"]) for x in ids]
    if metric == "mrr":
        return [float(rows[x].get("mrr_value", 1/rows[x]["rank"])) for x in ids]
    return [float(rows[x][metric]) for x in ids]


def compare(ids: list[str], arms: dict[str, dict[str, dict[str, Any]]], first: str, second: str, offset: int) -> dict[str, Any]:
    parents = [arms[first][x]["parent_id"] for x in ids]
    result = {"n": len(ids), "parents": len(set(parents))}
    for index, metric in enumerate(("top1", "mrr", "nll", "entropy", "gold_margin")):
        a = metric_values(arms[first], ids, metric); b = metric_values(arms[second], ids, metric)
        result[metric] = {
            first: statistics.fmean(a), second: statistics.fmean(b),
            **bootstrap([x-y for x, y in zip(a, b)], parents, offset + index),
        }
    return result


def analyse(seeds: list[int]) -> dict[str, Any]:
    raw = {(arm, seed): load_scores(arm, seed) for arm in ARMS for seed in seeds}
    ids = sorted(set.intersection(*(set(value) for value in raw.values())))
    if len(ids) != N_FINAL:
        raise AssertionError(len(ids))
    per_seed = {}
    for sidx, seed in enumerate(seeds):
        arms = {arm: raw[(arm, seed)] for arm in ARMS}
        per_seed[str(seed)] = {
            "arms": {arm: {
                metric: bootstrap(metric_values(arms[arm], ids, metric), [arms[arm][x]["parent_id"] for x in ids], 1000*sidx + 100*i)
                for i, metric in enumerate(("top1", "mrr", "nll", "entropy", "gold_margin"))
            } for arm in ARMS},
            "contrasts": {
                "raw_minus_base": compare(ids, arms, "raw", "base", 1000*sidx + 10),
                "semantic_minus_base": compare(ids, arms, "semantic", "base", 1000*sidx + 20),
                "semantic_minus_raw": compare(ids, arms, "semantic", "raw", 1000*sidx + 30),
            },
        }
    combined = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for rid in ids:
            item = dict(raw[(arm, seeds[0])][rid])
            item["correct"] = statistics.fmean(float(raw[(arm, seed)][rid]["correct"]) for seed in seeds)
            item["rank"] = statistics.fmean(raw[(arm, seed)][rid]["rank"] for seed in seeds)
            item["mrr_value"] = statistics.fmean(1/raw[(arm, seed)][rid]["rank"] for seed in seeds)
            for metric in ("nll", "entropy", "gold_margin"):
                item[metric] = statistics.fmean(raw[(arm, seed)][rid][metric] for seed in seeds)
            item["scores_mean"] = [
                statistics.fmean(raw[(arm, seed)][rid]["scores_mean"][index] for seed in seeds)
                for index in range(6)
            ]
            item["pred_index"] = max(range(6), key=lambda index: (item["scores_mean"][index], -index))
            item["ensemble_correct"] = item["pred_index"] == item["answer_index"]
            combined[arm][rid] = item
    overall = {
        "arms": {arm: {
            metric: bootstrap(metric_values(combined[arm], ids, metric), [combined[arm][x]["parent_id"] for x in ids], 5000 + 100*i)
            for i, metric in enumerate(("top1", "mrr", "nll", "entropy", "gold_margin"))
        } for arm in ARMS},
        "contrasts": {
            "raw_minus_base": compare(ids, combined, "raw", "base", 5100),
            "semantic_minus_base": compare(ids, combined, "semantic", "base", 5200),
            "semantic_minus_raw": compare(ids, combined, "semantic", "raw", 5300),
        },
    }
    org = overall["contrasts"]["semantic_minus_raw"]["top1"]
    hist = overall["contrasts"]["raw_minus_base"]["top1"]
    sem_base = overall["contrasts"]["semantic_minus_base"]["top1"]
    seed1_org = per_seed["1"]["contrasts"]["semantic_minus_raw"]["top1"]
    seed2_authorized = seed1_org["value"] >= .02 and seed1_org["ci95"][0] > 0
    if org["value"] >= .05 and org["ci95"][0] > 0 and all(per_seed[str(seed)]["contrasts"]["semantic_minus_raw"]["top1"]["value"] > 0 for seed in seeds):
        verdict = "REASONING_LAYER_SIGNAL_FOUND"
    elif hist["value"] > 0 and hist["ci95"][0] > 0 and org["value"] < .02:
        verdict = "HISTORY_SIGNAL_ONLY" if org["value"] >= 0 else "V1_SEMANTIC_COMPRESSION_FAILED"
    elif org["value"] < 0:
        verdict = "V1_SEMANTIC_COMPRESSION_FAILED"
    elif hist["value"] < 0 and sem_base["value"] < 0 and hist["ci95"][1] < 0 and sem_base["ci95"][1] < 0:
        verdict = "ENRICHED_STATE_HURTS"
    else:
        verdict = "NO_REASONING_LAYER_SIGNAL"

    metadata = combined["base"]
    strata = {"depth": {}, "trajectory_position": {}, "open_goal_count": {}, "dependency_count": {}, "case_label_presence": {}, "module_presence": {}}
    selectors = {
        "depth": lambda row: row["depth_bin"],
        "trajectory_position": lambda row: count_bin(row["trajectory_position"]),
        "open_goal_count": lambda row: count_bin(row["open_goal_count"]),
        "dependency_count": lambda row: count_bin(row["dependency_edge_count"]),
        "case_label_presence": lambda row: str(bool(row["case_label_present"])).lower(),
    }
    for name, selector in selectors.items():
        buckets: dict[str, list[str]] = collections.defaultdict(list)
        for rid in ids:
            buckets[selector(metadata[rid])].append(rid)
        for index, (bucket, subset_ids) in enumerate(sorted(buckets.items())):
            strata[name][bucket] = {
                "semantic_minus_raw": compare(subset_ids, combined, "semantic", "raw", 6000 + index*20),
                "semantic_minus_base": compare(subset_ids, combined, "semantic", "base", 6010 + index*20),
            }
    for module in ("goals", "dependencies", "branch_scope", "history"):
        for present in (False, True):
            subset_ids = [rid for rid in ids if bool(metadata[rid]["module_presence"][module]) == present]
            if subset_ids:
                strata["module_presence"][f"{module}:{str(present).lower()}"] = {
                    "semantic_minus_raw": compare(subset_ids, combined, "semantic", "raw", 7000 + len(strata["module_presence"])*20),
                    "semantic_minus_base": compare(subset_ids, combined, "semantic", "base", 7010 + len(strata["module_presence"])*20),
                }

    patterns = collections.Counter(); diagnostic_rows = []
    for rid in ids:
        correct = {arm: combined[arm][rid]["ensemble_correct"] for arm in ARMS}
        key = (correct["base"], correct["raw"], correct["semantic"])
        names = {
            (True, True, True): "ALL_CORRECT", (False, False, False): "ALL_WRONG",
            (False, False, True): "SEMANTIC_ONLY", (False, True, False): "RAW_ONLY",
            (True, False, False): "BASE_ONLY", (False, True, True): "SEMANTIC_RAW_CORRECT_BASE_WRONG",
            (True, False, True): "BASE_SEMANTIC_CORRECT_RAW_WRONG", (True, True, False): "BASE_RAW_CORRECT_SEMANTIC_WRONG",
        }
        pattern = names[key]; patterns[pattern] += 1
        base_row = combined["base"][rid]
        diagnostic_rows.append({
            "record_id": rid, "theorem_parent": base_row["parent_id"], "depth": base_row["depth"],
            "trajectory_position": base_row["trajectory_position"],
            "token_counts": {arm: combined[arm][rid]["prompt_tokens"] for arm in ARMS},
            "module_presence": base_row["module_presence"], "dependency_edge_count": base_row["dependency_edge_count"],
            "open_goal_count": base_row["open_goal_count"], "history_length": base_row["history_length"],
            "case_label_present": base_row["case_label_present"], "gold_candidate": f"C{base_row['answer_index']}",
            "arms": {arm: {"scores": combined[arm][rid]["scores_mean"], "prediction": f"C{combined[arm][rid]['pred_index']}", "correct": correct[arm]} for arm in ARMS},
            "pattern": pattern,
        })
    write_jsonl(HERE / "diagnostics/final_a_rows.jsonl", diagnostic_rows)
    write_json(HERE / "diagnostics/pattern_summary.json", dict(patterns))
    write_json(HERE / "diagnostics/module_strata.json", strata)

    result = {
        "verdict": verdict, "seeds": seeds, "per_seed": per_seed, "overall": overall,
        "seed2": "AUTHORIZED" if seed2_authorized and seeds == [1] else "RUN" if len(seeds) == 2 else "NOT_AUTHORIZED",
        "seed2_gate": {"rule": "seed1 semantic-raw >=2pp and CI lower >0", "seed1": seed1_org},
        "patterns": dict(patterns), "final_b": "SEALED_NOT_OPENED",
    }
    write_json(HERE / "diagnostics" / ("analysis_seed1.json" if seeds == [1] else "final_analysis.json"), result)
    if len(seeds) == 2:
        write_json(HERE / "diagnostics/final_analysis.json", result)
    return result


def failure_analysis(analysis: dict[str, Any]) -> None:
    if analysis["verdict"] == "REASONING_LAYER_SIGNAL_FOUND":
        return
    records = {x["record_id"]: x for x in load_records("final_a")}
    rows = [json.loads(line) for line in (HERE / "diagnostics/final_a_rows.jsonl").read_text().splitlines()]
    raw_only = [row for row in rows if row["pattern"] in {"RAW_ONLY", "BASE_RAW_CORRECT_SEMANTIC_WRONG"}]
    semantic_only = [row for row in rows if row["pattern"] in {"SEMANTIC_ONLY", "BASE_SEMANTIC_CORRECT_RAW_WRONG"}]

    def losses(row: dict[str, Any]) -> dict[str, Any]:
        record = records[row["record_id"]]
        history = record["history"]
        exact_families = [tactic_family(x["action"]) for x in history]
        return {
            "history_events": len(history),
            "exact_prior_targets_omitted": sum(bool(parse_lean_state(x["state_after"])["goals"]) for x in history),
            "exact_prior_hypotheses_omitted": sum(sum(len(g["hypotheses"]) for g in parse_lean_state(x["state_after"])["goals"]) for x in history),
            "exact_tactic_arguments_omitted": sum(x["action"].strip() != family for x, family in zip(history, exact_families)),
            "prior_intermediate_proposition_content_omitted": bool(history),
            "exact_prior_state_content_omitted": bool(history),
            "tactic_retained_as_family_only": bool(history),
            "branch_ancestry_available_in_raw": any("case " in x["state_before"] or "case " in x["state_after"] for x in history),
            "window_saturated": len(history) == HISTORY_WINDOW,
        }

    inventories = {row["record_id"]: losses(row) for row in rows}
    keys = next(iter(inventories.values())).keys()
    def aggregate(subset: list[dict[str, Any]]) -> dict[str, Any]:
        return {key: statistics.fmean(float(inventories[x["record_id"]][key]) for x in subset) if subset else None for key in keys}
    info = {
        "raw_only_rows": len(raw_only), "semantic_only_rows": len(semantic_only),
        "raw_only_loss_profile": aggregate(raw_only), "semantic_only_loss_profile": aggregate(semantic_only),
        "all_rows_loss_profile": aggregate(rows),
        "interpretation": "RAW_HISTORY exposes exact prior states, targets, hypotheses and tactic arguments; V1 retains goal/dependency structure for the current state plus tactic families and coarse deltas only.",
    }
    write_json(HERE / "diagnostics/information_loss.json", info)
    org = analysis["overall"]["contrasts"]["semantic_minus_raw"]["top1"]
    hist = analysis["overall"]["contrasts"]["raw_minus_base"]["top1"]
    v2 = hist["value"] > 0 and org["value"] < 0 and len(raw_only) > len(semantic_only)
    content = f"""# V1 failure analysis

Final verdict: `{analysis['verdict']}`. RAW−BASE Top-1 is {100*hist['value']:+.2f}pp with 95% CI [{100*hist['ci95'][0]:+.2f}, {100*hist['ci95'][1]:+.2f}]pp. SEMANTIC−RAW is {100*org['value']:+.2f}pp with 95% CI [{100*org['ci95'][0]:+.2f}, {100*org['ci95'][1]:+.2f}]pp.

## Causal answers

1. RAW_HISTORY beat BASE: **{'yes' if hist['value'] > 0 else 'no'}**; credible CI: **{'yes' if hist['ci95'][0] > 0 else 'no'}**.
2. V1 lost performance relative to RAW: **{'yes' if org['value'] < 0 else 'no'}**.
3. RAW-only patterns: {len(raw_only)}; semantic-only patterns: {len(semantic_only)}.
4. Dependency, branch, goal, history and depth associations are recorded in `module_strata.json`; they are observational strata, not module ablations.
5. Exact previous tactic arguments, targets, hypotheses and intermediate state content are available to RAW but intentionally compressed away by V1.
6. Failed-route memory, goal genealogy, strategy/lemma role and full branch ancestry remain missing-evidence candidates only; passive traces do not establish them.

## Dominant information-loss mechanism

V1 reduces exact prior tactic text to tactic family and exact prior states/propositions to coarse deltas. RAW-only loss profile: `{json.dumps(info['raw_only_loss_profile'], sort_keys=True)}`.

## V2 decision

Evidence threshold for proposing one V2 is **{'met' if v2 else 'not met'}**. This file does not alter V1 and FINAL_B remains sealed. A V2, if separately authorized, must cite these FINAL_A row counts and preserve only the specific exact-history content associated with RAW-only wins.
"""
    (HERE / "diagnostics/v1_failure_analysis.md").write_text(content, encoding="utf-8")


def finalize(seeds: list[int]) -> None:
    analysis_path = HERE / "diagnostics" / ("analysis_seed1.json" if seeds == [1] else "final_analysis.json")
    analysis = json.loads(analysis_path.read_text())
    failure_analysis(analysis)
    adapter_root = HERE / "adapters"
    adapter_root.mkdir(exist_ok=True)
    for seed in seeds:
        for arm in ARMS:
            train_result = json.loads((HERE / "train" / f"{arm}_seed{seed}.json").read_text())
            destination = adapter_root / f"{arm}_seed{seed}"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(train_result["adapter_path"], destination, ignore=shutil.ignore_patterns("000*_adapters.safetensors"))
    token = json.loads((HERE / "audits/token_audit.json").read_text())
    overall = analysis["overall"]; org = overall["contrasts"]["semantic_minus_raw"]["top1"]
    depth = json.loads((HERE / "diagnostics/module_strata.json").read_text())["depth"]
    depth_lines = "\n".join(f"| {key} | {100*depth[key]['semantic_minus_raw']['top1']['value']:+.2f}pp |" for key in DEPTH_ORDER if key in depth)
    report = f"""# Reasoning-layer V1 FINAL_A report

## Final verdict

**`{analysis['verdict']}`** on {len(seeds)} seed(s). FINAL_B remains sealed and unopened.

| arm | Top-1 | 95% clustered CI | MRR | NLL | entropy | gold margin |
|---|---:|---:|---:|---:|---:|---:|
"""
    for arm in ARMS:
        metrics = overall["arms"][arm]
        report += f"| {arm.upper()} | {100*metrics['top1']['value']:.2f}% | [{100*metrics['top1']['ci95'][0]:.2f}, {100*metrics['top1']['ci95'][1]:.2f}]% | {metrics['mrr']['value']:.4f} | {metrics['nll']['value']:.4f} | {metrics['entropy']['value']:.4f} | {metrics['gold_margin']['value']:.4f} |\n"
    report += "\n## Primary contrasts\n\n"
    for name in ("raw_minus_base", "semantic_minus_base", "semantic_minus_raw"):
        value = overall["contrasts"][name]["top1"]
        report += f"- {name}: {100*value['value']:+.2f}pp, 95% CI [{100*value['ci95'][0]:+.2f}, {100*value['ci95'][1]:+.2f}]pp.\n"
    report += f"""

## Token economics

- BASE mean/median/p95/max: {token['arms']['base']['chat_prompt_tokens']['mean']:.1f} / {token['arms']['base']['chat_prompt_tokens']['median']:.1f} / {token['arms']['base']['chat_prompt_tokens']['p95']:.1f} / {token['arms']['base']['chat_prompt_tokens']['max']:.0f}.
- RAW mean/median/p95/max: {token['arms']['raw']['chat_prompt_tokens']['mean']:.1f} / {token['arms']['raw']['chat_prompt_tokens']['median']:.1f} / {token['arms']['raw']['chat_prompt_tokens']['p95']:.1f} / {token['arms']['raw']['chat_prompt_tokens']['max']:.0f}.
- SEMANTIC mean/median/p95/max: {token['arms']['semantic']['chat_prompt_tokens']['mean']:.1f} / {token['arms']['semantic']['chat_prompt_tokens']['median']:.1f} / {token['arms']['semantic']['chat_prompt_tokens']['p95']:.1f} / {token['arms']['semantic']['chat_prompt_tokens']['max']:.0f}.
- Ratios RAW/BASE {token['ratios']['raw_over_base']:.3f}×, SEMANTIC/BASE {token['ratios']['semantic_over_base']:.3f}×, SEMANTIC/RAW {token['ratios']['semantic_over_raw']:.3f}×. Zero truncation.

## SEMANTIC−RAW by depth

| depth | Top-1 delta |
|---|---:|
{depth_lines}

## Decision boundary

Organization gain is {100*org['value']:+.2f}pp with CI [{100*org['ci95'][0]:+.2f}, {100*org['ci95'][1]:+.2f}]pp. Seed 2 status: `{analysis['seed2']}`. Module-presence and information-loss diagnostics are machine-readable under `diagnostics/`; no module was retrained and V1 was not edited.
"""
    (HERE / "FINAL_A_REPORT.md").write_text(report, encoding="utf-8")
    manifest = json.loads((HERE / "RUN_MANIFEST.json").read_text())
    manifest["results"] = {
        "verdict": analysis["verdict"], "seeds": seeds,
        "analysis_sha256": sha(analysis_path), "report_sha256": sha(HERE / "FINAL_A_REPORT.md"),
        "prediction_files": {f"{arm}_seed{seed}": sha(HERE / "raw" / f"{arm}_seed{seed}_predictions.jsonl") for seed in seeds for arm in ARMS},
        "adapters": {str(path.relative_to(HERE)): sha(path) for path in sorted(adapter_root.glob("*/*")) if path.is_file()},
        "final_b": "SEALED_NOT_OPENED",
    }
    write_json(HERE / "RUN_MANIFEST.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    train_parser = sub.add_parser("train"); train_parser.add_argument("--arm", choices=ARMS, required=True); train_parser.add_argument("--seed", type=int, required=True)
    score_parser = sub.add_parser("score"); score_parser.add_argument("--arm", choices=ARMS, required=True); score_parser.add_argument("--seed", type=int, required=True)
    analyse_parser = sub.add_parser("analyse"); analyse_parser.add_argument("--seeds", type=int, nargs="+", required=True)
    finalize_parser = sub.add_parser("finalize"); finalize_parser.add_argument("--seeds", type=int, nargs="+", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        audit_and_prepare()
    elif args.command == "train":
        train(args.arm, args.seed)
    elif args.command == "score":
        score(args.arm, args.seed)
    elif args.command == "analyse":
        print(canonical(analyse(args.seeds)))
    elif args.command == "finalize":
        finalize(args.seeds)


if __name__ == "__main__":
    main()
