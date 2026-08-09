#!/usr/bin/env python3
"""Verify that the frozen HML submodule is clean and pinned as recorded."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "schemas" / "project_metadata.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def fail(message: str) -> None:
    print(f"hml_core pin check failed: {message}", file=sys.stderr)
    raise SystemExit(1)


try:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    fail(f"cannot read {METADATA_PATH}: {exc}")

expected = metadata.get("hml_commit_sha")
if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
    fail("metadata must contain a full 40-character hml_commit_sha")

try:
    actual = git("-C", "hml_core", "rev-parse", "HEAD")
    if actual != expected:
        fail(f"hml_core HEAD is {actual}, expected {expected}")

    submodule_status = git(
        "-C", "hml_core", "status", "--porcelain", "--untracked-files=all"
    )
    if submodule_status:
        fail(f"hml_core is dirty:\n{submodule_status}")

    tree = git("ls-tree", "HEAD", "hml_core").split()
    if len(tree) < 3 or tree[0] != "160000" or tree[1] != "commit":
        fail("HEAD does not record hml_core as a git submodule")
    if tree[2] != expected:
        fail(f"recorded submodule commit is {tree[2]}, expected {expected}")
except RuntimeError as exc:
    fail(str(exc))

print(f"hml_core is clean and pinned to {expected}")
