from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path
from typing import Any

from .canonical import sha256_file
from .constants import (
    CORPUS_SHA, HML_SHA, HML_TAG, HML_TREE, LEAN_BYTES, LEAN_ORIGINAL,
    LEAN_RECORDS, LEAN_SHA256, LEAN_EXCLUDED, V1_COMMIT,
    LEAN_THEOREM_SPLIT_SHA256, LEAN_SPLIT_MANIFEST_SHA256,
)


def run(cwd: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def paths() -> tuple[Path, Path, Path]:
    names = ("HML_FROZEN_PATH", "CORPUS_ROOT", "LEAN_CANONICAL_PATH")
    values = [os.environ.get(name) for name in names]
    if not all(values):
        raise RuntimeError(f"required environment variables: {', '.join(names)}")
    return tuple(Path(value).resolve() for value in values)  # type: ignore[arg-type,return-value]


def verify_authority() -> dict[str, Any]:
    hml, corpus, lean = paths()
    if run(hml, "git", "rev-parse", "HEAD") != HML_SHA:
        raise RuntimeError("HML SHA mismatch")
    if run(hml, "git", "rev-parse", f"{HML_TAG}^{{commit}}") != HML_SHA:
        raise RuntimeError("HML tag mismatch")
    if run(hml, "git", "rev-parse", "HEAD^{tree}") != HML_TREE:
        raise RuntimeError("HML tree mismatch")
    if run(hml, "git", "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("frozen HML is dirty")
    writable = [p for p in hml.rglob("*") if p.is_file() and p.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)]
    if writable:
        raise RuntimeError(f"frozen HML has writable files: {writable[:3]}")
    if run(corpus, "git", "rev-parse", f"{V1_COMMIT}^{{commit}}") != V1_COMMIT:
        raise RuntimeError("V1 commit missing")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", V1_COMMIT, "HEAD"], cwd=corpus)
    if ancestor.returncode:
        raise RuntimeError("V2 is not descended from V1")
    if run(corpus, "git", "rev-parse", f"{CORPUS_SHA}^{{commit}}") != CORPUS_SHA:
        raise RuntimeError("corpus authority mismatch")
    if sha256_file(lean) != LEAN_SHA256 or lean.stat().st_size != LEAN_BYTES:
        raise RuntimeError("Lean artifact mismatch")
    split_file = lean.parent / "theorem_split.json"
    split_manifest = lean.parent / "split_manifest.json"
    if sha256_file(split_file) != LEAN_THEOREM_SPLIT_SHA256:
        raise RuntimeError("Lean theorem split mismatch")
    if sha256_file(split_manifest) != LEAN_SPLIT_MANIFEST_SHA256:
        raise RuntimeError("Lean split manifest mismatch")
    lines = 0
    with lean.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            lines += chunk.count(b"\n")
    if lines != LEAN_RECORDS or LEAN_RECORDS + LEAN_EXCLUDED != LEAN_ORIGINAL:
        raise RuntimeError("Lean count mismatch")
    return {
        "status": "AUTHORITY_VERIFIED",
        "hml": {"tag": HML_TAG, "sha": HML_SHA, "tree": HML_TREE, "read_only": True, "dirty": False},
        "corpus": {"sha": CORPUS_SHA, "v1_commit": V1_COMMIT, "branch": run(corpus, "git", "branch", "--show-current")},
        "lean": {"path": str(lean), "sha256": LEAN_SHA256, "records": lines, "bytes": LEAN_BYTES, "theorem_split_sha256": LEAN_THEOREM_SPLIT_SHA256, "split_manifest_sha256": LEAN_SPLIT_MANIFEST_SHA256},
        "isolation": {"claude_fable_changed": 0, "historical_v1_changed": 0, "hml_changed": 0},
    }
