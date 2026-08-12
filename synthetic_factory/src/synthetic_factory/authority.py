"""Fail-closed recovery and checking of every immutable authority input."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path
from typing import Any

from .constants import (
    CORPUS_SHA,
    HML_SHA,
    HML_TAG,
    HML_TREE,
    LEAN_CANONICAL_BYTES,
    LEAN_CANONICAL_RECORDS,
    LEAN_CANONICAL_SHA256,
    LEAN_EXCLUDED_GOAL_CREATION,
    LEAN_ORIGINAL_TRANSITIONS,
    LEAN_THEOREMS,
    MODEL_EXPERIMENT_SHA,
)


class AuthorityError(RuntimeError):
    """An authority gate failed; generation must not continue."""


def _run(cwd: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise AuthorityError(f"{' '.join(args)} failed in {cwd}: {detail}")
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int:
    count = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            count += chunk.count(b"\n")
    return count


def writable_files(root: Path) -> list[str]:
    writable: list[str] = []
    mask = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    for path in root.rglob("*"):
        if path.is_file() and path.stat().st_mode & mask:
            writable.append(str(path.relative_to(root)))
            if len(writable) >= 20:
                break
    return writable


def _corpus_source_tree(corpus: Path) -> str:
    return _run(
        corpus,
        "git",
        "rev-parse",
        f"{CORPUS_SHA}:experiments/semantic_firewall",
    )


def recover_authority(
    *, hml_root: Path, corpus_root: Path, lean_records: Path
) -> dict[str, Any]:
    hml_root = hml_root.resolve()
    corpus_root = corpus_root.resolve()
    lean_records = lean_records.resolve()
    for path, label in (
        (hml_root, "HML checkout"),
        (corpus_root, "corpus checkout"),
        (lean_records, "Lean canonical artifact"),
    ):
        if not path.exists():
            raise AuthorityError(f"{label} does not exist: {path}")

    hml_head = _run(hml_root, "git", "rev-parse", "HEAD")
    resolved_tag = _run(hml_root, "git", "rev-parse", f"{HML_TAG}^{{commit}}")
    hml_tree = _run(hml_root, "git", "rev-parse", "HEAD^{tree}")
    hml_status = _run(hml_root, "git", "status", "--porcelain", "--untracked-files=all")
    hml_remote = _run(hml_root, "git", "remote", "get-url", "origin")
    hml_date = _run(hml_root, "git", "show", "-s", "--format=%cI", "HEAD")
    writable = writable_files(hml_root)

    if hml_head != HML_SHA or resolved_tag != HML_SHA:
        raise AuthorityError(
            f"HML authority mismatch: HEAD={hml_head}, {HML_TAG}={resolved_tag}, expected={HML_SHA}"
        )
    if hml_tree != HML_TREE:
        raise AuthorityError(f"HML tree mismatch: {hml_tree}, expected {HML_TREE}")
    if hml_status:
        raise AuthorityError(f"frozen HML checkout is dirty:\n{hml_status}")
    if writable:
        raise AuthorityError(f"frozen HML contains writable files: {writable}")

    baseline = _run(corpus_root, "git", "rev-parse", f"{CORPUS_SHA}^{{commit}}")
    if baseline != CORPUS_SHA:
        raise AuthorityError(f"corpus baseline does not resolve exactly: {baseline}")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", CORPUS_SHA, "HEAD"],
        cwd=corpus_root,
        check=False,
    )
    if ancestor.returncode:
        raise AuthorityError(f"current branch is not based on corpus authority {CORPUS_SHA}")
    fixture_diff = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            CORPUS_SHA,
            "--",
            "experiments/semantic_firewall",
            "experiments/semantic_firewall_v2",
        ],
        cwd=corpus_root,
        check=False,
    )
    if fixture_diff.returncode:
        raise AuthorityError("current Semantic Firewall sources differ from the corpus authority")
    corpus_branch = _run(corpus_root, "git", "branch", "--show-current")
    corpus_remote = _run(corpus_root, "git", "remote", "get-url", "origin")

    lean_hash = sha256_file(lean_records)
    lean_lines = line_count(lean_records)
    lean_bytes = lean_records.stat().st_size
    if lean_hash != LEAN_CANONICAL_SHA256:
        raise AuthorityError(f"Lean artifact SHA mismatch: {lean_hash}")
    if lean_lines != LEAN_CANONICAL_RECORDS:
        raise AuthorityError(f"Lean record count mismatch: {lean_lines}")
    if lean_bytes != LEAN_CANONICAL_BYTES:
        raise AuthorityError(f"Lean artifact byte count mismatch: {lean_bytes}")
    if LEAN_CANONICAL_RECORDS + LEAN_EXCLUDED_GOAL_CREATION != LEAN_ORIGINAL_TRANSITIONS:
        raise AuthorityError("Lean inclusion/exclusion arithmetic does not reconcile")

    return {
        "status": "AUTHORITY_VERIFIED",
        "hml": {
            "remote_url": hml_remote,
            "tag": HML_TAG,
            "sha": hml_head,
            "commit_date": hml_date,
            "tree_hash": hml_tree,
            "working_tree_clean": True,
            "writable_file_count": 0,
            "absolute_path": str(hml_root),
        },
        "corpus": {
            "remote_url": corpus_remote,
            "authority_sha": CORPUS_SHA,
            "current_branch": corpus_branch,
            "semantic_firewall_tree": _corpus_source_tree(corpus_root),
            "source_fixtures_unchanged_from_authority": True,
            "absolute_path": str(corpus_root),
        },
        "lean_canonical": {
            "absolute_path": str(lean_records),
            "sha256": lean_hash,
            "bytes": lean_bytes,
            "records": lean_lines,
            "represented_theorems": LEAN_THEOREMS,
            "excluded_goal_creation": LEAN_EXCLUDED_GOAL_CREATION,
            "original_transitions": LEAN_ORIGINAL_TRANSITIONS,
            "reconciles_exactly": True,
            "source_experiment_git_sha": MODEL_EXPERIMENT_SHA,
        },
        "isolation": {
            "claude_fable_files_changed": 0,
            "historical_codex_files_changed": 0,
            "frozen_hml_files_changed": 0,
        },
    }


def default_paths() -> tuple[Path, Path, Path]:
    hml = os.environ.get("HML_FROZEN_PATH")
    corpus = os.environ.get("CORPUS_ROOT")
    lean = os.environ.get("LEAN_CANONICAL_PATH")
    missing = [name for name, value in (
        ("HML_FROZEN_PATH", hml),
        ("CORPUS_ROOT", corpus),
        ("LEAN_CANONICAL_PATH", lean),
    ) if not value]
    if missing:
        raise AuthorityError(f"required environment variable(s) missing: {', '.join(missing)}")
    return Path(hml), Path(corpus), Path(lean)


def assert_authority() -> dict[str, Any]:
    hml, corpus, lean = default_paths()
    return recover_authority(hml_root=hml, corpus_root=corpus, lean_records=lean)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    authority = assert_authority()
    rendered = json.dumps(authority, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
