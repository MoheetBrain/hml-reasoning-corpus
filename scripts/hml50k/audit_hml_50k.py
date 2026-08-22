#!/usr/bin/env python3
"""Independent full-corpus audits for HML50K_TEACHING.

Run with the experiment virtual environment so the pinned Qwen tokenizer is available:

  PYTHONPATH=/tmp/hml-vnext-68178f0/src \
    /Users/moheet/hml-model-experiments/.venv/bin/python \
    scripts/hml50k/audit_hml_50k.py
"""

from __future__ import annotations

import argparse
import collections
import copy
import gzip
import hashlib
import json
import re
import statistics
import subprocess
from pathlib import Path

import pyarrow.parquet as pq
from transformers import AutoTokenizer

from hamiltonian_lang.semantic_state import export_state, parse_state


VIEWS = ("HML_WORKED_UTF8", "STRUCTURED_NEUTRAL_WORKED")
TASKS = ("NEXT_ACTION_SELECT", "STATE_DELTA_PREDICT", "VALIDITY_JUDGE", "WORKED_CONTINUATION")
SPLITS = ("train", "dev", "final")
MAX_SEQUENCE = 6_144
TOKENIZER_COMMIT = "b968826d9c46dd6066d109eabc6255188de91218"
TOKENIZER_PATH = Path(
    "/Users/moheet/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/"
    + TOKENIZER_COMMIT
)


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def q(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * (len(ordered) - 1)))]


def load_canonical(root: Path) -> tuple[dict[str, dict], dict]:
    records: dict[str, dict] = {}
    parents = collections.defaultdict(set)
    signatures = collections.defaultdict(set)
    duplicate_ids = 0
    duplicate_signatures = 0
    for row in rows(root / "canonical" / "records.jsonl.gz"):
        if row["record_id"] in records:
            duplicate_ids += 1
        records[row["record_id"]] = row
        parents[row["split"]].add(row["parent_id"])
        neutral = row["neutral_transition"]
        before = neutral["state_before"]["claims"]["p0"]["proposition"]
        after = neutral["state_after"]["claims"]["c1"]["proposition"]
        candidates = row["candidate_audit"]["candidates"]
        gold = row["candidate_audit"]["gold_candidate_id"]
        tactic = next(x["tactic_text"] for x in candidates if x["candidate_id"] == gold)
        signature = digest_text("\0".join(map(normalise, (before, tactic, after))))
        if any(signature in values for split, values in signatures.items() if split != row["split"]):
            duplicate_signatures += 1
        signatures[row["split"]].add(signature)
    overlaps = {
        "train_dev": len(parents["train"] & parents["dev"]),
        "train_final": len(parents["train"] & parents["final"]),
        "dev_final": len(parents["dev"] & parents["final"]),
    }
    signature_overlaps = {
        "train_dev": len(signatures["train"] & signatures["dev"]),
        "train_final": len(signatures["train"] & signatures["final"]),
        "dev_final": len(signatures["dev"] & signatures["final"]),
    }
    audit = {
        "result": "PASS" if not duplicate_ids and not duplicate_signatures and not any(overlaps.values()) else "FAIL",
        "records": len(records),
        "record_id_duplicates": duplicate_ids,
        "near_duplicate_signature_duplicates_seen_during_stream": duplicate_signatures,
        "parent_overlap": overlaps,
        "near_duplicate_signature_overlap": signature_overlaps,
        "signature": "sha256(whitespace-collapsed state_before + tactic + state_after)",
    }
    return records, audit


