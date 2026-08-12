"""Deterministic Stage-100 generation from current verified corpus transitions."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .audits import jsonl_bytes, write_reports
from .authority import assert_authority, sha256_file
from .mutations import mutate_valid_case
from .records import build_pair, source_bundle_sha
from .verifier_runner import verify_payload


def factory_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_cases(corpus_root: Path) -> list[Path]:
    base = corpus_root / "experiments" / "semantic_firewall" / "data"
    return sorted(
        path
        for split in ("dev", "final")
        for path in (base / split / "cases").glob("*.json")
    )


def generate_records(*, limit: int = 100) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    authority = assert_authority()
    corpus_root = Path(os.environ["CORPUS_ROOT"]).resolve()
    root = factory_root()
    generator_sha = source_bundle_sha(root)
    records: list[dict[str, Any]] = []
    source_verdicts: collections.Counter[str] = collections.Counter()
    source_families: collections.Counter[str] = collections.Counter()
    scanned = source_cases(corpus_root)

    for path in scanned:
        source = json.loads(path.read_text(encoding="utf-8"))
        checked = verify_payload(source)
        original = checked["replay"]
        source_verdicts[original["verdict"]] += 1
        if original["verdict"] != "VALID":
            continue
        mutation = mutate_valid_case(source)
        counterfactual_checked = verify_payload(mutation.payload)
        mutated = counterfactual_checked["replay"]
        if mutated["verdict"] == "UNRESOLVED":
            raise RuntimeError(
                f"{source['case_id']}: mutation became UNRESOLVED; never convert it to INVALID"
            )
        if mutated["verdict"] != "INVALID":
            raise RuntimeError(
                f"{source['case_id']}: counterfactual is {mutated['verdict']}, expected INVALID"
            )
        pair = build_pair(
            source=source,
            mutated=mutation.payload,
            mutation_family=mutation.family,
            mutation_description=mutation.description,
            expected_error_class=mutation.expected_error_class,
            original_result=original,
            mutated_result=mutated,
            original_runtime_result=checked["runtime_without_attestations"],
            mutated_runtime_result=counterfactual_checked["runtime_without_attestations"],
            generator_sha=generator_sha,
            source_path=str(path.relative_to(corpus_root)),
            source_file_sha256=sha256_file(path),
        )
        records.append(pair)
        source_families[mutation.family] += 1

    records.sort(key=lambda row: row["pair_id"])
    if len(records) < limit:
        raise RuntimeError(f"only {len(records)} certified pairs available; requested {limit}")
    records = records[:limit]
    if limit == 100 and len(records) != 100:
        raise RuntimeError("Stage 100 must contain exactly 100 pairs")

    source_manifest = {
        "source": "current corpus Semantic Firewall DEV and FINAL cases",
        "authority": authority["corpus"],
        "files_scanned": len(scanned),
        "source_verdict_distribution": dict(sorted(source_verdicts.items())),
        "certified_valid_sources_selected": len(records),
        "selected_family_distribution": dict(sorted(source_families.items())),
        "selection_rule": (
            "No label file is consulted. Import every current DEV/FINAL case through frozen "
            "HML and retain only records whose current replay verdict is VALID."
        ),
        "lean_scale_source": authority["lean_canonical"],
        "lean_scale_status": "PINNED_NOT_YET_A_VERIFIER_TRANSITION_SOURCE",
    }
    # A second full authority check catches source/HML mutation during generation.
    after = assert_authority()
    for section, fields in {
        "hml": ("sha", "tree_hash", "working_tree_clean", "writable_file_count"),
        "lean_canonical": ("sha256", "bytes", "records"),
        "corpus": ("authority_sha", "semantic_firewall_tree"),
    }.items():
        for field in fields:
            if authority[section][field] != after[section][field]:
                raise RuntimeError(f"authority changed during generation: {section}.{field}")
    return records, source_manifest


def write_stage100(*, output: Path | None = None) -> dict[str, Any]:
    root = factory_root()
    authority = assert_authority()
    records, source_manifest = generate_records(limit=100)
    payload = jsonl_bytes(records)
    dataset_sha = hashlib.sha256(payload).hexdigest()
    output = output or root / "data" / "stage100" / "canonical_pairs.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(output)
    generator_sha = records[0]["generator_sha"]
    audits = write_reports(
        factory_root=root,
        authority=authority,
        records=records,
        source_manifest=source_manifest,
        dataset_sha256=dataset_sha,
        generator_sha=generator_sha,
    )
    (root / "manifests" / "authority.json").write_text(
        json.dumps(authority, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "output": str(output),
        "records": len(records),
        "sha256": dataset_sha,
        "generator_sha256": generator_sha,
        **audits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, choices=[100], default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = write_stage100(output=args.output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
