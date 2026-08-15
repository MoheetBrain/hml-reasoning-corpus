#!/usr/bin/env python3
"""Build the VNext HML-input / AST-JSON-output EXECUTE projection.

This exporter performs no semantic rendering.  It joins the authoritative
HML_LINEAR and AST model-ready views by record_id and copies two existing
strings verbatim:

    input_text  <- HML_LINEAR.input_text
    target_text <- AST.target_text

Canonical records are used only for membership, mechanism, provenance, and the
same leakage audit used by the D1/D2 export patch.  Splits and snapshots are
read-only inputs.
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
import sys
import tempfile
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts.vnext.action_leakage_policy import action_leakage  # noqa: E402


SOURCE_EXPORT_COMMIT = "a2f992a6d474638814a1f1f7809f4015db3894c5"
CANONICAL_DATA_COMMIT = "09521ae992af5ca583a346da66c93d986e709386"
HML_SEMANTIC_COMMIT = "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
FABLE_RESULT_COMMIT = "ccf2a43"
CONTRACT_VERSION = "vnext-translation-contract-1.0.0"
VIEW_FAMILY = "HML_IN_JSON_OUT"
VIEW_VERSION = "hml-linear-input+canonical-ast-json-output-record-join@1.0.0"
SPLITS = ("train", "dev", "test")
SOURCE_ARMS = ("HML_LINEAR", "AST")
ORIGINAL_GRID_ARMS = ("HML_LINEAR", "HML_TREE", "AST", "STRUCTURED_NEUTRAL")
MAXSEQ = 6144
GENERATION_RESERVE = 16
MODEL_ID = "mlx-community/gemma-4-E4B-it-qat-4bit"
MODEL_REVISION = "0f35c6f6d386f7f74e628bd7c6526ce531212300"
PROMPT = (
    "Below is a mathematical proof state and the action applied to it.\n\n{inp}\n\n"
    "Produce the exact resulting state in the same format. Output the resulting "
    "state only."
)
EXPECTED_SOURCE_HASHES = {
    "views/HML_LINEAR/train.jsonl.gz": "e2215950a672bbeba40db6fc881429217e3d305671ab1d17034a6460375e0a70",
    "views/HML_LINEAR/dev.jsonl.gz": "b1996172d27a6c97b0d3120633105f90bc76ae5184741a4bd66d8b45a58926c3",
    "views/HML_LINEAR/test.jsonl.gz": "4bd9292f6f3b5cb3207a4ed14dcbbec46def87f0f6c7e6e5120b3d33ea09641c",
    "views/AST/train.jsonl.gz": "fc9b1dab24dc23c2df8fca5931df0284ee140073b949cbe8732616ee93563571",
    "views/AST/dev.jsonl.gz": "4403feb230269d3f95cb83d12abefd4c9373c961d2117b5c201955194abd8d9b",
    "views/AST/test.jsonl.gz": "2e18804a3785f756ffc6fd0bf21d3494a915c60a3ac55f399a2b3c7a892e581f",
}
EXPECTED_CANONICAL_HASHES = {
    "train.jsonl.gz": "1e80f0abe3537c1dad7d1009ad761a516bfc2ba26e50fc95fae3ac817a22c025",
    "dev.jsonl.gz": "02487fe0247398e8ff46bb3a26480f9c6280dbe129a3ad7486377fb88b4f22dd",
    "test.jsonl.gz": "54c3613d0a71b17a8f70aade72162231fc3db9af5c965c5810d4c73ccfbd118b",
    "snapshots.json": "700106a1728526231e4a5074690d444f27ae2b071b73f95768fe390232eb6fcc",
}
EXPECTED_EXECUTE_COUNTS = {"train": 3254, "dev": 392, "test": 378}
EXPECTED_MECHANISM_COUNTS = {
    "assumption": 24,
    "branch_join": 8,
    "goal_close": 1659,
    "goal_create": 292,
    "implicit_logical_weakening": 16,
    "nested_branch": 24,
    "obligations": 8,
    "ordinary_claim_derivation": 4000,
}
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": file_sha(path)}


def read_gzip(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def deterministic_gzip(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                for row in rows:
                    text.write(canonical(row) + "\n")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def stats(values: list[int]) -> dict:
    if not values:
        return {"max": 0, "mean": 0, "median": 0, "p90": 0, "p99": 0, "records": 0}
    return {
        "max": max(values),
        "mean": round(statistics.fmean(values), 3),
        "median": statistics.median(values),
        "p90": percentile(values, 0.90),
        "p99": percentile(values, 0.99),
        "records": len(values),
    }


def signature(record_ids: Iterable[str]) -> str:
    return digest_text(canonical(sorted(record_ids)))


def decode_json_ast(value):
    node = value["node"]
    if node == "OBJECT":
        return {field["name"]: decode_json_ast(field["value"]) for field in value["fields"]}
    if node == "ARRAY":
        return [decode_json_ast(item) for item in value["items"]]
    if node == "NULL":
        return None
    return value["value"]


def action_from_hml(input_text: str) -> dict:
    before, separator, action_text = input_text.rpartition("\nACTION ")
    if not separator or not before or not action_text:
        raise AssertionError("HML_LINEAR input lacks the canonical ACTION envelope")
    action = json.loads(action_text)
    if not isinstance(action, dict):
        raise AssertionError("HML_LINEAR ACTION envelope is not an object")
    return action


def action_from_ast(input_text: str) -> dict:
    decoded = decode_json_ast(json.loads(input_text))
    if set(decoded) != {"action", "state_before"} or not isinstance(decoded["action"], dict):
        raise AssertionError("AST input does not decode to the safe model-input schema")
    return decoded["action"]


def exporter_commit() -> str:
    relative = Path(__file__).resolve().relative_to(ROOT)
    if subprocess.run(
        ["git", "diff", "--quiet", "--", str(relative)], cwd=ROOT
    ).returncode != 0:
        raise AssertionError("exporter must be committed before release generation")
    value = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(relative)], cwd=ROOT, text=True
    ).strip()
    if len(value) != 40:
        raise AssertionError("could not resolve the exporter commit")
    return value


def assert_authority(data_root: Path) -> dict:
    manifest_path = data_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest["codex_corpus_commit"] != CANONICAL_DATA_COMMIT:
        raise AssertionError("canonical VNext data commit mismatch")
    if manifest["hml_semantic_commit"] != HML_SEMANTIC_COMMIT:
        raise AssertionError("VNext semantic pin mismatch")
    if manifest["contract_version"] != CONTRACT_VERSION:
        raise AssertionError("translation contract mismatch")
    for relative, expected in {**EXPECTED_SOURCE_HASHES, **EXPECTED_CANONICAL_HASHES}.items():
        path = data_root / relative
        actual = file_sha(path)
        if actual != expected:
            raise AssertionError(f"source authority hash mismatch: {relative} {actual}")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_EXPORT_COMMIT, "HEAD"], cwd=ROOT
    ).returncode != 0:
        raise AssertionError("source export commit is not in the current branch ancestry")
    return manifest


def load_sources(data_root: Path) -> tuple[dict, dict, dict]:
    canonical_rows = []
    canonical_by_id = {}
    source_views = {arm: {} for arm in SOURCE_ARMS}
    source_order = {split: [] for split in SPLITS}
    for split in SPLITS:
        for row in read_gzip(data_root / f"{split}.jsonl.gz"):
            record_id = row["record_id"]
            if record_id in canonical_by_id:
                raise AssertionError(f"duplicate canonical record_id: {record_id}")
            if row["split"] != split:
                raise AssertionError(f"canonical split mismatch: {record_id}")
            canonical_by_id[record_id] = row
            canonical_rows.append(row)
        for arm in SOURCE_ARMS:
            for row in read_gzip(data_root / "views" / arm / f"{split}.jsonl.gz"):
                record_id = row["record_id"]
                if record_id in source_views[arm]:
                    raise AssertionError(f"duplicate {arm} record_id: {record_id}")
                if row["representation"] != arm or row["split"] != split:
                    raise AssertionError(f"{arm} representation/split mismatch: {record_id}")
                source_views[arm][record_id] = row
                if arm == "HML_LINEAR":
                    source_order[split].append(record_id)
    canonical_ids = set(canonical_by_id)
    if len(canonical_ids) != 10000:
        raise AssertionError("canonical VNext universe is not exactly 10,000 records")
    if any(set(source_views[arm]) != canonical_ids for arm in SOURCE_ARMS):
        raise AssertionError("HML_LINEAR/AST/canonical record-id parity failed")
    return canonical_by_id, source_views, source_order


def project_execute(
    canonical_by_id: dict, source_views: dict, source_order: dict
) -> tuple[dict[str, list[dict]], list[dict], dict]:
    output = {split: [] for split in SPLITS}
    leakage_rows = []
    parity = collections.Counter()
    action_fields = collections.Counter()
    execute_counts = collections.Counter()
    mechanism_counts = collections.Counter()
    execute_ids = {split: [] for split in SPLITS}

    for split in SPLITS:
        for record_id in source_order[split]:
            canonical_row = canonical_by_id[record_id]
            hml = source_views["HML_LINEAR"][record_id]
            ast = source_views["AST"][record_id]
            if not canonical_row["task_eligibility"]["EXECUTE"]:
                continue
            execute_counts[split] += 1
            execute_ids[split].append(record_id)
            mechanism_counts.update(canonical_row["mechanisms"])

            if hml["split"] != ast["split"] or hml["split"] != canonical_row["split"]:
                raise AssertionError(f"split parity failed: {record_id}")
            if hml["task_eligibility"] != ast["task_eligibility"]:
                raise AssertionError(f"task metadata parity failed: {record_id}")
            if hml["audit_metadata"]["canonical_transition_sha256"] != canonical_row["canonical_sha256"]:
                raise AssertionError(f"HML canonical transition identity failed: {record_id}")
            if ast["audit_metadata"]["canonical_transition_sha256"] != canonical_row["canonical_sha256"]:
                raise AssertionError(f"AST canonical transition identity failed: {record_id}")
            if hml["audit_metadata"]["action_provenance"] != ast["audit_metadata"]["action_provenance"]:
                raise AssertionError(f"source/action provenance parity failed: {record_id}")

            hml_action = action_from_hml(hml["input_text"])
            ast_action = action_from_ast(ast["input_text"])
            if hml_action != ast_action:
                raise AssertionError(f"action identity failed: {record_id}")
            present = [field for field in ("tactic_text", "action_text") if hml_action.get(field)]
            if len(present) != 1:
                raise AssertionError(f"action/tactic presence failed: {record_id}")
            action_fields[present[0]] += 1
            expected_action_hash = digest_text(hml_action[present[0]])
            if hml["audit_metadata"]["action_provenance"]["action_sha256"] != expected_action_hash:
                raise AssertionError(f"action/tactic provenance hash failed: {record_id}")

            input_text = hml["input_text"]
            target_text = ast["target_text"]
            if not isinstance(input_text, str) or not isinstance(target_text, str):
                raise AssertionError(f"non-string joined model field: {record_id}")
            if digest_text(input_text) != hml["audit_metadata"]["input_sha256"]:
                raise AssertionError(f"HML input hash failed: {record_id}")
            if digest_text(target_text) != ast["audit_metadata"]["target_sha256"]:
                raise AssertionError(f"AST target hash failed: {record_id}")

            joined = {
                "audit_metadata": {
                    "action_provenance": hml["audit_metadata"]["action_provenance"],
                    "canonical_transition_sha256": canonical_row["canonical_sha256"],
                    "input_sha256": hml["audit_metadata"]["input_sha256"],
                    "renderer_version": VIEW_VERSION,
                    "target_sha256": ast["audit_metadata"]["target_sha256"],
                },
                "input_text": input_text,
                "record_id": record_id,
                "representation": VIEW_FAMILY,
                "split": split,
                "target_text": target_text,
                "task_eligibility": hml["task_eligibility"],
            }
            if joined["input_text"] != hml["input_text"]:
                raise AssertionError(f"HML input identity failed: {record_id}")
            if joined["target_text"] != ast["target_text"]:
                raise AssertionError(f"AST target identity failed: {record_id}")
            parity.update(("record", "split", "provenance", "action", "input", "target"))
            output[split].append(joined)

            fresh_leakage = action_leakage(canonical_row, hml_action)
            fresh_leakage["input_sha256"] = joined["audit_metadata"]["input_sha256"]
            fresh_leakage["target_sha256"] = joined["audit_metadata"]["target_sha256"]
            fresh_leakage["view_family"] = VIEW_FAMILY
            leakage_rows.append(fresh_leakage)

    if dict(execute_counts) != EXPECTED_EXECUTE_COUNTS:
        raise AssertionError(f"EXECUTE split count regression: {dict(execute_counts)}")
    if dict(sorted(mechanism_counts.items())) != EXPECTED_MECHANISM_COUNTS:
        raise AssertionError(f"EXECUTE mechanism regression: {dict(mechanism_counts)}")
    if action_fields != {"tactic_text": 4000, "action_text": 24}:
        raise AssertionError(f"action/tactic count regression: {dict(action_fields)}")
    if any(row["classification"] != "A_LEGITIMATE_ACTION_SEMANTICS" for row in leakage_rows):
        failures = [row["record_id"] for row in leakage_rows if row["classification"] != "A_LEGITIMATE_ACTION_SEMANTICS"]
        raise AssertionError("joined-pair leakage audit failed: " + ",".join(failures))
    total = sum(EXPECTED_EXECUTE_COUNTS.values())
    if any(parity[name] != total for name in ("record", "split", "provenance", "action", "input", "target")):
        raise AssertionError(f"projection parity count failed: {dict(parity)}")
    return output, leakage_rows, {
        "action_field_counts": dict(sorted(action_fields.items())),
        "execute_counts": dict(execute_counts),
        "execute_ids": execute_ids,
        "mechanism_counts": dict(sorted(mechanism_counts.items())),
        "parity_counts": dict(sorted(parity.items())),
    }


def token_lengths(tokenizer, texts: list[str], batch_size: int = 128) -> list[int]:
    lengths = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(texts[start : start + batch_size], add_special_tokens=True)
        lengths.extend(len(ids) for ids in encoded["input_ids"])
    return lengths


def measure_arm(tokenizer, rows_by_split: dict[str, list[dict]]) -> tuple[dict, dict]:
    per_id = {}
    summaries = {}
    for split in SPLITS:
        rows = rows_by_split[split]
        prompted = [PROMPT.format(inp=row["input_text"]) for row in rows]
        targets = [row["target_text"] for row in rows]
        input_lengths = token_lengths(tokenizer, prompted)
        target_lengths = token_lengths(tokenizer, targets)
        total_lengths = [a + b for a, b in zip(input_lengths, target_lengths)]
        fit_lengths = [value + GENERATION_RESERVE for value in total_lengths]
        for row, input_length, target_length, total_length, fit_length in zip(
            rows, input_lengths, target_lengths, total_lengths, fit_lengths
        ):
            per_id[row["record_id"]] = {
                "input": input_length,
                "target": target_length,
                "total": total_length,
                "fit_length": fit_length,
                "fits": fit_length <= MAXSEQ,
            }
        summaries[split] = {
            "fit": sum(value <= MAXSEQ for value in fit_lengths),
            "input": stats(input_lengths),
            "raw": len(rows),
            "target": stats(target_lengths),
            "total": stats(total_lengths),
            "total_with_generation_reserve": stats(fit_lengths),
        }
    all_values = list(per_id.values())
    summaries["all"] = {
        "fit": sum(item["fits"] for item in all_values),
        "input": stats([item["input"] for item in all_values]),
        "raw": len(all_values),
        "target": stats([item["target"] for item in all_values]),
        "total": stats([item["total"] for item in all_values]),
        "total_with_generation_reserve": stats([item["fit_length"] for item in all_values]),
    }
    return per_id, summaries


def original_grid_fit(tokenizer, data_root: Path, execute_ids: dict[str, list[str]]) -> set[str]:
    execute_universe = set().union(*execute_ids.values())
    fit = set(execute_universe)
    for arm in ORIGINAL_GRID_ARMS:
        arm_by_id = {}
        for split in SPLITS:
            for row in read_gzip(data_root / "views" / arm / f"{split}.jsonl.gz"):
                if row["record_id"] in execute_universe:
                    arm_by_id[row["record_id"]] = row
        if set(arm_by_id) != execute_universe:
            raise AssertionError(f"original-grid EXECUTE parity failed: {arm}")
        ordered_ids = sorted(arm_by_id)
        input_lengths = token_lengths(
            tokenizer, [PROMPT.format(inp=arm_by_id[record_id]["input_text"]) for record_id in ordered_ids]
        )
        target_lengths = token_lengths(
            tokenizer, [arm_by_id[record_id]["target_text"] for record_id in ordered_ids]
        )
        arm_fit = {
            record_id
            for record_id, input_length, target_length in zip(ordered_ids, input_lengths, target_lengths)
            if input_length + target_length + GENERATION_RESERVE <= MAXSEQ
        }
        fit &= arm_fit
    return fit


def tokenizer_authority(tokenizer_path: Path, transformers_version: str) -> dict:
    hashes = {}
    for name in TOKENIZER_FILES:
        path = tokenizer_path / name
        if not path.exists():
            raise AssertionError(f"missing pinned tokenizer file: {path}")
        hashes[name] = file_record(path)
    return {
        "files": hashes,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "transformers_version": transformers_version,
    }


def select_goldens(canonical_by_id: dict, projected_by_id: dict, source_views: dict) -> list[dict]:
    execute = [
        row for row in canonical_by_id.values() if row["task_eligibility"]["EXECUTE"]
    ]
    selectors = (
        ("ordinary_derivation", lambda mechanisms: mechanisms == ["ordinary_claim_derivation"]),
        ("goal_close", lambda mechanisms: "goal_close" in mechanisms),
        ("goal_create", lambda mechanisms: "goal_create" in mechanisms),
        (
            "assumption_nested_branch",
            lambda mechanisms: "assumption" in mechanisms and "nested_branch" in mechanisms,
        ),
    )
    goldens = []
    for label, predicate in selectors:
        candidates = sorted(
            (row for row in execute if predicate(row["mechanisms"])),
            key=lambda row: row["record_id"],
        )
        if not candidates:
            raise AssertionError(f"no source record available for golden category: {label}")
        canonical_row = candidates[0]
        record_id = canonical_row["record_id"]
        projected = projected_by_id[record_id]
        hml = source_views["HML_LINEAR"][record_id]
        ast = source_views["AST"][record_id]
        input_equal = projected["input_text"] == hml["input_text"]
        target_equal = projected["target_text"] == ast["target_text"]
        if not input_equal or not target_equal:
            raise AssertionError(f"golden cross-projection identity failed: {record_id}")
        goldens.append({
            "category": label,
            "input_identity": input_equal,
            "input_sha256": digest_text(projected["input_text"]),
            "mechanisms": canonical_row["mechanisms"],
            "record_id": record_id,
            "split": canonical_row["split"],
            "target_identity": target_equal,
            "target_sha256": digest_text(projected["target_text"]),
        })
    return goldens


def build(data_root: Path, output_root: Path, tokenizer_path: Path) -> list[str]:
    source_manifest = assert_authority(data_root)
    exporter_sha = exporter_commit()
    canonical_by_id, source_views, source_order = load_sources(data_root)
    projected, leakage_rows, audit = project_execute(canonical_by_id, source_views, source_order)
    projected_by_id = {row["record_id"]: row for rows in projected.values() for row in rows}

    try:
        import transformers
        from transformers import AutoTokenizer
    except ImportError as error:
        raise SystemExit(
            "Exact token audit requires transformers; run with the FABLE environment "
            "used for the completed grid."
        ) from error
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
    tokenizer_info = tokenizer_authority(tokenizer_path, transformers.__version__)

    ast_execute = {
        split: [source_views["AST"][record_id] for record_id in audit["execute_ids"][split]]
        for split in SPLITS
    }
    joined_lengths, joined_summaries = measure_arm(tokenizer, projected)
    ast_lengths, ast_summaries = measure_arm(tokenizer, ast_execute)
    joined_fit = {record_id for record_id, value in joined_lengths.items() if value["fits"]}
    ast_fit = {record_id for record_id, value in ast_lengths.items() if value["fits"]}
    pair_fit = joined_fit & ast_fit
    completed_control_fit = original_grid_fit(tokenizer, data_root, audit["execute_ids"])
    comparison_fit = joined_fit & completed_control_fit

    view_relatives = [f"views/{VIEW_FAMILY}/{split}.jsonl.gz" for split in SPLITS]
    for split, relative in zip(SPLITS, view_relatives):
        deterministic_gzip(output_root / relative, projected[split])

    support_dir = output_root / "reverse_projection"
    raw_relative = "reverse_projection/raw_execute_membership.json"
    fit_relative = "reverse_projection/matched_fit_ids_maxseq6144.json"
    leakage_relative = "reverse_projection/leakage_audit.jsonl.gz"
    token_relative = "reverse_projection/token_audit.json"
    golden_relative = "reverse_projection/golden_checks.json"
    manifest_relative = "reverse_projection_manifest.json"

    raw_membership = {
        "counts": audit["execute_counts"],
        "record_id_signature": signature(projected_by_id),
        "record_ids_by_split": {
            split: sorted(audit["execute_ids"][split]) for split in SPLITS
        },
        "schema_version": "hmltn-reverse-projection-membership-1.0.0",
        "source_export_commit": SOURCE_EXPORT_COMMIT,
        "view_family": VIEW_FAMILY,
    }
    write_json(output_root / raw_relative, raw_membership)

    by_split_fit = {}
    comparison_ids = {}
    for split in SPLITS:
        raw_ids = set(audit["execute_ids"][split])
        selected = sorted(raw_ids & comparison_fit)
        comparison_ids[split] = selected
        by_split_fit[split] = {
            "ast_control_excluded_ids": sorted(raw_ids - ast_fit),
            "ast_control_fit": len(raw_ids & ast_fit),
            "comparison_fit": len(selected),
            "completed_four_arm_control_fit": len(raw_ids & completed_control_fit),
            "hml_in_json_out_excluded_ids": sorted(raw_ids - joined_fit),
            "hml_in_json_out_fit": len(raw_ids & joined_fit),
            "pair_fit": len(raw_ids & pair_fit),
            "raw": len(raw_ids),
        }
    matched_fit = {
        "by_split": by_split_fit,
        "comparison_record_id_signature": signature(comparison_fit),
        "comparison_record_ids_by_split": comparison_ids,
        "criterion": {
            "expression": "prompted_input_tokens + target_tokens + generation_reserve <= maxseq",
            "generation_reserve": GENERATION_RESERVE,
            "maxseq": MAXSEQ,
            "prompt_sha256": digest_text(PROMPT),
        },
        "equivalence_checks": {
            "pair_fit_equals_completed_four_arm_control_fit": pair_fit == completed_control_fit,
            "pair_fit_equals_reusable_comparison_fit": pair_fit == comparison_fit,
        },
        "schema_version": "hmltn-reverse-projection-fit-1.0.0",
        "view_family": VIEW_FAMILY,
    }
    write_json(output_root / fit_relative, matched_fit)
    deterministic_gzip(output_root / leakage_relative, leakage_rows)

    token_audit = {
        "arms": {
            "AST_JSON_IN_JSON_OUT_CONTROL": ast_summaries,
            VIEW_FAMILY: joined_summaries,
        },
        "counting_contract": {
            "generation_reserve": GENERATION_RESERVE,
            "input_definition": "tokenizer(PROMPT.format(inp=input_text))",
            "maxseq": MAXSEQ,
            "prompt": PROMPT,
            "target_definition": "tokenizer(target_text)",
        },
        "schema_version": "hmltn-reverse-projection-token-audit-1.0.0",
        "tokenizer": tokenizer_info,
    }
    write_json(output_root / token_relative, token_audit)

    goldens = {
        "checks": select_goldens(canonical_by_id, projected_by_id, source_views),
        "schema_version": "hmltn-reverse-projection-goldens-1.0.0",
        "view_family": VIEW_FAMILY,
    }
    write_json(output_root / golden_relative, goldens)

    support_relatives = [raw_relative, fit_relative, leakage_relative, token_relative, golden_relative]
    generated_relatives = view_relatives + support_relatives
    generated_files = {
        relative: file_record(output_root / relative) for relative in generated_relatives
    }
    source_files = {
        relative: file_record(data_root / relative)
        for relative in sorted({**EXPECTED_SOURCE_HASHES, **EXPECTED_CANONICAL_HASHES})
    }
    exporter_relative = str(Path(__file__).resolve().relative_to(ROOT))
    manifest = {
        "authority": {
            "canonical_data_commit": CANONICAL_DATA_COMMIT,
            "contract_version": CONTRACT_VERSION,
            "exporter_commit": exporter_sha,
            "exporter_path": exporter_relative,
            "exporter_sha256": file_sha(Path(__file__).resolve()),
            "fable_result_commit": FABLE_RESULT_COMMIT,
            "hml_semantic_commit": HML_SEMANTIC_COMMIT,
            "source_export_commit": SOURCE_EXPORT_COMMIT,
            "source_manifest_sha256": file_sha(data_root / "manifest.json"),
        },
        "derivation": {
            "input": "byte-identical HML_LINEAR.input_text joined by record_id",
            "kind": "DETERMINISTIC_RECORD_ID_JOIN",
            "semantic_translation": False,
            "target": "byte-identical AST.target_text joined by record_id",
        },
        "files": generated_files,
        "fit": {
            "comparison_counts": {
                split: by_split_fit[split]["comparison_fit"] for split in SPLITS
            },
            "manifest": fit_relative,
            "maxseq": MAXSEQ,
        },
        "goldens": {"checks": len(goldens["checks"]), "path": golden_relative},
        "leakage": {
            "ambiguous": 0,
            "checked": len(leakage_rows),
            "direct_target_revealing": 0,
            "path": leakage_relative,
            "result": "PASS",
        },
        "mechanism_counts": audit["mechanism_counts"],
        "parity": {
            "action_field_counts": audit["action_field_counts"],
            "checks": audit["parity_counts"],
            "result": "PASS",
        },
        "raw_execute_counts": audit["execute_counts"],
        "schema_version": "hmltn-reverse-projection-manifest-1.0.0",
        "source_files": source_files,
        "source_root_manifest_schema": source_manifest["schema_version"],
        "token_audit": {"path": token_relative, "tokenizer": tokenizer_info},
        "view_family": VIEW_FAMILY,
        "view_version": VIEW_VERSION,
    }
    write_json(output_root / manifest_relative, manifest)
    return generated_relatives + [manifest_relative]


def check_rebuild(data_root: Path, output_root: Path, tokenizer_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="hmltn-reverse-projection-") as temp:
        rebuilt_root = Path(temp)
        relatives = build(data_root, rebuilt_root, tokenizer_path)
        mismatches = []
        for relative in relatives:
            expected = output_root / relative
            rebuilt = rebuilt_root / relative
            if not expected.exists() or expected.read_bytes() != rebuilt.read_bytes():
                mismatches.append(relative)
        if mismatches:
            raise AssertionError("deterministic rebuild mismatch: " + ",".join(mismatches))
        print(json.dumps({"files_checked": len(relatives), "result": "PASS"}, sort_keys=True))


def main() -> int:
    default_model = (
        Path.home()
        / ".cache/huggingface/hub/models--mlx-community--gemma-4-E4B-it-qat-4bit"
        / "snapshots"
        / MODEL_REVISION
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=ROOT / "data/vnext_10k")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data/vnext_10k")
    parser.add_argument("--tokenizer-model", type=Path, default=default_model)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_rebuild(args.data_root, args.output_root, args.tokenizer_model)
    else:
        relatives = build(args.data_root, args.output_root, args.tokenizer_model)
        print(json.dumps({"files_written": len(relatives), "result": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