def parity_audit(root: Path, canonical_records: dict[str, dict]) -> dict:
    counts = {}
    full_state_parity = 0
    candidate_order_parity = 0
    action_parity = 0
    errors = []
    for task in TASKS:
        for split in SPLITS:
            hp = root / "tasks" / task / VIEWS[0] / f"{split}.jsonl.gz"
            np = root / "tasks" / task / VIEWS[1] / f"{split}.jsonl.gz"
            count = 0
            hi, ni = rows(hp), rows(np)
            while True:
                try:
                    h = next(hi)
                except StopIteration:
                    h = None
                try:
                    n = next(ni)
                except StopIteration:
                    n = None
                if h is None or n is None:
                    if h is not None or n is not None:
                        errors.append(f"length mismatch {task}/{split}")
                    break
                count += 1
                if (h["record_id"], h["parent_id"], h["split"], h["task"]) != (
                    n["record_id"], n["parent_id"], n["split"], n["task"]
                ):
                    errors.append(f"identity mismatch {task}/{split}/{count}")
                    continue
                source_id = h.get("source_record_id", h["record_id"])
                base = canonical_records[source_id]
                expected_sha = base["canonical_transition_sha256"]
                if h["audit_metadata"]["canonical_transition_sha256"] != expected_sha or n["audit_metadata"]["canonical_transition_sha256"] != expected_sha:
                    errors.append(f"canonical hash mismatch {h['record_id']}")
                if task in {"NEXT_ACTION_SELECT", "VALIDITY_JUDGE"} and h["target_text"] != n["target_text"]:
                    errors.append(f"label mismatch {h['record_id']}")
                if task == "NEXT_ACTION_SELECT":
                    candidates = [
                        {"candidate_id": x["candidate_id"], "tactic_text": x["tactic_text"]}
                        for x in base["candidate_audit"]["candidates"]
                    ]
                    neutral_input = json.loads(n["input_text"])
                    expected_block = "\n".join(f"{x['candidate_id']} :: {x['tactic_text']}" for x in candidates)
                    if neutral_input["candidates"] != candidates or expected_block not in h["input_text"]:
                        errors.append(f"candidate ordering mismatch {h['record_id']}")
                    else:
                        candidate_order_parity += 1
                    hml_state = h["input_text"].split("\n\n", 1)[1].split(
                        "\nChoose the single most useful next tactic", 1
                    )[0] + "\n"
                    if export_state(parse_state(hml_state)) != neutral_input["state_before"]:
                        errors.append(f"select-state parity mismatch {h['record_id']}")
                    else:
                        full_state_parity += 1
                elif task == "STATE_DELTA_PREDICT":
                    hml_state, h_action = h["input_text"].rsplit("\nACTION ", 1)
                    neutral_input = json.loads(n["input_text"])
                    if export_state(parse_state(hml_state + "\n")) != neutral_input["state_before"]:
                        errors.append(f"delta-before parity mismatch {h['record_id']}")
                    if json.loads(h_action) != neutral_input["action"]:
                        errors.append(f"delta-action parity mismatch {h['record_id']}")
                    else:
                        action_parity += 1
                    if export_state(parse_state(h["target_text"])) != json.loads(n["target_text"]):
                        errors.append(f"delta-target parity mismatch {h['record_id']}")
                    else:
                        full_state_parity += 1
                elif task == "WORKED_CONTINUATION":
                    hml_state, h_action = h["input_text"].rsplit("\nTRAJECTORY_ACTION ", 1)
                    neutral_input = json.loads(n["input_text"])
                    if export_state(parse_state(hml_state + "\n")) != neutral_input["state_before"]:
                        errors.append(f"continuation-before parity mismatch {h['record_id']}")
                    if json.loads(h_action) != neutral_input["trajectory_action"]:
                        errors.append(f"continuation-action parity mismatch {h['record_id']}")
                    else:
                        action_parity += 1
                elif task == "VALIDITY_JUDGE":
                    hml_state, h_action = h["input_text"].rsplit("\nPROPOSED_ACTION ", 1)
                    neutral_input = json.loads(n["input_text"])
                    if export_state(parse_state(hml_state + "\n")) != neutral_input["state_before"]:
                        errors.append(f"judge-state parity mismatch {h['record_id']}")
                    if json.loads(h_action) != neutral_input["proposed_action"]:
                        errors.append(f"judge-action parity mismatch {h['record_id']}")
                    else:
                        action_parity += 1
            counts[f"{task}/{split}"] = count
    return {
        "result": "PASS" if not errors else "FAIL",
        "paired_counts": counts,
        "full_state_semantic_parity_checks": full_state_parity,
        "candidate_order_checks": candidate_order_parity,
        "action_envelope_checks": action_parity,
        "errors": errors[:100],
    }


