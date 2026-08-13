#!/usr/bin/env python3
"""Attest the frozen Codex translation bundle against exact HML VNext semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "contracts/hml_vnext/VNEXT_TRANSLATION_LOCK.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hml-root", type=Path, required=True)
    args = parser.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    expected_commit = lock["hml_semantic_commit"]
    actual_commit = git(args.hml_root, "rev-parse", "HEAD")
    if actual_commit != expected_commit:
        raise SystemExit(f"HML commit mismatch: {actual_commit} != {expected_commit}")
    if git(args.hml_root, "status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("HML runtime checkout is dirty")
    writable = [path for path in args.hml_root.rglob("*") if path.is_file() and path.stat().st_mode & 0o222]
    if writable:
        raise SystemExit(f"HML runtime checkout contains writable files: {writable[:3]}")

    for item in lock["files"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise SystemExit(f"contract hash mismatch: {path}")
    contract_path = ROOT / lock["files"]["json_contract"]["path"]
    fixtures_path = ROOT / lock["files"]["golden_fixtures"]["path"]
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["contract_version"] != lock["contract_version"]:
        raise SystemExit("translation contract version mismatch")
    if not expected_commit.startswith(contract["hml_semantic_commit"]):
        raise SystemExit("translation contract HML commit mismatch")

    source_root = args.hml_root / "src"
    sys.path.insert(0, str(source_root))
    from hamiltonian_lang.semantic_state import (  # type: ignore[import-not-found]
        export_transition,
        import_transition,
        parse_transition,
        render_transition,
        verify_replay,
        verify_runtime,
    )
    from hamiltonian_lang.semantic_state.tree_view import (  # type: ignore[import-not-found]
        parse_tree_transition,
        render_tree_transition,
    )
    from hamiltonian_lang.semantic_state.verify import (  # type: ignore[import-not-found]
        _BRANCH_KINDS,
        _CANDIDATE_KINDS,
        _EXACTNESS_KINDS,
    )

    allowed = contract["allowed_state_effects"]
    assert set(allowed["candidate_effect.kind"]) == set(_CANDIDATE_KINDS)
    assert set(allowed["branch_effect.kind"]) == set(_BRANCH_KINDS)
    assert set(allowed["exactness_effect.kind"]) == set(_EXACTNESS_KINDS)

    fixtures: list[dict[str, Any]] = [
        json.loads(line) for line in fixtures_path.read_text(encoding="utf-8").splitlines() if line
    ]
    assert len(fixtures) == 20
    roundtrips = 0
    refusals = 0
    for fixture in fixtures:
        digest = hashlib.sha256(fixture["source_fragment"].encode("utf-8")).hexdigest()
        assert fixture["expected_provenance"] == f"sha256:{digest}"
        if fixture["expected_refusal"] is not None:
            assert fixture["neutral"] is None
            assert fixture["expected_refusal"] in contract["refusal_codes"]
            refusals += 1
            continue
        assert fixture["neutral"]["source"]["span_sha256"] == digest
        transition = import_transition(fixture["neutral"])
        verify = verify_replay if fixture["trust_mode"] == "replay" else verify_runtime
        result = verify(transition)
        assert str(result.verdict) == fixture["expected_verdict"], (
            fixture["fixture_id"], result.to_dict()
        )
        if fixture["expected_error_class"]:
            assert result.findings
            assert str(result.findings[0].error_class) == fixture["expected_error_class"]
        assert list(transition.action.dependencies) == fixture["expected_dependencies"]
        assert import_transition(export_transition(transition)) == transition
        assert parse_transition(render_transition(transition)) == transition
        assert parse_tree_transition(render_tree_transition(transition)) == transition
        roundtrips += 1
    print(
        json.dumps(
            {
                "contract_version": contract["contract_version"],
                "fixtures": f"{len(fixtures)}/{len(fixtures)}",
                "hml_commit": actual_commit,
                "hml_linear_roundtrips": f"{roundtrips}/{roundtrips}",
                "hml_tree_roundtrips": f"{roundtrips}/{roundtrips}",
                "neutral_roundtrips": f"{roundtrips}/{roundtrips}",
                "refusals": f"{refusals}/{refusals}",
                "result": "PASS",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
