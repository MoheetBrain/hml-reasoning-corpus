#!/usr/bin/env python3
"""Build or verify the refusal-package manifest for the final structural mission."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ESCAPE_RE = re.compile(rb"\\u[0-9a-fA-F]{4}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> list[dict]:
    data_root = root / "data" / "hml_structural_final"
    paths = [
        path for path in data_root.rglob("*")
        if path.is_file() and path.name not in {
            "STRUCTURAL_MANIFEST.json", "STRUCTURAL_MANIFEST.sha256"
        }
    ]
    paths.extend([
        root / "scripts" / "structural_final" / "scan_lean_structure.py",
        root / "scripts" / "structural_final" / "scan_lean_raw.py",
        root / "scripts" / "structural_final" / "build_manifest.py",
        root / "tests" / "test_structural_final.py",
    ])
    return [
        {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(set(paths))
    ]


def build(root: Path) -> dict:
    return {
        "artifact": "hml_structural_final_refusal_package_v1",
        "verdict": "INSUFFICIENT_STRUCTURAL_DATA",
        "created_utc_date": "2026-08-17",
        "corpus_base_commit": "91fdda35851caa0445c1becdb1d7a756d5bcee3d",
        "semantic_authority": "68178f07784d2a17a9aed9c4dedbea9c740c97a0",
        "semantic_consolidation_checkout": "73184c5",
        "frozen_hml_submodule_untouched": "5688aba18632b65a8709aa1d85577d31a67dba6a",
        "source": {
            "name": "LeanDojo Benchmark 4 random split",
            "mathlib_commit": "29dcec074de168ac2bf835a77ef68bbe069194c5",
            "archive_sha256_reported_truncated": "19b9a319...a98a4",
            "archive_sha256_note": "The upstream local manifest records only this truncated value; no full digest is asserted here.",
            "canonical_rows": 241265,
            "canonical_sha256": "8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869",
            "raw_transitions_scanned": 259580,
            "fresh_exact_transitions": 216623,
            "old_history_transitions_excluded": 42957,
        },
        "selection": {
            "seed": 20260817,
            "admitted_records": 0,
            "model_facing_views_emitted": 0,
            "reason": "Frozen population readiness gate failed before selection.",
        },
        "files": inventory(root),
    }


def write(root: Path) -> None:
    target = root / "data" / "hml_structural_final" / "STRUCTURAL_MANIFEST.json"
    payload = json.dumps(build(root), ensure_ascii=False, indent=2) + "\n"
    target.write_text(payload, encoding="utf-8")
    sidecar = target.with_suffix(".sha256")
    sidecar.write_text(f"{sha256(target)}  {target.name}\n", encoding="utf-8")


def verify(root: Path) -> None:
    target = root / "data" / "hml_structural_final" / "STRUCTURAL_MANIFEST.json"
    actual = json.loads(target.read_text(encoding="utf-8"))
    expected = build(root)
    if actual != expected:
        raise SystemExit("manifest content does not match current files")
    expected_sidecar = f"{sha256(target)}  {target.name}\n"
    sidecar = target.with_suffix(".sha256").read_text(encoding="utf-8")
    if sidecar != expected_sidecar:
        raise SystemExit("manifest sidecar digest mismatch")
    for path in (root / "data" / "hml_structural_final").rglob("*.json"):
        if path == target:
            continue
        if ESCAPE_RE.search(path.read_bytes()):
            raise SystemExit(f"literal Unicode escape found in {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.root.resolve())
    else:
        write(args.root.resolve())


if __name__ == "__main__":
    main()