def token_and_unicode_audit(root: Path, tokenizer) -> tuple[dict, dict, dict[str, dict[str, int]]]:
    token_files = {}
    unicode_files = {}
    primary_train_tokens: dict[str, dict[str, int]] = {view: {} for view in VIEWS}
    json_escape = re.compile(r"(?<!\\)\\u[0-9a-fA-F]{4}")
    for task in TASKS:
        for view in VIEWS:
            for split in SPLITS:
                path = root / "tasks" / task / view / f"{split}.jsonl.gz"
                input_lengths: list[int] = []
                target_lengths: list[int] = []
                combined_lengths: list[int] = []
                escape_count = 0
                non_ascii = 0
                stream = gzip.open(path, "rt", encoding="utf-8")
                batch_rows = []
                batch_raw = []

                def consume(batch_rows, batch_raw):
                    nonlocal escape_count, non_ascii
                    if not batch_rows:
                        return
                    input_ids = tokenizer(
                        [x["input_text"] for x in batch_rows], add_special_tokens=False,
                        padding=False, truncation=False,
                    )["input_ids"]
                    target_ids = tokenizer(
                        [x["target_text"] for x in batch_rows], add_special_tokens=False,
                        padding=False, truncation=False,
                    )["input_ids"]
                    for row, raw, inp, target in zip(batch_rows, batch_raw, input_ids, target_ids):
                        il, tl = len(inp), len(target)
                        input_lengths.append(il)
                        target_lengths.append(tl)
                        combined_lengths.append(il + tl)
                        escape_count += len(json_escape.findall(raw))
                        non_ascii += sum(ord(ch) > 127 for ch in row["input_text"] + row["target_text"])
                        if task == "NEXT_ACTION_SELECT" and split == "train":
                            primary_train_tokens[view][row["record_id"]] = il + tl

                for raw in stream:
                    batch_raw.append(raw)
                    batch_rows.append(json.loads(raw))
                    if len(batch_rows) == 256:
                        consume(batch_rows, batch_raw)
                        batch_rows, batch_raw = [], []
                consume(batch_rows, batch_raw)
                stream.close()
                key = f"tasks/{task}/{view}/{split}.jsonl.gz"
                token_files[key] = {
                    "rows": len(combined_lengths),
                    "input_mean": round(statistics.fmean(input_lengths), 3),
                    "input_p50": q(input_lengths, 0.50),
                    "input_p95": q(input_lengths, 0.95),
                    "input_p99": q(input_lengths, 0.99),
                    "input_max": max(input_lengths),
                    "target_mean": round(statistics.fmean(target_lengths), 3),
                    "target_p95": q(target_lengths, 0.95),
                    "target_max": max(target_lengths),
                    "combined_max": max(combined_lengths),
                    "over_6144": sum(x > MAX_SEQUENCE for x in combined_lengths),
                    "over_8192": sum(x > 8_192 for x in combined_lengths),
                }
                unicode_files[key] = {
                    "json_unicode_escape_sequences": escape_count,
                    "literal_non_ascii_codepoints": non_ascii,
                }
    token_result = "PASS" if all(v["over_6144"] == 0 for v in token_files.values()) else "FAIL"
    unicode_result = "PASS" if all(v["json_unicode_escape_sequences"] == 0 for v in unicode_files.values()) else "FAIL"
    return (
        {
            "result": token_result,
            "tokenizer": "Qwen/Qwen3-8B",
            "tokenizer_commit": TOKENIZER_COMMIT,
            "local_files_only": True,
            "max_sequence_gate": MAX_SEQUENCE,
            "recommended_max_sequence": {
                "NEXT_ACTION_SELECT": 6144,
                "STATE_DELTA_PREDICT": 8192,
                "WORKED_CONTINUATION": 8192,
                "reason": "raw input+target maxima for delta/continuation are close to 6144; reserve room for chat/BOS/EOS template tokens",
            },
            "files": token_files,
        },
        {
            "result": unicode_result,
            "ensure_ascii_required": False,
            "files": unicode_files,
        },
        primary_train_tokens,
    )


