#!/usr/bin/env python3
"""Read-only probes mapping firewall requirements to pinned HML behavior."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HML = ROOT / "hml_core"
HML_SRC = HML / "src"
OUTPUT = ROOT / "experiments/semantic_firewall/results/current_hml_probe.json"
EXPECTED_SHA = "5688aba18632b65a8709aa1d85577d31a67dba6a"

sys.path.insert(0, str(HML_SRC))

from hamiltonian_lang import compile_source  # noqa: E402


def status(result: Any, label: str) -> str | None:
    return (result.reasoning.derivation_status or {}).get(label) if result.reasoning else None


def probe(name: str, source: str, expectation: dict[str, Any]) -> dict[str, Any]:
    result = compile_source(source, f"<semantic-firewall:{name}>")
    return {
        "probe_id": name,
        "ok": result.ok(),
        "diagnostic_codes": [diagnostic.code for diagnostic in result.diagnostics.items],
        "derivation_status": dict(result.reasoning.derivation_status) if result.reasoning else {},
        "goal_status": dict(result.reasoning.goal_status) if result.reasoning else {},
        "open_obligations": [obligation.to_dict() for obligation in result.reasoning.open_obligations()] if result.reasoning else [],
        "expectation": expectation,
    }


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    hml_before = git("-C", "hml_core", "status", "--porcelain", "--untracked-files=all")
    if hml_before:
        raise RuntimeError("hml_core is dirty before read-only probes")
    actual_sha = git("-C", "hml_core", "rev-parse", "HEAD")
    if actual_sha != EXPECTED_SHA:
        raise RuntimeError(f"unexpected HML SHA {actual_sha}")

    prelude = "module M\nvar x : Real\nvar y : Real\nvar k : Real\n"
    probes = [
        probe(
            "DEP-LEGAL",
            prelude
            + "assume a1 : y = 2.0 * x\n"
            + "derive d1 : 2.0 * x = y from a1 by symmetry\n"
            + "derive d2 : y = 2.0 * x from d1 by symmetry\n",
            {"ok": True, "d2": "VERIFIED"},
        ),
        probe(
            "DEP-FUTURE-ILLEGAL",
            prelude
            + "derive d1 : 2.0 * x = y from a1 by symmetry\n"
            + "assume a1 : y = 2.0 * x\n",
            {"ok": False, "diagnostic": "HML-R703"},
        ),
        probe(
            "SCOPE-LEGAL",
            prelude + "scope\n    assume x > 0.0\n    require log(x) = log(x)\nend\n",
            {"ok": True},
        ),
        probe(
            "SCOPE-LEAK-ILLEGAL",
            prelude + "scope\n    assume x > 0.0\nend\nrequire log(x) = log(x)\n",
            {"ok": False},
        ),
        probe(
            "PRECONDITION-DISCHARGED",
            prelude
            + "assume p0 : k != 0.0\nassume p1 : x = y\n"
            + "derive d1 : x / k = y / k from p1 by divide_both_sides(by := k)\n",
            {"ok": True, "d1": "VERIFIED"},
        ),
        probe(
            "PRECONDITION-OPEN",
            prelude
            + "assume p1 : x = y\n"
            + "derive d1 : x / k = y / k from p1 by divide_both_sides(by := k)\n",
            {"d1": "CHECKED", "open_obligations": 1},
        ),
        probe(
            "PRECONDITION-REFUTED",
            prelude
            + "assume p1 : x = y\n"
            + "derive d1 : x * (1.0 / 0.0) = y * (1.0 / 0.0) from p1 by multiply_both_sides(by := 1.0 / 0.0)\n",
            {"ok": False, "d1": "REJECTED", "diagnostic": "HML-R715"},
        ),
        probe(
            "OBLIGATION-PROPAGATES",
            prelude
            + "assume a1 : y = 2.0 * x\n"
            + "derive d1 : y / k = 2.0 * x / k from a1 by divide_both_sides(by := k)\n"
            + "derive d2 : 2.0 * x / k = y / k from d1 by symmetry\n",
            {"d1": "CHECKED", "d2": "CHECKED"},
        ),
        probe(
            "WARRANT-UNKNOWN-ILLEGAL",
            prelude
            + "assume a1 : y = 2.0 * x\n"
            + "derive d1 : y = 2.0 * x from a1 by invented_rule\n",
            {"ok": False, "diagnostic": "HML-R704"},
        ),
        probe(
            "EPISTEMIC-COMPUTED",
            prelude
            + "assume a1 : y = 2.0 * x\n"
            + "derive d1 : 2.0 * x = y from a1 by symmetry\n",
            {"ok": True, "d1": "VERIFIED", "source_cannot_set_status": True},
        ),
        probe(
            "GOAL-LEGAL",
            prelude
            + "assume a1 : y = 2.0 * x\n"
            + "goal g1 : 2.0 * x = y\n"
            + "derive d1 : 2.0 * x = y from a1 by symmetry\n"
            + "proved g1 by d1\n",
            {"ok": True, "d1": "VERIFIED", "g1": "PROVED"},
        ),
        probe(
            "TYPE-DOMAIN-ILLEGAL",
            "module M\nparam x : Real\nrequire log(x) = log(x)\n",
            {"ok": False, "type_guard": "PositiveReal"},
        ),
        probe(
            "TYPE-DOMAIN-LEGAL",
            "module M\nparam x : PositiveReal\nrequire log(x) = log(x)\n",
            {"ok": True},
        ),
    ]

    result = {
        "probe_version": "semantic-firewall-current-hml-0.1.0",
        "hml_core_sha": actual_sha,
        "hml_modified": False,
        "probes": probes,
        "static_findings": [
            {
                "requirement": "CANDIDATES",
                "support": "CURRENT_HML_NOT_EXPRESSIBLE",
                "evidence": "No first-class candidate node or candidate verification lifecycle exists in ast/nodes.py or reasoning/check.py.",
            },
            {
                "requirement": "BRANCH_JOIN",
                "support": "CURRENT_HML_NOT_EXPRESSIBLE",
                "evidence": "ScopeStmt provides lexical frames, but no case partition, exhaustive/disjoint certificate, or safe join rule exists.",
            },
            {
                "requirement": "WARRANT",
                "support": "CURRENT_HML_PARTIAL",
                "evidence": "Trusted kernel rules and a static checked-certificate registry exist; broad theorem/domain evidence adapters do not.",
            },
        ],
    }
    hml_after = git("-C", "hml_core", "status", "--porcelain", "--untracked-files=all")
    if hml_after:
        raise RuntimeError("hml_core changed during read-only probes")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"hml_core_sha": actual_sha, "probes": len(probes), "hml_modified": False}, indent=2))


if __name__ == "__main__":
    main()

