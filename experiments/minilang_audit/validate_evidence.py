#!/usr/bin/env python3
"""Validate the compact MiniLang audit evidence without the source archive."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_json(name: str):
    with (HERE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest = load_json("source_manifest.json")
    semantics = load_json("operation_semantics.json")
    mapping = load_json("hml_mapping.json")
    stats = load_json("operation_statistics.json")
    failures = load_json("translation_failures.json")

    archive = manifest["archive"]
    assert archive["sha256"] == (
        "1562c84524c0851682e47b32243c0e2dcbfb47daaf6820bcb5c216ae8f12bc82"
    )
    assert archive["md5"] == "6f5a1fe82aa182945f6520f7682fa05f"
    assert archive["official_md5_match"] is True
    assert manifest["identity"]["published_artifact_version"] == "v2"
    assert manifest["license"]["artifact"] == (
        "GNU Affero General Public License v3 or later"
    )

    tree_gz = HERE / "source_tree.txt.gz"
    with gzip.open(tree_gz, "rb") as handle:
        tree = handle.read()
    assert len(tree.splitlines()) == manifest["tree"]["entry_count"] == 42_699
    assert sha256_bytes(tree) == manifest["tree"]["full_tree_sha256"]

    assert len(semantics["operations"]) == 10
    semantic_ids = {entry["semantic_id"] for entry in semantics["operations"]}
    assert semantic_ids == {
        "INTRO",
        "HAVE",
        "CONSIDER_OR",
        "CONSIDER_EXISTS",
        "RULE",
        "CHOOSE",
        "SIMPLIFY",
        "CASE_SPLIT",
        "INDUCT",
        "END_OR_NEXT",
    }
    assert len(mapping["minilang_to_hml"]) == 10
    assert len(mapping["hml_to_minilang"]) == 18
    assert len(mapping["semantic_firewall"]) == 15

    assert stats["translated_proof_count"] == 290_185
    assert stats["total_serialized_commands"] == 1_519_944
    assert stats["unique_implemented_command_labels_observed"] == 17
    assert sum(stats["operation_frequencies"].values()) == 1_519_944

    summary = failures["summary"]
    assert summary["source_goal_count"] == 340_267
    assert summary["verified_refined_translation_count"] == 290_185
    assert summary["recorded_refined_failure_count"] == 39_504
    assert summary["missing_refined_record_count"] == 10_578
    assert sum(summary["recorded_failure_taxonomy"].values()) == 39_504
    assert len(failures["stratified_samples"]) == 165
    assert all(sample["original_isar"] is not None for sample in failures["stratified_samples"])

    examples = []
    with (HERE / "representative_examples.jsonl").open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            assert row["exact_original_isar"]
            assert row["translated_minilang"]
            assert row["source_theorem_identity"]
            assert len(row["provenance_sha256"]) == 64
            examples.append(row)
    assert len(examples) == 78
    reasons = Counter(reason for row in examples for reason in row["selection_reasons"])
    for operation in {
        "INTRO",
        "HAVE",
        "CONSIDER",
        "RULE",
        "CHOOSE",
        "SIMP",
        "CASE_SPLIT",
        "INDUCT",
        "END",
        "NEXT",
    }:
        assert reasons[operation] == 10

    for report in {
        "minilang_artifact_audit.md",
        "minilang_hml_mapping.md",
        "minilang_translation_failure_audit.md",
        "minilang_learning_experiment.md",
        "minilang_hml_implications.md",
    }:
        assert (ROOT / "reports" / report).is_file()

    print("MiniLang compact evidence validation: PASS")
    print(f"archive_sha256={archive['sha256']}")
    print(f"tree_entries={manifest['tree']['entry_count']}")
    print(f"semantic_operations={len(semantics['operations'])}")
    print(f"representative_examples={len(examples)}")


if __name__ == "__main__":
    main()
