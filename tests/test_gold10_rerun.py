#!/usr/bin/env python3
"""Corpus-side regression and soundness probes for the controlled Gold-10 rerun."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HML = ROOT / "hml_core"
PIN = "5688aba18632b65a8709aa1d85577d31a67dba6a"
BASE = "467a4866756e6653c1b618a1eed479cda8d5927a"

sys.dont_write_bytecode = True
sys.path.insert(0, str(HML / "src"))

from hamiltonian_lang import compile_source  # noqa: E402
from hamiltonian_lang.ast.nodes import GoalStatus, Ref, walk  # noqa: E402
from hamiltonian_lang.reasoning.binders import CaptureError, instantiate  # noqa: E402


G06 = """module G06
var P : Bool
var Q : Bool
assume a1 : P implies Q
assume a2 : Q
goal g0 : P
"""
WITNESSES = "holds := P and Q, fails := (not P) and Q"
CERT = (
    "evidence e1 : determines_neither P from a1, a2 "
    "by propositional_underdetermination_v1(" + WITNESSES + ")\n"
)


def _errors(result):
    return [f"{d.code}:{d.message}" for d in result.diagnostics.items]


def _canonical_payload(doc: dict) -> dict:
    """Remove only Phase-B rendering/pin metadata; retain mathematics and oracles."""
    out = copy.deepcopy(doc)
    out.pop("renderings", None)
    out.get("verification", {}).pop("hml_core_sha", None)
    return out


def _old_doc(relative: str) -> dict:
    result = subprocess.run(
        ["git", "show", f"{BASE}:{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_same_gold10_math_and_oracles_are_frozen() -> None:
    for path in sorted((ROOT / "data" / "gold_10").glob("G*.json")):
        relative = path.relative_to(ROOT).as_posix()
        current = json.loads(path.read_text(encoding="utf-8"))
        assert _canonical_payload(current) == _canonical_payload(_old_doc(relative)), relative


def test_adapted_gold10_has_expected_semantic_outcomes() -> None:
    expected = {
        "G01_equation_isolation": ("VERIFIED", "VALID"),
        "G02_algebraic_substitution": ("VERIFIED", "VALID"),
        "G03_function_dependency_chain": (None, "VALID"),
        "G04_inequality_transform": ("PROVED", None),
        "G05_direct_implication": ("PROVED", None),
        "G06_implication_undetermined": ("UNDERDETERMINED", "VALID"),
        "G07_quantifier_binder": ("OPEN", None),
        "G08_contrapositive": ("PROVED", None),
        "G09_probability_conditioning": (None, "VALID"),
        "G10_calculus_precondition": (None, "VALID"),
    }
    env = os.environ.copy()
    env["PYTHONPATH"] = str(HML / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for path in sorted((ROOT / "examples" / "gold_10").glob("*/hml/program.hml")):
        result = subprocess.run(
            [sys.executable, "-m", "hamiltonian_lang.cli", "check", str(path)],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{path}: {result.stderr}"
        key = path.parts[-3]
        goal, evidence = expected[key]
        if goal:
            assert goal in result.stdout, f"{key}: {result.stdout}"
        if evidence:
            compiled = compile_source(path.read_text(encoding="utf-8"), str(path))
            assert compiled.ok()
            assert evidence in compiled.reasoning.evidence_status.values(), key


def test_unknown_is_not_underdetermined() -> None:
    result = compile_source(G06, "<unknown>")
    assert result.ok()
    assert result.reasoning.goal_status["g0"] == GoalStatus.OPEN
    assert result.reasoning.goal_status["g0"] != GoalStatus.UNDERDETERMINED


def test_stale_context_certificate_is_rejected() -> None:
    result = compile_source(G06 + CERT + "assume a3 : P\nundetermined g0 by e1\n", "<stale>")
    assert not result.ok()
    assert any("different context" in error for error in _errors(result))
    assert result.reasoning.goal_status["g0"] != GoalStatus.UNDERDETERMINED


def test_wrong_context_and_forged_certificate_are_rejected() -> None:
    wrong_context = compile_source(
        G06
        + "evidence e1 : determines_neither P from a1 "
        + "by propositional_underdetermination_v1(" + WITNESSES + ")\n"
        + "undetermined g0 by e1\n",
        "<wrong-context>",
    )
    assert not wrong_context.ok()
    assert any("every established claim" in error for error in _errors(wrong_context))

    forged = compile_source(
        G06
        + "evidence e1 : determines_neither P from a1, a2 "
        + "by propositional_underdetermination_v1(holds := P and not Q, fails := (not P) and Q)\n"
        + "undetermined g0 by e1\n",
        "<forged>",
    )
    assert not forged.ok()
    assert any("does not satisfy premise" in error for error in _errors(forged))


def test_unregistered_checker_cannot_enter_the_trusted_boundary() -> None:
    result = compile_source(
        G06
        + "evidence e1 : determines_neither P from a1, a2 by no_such_checker()\n"
        + "undetermined g0 by e1\n",
        "<unregistered>",
    )
    assert not result.ok()
    assert any("not a registered trusted checker" in error for error in _errors(result))
    assert result.reasoning.goal_status["g0"] != GoalStatus.UNDERDETERMINED


def test_quantifier_wrong_domain_and_witness_specific_intro_are_rejected() -> None:
    wrong_domain = compile_source(
        """module Q
var r : Real
assume a1 : forall x : Natural . x >= 0.0
derive d1 : r >= 0.0 from a1 by forall_elim(at := r)
""",
        "<wrong-domain>",
    )
    assert not wrong_domain.ok()
    assert any("does not inhabit the binder's domain" in error for error in _errors(wrong_domain))

    witness_specific = compile_source(
        """module Q
var a : Natural
assume a1 : forall x : Natural . x >= 0.0
assume a2 : a = 0.0
derive d1 : a >= 0.0 from a1 by forall_elim(at := a)
derive d2 : forall a : Natural . a >= 0.0 from d1 by forall_intro(var := a)
""",
        "<witness-specific>",
    )
    assert not witness_specific.ok()
    assert any("is not arbitrary" in error for error in _errors(witness_specific))


def test_binder_capture_is_rejected_at_the_corpus_import_boundary() -> None:
    result = compile_source(
        """module B
goal g1 : forall x : Natural . x >= 0.0
goal g2 : forall y : Natural . y >= 1.0
""",
        "<capture>",
    )
    assert result.ok()
    outer = next(s.proposition for s in result.module.statements if getattr(s, "label", None) == "g1")
    other = next(s.proposition for s in result.module.statements if getattr(s, "label", None) == "g2")
    bound_ref = next(x for x in walk(other) if isinstance(x, Ref) and x.symbol_id.depth > 0)
    try:
        instantiate(outer, bound_ref)
    except CaptureError:
        pass
    else:
        raise AssertionError("binder capture was not rejected")


def test_hml_pin_cleanliness_and_git_record_are_enforced() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "check_hml_core_pin.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert subprocess.run(
        ["git", "-C", str(HML), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == PIN
    assert subprocess.run(
        ["git", "-C", str(HML), "status", "--porcelain", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout == ""
    assert not [p for p in HML.rglob("*") if p.is_file() and p.stat().st_mode & 0o222]


if __name__ == "__main__":
    for name in sorted(name for name in globals() if name.startswith("test_")):
        globals()[name]()
        print(f"{name}: PASS")