def trajectory_audit(canonical_records: dict[str, dict]) -> dict:
    by_parent = collections.defaultdict(list)
    predecessor_errors = successor_errors = 0
    for row in canonical_records.values():
        by_parent[row["parent_id"]].append(row)
    complete = 0
    depth_counts = collections.Counter()
    long_rows = 0
    for values in by_parent.values():
        values.sort(key=lambda x: x["trajectory_step_index"])
        indices = [x["trajectory_step_index"] for x in values]
        proof_length = values[0]["proof_length"]
        complete += int(indices == list(range(proof_length)))
        for index, row in enumerate(values):
            expected_previous = values[index - 1]["record_id"] if index and indices[index - 1] + 1 == indices[index] else None
            expected_next = values[index + 1]["record_id"] if index + 1 < len(values) and indices[index] + 1 == indices[index + 1] else None
            predecessor_errors += int(row["predecessor_record_id"] != expected_previous)
            successor_errors += int(row["successor_record_id"] != expected_next)
            depth_counts[row["depth_bin"]] += 1
            long_rows += int(row["depth"] >= 11)
    return {
        "result": "PASS" if predecessor_errors == 0 and successor_errors == 0 else "FAIL",
        "parents": len(by_parent),
        "complete_trajectories": complete,
        "partial_trajectories": len(by_parent) - complete,
        "predecessor_link_errors": predecessor_errors,
        "successor_link_errors": successor_errors,
        "depth_counts": dict(sorted(depth_counts.items())),
        "rows_at_depth_11_plus": long_rows,
    }


def mutation_audit(canonical_records: dict[str, dict]) -> dict:
    rich = {
        "state": {
            "claims": {"h0": {"proposition": "x > 0", "scope": "s0", "dependencies": []}},
            "goals": {"g0": {"proposition": "x² ≥ 0", "scope": "s0", "status": "OPEN"}},
            "branches": {"b0": {"scope": "s0", "parent_id": None}},
            "obligations": {"o0": {"proposition": "x ≠ 0", "dependencies": ["h0"]}},
            "active_scopes": ["global", "s0"],
        },
        "action": {"operation": "TRANSFORM", "dependencies": ["h0"]},
    }
    mutations = {
        "hypothesis": ("state", "claims", "h0", "proposition"),
        "goal": ("state", "goals", "g0", "proposition"),
        "action": ("action", "operation"),
        "scope": ("state", "active_scopes"),
        "branch": ("state", "branches", "b0", "parent_id"),
        "obligation": ("state", "obligations", "o0", "proposition"),
        "dependency": ("action", "dependencies"),
    }
    detected = {}
    base_hash = digest_text(canonical(rich))
    for name, path in mutations.items():
        changed = copy.deepcopy(rich)
        ref = changed
        for key in path[:-1]:
            ref = ref[key]
        key = path[-1]
        if name in {"scope", "dependency"}:
            ref[key] = [*ref[key], "MUTATED"]
        else:
            ref[key] = "MUTATED"
        detected[name] = digest_text(canonical(changed)) != base_hash

    sample = next(iter(canonical_records.values()))
    actual = sample["neutral_transition"]
    actual_mutations = {}
    for name, mutate in {
        "corpus_claim": lambda x: x["state_before"]["claims"]["p0"].update(proposition="MUTATED"),
        "corpus_action": lambda x: x["action"].update(operation="MUTATED"),
        "corpus_dependency": lambda x: x["action"].update(dependencies=[]),
    }.items():
        changed = copy.deepcopy(actual)
        mutate(changed)
        actual_mutations[name] = canonical(changed) != canonical(actual)
    all_detected = all(detected.values()) and all(actual_mutations.values())
    return {
        "result": "PASS" if all_detected else "FAIL",
        "synthetic_cross_boundary_mutations_detected": detected,
        "actual_corpus_mutations_detected": actual_mutations,
        "comparison": "canonical semantic-object equality/hash; any changed field rejects parity",
    }


