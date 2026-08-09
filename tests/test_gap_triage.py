"""Read-only diagnostics supporting the Gold-10 semantic-gap handoff.

This test deliberately inspects the frozen submodule as text and through Git. It does
not import code from ``hml_core`` or write Python bytecode there, and it does not edit
or regenerate any trajectory.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HML = ROOT / "hml_core"
PIN = "164d1946e91216c093478132caa0d06427259682"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_submodule_is_clean_pinned_and_read_only() -> None:
    head = subprocess.run(
        ["git", "-C", str(HML), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head == PIN

    status = subprocess.run(
        ["git", "-C", str(HML), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert status == ""

    writable = [
        str(path.relative_to(ROOT))
        for path in HML.rglob("*")
        if path.is_file() and path.stat().st_mode & 0o222
    ]
    assert writable == [], f"hml_core has writable files: {writable}"


def test_gold10_baseline_counts_are_unchanged() -> None:
    actions = []
    for path in sorted((ROOT / "data" / "gold_10").glob("G*.json")):
        actions.extend(json.loads(path.read_text(encoding="utf-8"))["actions"])

    assert len(actions) == 23
    assert sum(a["hml_support"] == "EXPRESSIBLE_CURRENT_HML" for a in actions) == 11
    assert sum(a["hml_support"] == "EXPRESSIBLE_WITH_LIBRARY" for a in actions) == 8
    assert sum(a["hml_support"] == "REQUIRES_NEW_CORE_SEMANTIC" for a in actions) == 3
    assert sum(a["hml_support"] == "AMBIGUOUS_OR_HUMAN_IMPLICIT" for a in actions) == 1


def test_triage_report_covers_all_six_gaps_and_required_classes() -> None:
    report = _read("reports/GOLD_10_GAP_TRIAGE_HANDOFF.md")
    for gap in range(1, 7):
        gap_id = f"GAP-{gap:04d}"
        assert report.count(gap_id) >= 2

    for classification in (
        "CORE_SEMANTIC_MISSING",
        "LIBRARY_MISSING",
        "TRANSLATION/CANONICALIZATION_PROBLEM",
    ):
        assert classification in report


def test_frozen_hml_capabilities_and_v2_boundaries_are_present() -> None:
    kernel = _read("hml_core/src/hamiltonian_lang/reasoning/kernel.py")
    nodes = _read("hml_core/src/hamiltonian_lang/ast/nodes.py")
    evaluator = _read("hml_core/src/hamiltonian_lang/verification/obligations/evaluate.py")
    checkers = _read("hml_core/src/hamiltonian_lang/verification/obligations/checkers.py")
    schema = _read("schemas/trajectory.schema.json")

    # Current v2 kernel boundary: structural rules exist, but these Gold-10 domain
    # operations are not trusted v2 rules.
    assert '"modus_ponens"' in kernel
    assert '"conditional_product"' not in kernel
    assert '"universal_introduction"' not in kernel
    assert '"differentiate"' not in kernel

    # Current HML already has evaluation infrastructure, while its v2 goal status set
    # does not yet include a certified underdetermination terminal state.
    assert "def evaluate(" in evaluator
    assert "functions" in evaluator
    assert "closed_arithmetic_equality" in checkers
    assert "UNDETERMINED" not in nodes

    # The neutral schema can record the distinction, but its action support field is
    # still a single coarse classification; this is a diagnostic fact for the handoff.
    assert '"GAP_DOCUMENTED"' in schema
    assert '"verified_as_undetermined"' in schema
    assert '"hml_support"' in schema
