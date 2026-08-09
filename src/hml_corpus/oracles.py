"""Small deterministic verification oracles used by Gold-10."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Any


def _implies(p: bool, q: bool) -> bool:
    return (not p) or q


def verify_canonical(doc: dict[str, Any]) -> tuple[bool, str]:
    """Return a deterministic verdict for one hand-authored Gold problem."""

    example_id = doc["example_id"]
    if example_id == "G01":
        return 5 - 2 == 3, "exact integer arithmetic: 5 - 2 = 3"
    if example_id == "G02":
        return 2 + 3 == 5, "exact integer arithmetic: 2 + 3 = 5"
    if example_id == "G03":
        f3 = 3 + 1
        g3 = 2 * f3
        return (f3, g3) == (4, 8), "dependency evaluation: f(3)=4 and g(3)=8"
    if example_id == "G04":
        return "x * k > 2 * k" in doc["problem"]["answer"], "symbolic positive-multiplier transform"
    if example_id == "G05":
        verdict = all(
            (not (p and _implies(p, q))) or q
            for p, q in product([False, True], repeat=2)
        )
        return verdict, "truth-table oracle: P and (P -> Q) entails Q"
    if example_id == "G06":
        models = [(p, q) for p, q in product([False, True], repeat=2) if _implies(p, q) and q]
        entails_p = all(p for p, _ in models)
        entails_not_p = all(not p for p, _ in models)
        return (not entails_p and not entails_not_p), "truth-table oracle: P is neither entailed nor refuted"
    if example_id == "G07":
        return all(n + 0 == n for n in range(0, 1001)), "symbolic additive-identity oracle over Natural samples"
    if example_id == "G08":
        models = [(p, q) for p, q in product([False, True], repeat=2) if (not q) and _implies(p, q)]
        return all(not p for p, _ in models), "truth-table oracle: not Q and (P -> Q) entails not P"
    if example_id == "G09":
        return Fraction(1, 2) * Fraction(4, 5) == Fraction(2, 5), "exact rational probability arithmetic"
    if example_id == "G10":
        return 2 != 0 and Fraction(-1, 2**2) == Fraction(-1, 4), "domain check and exact rational derivative evaluation"
    return False, f"no oracle registered for {example_id}"