def old_parent_ids(repo: Path) -> set[str]:
    output = set()
    with gzip.open(repo / "data/vnext_10k/full_audit_records.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("source_family") == "LEAN_DOJO":
                output.add(row["parent_id"])
    return output


def final_contamination_audit(repo: Path, canonical_records: dict[str, dict]) -> dict:
    old = old_parent_ids(repo)
    by_split = collections.defaultdict(set)
    source_ids = collections.defaultdict(set)
    for row in canonical_records.values():
        by_split[row["split"]].add(row["parent_id"])
        source_ids[row["split"]].add(row["canonical_source_example_id"])
    metrics = {
        "final_parents_in_old_vnext_or_autopsy": len(by_split["final"] & old),
        "final_parents_in_train": len(by_split["final"] & by_split["train"]),
        "final_parents_in_dev": len(by_split["final"] & by_split["dev"]),
        "final_source_ids_in_train": len(source_ids["final"] & source_ids["train"]),
        "final_source_ids_in_dev": len(source_ids["final"] & source_ids["dev"]),
    }
    return {
        "result": "PASS" if not any(metrics.values()) else "FAIL",
        "old_vnext_parent_universe": len(old),
        "final_records": len(source_ids["final"]),
        "final_parents": len(by_split["final"]),
        "metrics": metrics,
        "final_source_split": "LeanDojo official test",
    }


def source_inventory(repo: Path) -> dict:
    artifact = Path("/Users/moheet/hml_research_artifacts")
    hf = artifact / "hf_sources"
    def parquet_count(pattern: str) -> int:
        return sum(pq.ParquetFile(path).metadata.num_rows for path in sorted(Path().glob(pattern)))

    # Path.glob cannot expand an absolute pattern, so use rglob per source below.
    stp = sum(pq.ParquetFile(p).metadata.num_rows for p in (hf / "STP_Lean_0320/data").glob("*.parquet"))
    numina = pq.ParquetFile(hf / "NuminaMath-LEAN/data/train-00000-of-00001.parquet").metadata.num_rows
    herald = pq.ParquetFile(hf / "Herald_proofs/data/train-00000-of-00001.parquet").metadata.num_rows
    state_tactic = pq.ParquetFile(hf / "state_tactic_pairs/data/train-00000-of-00001.parquet").metadata.num_rows
    math_rows = pq.ParquetFile(repo / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet").metadata.num_rows
    amps_rows = pq.ParquetFile(repo / "data/raw/amps_khan/0000.parquet").metadata.num_rows
    prm = {}
    for p in sorted((artifact / "prm800k_raw/prm800k/data").glob("*.jsonl")):
        with p.open() as stream:
            prm[p.name] = sum(1 for _ in stream)
    items = [
        {
            "source": "LeanDojo canonical exact transitions",
            "path": str(artifact / "lean_domino_v2/lean_canonical_records.jsonl"),
            "examples": 241_265,
            "status": "FORMAL_TRACE",
            "selected": 56_000,
            "decision": "selected: exact state/action/state-after, current HML-representable, strongest task-native source",
        },
        {
            "source": "LeanDojo raw benchmark",
            "path": str(artifact / "leandojo_raw/leandojo_benchmark_4/random"),
            "examples": 259_580,
            "status": "FORMAL_TRACE",
            "selected": 0,
            "decision": "used only to recover premise annotations and verify exact canonical trace identity",
        },
        {"source": "STP_Lean_0320", "path": str(hf / "STP_Lean_0320"), "examples": stp,
         "status": "FORMAL_PROOF_TEXT_MIXED_WITH_CONJECTURING", "selected": 0,
         "decision": "not state/action/state-after; 51,273 conjecturing rows require separate policy"},
        {"source": "NuminaMath-LEAN", "path": str(hf / "NuminaMath-LEAN"), "examples": numina,
         "status": "FORMAL_PROOF_TEXT", "selected": 0, "decision": "proof text, not exact traced next-state transitions"},
        {"source": "Herald proofs", "path": str(hf / "Herald_proofs"), "examples": herald,
         "status": "FORMAL_PROOF_TEXT_WITH_NATURAL_ANNOTATION", "selected": 0,
         "decision": "not exact traced next-state transitions"},
        {"source": "state_tactic_pairs", "path": str(hf / "state_tactic_pairs"), "examples": state_tactic,
         "status": "STATE_ACTION_ONLY", "selected": 0, "decision": "missing state_after; ineligible for delta/continuation core"},
        {"source": "Pythagoras SFT", "path": str(hf / "Pythagoras_SFT"), "examples": 126_113,
         "status": "SFT_PROOF_TEXT", "selected": 0, "decision": "not exact traced next-state transitions"},
        {"source": "PRM800K", "path": str(artifact / "prm800k_raw/prm800k/data"), "examples": sum(prm.values()),
         "status": "HUMAN_PROCESS_LABEL", "selected": 0,
         "decision": "valuable separate status class, but not mixed into formal-trace core merely for source quotas", "files": prm},
        {"source": "Hendrycks MATH", "path": str(repo / "data/raw/math"), "examples": math_rows,
         "status": "WORKED_SOLUTION_UNVERIFIED_HERE", "selected": 0,
         "decision": "solution segmentation would not preserve exact transition semantics without a new audit"},
        {"source": "AMPS/Khan", "path": str(repo / "data/raw/amps_khan"), "examples": amps_rows,
         "status": "PROCEDURAL_TEXT_UNVERIFIED_HERE", "selected": 0,
         "decision": "not promoted solely to fill a preferred source mix"},
    ]
    return {
        "result": "COMPLETE_LOCAL_INVENTORY",
        "inventory_date": "2026-08-22",
        "sources": items,
        "available_examples_sum_non_deduplicated": sum(x["examples"] for x in items),
        "core_selection_rationale": "quality over source proportions: exact formal transitions already exceed the 50k TRAIN gate",
    }


def rung_budget(root: Path, token_maps: dict[str, dict[str, int]]) -> dict:
    budgets = {}
    for size in (10_000, 30_000, 50_000):
        ids = json.loads((root / "rungs" / f"{size // 1000}k" / "record_ids.json").read_text())
        for view in VIEWS:
            one_epoch_tokens = sum(token_maps[view][rid] for rid in ids)
            reference_prompt_tokens = 209.6 if view == "HML_WORKED_UTF8" else 244.7
            prompt_length_scale = (one_epoch_tokens / size) / reference_prompt_tokens
            key = f"{size // 1000}k/{view}"
            budgets[key] = {
                "examples": size,
                "one_epoch_input_plus_target_tokens": one_epoch_tokens,
                "epochs": {
                    "0.5": {"iterations_batch2": (size + 3) // 4, "tokens": one_epoch_tokens // 2},
                    "1.0": {"iterations_batch2": (size + 1) // 2, "tokens": one_epoch_tokens},
                    "2.0": {"iterations_batch2": size, "tokens": 2 * one_epoch_tokens},
                },
                "mean_input_plus_target_tokens": round(one_epoch_tokens / size, 3),
                "prompt_length_scale_vs_prior_calibration": round(prompt_length_scale, 3),
            }
            for epoch in budgets[key]["epochs"].values():
                iterations = epoch["iterations_batch2"]
                epoch["estimated_wall_minutes_per_seed"] = [
                    round(iterations / 1000 * seconds * prompt_length_scale / 60, 1)
                    for seconds in (335, 579)
                ]
    return {
        "task": "NEXT_ACTION_SELECT",
        "batch_size_assumption": 2,
        "budgets": budgets,
        "runtime_calibration": {
            "prior_model": "Qwen/Qwen3-8B BF16 on the same Mac",
            "observed_prior_training_range_seconds_per_1000_iterations": [335, 579],
            "scaling": "prior seconds/1k iterations multiplied by new mean-token/prior-mean-token ratio (209.6 HML, 244.7 neutral)",
            "warning": "planning range only; prompt-length scaling is heuristic and this mission ran no model training",
        },
    }


def refresh_manifest(root: Path) -> None:
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {
            "manifest.json", "HML50K_MANIFEST.json", "SHA256SUMS", "HML50K_MANIFEST.sha256"
        }:
            files[str(path.relative_to(root))] = {"sha256": file_sha(path), "bytes": path.stat().st_size}
    manifest["files"] = files
    manifest["post_build_audits"] = {
        "token_length": "audits/token_length_audit.json",
        "unicode": "audits/unicode_audit.json",
        "parity": "audits/parity_audit.json",
        "dedup": "audits/dedup_audit.json",
        "trajectory": "audits/trajectory_depth_audit.json",
        "mutation": "audits/mutation_tests.json",
        "final_contamination": "audits/final_split_contamination_audit.json",
    }
    write_json(manifest_path, manifest)
    hml_manifest = root / "HML50K_MANIFEST.json"
    write_json(hml_manifest, manifest)
    (root / "HML50K_MANIFEST.sha256").write_text(
        f"{file_sha(hml_manifest)}  HML50K_MANIFEST.json\n", encoding="utf-8"
    )
    (root / "SHA256SUMS").write_text(
        "".join(f"{meta['sha256']}  {name}\n" for name, meta in sorted(files.items())),
        encoding="utf-8",
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=repo / "data/hml_50k_final")
    args = parser.parse_args()
    root = args.root.resolve()
    canonical_records, dedup = load_canonical(root)
    parity = parity_audit(root, canonical_records)
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, local_files_only=True, trust_remote_code=False)
    token, unicode, token_maps = token_and_unicode_audit(root, tokenizer)
    trajectory = trajectory_audit(canonical_records)
    mutation = mutation_audit(canonical_records)
    contamination = final_contamination_audit(repo, canonical_records)
    inventory = source_inventory(repo)
    budget = rung_budget(root, token_maps)
    outputs = {
        "dedup_audit.json": dedup,
        "parity_audit.json": parity,
        "token_length_audit.json": token,
        "unicode_audit.json": unicode,
        "trajectory_depth_audit.json": trajectory,
        "mutation_tests.json": mutation,
        "final_split_contamination_audit.json": contamination,
        "source_inventory.json": inventory,
        "training_budgets.json": budget,
    }
    for name, value in outputs.items():
        write_json(root / "audits" / name, value)
    # Make the combined build audit available under the explicit requested names too.
    combined = json.loads((root / "audits/leakage_candidate_audit.json").read_text())
    write_json(root / "audits/candidate_audit.json", combined)
    write_json(root / "audits/leakage_audit.json", {
        key: value for key, value in combined.items()
        if key not in {"mean_gold_tactic_characters", "mean_distractor_tactic_characters"}
    })
    results = {name: value.get("result", "INVENTORY") for name, value in outputs.items()}
    if any(value == "FAIL" for value in results.values()):
        raise AssertionError(f"post-build audit failed: {results}")
    refresh_manifest(root)
    print(canonical({"result": "PASS", "records": len(canonical_records), "audits": results}))


if __name__ == "__main__":
    main()
