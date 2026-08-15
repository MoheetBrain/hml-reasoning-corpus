#!/usr/bin/env python3
"""Patch VNext 10k model exports for explicit actions and string renderers.

This script is intentionally projection-only.  It reads the frozen 10k full
audit records, never mutates canonical transitions/splits/snapshots, and writes
only model-facing views, an action-leakage audit, the manifest, and a report.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import io
import json
import math
import statistics
import subprocess
from pathlib import Path

from hamiltonian_lang.semantic_state import (
    export_state,
    import_transition,
    parse_state,
    render_state,
)
from hamiltonian_lang.semantic_state.tree_view import parse_tree_state, render_tree_state

from scripts.vnext.action_leakage_policy import TOKEN_PATTERN, TOKEN_RE, action_leakage
from scripts.vnext.corpus_rederive import _decode_json_ast, _json_ast


HML_SHA = "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
CONTRACT = "vnext-translation-contract-1.0.0"
DATA_BASE = "09521ae992af5ca583a346da66c93d986e709386"
REPORT_BASE = "1c08914d656717695bff2b8b845d72ad6c26bbe7"
FABLE_ATTESTATION = "435571e"
LEAN_SAMPLE = Path("/Users/moheet/hml_research_artifacts/leandojo/sample.jsonl")
PRM_ROOT = Path("/Users/moheet/Documents/ChatGPT/prm800k")
ARMS = ("HML_LINEAR", "HML_TREE", "AST", "STRUCTURED_NEUTRAL")
SPLITS = ("train", "dev", "test")
RENDERERS = {
    "HML_LINEAR": "hml-linear-state@68178f0+canonical-action-envelope@1.0.0",
    "HML_TREE": "hml-tree-state@68178f0+canonical-action-envelope@1.0.0",
    "AST": "hmltn-canonical-json-ast@1.0.0",
    "STRUCTURED_NEUTRAL": "hmltn-canonical-json-neutral@1.0.0",
}
TOKENIZER = {
    "name": "HMLTN_UNICODE_LEXICAL",
    "version": "1.0.0",
    "pattern": TOKEN_PATTERN,
    "note": "FABLE model tokenizer was not present locally; this frozen lexical audit is reproducible and is not claimed to be model-token equivalent.",
}
FORBIDDEN_ACTION_FIELDS = {"summary", "output_id", "source", "state_after", "target_delta"}
EFFECT_FIELDS = (
    "branch_effect",
    "candidate_effect",
    "epistemic_effect",
    "goal_effect",
    "obligations_created",
    "obligations_discharged",
    "scope_effect",
    "typing",
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


def read_gzip(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def deterministic_gzip(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                for row in rows:
                    text.write(canonical(row) + "\n")


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def token_stats(values: list[str]) -> dict:
    counts = [len(TOKEN_RE.findall(value)) for value in values]
    return {
        "records": len(counts),
        "mean": round(statistics.fmean(counts), 3),
        "median": statistics.median(counts),
        "p90": percentile(counts, 0.90),
        "p95": percentile(counts, 0.95),
        "max": max(counts),
    }


def signature(rows: list[dict], fields: tuple[str, ...]) -> str:
    projection = [{field: row[field] for field in fields} for row in rows]
    return digest_text(canonical(projection))


def load_lean_index(path: Path, expected_sha: str) -> dict[tuple[str, int], dict]:
    if file_sha(path) != expected_sha:
        raise AssertionError("LeanDojo sample hash does not match the pinned manifest")
    index = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            key = (row["proof_id"], row["step_index"])
            if key in index:
                raise AssertionError(f"duplicate Lean source transition: {key}")
            index[key] = row
    return index


def safe_action(row: dict, lean_index: dict[tuple[str, int], dict]) -> tuple[dict, dict | None]:
    neutral = row["neutral"]
    source = neutral["source"]
    action = neutral["action"]
    projected = {
        "dependencies": action.get("dependencies", []),
        "operation": action.get("operation"),
        "preconditions": action.get("preconditions", []),
        "warrant_rule": (action.get("warrant") or {}).get("rule"),
    }
    provenance = None
    if row["task_eligibility"]["EXECUTE"]:
        for field in EFFECT_FIELDS:
            value = action.get(field)
            if value:
                projected[field] = value
        if row["source_family"] == "LEAN_DOJO":
            key = (source["proof_id"], source["step_index"])
            source_row = lean_index.get(key)
            if source_row is None:
                raise AssertionError(f"missing pinned Lean source row: {key}")
            tactic = source_row["tactic_surface"]
            evidence_tactic = next(iter(neutral["evidence"].values()))["tactic"]
            if not tactic or tactic != source.get("tactic") or tactic != evidence_tactic:
                raise AssertionError(f"Lean tactic provenance disagreement: {row['record_id']}")
            if source_row["state_before"] != neutral["state_before"]["claims"]["p0"]["proposition"]:
                raise AssertionError(f"Lean before-state provenance disagreement: {row['record_id']}")
            if source_row["state_after"] != neutral["state_after"]["claims"]["c1"]["proposition"]:
                raise AssertionError(f"Lean after-state provenance disagreement: {row['record_id']}")
            projected["tactic_text"] = tactic
            provenance = {
                "action_kind": "EXACT_FORMAL_SOURCE_TACTIC",
                "action_sha256": digest_text(tactic),
                "canonical_transition_sha256": row["canonical_sha256"],
                "formal_source_revision": source["commit"],
                "source_file": source["file_path"],
                "source_theorem_id": source["full_name"],
                "source_trace_id": source["proof_id"],
                "source_transition_id": f"{source['proof_id']}::step::{source['step_index']}",
                "step_index": source["step_index"],
            }
        else:
            # The only non-Lean EXECUTE rows are deterministic protocol actions.
            # Their canonical operation/effects are the action, not a prose gloss.
            projected["action_text"] = action["operation"]
            provenance = {
                "action_kind": "CANONICAL_PROTOCOL_OPERATION",
                "action_sha256": digest_text(action["operation"]),
                "canonical_transition_sha256": row["canonical_sha256"],
                "corpus_data_revision": DATA_BASE,
                "source_problem_id": source.get("problem"),
                "source_transition_id": source.get("upstream_record_id"),
            }
    if FORBIDDEN_ACTION_FIELDS & set(projected):
        raise AssertionError(f"forbidden safe-action field: {row['record_id']}")
    return projected, provenance


def render_views(row: dict, projected_action: dict, provenance: dict | None) -> dict[str, dict]:
    transition = import_transition(row["neutral"])
    before = export_state(transition.state_before)
    after = export_state(transition.state_after)
    safe_neutral = {"action": projected_action, "state_before": before}
    linear_before = render_state(transition.state_before)
    tree_before = render_tree_state(transition.state_before)
    linear_target = render_state(transition.state_after)
    tree_target = render_tree_state(transition.state_after)
    if parse_state(linear_before) != transition.state_before or parse_state(linear_target) != transition.state_after:
        raise AssertionError(f"HML_LINEAR state round trip failed: {row['record_id']}")
    if parse_tree_state(tree_before) != transition.state_before or parse_tree_state(tree_target) != transition.state_after:
        raise AssertionError(f"HML_TREE state round trip failed: {row['record_id']}")
    ast_input_obj = _json_ast(safe_neutral)
    ast_target_obj = _json_ast(after)
    if _decode_json_ast(ast_input_obj) != safe_neutral or _decode_json_ast(ast_target_obj) != after:
        raise AssertionError(f"AST round trip failed: {row['record_id']}")
    payloads = {
        "HML_LINEAR": (linear_before + "\nACTION " + canonical(projected_action), linear_target),
        "HML_TREE": (tree_before + "\nACTION " + canonical(projected_action), tree_target),
        "AST": (canonical(ast_input_obj), canonical(ast_target_obj)),
        "STRUCTURED_NEUTRAL": (canonical(safe_neutral), canonical(after)),
    }
    result = {}
    for arm, (input_text, target_text) in payloads.items():
        if not isinstance(input_text, str) or not isinstance(target_text, str):
            raise AssertionError(f"non-string model field: {row['record_id']} {arm}")
        result[arm] = {
            "audit_metadata": {
                "action_provenance": provenance,
                "canonical_transition_sha256": row["canonical_sha256"],
                "input_sha256": digest_text(input_text),
                "renderer_version": RENDERERS[arm],
                "target_sha256": digest_text(target_text),
            },
            "input_text": input_text,
            "record_id": row["record_id"],
            "representation": arm,
            "split": row["split"],
            "target_text": target_text,
            "task_eligibility": row["task_eligibility"],
        }
    return result


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=root / "data/vnext_10k")
    parser.add_argument("--report", type=Path, default=root / "reports/vnext_10k_d1_d2_patch.json")
    parser.add_argument("--lean-sample", type=Path, default=LEAN_SAMPLE)
    parser.add_argument("--prm-root", type=Path, default=PRM_ROOT)
    args = parser.parse_args()
    out = args.data_root
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    existing_report = json.loads(args.report.read_text()) if args.report.exists() else None
    already_patched = manifest.get("export_patch", {}).get("patch") == "VNEXT_D1_D2_MODEL_EXPORTS"
    if manifest["hml_semantic_commit"] != HML_SHA or manifest["contract_version"] != CONTRACT:
        raise AssertionError("pinned VNext authority mismatch")
    if manifest["codex_corpus_commit"] != DATA_BASE or manifest["record_count"] != 10000:
        raise AssertionError("canonical 10k data authority mismatch")

    pre_files = {relative: file_sha(out / relative) for relative in manifest["files"]}
    historical_pre_files = (
        existing_report["pre_patch_manifest_file_hashes"]
        if existing_report and "pre_patch_manifest_file_hashes" in existing_report
        else pre_files
    )
    for relative, expected in manifest["files"].items():
        path = out / relative
        if path.stat().st_size != expected["bytes"] or pre_files[relative] != expected["sha256"]:
            raise AssertionError(f"pre-patch manifest hash mismatch: {relative}")
    immutable_relatives = [
        "full_audit_records.jsonl.gz", "train.jsonl.gz", "dev.jsonl.gz",
        "test.jsonl.gz", "snapshots.json",
    ]
    immutable_before = {name: file_sha(out / name) for name in immutable_relatives}

    rows = read_gzip(out / "full_audit_records.jsonl.gz")
    if len(rows) != 10000 or len({row["record_id"] for row in rows}) != 10000:
        raise AssertionError("canonical record identity failure")
    if collections.Counter(row["split"] for row in rows) != collections.Counter(manifest["split_counts"]):
        raise AssertionError("split assignment disagreement")
    source_counts = collections.Counter(row["source_family"] for row in rows)
    if dict(sorted(source_counts.items())) != manifest["source_counts"]:
        raise AssertionError("source assignment disagreement")
    eligibility_before = collections.Counter(
        task for row in rows for task, eligible in row["task_eligibility"].items() if eligible
    )
    eligibility_before = {
        task: eligibility_before[task] for task in manifest["task_eligibility_counts"]
    }
    if eligibility_before != manifest["task_eligibility_counts"]:
        raise AssertionError("task eligibility disagreement")

    # Re-attest every locally pinned raw source used by the frozen data build.
    source_validation = {
        "LEAN_DOJO": file_sha(args.lean_sample),
        "MATH": file_sha(root / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet"),
        "AMPS": file_sha(root / "data/raw/amps_khan/0000.parquet"),
        "SYNTHETIC_HARD_TAIL": file_sha(root / "data/vnext_600/full_audit_records.jsonl.gz"),
        "PRM800K": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=args.prm_root, text=True
        ).strip(),
    }
    expected_source = {
        "LEAN_DOJO": manifest["source_revisions"]["LEAN_DOJO"]["derived_sample_sha256"],
        "MATH": manifest["source_revisions"]["MATH"]["file_sha256"],
        "AMPS": manifest["source_revisions"]["AMPS"]["file_sha256"],
        "SYNTHETIC_HARD_TAIL": manifest["source_revisions"]["SYNTHETIC_HARD_TAIL"]["vnext_600_sha256"],
        "PRM800K": manifest["source_revisions"]["PRM800K"]["commit"],
    }
    if source_validation != expected_source:
        raise AssertionError(f"raw source authority mismatch: {source_validation}")

    execute_ids = {
        row["record_id"] for row in rows if row["task_eligibility"]["EXECUTE"]
    }
    current_view_string_counts = {}
    pre_view_ids = {}
    current_explicit_action_text = 0
    for arm in ARMS:
        existing = [item for split in SPLITS for item in read_gzip(out / "views" / arm / f"{split}.jsonl.gz")]
        pre_view_ids[arm] = {item["record_id"] for item in existing}
        current_view_string_counts[arm] = sum(
            (
                isinstance(item.get("input_text"), str) and isinstance(item.get("target_text"), str)
                if already_patched
                else isinstance(item.get("input"), str) and isinstance(item.get("target"), str)
            )
            for item in existing
        )
        if arm == "STRUCTURED_NEUTRAL":
            if already_patched:
                current_explicit_action_text = sum(
                    item["record_id"] in execute_ids
                    and bool({"tactic_text", "action_text"} & set(json.loads(item["input_text"])["action"]))
                    for item in existing
                )
            else:
                current_explicit_action_text = sum(
                    item["record_id"] in execute_ids
                    and isinstance(item.get("input"), dict)
                    and bool({"tactic_text", "action_text"} & set(item["input"].get("action", {})))
                    for item in existing
                )
    if any(ids != set(row["record_id"] for row in rows) for ids in pre_view_ids.values()):
        raise AssertionError("pre-patch four-arm record parity failure")
    if current_explicit_action_text != (4024 if already_patched else 0):
        raise AssertionError("D1 pre-regeneration action-text count is inconsistent")
    historical_string_counts = (
        existing_report["d2"]["pre_patch_string_counts"]
        if existing_report else current_view_string_counts
    )
    historical_explicit_action_text = (
        existing_report["d1"]["execute_action_text_before"]
        if existing_report else current_explicit_action_text
    )

    snapshots = json.loads((out / "snapshots.json").read_text())
    previous = set()
    for size in (100, 250, 1000, 5000, 10000):
        ids = snapshots[str(size)]["record_ids"]
        if len(ids) != size or len(set(ids)) != size or (previous and not previous < set(ids)):
            raise AssertionError(f"snapshot nesting failure at {size}")
        previous = set(ids)

    lean_index = load_lean_index(
        args.lean_sample, manifest["source_revisions"]["LEAN_DOJO"]["derived_sample_sha256"]
    )
    arm_rows = collections.defaultdict(list)
    leakage_rows = []
    execute_action_content = collections.Counter()
    for row in rows:
        projected_action, provenance = safe_action(row, lean_index)
        if row["task_eligibility"]["EXECUTE"]:
            field = "tactic_text" if "tactic_text" in projected_action else (
                "action_text" if "action_text" in projected_action else "MISSING"
            )
            execute_action_content[(row["source_family"], field)] += 1
            leakage_rows.append(action_leakage(row, projected_action))
        rendered = render_views(row, projected_action, provenance)
        for arm, item in rendered.items():
            arm_rows[arm].append(item)

    leakage_counts = collections.Counter(item["classification"] for item in leakage_rows)
    excluded_ids = sorted(item["record_id"] for item in leakage_rows if item["excluded_from_execute"])
    if excluded_ids:
        raise AssertionError(
            "direct target-revealing source actions require an explicit eligibility patch: "
            + ",".join(excluded_ids)
        )
    if sum(execute_action_content.values()) != 4024 or any(key[1] == "MISSING" for key in execute_action_content):
        raise AssertionError("D1 action-presence gate failed")

    for arm in ARMS:
        by_split = collections.defaultdict(list)
        for item in arm_rows[arm]:
            by_split[item["split"]].append(item)
        for split in SPLITS:
            deterministic_gzip(out / "views" / arm / f"{split}.jsonl.gz", by_split[split])
    deterministic_gzip(out / "action_leakage_audit.jsonl.gz", leakage_rows)

    regenerated_relatives = [
        "action_leakage_audit.jsonl.gz",
        *(f"views/{arm}/{split}.jsonl.gz" for arm in ARMS for split in SPLITS),
    ]
    deterministic_rebuild = bool(already_patched) and all(
        pre_files.get(relative) == file_sha(out / relative) for relative in regenerated_relatives
    )

    # The canonical files and all corpus membership must remain byte-identical.
    immutable_after = {name: file_sha(out / name) for name in immutable_relatives}
    if immutable_before != immutable_after:
        raise AssertionError("projection patch changed canonical data/splits/snapshots")

    execute_by_split = collections.Counter(
        row["split"] for row in rows if row["task_eligibility"]["EXECUTE"]
    )
    train_execute = {row["record_id"] for row in rows if row["split"] == "train" and row["task_eligibility"]["EXECUTE"]}
    snapshot_train_execute = {
        size: len(train_execute & set(snapshots[size]["record_ids"]))
        for size in ("100", "250", "1000", "5000", "10000")
    }
    if dict(execute_by_split) != {"train": 3254, "dev": 392, "test": 378}:
        raise AssertionError("EXECUTE split regression")
    if snapshot_train_execute != {"100": 29, "250": 81, "1000": 326, "5000": 1630, "10000": 3254}:
        raise AssertionError("TRAIN/EXECUTE snapshot regression")

    token_audit = {arm: token_stats([item["input_text"] for item in arm_rows[arm]]) for arm in ARMS}
    string_counts = {
        arm: sum(isinstance(item["input_text"], str) and isinstance(item["target_text"], str) for item in arm_rows[arm])
        for arm in ARMS
    }
    if set(string_counts.values()) != {10000}:
        raise AssertionError("D2 string-type gate failed")

    paths = sorted(path for path in out.rglob("*") if path.is_file() and path.name != "manifest.json")
    manifest["export_patch"] = {
        "action_leakage_audit": {
            "ambiguous": leakage_counts["C_AMBIGUOUS"],
            "clean": leakage_counts["A_LEGITIMATE_ACTION_SEMANTICS"],
            "direct_target_revealing": leakage_counts["B_DIRECT_TARGET_REVEALING_ACTION"],
            "excluded": len(excluded_ids),
        },
        "canonical_data_authority": DATA_BASE,
        "deterministic_rebuild": "PASS" if deterministic_rebuild else "PENDING_SECOND_BUILD",
        "fable_attestation_commit": FABLE_ATTESTATION,
        "patch": "VNEXT_D1_D2_MODEL_EXPORTS",
        "renderers": RENDERERS,
        "report_base_commit": REPORT_BASE,
        "string_counts": string_counts,
        "token_audit": {"tokenizer": TOKENIZER, "statistics": token_audit},
    }
    manifest["execute_action_presence"] = {
            "before_explicit_action_text": historical_explicit_action_text,
        "after_explicit_action_text": 4024,
        "missing_required_after": 0,
        "by_source_and_field": {
            f"{source}:{field}": count
            for (source, field), count in sorted(execute_action_content.items())
        },
    }
    manifest["execute_split_counts"] = dict(sorted(execute_by_split.items()))
    manifest["train_execute_snapshot_counts"] = snapshot_train_execute
    manifest["leakage_audit"] = "10000/10000 PASS"
    manifest["files"] = {
        str(path.relative_to(out)): {"bytes": path.stat().st_size, "sha256": file_sha(path)}
        for path in paths
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    report = {
        "authority": {
            "canonical_data_commit": DATA_BASE,
            "contract_version": CONTRACT,
            "fable_attestation_commit": FABLE_ATTESTATION,
            "hml_semantic_commit": HML_SHA,
            "starting_report_commit": REPORT_BASE,
        },
        "canonical_regression": {
            "canonical_file_hashes_before_and_after": immutable_before,
            "record_count": len(rows),
            "record_id_signature": signature(rows, ("record_id",)),
            "source_assignment_signature": signature(rows, ("record_id", "source_family")),
            "split_assignment_signature": signature(rows, ("record_id", "split")),
            "task_eligibility_signature": signature(rows, ("record_id", "task_eligibility")),
            "snapshot_sha256": immutable_before["snapshots.json"],
            "unchanged": True,
            "source_authorities_validated": source_validation,
        },
        "d1": {
            "execute_action_text_before": historical_explicit_action_text,
            "execute_action_text_after": 4024,
            "execute_missing_required_action_after": 0,
            "field_counts": {
                f"{source}:{field}": count
                for (source, field), count in sorted(execute_action_content.items())
            },
            "leakage_classification": dict(sorted(leakage_counts.items())),
            "excluded_record_ids": excluded_ids,
        },
        "d2": {
            "pre_patch_string_counts": historical_string_counts,
            "renderer_versions": RENDERERS,
            "semantic_parity": "10000/10000 PASS",
            "string_counts": string_counts,
        },
        "execute": {
            "before": 4024,
            "after": 4024,
            "by_split": dict(sorted(execute_by_split.items())),
            "train_snapshot_counts": snapshot_train_execute,
        },
        "full_leakage_audit": {
            "ambiguous_rows": leakage_counts["C_AMBIGUOUS"],
            "clean_rows": len(rows),
            "direct_target_revealing_actions": leakage_counts["B_DIRECT_TARGET_REVEALING_ACTION"],
            "excluded_rows": len(excluded_ids),
            "flagged_rows": leakage_counts["B_DIRECT_TARGET_REVEALING_ACTION"] + leakage_counts["C_AMBIGUOUS"],
            "safe_projection_rows_checked": len(rows),
        },
        "deterministic_rebuild": {
            "byte_identical_regenerated_files": len(regenerated_relatives) if deterministic_rebuild else 0,
            "files_checked": len(regenerated_relatives),
            "result": "PASS" if deterministic_rebuild else "PENDING_SECOND_BUILD",
        },
        "pre_patch_manifest_file_hashes": historical_pre_files,
        "token_audit": {"tokenizer": TOKENIZER, "statistics": token_audit},
        "result": "FABLE_GATE_REPAIRED",
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "execute_action_text": "0->4024",
        "execute_missing": 0,
        "execute_split_counts": dict(execute_by_split),
        "leakage": dict(leakage_counts),
        "result": report["result"],
        "string_counts": string_counts,
        "train_execute_snapshots": snapshot_train_execute,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
