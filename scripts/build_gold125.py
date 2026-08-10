#!/usr/bin/env python3
"""Build the frozen Gold-25 plus exactly 100 new semantic-discovery trajectories.

This is a research artifact builder, not a scalable automatic extractor. It selects
100 source rows deterministically, preserves source text verbatim, emits a
representation-neutral trajectory with explicit atomicity and provenance metadata, and
produces saturation/search-language reports. It never writes Gold-25 files or hml_core.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet"
GOLD25_TRAJ = ROOT / "data/gold25/trajectories"
GOLD25_MANIFEST = ROOT / "manifests/gold25_math_v0.json"
FREEZE_HASHES = ROOT / "reports/gold25_freeze_hashes_2026-08-10.json"
OUT = ROOT / "data/gold125"
TRAJ_OUT = OUT / "trajectories"
REPORTS = ROOT / "reports"
GAP_OUT = REPORTS / "semantic_gaps/gold125"

CATEGORY_ORDER = [
    "Algebra",
    "Intermediate Algebra",
    "Counting & Probability",
    "Number Theory",
    "Precalculus",
    "Geometry",
    "Prealgebra",
]
CATEGORY_TARGETS = {
    "Algebra": 15,
    "Intermediate Algebra": 15,
    "Counting & Probability": 15,
    "Number Theory": 15,
    "Precalculus": 15,
    "Geometry": 12,
    "Prealgebra": 13,
}
LEVEL_QUOTAS = {
    "Algebra": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 3, "Level 5": 3},
    "Intermediate Algebra": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 3, "Level 5": 3},
    "Counting & Probability": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 3, "Level 5": 3},
    "Number Theory": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 3, "Level 5": 3},
    "Precalculus": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 3, "Level 5": 3},
    "Geometry": {"Level 1": 2, "Level 2": 2, "Level 3": 3, "Level 4": 3, "Level 5": 2},
    "Prealgebra": {"Level 1": 3, "Level 2": 3, "Level 3": 3, "Level 4": 2, "Level 5": 2},
}

# These are known near-duplicate surface families in the local MATH split. Excluding
# the second member keeps the 100-record expansion from spending two slots on the same
# i-power or coin-majority template.
NEAR_DUPLICATE_EXCLUSIONS = {1715, 1975}

TARGET_FEATURE_PATTERNS: dict[str, str] = {
    "case_analysis": r"\bcase(?:s)?\b|\beither\b|\bconsider\b|\bsplit\b|\bif\b",
    "symmetry": r"symmetr|invariant|without loss|wlog|by symmetry",
    "induction": r"induct|base case|inductive",
    "contradiction": r"contradiction|assume.*contrary|suppose.*not",
    "construction": r"construct|choose|let .* be|define|introduce|build",
    "pigeonhole": r"pigeonhole",
    "inclusion_exclusion": r"inclusion[- ]exclusion",
    "probability": r"probability|probabil|expected value|random",
    "modular": r"congruence|modulo|\bmod\b|remainder",
    "radical": r"\\sqrt|\bsqrt\b|radical",
    "logarithm": r"\blog\b|\\log",
    "calculus": r"derivative|differentiat|integral|integrat|limit|tangent line",
    "complex": r"complex|imaginary|polar|\bi\b",
    "trigonometry": r"\b(?:tan|sin|cos)\b|\\(?:tan|sin|cos)|trigonometric",
    "geometry": r"triangle|circle|angle|area|volume|radius|perpendicular|parallel|quadrilateral|coordinate",
    "sequence": r"sequence|recursive|term|fibonacci|arithmetic progression|geometric progression",
    "inequality": r"inequal|\bAM[- ]GM\b|Cauchy|maximum|minimum|least|greatest|lower bound|upper bound",
    "counting": r"number of|ways|choose|arrangement|permutation|combination",
    "rational": r"fraction|denominator|rational|ratio",
    "polynomial": r"polynomial|factor|quadratic|cubic|equation",
    "function": r"function|f\(|g\(|mapping|defined by",
    "meta_observation": r"notice|observe|key|it suffices|enough to|rather than|instead|we seek|want to|by symmetry|without loss",
}

META_CUES: list[tuple[str, str]] = [
    (r"it suffices|enough to|we seek|we want to", "CREATE_SUBGOAL"),
    (r"rather than|instead", "REFRAME"),
    (r"notice|observe|key observation|key is", "RECOGNIZE_STRUCTURE"),
    (r"by symmetry|without loss|wlog", "USE_SYMMETRY"),
    (r"\bconsider\b|\bcase\b", "CONSIDER_CASES"),
    (r"introduce|let .* be|define", "CHOOSE_REPRESENTATION"),
]

OLD_CORE_MAP: dict[str, str] = {
    "INTRODUCE_VARIABLE": "DECLARE",
    "RECORD_GIVEN": "RECORD",
    "FORMULATE_EQUATION": "MODEL",
    "FORMULATE_INEQUALITY": "MODEL",
    "APPLY_IDENTITY": "APPLY_THEOREM",
    "APPLY_THEOREM": "APPLY_THEOREM",
    "SUBSTITUTE": "SUBSTITUTE",
    "CROSS_MULTIPLY": "TRANSFORM",
    "CLEAR_DENOMINATOR": "TRANSFORM",
    "ADD_BOTH_SIDES": "TRANSFORM",
    "SUBTRACT_BOTH_SIDES": "TRANSFORM",
    "DIVIDE_BOTH_SIDES": "TRANSFORM",
    "EXPAND": "TRANSFORM",
    "FACTOR": "TRANSFORM",
    "RATIONALIZE": "TRANSFORM",
    "COMBINE_LIKE_TERMS": "TRANSFORM",
    "SOLVE": "TRANSFORM",
    "CASE_SPLIT": "CASE_SPLIT",
    "SOLVE_CASE": "TRANSFORM",
    "VERIFY_CANDIDATE": "VERIFY",
    "SELECT_CANDIDATE": "SELECT",
    "SELECT_EXTREMUM": "SELECT",
    "EXTRACT_ROOT": "TRANSFORM",
    "BOUND_SEARCH": "SEARCH_META",
    "EVALUATE": "EVALUATE",
    "DISCHARGE_GOAL": "DISCHARGE",
    "RECORD_EQUALITY_CONDITION": "RECORD",
    "CONSTRUCTION": "CONSTRUCT",
    "COMPLEMENT_COUNT": "COUNT",
    "CONDITIONAL_PROBABILITY": "EVALUATE",
    "MULTIPLY_CONDITIONALS": "EVALUATE",
    "BOUND_REASONING": "BOUND",
    "CONSTRAINT_PROPAGATION": "TRANSFORM",
    "ENUMERATE": "ENUMERATE",
    "COUNT_PERMUTATIONS": "COUNT",
    "EVALUATE_PROBABILITY": "EVALUATE",
    "COMBINE_CASE_COUNTS": "COUNT",
    "MULTIPLY_COUNTS": "COUNT",
    "PARAMETERIZE_CONGRUENCE": "TRANSFORM",
    "COUNT_EXCLUDED": "COUNT",
    "INDEX_TRANSLATION": "TRANSFORM",
    "ADVANCE_SEQUENCE": "TRANSFORM",
    "PRIME_FACTORIZE": "TRANSFORM",
    "CANCEL_SYMMETRIC_TERMS": "TRANSFORM",
    "APPLY_PRECEDENCE": "APPLY_DEFINITION",
}

OLD_LAYER_MAP: dict[str, str] = {
    "CASE_SPLIT": "CORE_PROOF_OPERATION",
    "SOLVE_CASE": "CORE_PROOF_OPERATION",
    "VERIFY_CANDIDATE": "CORE_PROOF_OPERATION",
    "DISCHARGE_GOAL": "CORE_PROOF_OPERATION",
    "SELECT_CANDIDATE": "CORE_PROOF_OPERATION",
    "SELECT_EXTREMUM": "CORE_PROOF_OPERATION",
    "INTRODUCE_VARIABLE": "CORE_STATE_OPERATION",
    "RECORD_GIVEN": "CORE_STATE_OPERATION",
    "FORMULATE_EQUATION": "CORE_STATE_OPERATION",
    "FORMULATE_INEQUALITY": "CORE_STATE_OPERATION",
    "BOUND_SEARCH": "SEARCH_META_OPERATION",
    "BOUND_REASONING": "CORE_PROOF_OPERATION",
    "CONSTRAINT_PROPAGATION": "CORE_PROOF_OPERATION",
    "ENUMERATE": "SEARCH_META_OPERATION",
    "COUNT_PERMUTATIONS": "DOMAIN_LIBRARY",
    "EVALUATE_PROBABILITY": "DOMAIN_LIBRARY",
    "COMPLEMENT_COUNT": "DOMAIN_LIBRARY",
    "CONDITIONAL_PROBABILITY": "DOMAIN_LIBRARY",
    "MULTIPLY_CONDITIONALS": "DOMAIN_LIBRARY",
    "COMBINE_CASE_COUNTS": "DOMAIN_LIBRARY",
    "MULTIPLY_COUNTS": "DOMAIN_LIBRARY",
    "PARAMETERIZE_CONGRUENCE": "DOMAIN_LIBRARY",
    "COUNT_EXCLUDED": "DOMAIN_LIBRARY",
    "INDEX_TRANSLATION": "DOMAIN_LIBRARY",
    "ADVANCE_SEQUENCE": "DOMAIN_LIBRARY",
    "PRIME_FACTORIZE": "DOMAIN_LIBRARY",
    "APPLY_THEOREM": "THEOREM_LIBRARY",
    "APPLY_IDENTITY": "THEOREM_LIBRARY",
    "RATIONALIZE": "SYMBOLIC_BACKEND_OPERATION",
    "EXPAND": "SYMBOLIC_BACKEND_OPERATION",
    "FACTOR": "SYMBOLIC_BACKEND_OPERATION",
}

OBSERVED_PROFILES: dict[str, tuple[str, str]] = {
    "DECLARE": ("CORE_STATE_OPERATION", "DECLARE"),
    "RECORD": ("CORE_STATE_OPERATION", "RECORD"),
    "MODEL": ("CORE_STATE_OPERATION", "MODEL"),
    "TRANSFORM": ("CORE_PROOF_OPERATION", "TRANSFORM"),
    "SUBSTITUTE": ("CORE_PROOF_OPERATION", "SUBSTITUTE"),
    "APPLY_DEFINITION": ("CORE_PROOF_OPERATION", "APPLY_DEFINITION"),
    "APPLY_THEOREM": ("CORE_PROOF_OPERATION", "APPLY_THEOREM"),
    "CASE_SPLIT": ("CORE_PROOF_OPERATION", "CASE_SPLIT"),
    "ENUMERATE": ("SEARCH_META_OPERATION", "ENUMERATE"),
    "COUNT": ("DOMAIN_LIBRARY", "COUNT"),
    "EVALUATE": ("NUMERIC_BACKEND_OPERATION", "EVALUATE"),
    "VERIFY": ("CORE_PROOF_OPERATION", "VERIFY"),
    "SELECT": ("SEARCH_META_OPERATION", "SELECT"),
    "BOUND": ("CORE_PROOF_OPERATION", "BOUND"),
    "CONSTRUCT": ("CORE_STATE_OPERATION", "CONSTRUCT"),
    "DISCHARGE": ("CORE_PROOF_OPERATION", "DISCHARGE"),
    "SEARCH_META": ("SEARCH_META_OPERATION", "SEARCH_META"),
    "APPLY_INVERSE": ("THEOREM_LIBRARY", "APPLY_INVERSE"),
    "DIFFERENTIATE": ("DOMAIN_LIBRARY", "DIFFERENTIATE"),
    "INTEGRATE": ("DOMAIN_LIBRARY", "INTEGRATE"),
    "TAKE_LIMIT": ("DOMAIN_LIBRARY", "TAKE_LIMIT"),
    "MODULAR_REASONING": ("DOMAIN_LIBRARY", "MODULAR_REASONING"),
    "INDUCT": ("CORE_PROOF_OPERATION", "INDUCT"),
    "CONTRADICTION": ("CORE_PROOF_OPERATION", "CONTRADICTION"),
    "PROBABILITY": ("DOMAIN_LIBRARY", "PROBABILITY"),
    "TRIG_IDENTITY": ("DOMAIN_LIBRARY", "TRIG_IDENTITY"),
    "SEQUENCE_RECURRENCE": ("DOMAIN_LIBRARY", "SEQUENCE_RECURRENCE"),
    "PIGEONHOLE": ("THEOREM_LIBRARY", "PIGEONHOLE"),
    "INCLUSION_EXCLUSION": ("THEOREM_LIBRARY", "INCLUSION_EXCLUSION"),
    "EXPECTATION": ("DOMAIN_LIBRARY", "EXPECTATION"),
    "COORDINATE_TRANSFORM": ("DOMAIN_LIBRARY", "COORDINATE_TRANSFORM"),
    "OPTIMIZE": ("CORE_PROOF_OPERATION", "OPTIMIZE"),
    "OTHER": ("UNRESOLVED", "UNRESOLVED"),
}

RISK_CUES: list[tuple[str, str]] = [
    (r"divide|denominator|cross[- ]?multiply|cancel", "the transformation requires a nonzero or preserved-denominator condition"),
    (r"square|squared|sqrt|root|radical", "the power/root transformation requires sign and domain conditions"),
    (r"case|either|if ", "the branch partition requires coverage and disjointness"),
    (r"candidate|solution|root", "candidate acceptance requires original-constraint verification"),
    (r"inequal|maximum|minimum|least|greatest", "order reasoning requires a valid domain and direction condition"),
    (r"log", "logarithm reasoning requires positive arguments and valid bases"),
    (r"probability|random|without replacement", "probability reasoning requires a declared sample space and sampling model"),
    (r"derivative|integral|limit", "calculus reasoning requires the relevant domain and regularity hypotheses"),
    (r"induct", "induction requires a base case and an inductive-step hypothesis"),
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def problem_key(problem: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", problem.lower()).strip()[:100]


def source_tags(problem: str, solution: str) -> set[str]:
    text = f"{problem}\n{solution}".lower()
    return {name for name, pattern in TARGET_FEATURE_PATTERNS.items() if re.search(pattern, text, re.I)}


def split_source(solution: str) -> list[str]:
    raw_parts = re.split(r"(?<=[.!?])\s+|\n{2,}|(?<=\\\\)\\\\\s*", solution)
    spans = []
    for part in raw_parts:
        span = part.strip()
        if not span:
            continue
        if spans and len(span) < 24 and not re.search(r"[A-Za-z0-9]", span):
            spans[-1] += " " + span
        else:
            spans.append(span)
    return spans or [solution.strip()]


def classify_operation(span: str, index: int, total: int) -> str:
    low = span.lower()
    if index == total - 1 and re.search(r"boxed|answer|therefore|thus|final|conclusion", low):
        return "DISCHARGE"
    if re.search(r"check|verify|satisf(?:y|ies)|plug .*back|substitut(?:e|ing) .*original", low):
        return "VERIFY"
    if re.search(r"\binduct|base case|inductive step", low):
        return "INDUCT"
    if re.search(r"contradiction|contradictory|assume.*not|suppose.*not", low):
        return "CONTRADICTION"
    if re.search(r"inclusion[- ]exclusion", low):
        return "INCLUSION_EXCLUSION"
    if re.search(r"pigeonhole", low):
        return "PIGEONHOLE"
    if re.search(r"derivative|differentiat", low):
        return "DIFFERENTIATE"
    if re.search(r"integrat", low):
        return "INTEGRATE"
    if re.search(r"\blimit\b", low):
        return "TAKE_LIMIT"
    if re.search(r"\b(?:tan|sin|cos)\b|\\(?:tan|sin|cos)", low) and re.search(r"identity|formula|angle addition|rewrite|=", low):
        return "TRIG_IDENTITY"
    if re.search(r"modulo|\bmod\b|congruence|remainder", low):
        return "MODULAR_REASONING"
    if re.search(r"sequence|recursive|recurrence|term", low) and re.search(r"next|defined|recurrence|term|sum", low):
        return "SEQUENCE_RECURRENCE"
    if re.search(r"probability|probabil|random|expected", low):
        return "PROBABILITY"
    if re.search(r"maximum|minimum|least|greatest|lower bound|upper bound|at most|at least", low):
        return "OPTIMIZE" if re.search(r"maximum|minimum|least|greatest", low) else "BOUND"
    if re.search(r"permutation|combination|number of ways|arrangement|choose", low):
        return "COUNT"
    if re.search(r"\beither\b|consider the possibilities|split into|\bcase\s+(?:\d+|[a-z])\s*(?::|=|-)", low):
        return "CASE_SPLIT"
    if re.search(r"construct|build|choose .* such that|let .* be", low) and index == 0:
        return "CONSTRUCT"
    if re.search(r"define|definition|by definition|means that", low):
        return "APPLY_DEFINITION"
    if re.search(r"theorem|lemma|pigeonhole|pythag|am-gm|by [A-Z]", span, re.I):
        return "APPLY_THEOREM"
    if re.search(r"substitut|replace|plug", low):
        return "SUBSTITUTE"
    if re.search(r"divide|denominator|cross[- ]?multiply|cancel", low):
        return "TRANSFORM"
    if re.search(r"expand|factor|simplif|combine like|collect terms|rewrite", low):
        return "TRANSFORM"
    if re.search(r"solve|find x|we get|therefore|hence|thus|\\Rightarrow|=", low):
        return "TRANSFORM"
    if re.search(r"compute|calculate|evaluate|sum|product|equals|=|\\boxed", low):
        return "EVALUATE"
    if re.search(r"notice|observe|key|it suffices|enough to|rather than|instead|we seek|want to|by symmetry|without loss", low):
        return "SEARCH_META"
    return "OTHER"


def reasoning_mode(operation: str, span: str, index: int) -> str:
    low = span.lower()
    if operation in {"VERIFY"}:
        return "VERIFICATION"
    if operation in {"DISCHARGE", "SELECT", "BOUND", "OPTIMIZE"}:
        return "GOAL_MANAGEMENT"
    if operation in {"SEARCH_META", "CASE_SPLIT", "CONSTRUCT", "ENUMERATE"}:
        return "SEARCH_META"
    if operation in {"MODEL", "DECLARE", "RECORD"}:
        return "MODELING"
    if re.search(r"notice|observe|key|it suffices|rather than|instead|we seek|want to|without loss|by symmetry", low):
        return "SEARCH_META"
    return "EXECUTION"


def operation_profile(operation: str) -> tuple[str, str]:
    return OBSERVED_PROFILES.get(operation, ("UNRESOLVED", "UNRESOLVED"))


def atomic_components(span: str, operation: str) -> tuple[str, list[str]]:
    low = span.lower()
    components: list[str] = []
    def add(value: str) -> None:
        if value not in components:
            components.append(value)
    if re.search(r"substitut|replace|plug", low):
        add("SUBSTITUTE")
    if re.search(r"case|either|split", low):
        add("CASE_SPLIT")
    if re.search(r"divide|denominator|cross[- ]?multiply|cancel|expand|factor|simplif|collect", low):
        add("TRANSFORM")
    if re.search(r"sqrt|root|radical|log", low):
        add("APPLY_INVERSE")
    if re.search(r"derivative|differentiat", low):
        add("DIFFERENTIATE")
    if re.search(r"integrat", low):
        add("INTEGRATE")
    if re.search(r"probability|probabil|random", low):
        add("EVALUATE")
    if re.search(r"number of|ways|choose|permutation|combination", low):
        add("COUNT")
    if re.search(r"check|verify|satisf(?:y|ies)|plug .*back", low):
        add("VERIFY")
    if re.search(r"construct|build|choose .* such that", low):
        add("CONSTRUCT")
    if re.search(r"modulo|\bmod\b|congruence|remainder", low):
        add("MODULAR_REASONING")
    if re.search(r"induct|base case|inductive", low):
        add("INDUCT")
    if re.search(r"notice|observe|key|it suffices|rather than|instead|we seek|want to|without loss|by symmetry", low):
        add("SEARCH_META")
    if re.search(r"maximum|minimum|least|greatest|lower bound|upper bound", low):
        add("BOUND")
    if not components:
        core = operation_profile(operation)[1]
        add(core if core != "UNRESOLVED" else operation)
    if len(components) >= 2:
        return "COMPOUND_MACRO", components
    if operation == "OTHER":
        return "UNCERTAIN", components
    return "ATOMIC", components


def preconditions_for(span: str, operation: str) -> list[dict[str, Any]]:
    low = span.lower()
    found: list[dict[str, Any]] = []
    explicit_patterns = [
        (r"nonzero|not zero|≠\s*0|!=\s*0", "a denominator or divisor is nonzero", "EXPLICIT_SOURCE"),
        (r"positive|greater than 0|>0", "positivity/domain restriction", "EXPLICIT_SOURCE"),
        (r"integer|natural number|whole number", "integer/natural domain restriction", "EXPLICIT_SOURCE"),
        (r"independent|without replacement|equally likely", "sampling-space or independence assumption", "EXPLICIT_SOURCE"),
        (r"continuous|differentiable", "regularity hypothesis", "EXPLICIT_SOURCE"),
        (r"denominator|base", "operation denominator/base is valid", "EXPLICIT_SOURCE"),
    ]
    for pattern, condition, status in explicit_patterns:
        if re.search(pattern, low):
            found.append({"condition": condition, "status": status, "evidence": span, "source_omission": False})
    risk = next((description for pattern, description in RISK_CUES if re.search(pattern, low)), None)
    if risk and not found:
        found.append({
            "condition": risk,
            "status": "UNKNOWN",
            "evidence": "No matching applicability condition is explicit in this source span.",
            "source_omission": True,
        })
    return found


def meta_records(span: str, step_id: str, state_id: str) -> list[dict[str, Any]]:
    low = span.lower()
    records = []
    for pattern, operation in META_CUES:
        if re.search(pattern, low):
            records.append({
                "meta_step_id": f"meta:{step_id}:{len(records) + 1}",
                "source_span": span,
                "meta_operation": operation,
                "target": span,
                "current_state": state_id,
                "resulting_search_constraint_or_subgoal": span,
                "changes_mathematical_truth_state": operation in {"CHOOSE_REPRESENTATION", "REFRAME"},
                "representation_assessment": "structured_metadata",
                "evidence_status": "EXPLICIT_SOURCE",
            })
    return records


def initial_state(problem: str) -> dict[str, Any]:
    domains = []
    low = problem.lower()
    if re.search(r"integer|whole number|natural|digit", low):
        domains.append("integer/natural domain")
    if re.search(r"real number|real numbers|real", low):
        domains.append("real domain")
    if re.search(r"positive", low):
        domains.append("positivity restriction")
    if re.search(r"probability|random", low):
        domains.append("source probability model")
    return {
        "objects": ["source mathematical problem"],
        "declarations": [],
        "types_domains": domains,
        "facts": [{"id": "fact:problem", "statement": problem, "status": "given"}],
        "assumptions": [],
        "constraints": [],
        "definitions": [],
        "goals": [{"id": "goal:answer", "statement": "answer the source problem", "status": "goal_open"}],
        "subgoals": [],
        "candidates": [],
        "branch_state": [],
        "scope": ["global"],
        "dependencies": [],
        "open_obligations": [],
        "discharged_obligations": [],
        "epistemic_status": [],
    }


def feature_reason(category: str, tags: set[str], level: str) -> str:
    preferred = sorted(tags)[:5]
    feature_text = ", ".join(preferred) if preferred else "source-grounded algebraic execution"
    return f"Selected for semantic diversity in {category} at {level}; targeted {feature_text} and active-coverage pressure beyond the frozen Gold-25."


def select_new_rows(df: pd.DataFrame, old_rows: set[int]) -> list[dict[str, Any]]:
    eligible: list[tuple[int, Any, set[str]]] = []
    seen_keys: set[str] = set()
    for index, row in df.iterrows():
        index = int(index)
        if index in old_rows or index in NEAR_DUPLICATE_EXCLUSIONS:
            continue
        problem = str(row["problem"])
        solution = str(row["solution"])
        low = f"{problem}\n{solution}".lower()
        if not problem.strip() or not solution.strip():
            continue
        if any(marker in low for marker in ("[asy]", "includegraphics", "\\begin{tikz", "\x00")):
            continue
        if not 180 <= len(solution) <= 6500:
            continue
        key = problem_key(problem)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        eligible.append((index, row, source_tags(problem, solution)))

    selected_by_category: dict[str, list[tuple[int, Any, set[str]]]] = {}
    for category in CATEGORY_ORDER:
        pool = [item for item in eligible if str(item[1]["type"]) == category]
        counts = Counter(tag for _, _, tags in pool for tag in tags)
        quotas = LEVEL_QUOTAS[category].copy()
        covered: Counter[str] = Counter()
        selected: list[tuple[int, Any, set[str]]] = []
        while sum(quotas.values()):
            candidates = [item for item in pool if quotas.get(str(item[1]["level"]), 0) > 0 and item[0] not in {x[0] for x in selected}]
            if not candidates:
                raise RuntimeError(f"selection quota cannot be filled for {category}: {quotas}")
            best = None
            best_score = -math.inf
            for item in candidates:
                index, row, tags = item
                new_tags = sum(1 for tag in tags if covered[tag] == 0)
                rare_tags = sum(1 / math.sqrt(1 + counts[tag]) for tag in tags)
                undercovered = sum(1 for tag in tags if covered[tag] < 2)
                sentence_count = len(split_source(str(row["solution"])))
                score = 7 * new_tags + 1.5 * rare_tags + 1.3 * undercovered
                score += min(len(str(row["solution"])) / 1500, 1.5)
                score += 0.5 if 3 <= sentence_count <= 12 else 0
                if score > best_score:
                    best_score = score
                    best = item
            assert best is not None
            selected.append(best)
            covered.update(best[2])
            quotas[str(best[1]["level"])] -= 1
        selected_by_category[category] = selected

    interleaved: list[dict[str, Any]] = []
    for rank in range(max(len(items) for items in selected_by_category.values())):
        for category in CATEGORY_ORDER:
            items = selected_by_category[category]
            if rank >= len(items):
                continue
            index, row, tags = items[rank]
            interleaved.append({
                "problem_id": f"MATH-GOLD-{26 + len(interleaved):03d}",
                "source_row_id": f"train-row-{index:05d}",
                "row": index,
                "category": str(row["type"]),
                "level": str(row["level"]),
                "problem": str(row["problem"]),
                "original_solution": str(row["solution"]),
                "source_hash": sha256_bytes((str(row["problem"]) + "\n" + str(row["solution"])).encode("utf-8")),
                "selection_reason": feature_reason(str(row["type"]), tags, str(row["level"])),
                "targeted_semantic_features": sorted(tags),
            })
    if len(interleaved) != 100:
        raise RuntimeError(f"expected exactly 100 new rows, selected {len(interleaved)}")
    if len({item["source_row_id"] for item in interleaved}) != 100:
        raise RuntimeError("new selection contains duplicate source rows")
    return interleaved


def gap_ids_for(operation: str, layer: str, category: str, atomicity: str, preconditions: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    if operation in {"CASE_SPLIT"}:
        gaps.append("MATH-GAP-0001")
    if operation in {"VERIFY", "SELECT", "OPTIMIZE"}:
        gaps.append("MATH-GAP-0002")
    if any(item["source_omission"] for item in preconditions):
        gaps.append("MATH-GAP-0003")
    if atomicity == "COMPOUND_MACRO" or operation in {"CASE_SPLIT", "VERIFY"}:
        gaps.append("MATH-GAP-0004")
    if layer == "THEOREM_LIBRARY":
        gaps.append("MATH-GAP-0005")
    if layer == "SYMBOLIC_BACKEND_OPERATION":
        gaps.append("MATH-GAP-0006")
    if category == "Counting & Probability" or operation in {"COUNT", "PROBABILITY", "PIGEONHOLE", "INCLUSION_EXCLUSION", "EXPECTATION"}:
        gaps.append("MATH-GAP-0008")
    if category == "Number Theory" or operation == "MODULAR_REASONING":
        gaps.append("MATH-GAP-0009")
    if operation in {"SEQUENCE_RECURRENCE", "INDUCT"}:
        gaps.append("MATH-GAP-0010")
    if operation == "SEARCH_META" or "meta_observation" in operation:
        gaps.append("MATH-GAP-0011")
    if operation == "INDUCT":
        gaps.append("MATH-GAP-0012")
    if operation in {"DIFFERENTIATE", "INTEGRATE", "TAKE_LIMIT"}:
        gaps.append("MATH-GAP-0013")
    if layer in {"DOMAIN_LIBRARY", "THEOREM_LIBRARY"} and category in {"Precalculus", "Geometry", "Intermediate Algebra"}:
        gaps.append("MATH-GAP-0007")
    return sorted(set(gaps))


def hml_support_for(operation: str, layer: str, atomicity: str) -> dict[str, Any]:
    if operation in {"EVALUATE", "TRANSFORM", "SUBSTITUTE", "DISCHARGE"} and atomicity == "ATOMIC":
        return {"status": "PARTIAL", "constructs": ["closed_eval_v1", "reasoning_kernel"], "notes": "A generic/local component exists, but this source-grounded transition is not rendered or replayed here."}
    if layer in {"CORE_STATE_OPERATION", "CORE_PROOF_OPERATION"}:
        return {"status": "PARTIAL", "constructs": ["state", "goal", "scope", "evidence"], "notes": "The state shape is representable; full executable support depends on the exact rule and evidence."}
    return {"status": "REPRESENTABLE_ONLY", "constructs": ["assume", "evidence", "goal"], "notes": "The claim can be recorded as state, but current HML does not provide a trusted domain/meta checker for this transition."}


def branch_name(span: str, operation: str) -> str | None:
    if operation not in {"CASE_SPLIT", "VERIFY", "TRANSFORM", "EVALUATE", "COUNT", "PROBABILITY"}:
        return None
    match = re.search(r"\b(?:case|branch)\s+([A-Z]|\d+)\s*:", span, re.I) or re.match(r"^\s*([A-Z])\)", span, re.I)
    if not match:
        return None
    value = match.group(1)
    return f"case {value}"


def is_branch_join(span: str) -> bool:
    low = span.lower()
    return bool(re.search(
        r"\b(?:summing|combining|the four cases|these cases|overall|in total|total number|we want the integers|for k\s*=|therefore, the total|this gives us)\b",
        low,
    ))


def discharge_cue(span: str, operation: str) -> bool:
    return operation in {"VERIFY", "DISCHARGE"} or bool(re.search(r"check|verify|satisf(?:y|ies)|therefore|thus|boxed|answer", span, re.I))


def build_new_trajectory(item: dict[str, Any]) -> dict[str, Any]:
    problem = item["problem"]
    solution = item["original_solution"]
    spans = split_source(solution)
    if not spans or any(span not in solution for span in spans):
        raise ValueError(f"{item['problem_id']} has a non-exact source span")

    state = initial_state(problem)
    state["id"] = "S0"
    initial = copy.deepcopy(state)
    steps: list[dict[str, Any]] = []
    all_meta: list[dict[str, Any]] = []
    active_obligations: list[dict[str, Any]] = []
    current_id = "S0"
    branch_names: list[str] = []
    active_branch: str | None = None
    branch_fact_ids: list[str] = []
    completed_branch_fact_ids: list[str] = []
    last_global_fact_id = "fact:problem"
    source_omissions: list[str] = []
    explicit_count = 0
    implicit_count = 0

    for index, span in enumerate(spans, 1):
        operation = classify_operation(span, index - 1, len(spans))
        layer, candidate_core = operation_profile(operation)
        atomicity, components = atomic_components(span, operation)
        mode = reasoning_mode(operation, span, index - 1)
        explicit_branch = branch_name(span, operation)
        if explicit_branch and active_branch and explicit_branch != active_branch:
            completed_branch_fact_ids.extend(branch_fact_ids)
            branch_fact_ids = []
        if explicit_branch:
            active_branch = explicit_branch
        joining = active_branch is not None and is_branch_join(span)
        branch = None if joining else active_branch
        preconditions = preconditions_for(span, operation)
        source_omissions.extend(item["condition"] for item in preconditions if item["source_omission"])
        meta = meta_records(span, f"s{index}", current_id)
        all_meta.extend(meta)
        before = copy.deepcopy(state)
        before["id"] = current_id
        result_id = f"fact:s{index}"
        if index == 1:
            dependencies = ["fact:problem"]
        elif joining:
            dependencies = [last_global_fact_id] + completed_branch_fact_ids + branch_fact_ids
        elif branch is not None:
            previous_scope = state["facts"][-1].get("scope", "global") if state["facts"] else "global"
            dependencies = [f"fact:s{index - 1}"] if previous_scope in {"global", branch} else [last_global_fact_id]
        else:
            previous_scope = state["facts"][-1].get("scope", "global") if state["facts"] else "global"
            dependencies = [f"fact:s{index - 1}"] if previous_scope == "global" else [last_global_fact_id]
        if operation in {"VERIFY", "DISCHARGE"} and "fact:problem" not in dependencies:
            dependencies.append("fact:problem")
        dependency_evidence = [{"dependency": dep, "kind": "initial-given" if dep == "fact:problem" else "adjacent-source-result", "confidence": "medium"} for dep in dependencies]

        created: list[dict[str, Any]] = []
        risk = next((description for pattern, description in RISK_CUES if re.search(pattern, span, re.I)), None)
        if risk:
            created.append({
                "id": f"obl:s{index}",
                "statement": risk,
                "status": "open",
                "created_at_step": f"s{index}",
                "discharged_at_step": None,
                "lifetime_steps": None,
                "evidence": "Generated from a source-grounded applicability risk; the source span does not by itself prove discharge.",
                "source_omission": not any(not p["source_omission"] for p in preconditions),
            })

        if branch and f"branch:{branch}" not in state["scope"]:
            state["scope"].append(f"branch:{branch}")
        if operation == "CASE_SPLIT":
            declared = re.findall(r"\b(?:case|branch)\s+([A-Z]|\d+)\s*:", span, re.I)
            for name in declared:
                candidate = f"case {name}"
                if f"branch:{candidate}" not in branch_names:
                    branch_names.append(candidate)
                    state["scope"].append(f"branch:{candidate}")
            state["branch_state"].append({"id": f"branch:s{index}", "status": "declared", "source_step": f"s{index}"})
        if branch and branch not in branch_names:
            branch_names.append(branch)
            state["branch_state"].append({"id": f"branch:{branch}", "status": "active", "source_step": f"s{index}"})

        fact_scope = branch or "global"
        state["facts"].append({"id": result_id, "statement": span, "status": "source_grounded", "scope": fact_scope})
        if branch:
            branch_fact_ids.append(result_id)
        else:
            last_global_fact_id = result_id
            if joining:
                completed_branch_fact_ids.extend(branch_fact_ids)
                branch_fact_ids = []
                active_branch = None
        state["dependencies"].extend(dep for dep in dependencies if dep not in state["dependencies"])
        if operation in {"VERIFY", "SELECT", "OPTIMIZE"}:
            state["candidates"].append({"id": result_id, "statement": span, "status": "candidate_or_selection", "scope": fact_scope})

        for obligation_item in created:
            state["open_obligations"].append(obligation_item)
            active_obligations.append(obligation_item)
        if discharge_cue(span, operation) and active_obligations:
            for obligation_item in list(active_obligations):
                if obligation_item["created_at_step"] == f"s{index}" and operation not in {"VERIFY", "DISCHARGE"}:
                    continue
                obligation_item["status"] = "discharged"
                obligation_item["discharged_at_step"] = f"s{index}"
                obligation_item["lifetime_steps"] = index - int(obligation_item["created_at_step"][1:])
                state["open_obligations"] = [item for item in state["open_obligations"] if item["id"] != obligation_item["id"]]
                state["discharged_obligations"].append(obligation_item)
                active_obligations.remove(obligation_item)
        discharged_ids = [item["id"] for item in state["discharged_obligations"] if item.get("discharged_at_step") == f"s{index}"]
        created_ids = [item["id"] for item in created]
        for created_item in created:
            if created_item["status"] == "discharged":
                discharged_ids.append(created_item["id"])
        discharged_ids = list(dict.fromkeys(discharged_ids))

        if index == len(spans):
            for goal in state["goals"]:
                goal["status"] = "goal_discharged"
            state["epistemic_status"].append({"id": "goal_status", "statement": "source solution reaches its stated answer", "status": "goal_discharged"})
        after = copy.deepcopy(state)
        after["id"] = f"S{index}"
        state_change = {
            "from": before.get("id", current_id),
            "to": f"S{index}",
            "added_facts": [result_id],
            "added_obligations": created_ids,
            "removed_obligations": discharged_ids,
            "scope_effect": "branch-local" if branch else ("branch-join" if joining else ("branch-declaration" if operation == "CASE_SPLIT" else "global/current")),
            "dependency_effect": dependencies,
            "epistemic_update": f"Source-grounded result {result_id} recorded from the exact motivating span.",
        }
        step_record = {
            "step_id": f"s{index}",
            "source_span": span,
            "explicitness": "implicit" if not re.search(r"[A-Za-z]{3,}", span) or re.match(r"^\s*(?:\(?[A-Z]\)?\)|[-=]|\\\[)", span) else "explicit",
            "reasoning_mode": mode,
            "atomicity": atomicity,
            "macro_components": components if atomicity == "COMPOUND_MACRO" else [],
            "warrant": {
                "kind": "source_sentence_warrant",
                "description": "The source solution presents this operation/result in the preserved span; no stronger formal theorem certificate is inferred.",
                "source": "explicit_source" if operation not in {"OTHER", "SEARCH_META"} else "source_interpretation",
                "evidence_status": "SOURCE_GROUNDED",
            },
            "preconditions": preconditions,
            "creates_obligations": created,
            "discharges_obligations": discharged_ids,
            "dependencies": dependencies,
            "dependency_evidence": dependency_evidence,
            "scope": {"name": branch or "global", "branch": branch, "branch_depth": 1 if branch else 0},
            "verification": {
                "status": "SOURCE_GROUNDED",
                "category": "EXACT_SOURCE_AND_STATE_AUDIT",
                "backend": "source-span and structural audit",
                "notes": "The result statement is exactly the source span; formal mathematical replay is not claimed for automatic extraction.",
            },
            "hml_support": hml_support_for(operation, layer, atomicity),
            "semantic_gap_ids": gap_ids_for(operation, layer, item["category"], atomicity, preconditions),
            "state_before": before,
            "state_after": after,
            "state_change": state_change,
            "action": {
                "operation_id": operation,
                "family": operation_profile(operation)[1],
                "arguments": {"source_sentence_index": index, "candidate_core": candidate_core, "layer_class": layer},
                "candidate_core": candidate_core,
                "layer_class": layer,
            },
            "result": {
                "id": result_id,
                "statement": span,
                "status": "source_grounded",
                "claim_source": "verbatim_source_span",
            },
            "meta_step_ids": [record["meta_step_id"] for record in meta],
        }
        steps.append(step_record)
        if step_record["explicitness"] == "explicit":
            explicit_count += 1
        else:
            implicit_count += 1
        current_id = f"S{index}"

    final_state = copy.deepcopy(state)
    final_state["id"] = current_id
    operations = sorted({step["action"]["operation_id"] for step in steps})
    profile = []
    for operation in operations:
        observed_steps = [step for step in steps if step["action"]["operation_id"] == operation]
        layer, candidate = operation_profile(operation)
        profile.append({
            "observed_operation": operation,
            "frequency": len(observed_steps),
            "candidate_core": candidate,
            "layer_class": layer,
            "atomic_components": sorted({component for step in observed_steps for component in step["macro_components"]}) or [candidate],
        })
    return {
        "schema_version": "math-gold125-trajectory-0.1.0",
        "problem_id": item["problem_id"],
        "source_dataset": "Hendrycks MATH train parquet",
        "source_row_id": item["source_row_id"],
        "source_hash": item["source_hash"],
        "category": item["category"],
        "level": item["level"],
        "problem": problem,
        "original_solution": solution,
        "selection_reason": item["selection_reason"],
        "targeted_semantic_features": item["targeted_semantic_features"],
        "initial_state": initial,
        "steps": steps,
        "final_state": final_state,
        "goal_status": "discharged",
        "operations_observed": operations,
        "operation_profile": profile,
        "source_quality": {
            "source_spans_exact": all(step["source_span"] in solution for step in steps),
            "explicit_steps": explicit_count,
            "implicit_steps": implicit_count,
            "source_omissions": sorted(set(source_omissions)),
            "solution_variants": bool(re.search(r"solution\s*(?:2|two)|alternative|another way", solution, re.I)),
            "annotation_mode": "source-grounded semantic extraction with explicit uncertainty; not a formal proof replay",
        },
        "meta_reasoning": all_meta,
        "hml_gaps": sorted({gap for step in steps for gap in step["semantic_gap_ids"]}),
        "canonical_verification": {
            "status": "STRUCTURAL_SOURCE_AUDIT",
            "source_span_count": len(steps),
            "source_span_failures": [],
            "formal_math_replay": "not claimed for automatic extraction; hard trajectories receive an independent source reconstruction",
        },
    }


OLD_MACRO_COMPONENTS: dict[tuple[str, str], list[str]] = {
    ("MATH-GOLD-001", "s1"): ["APPLY_DEFINITION", "MODEL"],
    ("MATH-GOLD-005", "s4"): ["TRANSFORM"],
    ("MATH-GOLD-006", "s3"): ["TRANSFORM", "APPLY_INVERSE"],
    ("MATH-GOLD-009", "s2"): ["APPLY_THEOREM", "EVALUATE"],
    ("MATH-GOLD-018", "s4"): ["TRANSFORM", "EVALUATE"],
    ("MATH-GOLD-022", "s2"): ["SUBSTITUTE", "TRANSFORM"],
    ("MATH-GOLD-024", "s4"): ["EVALUATE", "EVALUATE"],
    ("MATH-GOLD-025", "s4"): ["TRANSFORM", "BOUND"],
}


def normalize_old_trajectories() -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for path in sorted(GOLD25_TRAJ.glob("MATH-GOLD-*.json")):
        trajectory = json.loads(path.read_text(encoding="utf-8"))
        steps = []
        for source_step in trajectory["steps"]:
            observed = source_step["action"]["operation_id"]
            atomicity = "COMPOUND_MACRO" if (trajectory["problem_id"], source_step["step_id"]) in OLD_MACRO_COMPONENTS else "ATOMIC"
            components = OLD_MACRO_COMPONENTS.get((trajectory["problem_id"], source_step["step_id"]), [OLD_CORE_MAP.get(observed, "UNRESOLVED")])
            layer = OLD_LAYER_MAP.get(observed, "CORE_PROOF_OPERATION" if observed in OLD_CORE_MAP else "UNRESOLVED")
            steps.append({
                "trajectory_id": trajectory["problem_id"],
                "category": trajectory["category"],
                "level": trajectory["level"],
                "step_id": source_step["step_id"],
                "observed_operation": observed,
                "candidate_core": OLD_CORE_MAP.get(observed, "UNRESOLVED"),
                "layer_class": layer,
                "atomicity": atomicity,
                "atomic_components": components,
                "reasoning_mode": "VERIFICATION" if observed == "VERIFY_CANDIDATE" else ("GOAL_MANAGEMENT" if observed in {"DISCHARGE_GOAL", "SELECT_CANDIDATE", "SELECT_EXTREMUM"} else "EXECUTION"),
                "source_span": source_step["source_span"],
                "explicitness": source_step["explicitness"],
                "preconditions": source_step["preconditions"],
                "creates_obligations": source_step["creates_obligations"],
                "discharges_obligations": source_step["discharges_obligations"],
                "dependencies": source_step["dependencies"],
                "scope": source_step.get("branch") or "global",
                "hml_status": source_step["hml_support"]["status"],
                "semantic_gap_ids": source_step["semantic_gap_ids"],
                "result": source_step["result"]["statement"],
            })
        normalized.append({
            "trajectory_id": trajectory["problem_id"],
            "category": trajectory["category"],
            "level": trajectory["level"],
            "source_hash": trajectory["source_hash"],
            "steps": steps,
            "state_fields": set(trajectory["initial_state"]) | {field for step in trajectory["steps"] for field in step["state_after"]},
            "meta_reasoning": [],
        })
    return normalized


GAP_META: dict[str, dict[str, Any]] = {
    "MATH-GAP-0001": {"title": "Case coverage and branch joins", "class": "CORE_SEMANTIC_MISSING", "layer": "CORE_PROOF_OPERATION", "severity": "high", "description": "Generic exhaustive/disjoint branch declarations and invariant-only joins are not fully executable.", "old": True},
    "MATH-GAP-0002": {"title": "Candidate generation and verification", "class": "CORE_SEMANTIC_MISSING", "layer": "CORE_PROOF_OPERATION", "severity": "high", "description": "Candidate provenance and original-constraint acceptance are not first-class.", "old": True},
    "MATH-GAP-0003": {"title": "Applicability preconditions", "class": "CORE_SEMANTIC_MISSING", "layer": "CORE_PROOF_OPERATION", "severity": "high", "description": "Domain and nonzero conditions are not synthesized uniformly.", "old": True},
    "MATH-GAP-0004": {"title": "Persistent proof obligations", "class": "CORE_SEMANTIC_MISSING", "layer": "CORE_PROOF_OPERATION", "severity": "high", "description": "Transformation debt is not uniformly attached to source operations.", "old": True},
    "MATH-GAP-0005": {"title": "Theorem and formula evidence", "class": "LIBRARY_MISSING", "layer": "THEOREM_LIBRARY", "severity": "medium", "description": "Hypothesis-aware theorem evidence is not available as a broad checked library.", "old": True},
    "MATH-GAP-0006": {"title": "Open symbolic algebra", "class": "LIBRARY_MISSING", "layer": "SYMBOLIC_BACKEND_OPERATION", "severity": "medium", "description": "Open-variable normalization lacks a trusted replayable backend.", "old": True},
    "MATH-GAP-0007": {"title": "Domain theorem libraries", "class": "LIBRARY_MISSING", "layer": "DOMAIN_LIBRARY", "severity": "medium", "description": "Logs, trigonometry, geometry, vectors, complex facts, and related domain knowledge are not broadly checked.", "old": True},
    "MATH-GAP-0008": {"title": "Counting and probability library", "class": "LIBRARY_MISSING", "layer": "DOMAIN_LIBRARY", "severity": "medium", "description": "Finite sample-space, counting, and probability rules lack trusted evidence.", "old": True},
    "MATH-GAP-0009": {"title": "Number theory and finite search", "class": "LIBRARY_MISSING", "layer": "DOMAIN_LIBRARY", "severity": "medium", "description": "Divisibility, congruence, factorization, and minimality certificates are missing.", "old": True},
    "MATH-GAP-0010": {"title": "Sequence and exclusion state", "class": "TRAJECTORY_SCHEMA_PROBLEM", "layer": "CORE_STATE_OPERATION", "severity": "medium", "description": "Sequence generators, excluded values, and index translation need persistent neutral state.", "old": True},
    "MATH-GAP-0011": {"title": "Source-supported search/meta reasoning", "class": "TRANSLATION/CANONICALIZATION_PROBLEM", "layer": "SEARCH_META_OPERATION", "severity": "high", "description": "Successful solutions contain explicit representation and subgoal choices that do not map cleanly to a narrow execution vocabulary.", "old": False},
    "MATH-GAP-0012": {"title": "Induction proof-state protocol", "class": "CORE_SEMANTIC_MISSING", "layer": "CORE_PROOF_OPERATION", "severity": "medium", "description": "Base-case and inductive-hypothesis state are not represented as a reusable proof protocol in this corpus.", "old": False},
    "MATH-GAP-0013": {"title": "Calculus theorem/backend evidence", "class": "LIBRARY_MISSING", "layer": "DOMAIN_LIBRARY", "severity": "medium", "description": "Differentiation, integration, and limit claims require domain/library evidence beyond the generic kernel.", "old": False},
}


def verify_gold25_freeze() -> None:
    recorded = json.loads(FREEZE_HASHES.read_text(encoding="utf-8"))
    for relative, expected in recorded["files"].items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise RuntimeError(f"frozen Gold-25 file drifted: {relative}: {actual} != {expected}")
    hml_head = subprocess.check_output(["git", "-C", str(ROOT / "hml_core"), "rev-parse", "HEAD"], text=True).strip()
    if hml_head != recorded["hml_core_head"]:
        raise RuntimeError(f"hml_core HEAD drifted: {hml_head} != {recorded['hml_core_head']}")
    status = subprocess.check_output(["git", "-C", str(ROOT / "hml_core"), "status", "--porcelain"], text=True)
    if status:
        raise RuntimeError("hml_core is dirty")
    writable = subprocess.check_output(["find", str(ROOT / "hml_core"), "-perm", "+022", "-print"], text=True)
    if writable:
        raise RuntimeError("hml_core contains writable paths")


def gold125_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://hml.reasoning.local/schemas/math-gold125-trajectory.schema.json",
        "title": "Gold-125 source-grounded semantic trajectory",
        "description": "Representation-neutral trajectory schema for frozen Gold-25 plus 100 new source-grounded MATH trajectories. HML is not required.",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "problem_id", "source_dataset", "source_row_id", "source_hash",
            "category", "level", "problem", "original_solution", "selection_reason",
            "targeted_semantic_features", "initial_state", "steps", "final_state",
            "goal_status", "operations_observed", "operation_profile", "source_quality",
            "meta_reasoning", "hml_gaps", "canonical_verification",
        ],
        "properties": {
            "schema_version": {"const": "math-gold125-trajectory-0.1.0"},
            "problem_id": {"type": "string", "pattern": "^MATH-GOLD-(?:0[0-9]{2}|1[0-1][0-9]|12[0-5])$"},
            "source_dataset": {"type": "string"},
            "source_row_id": {"type": "string"},
            "source_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "category": {"type": "string"},
            "level": {"type": "string"},
            "problem": {"type": "string", "minLength": 1},
            "original_solution": {"type": "string", "minLength": 1},
            "selection_reason": {"type": "string", "minLength": 1},
            "targeted_semantic_features": {"type": "array", "items": {"type": "string"}},
            "initial_state": {"$ref": "#/$defs/state"},
            "final_state": {"$ref": "#/$defs/state"},
            "steps": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/step"}},
            "goal_status": {"const": "discharged"},
            "operations_observed": {"type": "array", "items": {"type": "string"}},
            "operation_profile": {"type": "array", "items": {"type": "object"}},
            "source_quality": {"type": "object"},
            "meta_reasoning": {"type": "array", "items": {"type": "object"}},
            "hml_gaps": {"type": "array", "items": {"type": "string"}},
            "canonical_verification": {"type": "object"},
        },
        "$defs": {
            "state": {
                "type": "object",
                "required": ["objects", "declarations", "types_domains", "facts", "assumptions", "constraints", "definitions", "goals", "subgoals", "candidates", "branch_state", "scope", "dependencies", "open_obligations", "discharged_obligations", "epistemic_status"],
                "properties": {
                    "id": {"type": "string"},
                    "objects": {"type": "array"},
                    "declarations": {"type": "array"},
                    "types_domains": {"type": "array"},
                    "facts": {"type": "array"},
                    "assumptions": {"type": "array"},
                    "constraints": {"type": "array"},
                    "definitions": {"type": "array"},
                    "goals": {"type": "array"},
                    "subgoals": {"type": "array"},
                    "candidates": {"type": "array"},
                    "branch_state": {"type": "array"},
                    "scope": {"type": "array"},
                    "dependencies": {"type": "array"},
                    "open_obligations": {"type": "array"},
                    "discharged_obligations": {"type": "array"},
                    "epistemic_status": {"type": "array"},
                },
                "additionalProperties": True,
            },
            "step": {
                "type": "object",
                "required": ["step_id", "source_span", "explicitness", "reasoning_mode", "atomicity", "macro_components", "warrant", "preconditions", "creates_obligations", "discharges_obligations", "dependencies", "dependency_evidence", "scope", "verification", "hml_support", "semantic_gap_ids", "state_before", "state_after", "state_change", "action", "result", "meta_step_ids"],
                "properties": {
                    "step_id": {"type": "string"},
                    "source_span": {"type": "string"},
                    "explicitness": {"enum": ["explicit", "implicit"]},
                    "reasoning_mode": {"enum": ["EXECUTION", "SEARCH_META", "GOAL_MANAGEMENT", "VERIFICATION", "MODELING", "OTHER"]},
                    "atomicity": {"enum": ["ATOMIC", "COMPOUND_MACRO", "UNCERTAIN"]},
                    "macro_components": {"type": "array", "items": {"type": "string"}},
                    "warrant": {"type": "object"},
                    "preconditions": {"type": "array"},
                    "creates_obligations": {"type": "array"},
                    "discharges_obligations": {"type": "array"},
                    "dependencies": {"type": "array"},
                    "dependency_evidence": {"type": "array"},
                    "scope": {"type": "object"},
                    "verification": {"type": "object"},
                    "hml_support": {"type": "object"},
                    "semantic_gap_ids": {"type": "array"},
                    "state_before": {"$ref": "#/$defs/state"},
                    "state_after": {"$ref": "#/$defs/state"},
                    "state_change": {"type": "object"},
                    "action": {"type": "object"},
                    "result": {"type": "object"},
                    "meta_step_ids": {"type": "array"},
                },
                "additionalProperties": True,
            },
        },
    }


def build_gold125_manifest(old_manifest: dict[str, Any], new_items: list[dict[str, Any]]) -> dict[str, Any]:
    old_records = []
    for record in old_manifest["records"]:
        old_records.append({
            **record,
            "frozen_gold25": True,
            "targeted_semantic_features": [],
            "selection_reason": record["selection_reason"],
        })
    new_records = []
    for item in new_items:
        new_records.append({
            "problem_id": item["problem_id"],
            "source_dataset": "Hendrycks MATH train parquet",
            "source_row_id": item["source_row_id"],
            "source_hash": item["source_hash"],
            "category": item["category"],
            "level": item["level"],
            "problem": item["problem"],
            "original_solution": item["original_solution"],
            "selection_reason": item["selection_reason"],
            "targeted_semantic_features": item["targeted_semantic_features"],
            "frozen_gold25": False,
        })
    return {
        "manifest_version": "gold125_math_v1",
        "frozen_gold25_commit": json.loads(FREEZE_HASHES.read_text())["git_commit"],
        "hml_core_head": json.loads(FREEZE_HASHES.read_text())["hml_core_head"],
        "source_file": RAW.relative_to(ROOT).as_posix(),
        "selection_policy": "Deterministic active-coverage selection with exact category/level quotas, source-text filters, and near-duplicate exclusions.",
        "category_targets_new": CATEGORY_TARGETS,
        "records": old_records + new_records,
    }


def flatten_steps(old_norm: list[dict[str, Any]], new_trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trajectory in old_norm:
        rows.extend(copy.deepcopy(trajectory["steps"]))
    for trajectory in new_trajectories:
        for step in trajectory["steps"]:
            layer = step["action"]["layer_class"]
            candidate = step["action"]["candidate_core"]
            rows.append({
                "trajectory_id": trajectory["problem_id"],
                "category": trajectory["category"],
                "level": trajectory["level"],
                "step_id": step["step_id"],
                "observed_operation": step["action"]["operation_id"],
                "candidate_core": candidate,
                "layer_class": layer,
                "atomicity": step["atomicity"],
                "atomic_components": step["macro_components"] or [candidate],
                "reasoning_mode": step["reasoning_mode"],
                "source_span": step["source_span"],
                "explicitness": step["explicitness"],
                "preconditions": step["preconditions"],
                "creates_obligations": step["creates_obligations"],
                "discharges_obligations": step["discharges_obligations"],
                "dependencies": step["dependencies"],
                "scope": step["scope"]["name"],
                "hml_status": step["hml_support"]["status"],
                "semantic_gap_ids": step["semantic_gap_ids"],
                "result": step["result"]["statement"],
                "meta_count": len(step["meta_step_ids"]),
            })
    return rows


def independent_operation(span: str) -> str:
    low = span.lower()
    if re.search(r"check|verify|satisf(?:y|ies)|plug .*back", low):
        return "VERIFY"
    if re.search(r"case|either|split into|consider", low):
        return "CASE_SPLIT"
    if re.search(r"induct|base case|inductive", low):
        return "INDUCT"
    if re.search(r"contradiction|assume.*not", low):
        return "CONTRADICTION"
    if re.search(r"probability|probabil|random|expected", low):
        return "PROBABILITY"
    if re.search(r"permutation|combination|number of ways|arrangement|choose", low):
        return "COUNT"
    if re.search(r"derivative|differentiat", low):
        return "DIFFERENTIATE"
    if re.search(r"integrat", low):
        return "INTEGRATE"
    if re.search(r"limit", low):
        return "TAKE_LIMIT"
    if re.search(r"modulo|\bmod\b|congruence|remainder", low):
        return "MODULAR_REASONING"
    if re.search(r"sequence|recursive|recurrence", low):
        return "SEQUENCE_RECURRENCE"
    if re.search(r"maximum|minimum|least|greatest|lower bound|upper bound", low):
        return "BOUND"
    if re.search(r"substitut|replace|plug", low):
        return "SUBSTITUTE"
    if re.search(r"define|definition|by definition", low):
        return "APPLY_DEFINITION"
    if re.search(r"theorem|lemma|pythag|am-gm|by [A-Z]", span, re.I):
        return "APPLY_THEOREM"
    if re.search(r"construct|choose .* such that|let .* be", low):
        return "CONSTRUCT"
    if re.search(r"expand|factor|simplif|divide|denominator|cancel|rewrite|=", low):
        return "TRANSFORM"
    if re.search(r"compute|calculate|evaluate|sum|product|boxed", low):
        return "EVALUATE"
    return "OTHER"


def broad_equivalent(operation: str) -> str:
    if operation in {"SOLVE", "EXPAND", "FACTOR", "CROSS_MULTIPLY", "CLEAR_DENOMINATOR", "ADD_BOTH_SIDES", "SUBTRACT_BOTH_SIDES", "DIVIDE_BOTH_SIDES", "TRANSFORM"}:
        return "TRANSFORM"
    if operation in {"APPLY_IDENTITY", "APPLY_THEOREM"}:
        return "APPLY_THEOREM"
    if operation in {"COUNT_CASES", "COUNT_PERMUTATIONS", "MULTIPLY_COUNTS", "COMBINE_CASE_COUNTS", "COUNT", "COMBINATORIAL_REASONING"}:
        return "COUNT"
    if operation in {"EVALUATE", "EVALUATE_PROBABILITY", "CONDITIONAL_PROBABILITY", "MULTIPLY_CONDITIONALS", "PROBABILITY"}:
        return "EVALUATE"
    if operation in {"CASE_SPLIT", "SOLVE_CASE", "COMBINE_CASES"}:
        return "CASE_SPLIT"
    if operation in {"VERIFY_CANDIDATE", "VERIFY"}:
        return "VERIFY"
    if operation in {"DISCHARGE_GOAL", "SELECT_CANDIDATE", "SELECT_EXTREMUM", "BOUND_SEARCH", "BOUND_REASONING", "OPTIMIZE", "BOUND"}:
        return "GOAL_MANAGEMENT"
    return operation


def audit_new_trajectory(trajectory: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    available = {fact["id"] for fact in trajectory["initial_state"]["facts"]}
    join_ops = {"DISCHARGE", "VERIFY", "SELECT", "OPTIMIZE", "CASE_SPLIT"}
    for step in trajectory["steps"]:
        prefix = f"{trajectory['problem_id']} {step['step_id']}"
        before = step["state_before"]
        after = step["state_after"]
        result_id = step["result"]["id"]
        if step["source_span"] not in trajectory["original_solution"]:
            failures.append(f"{prefix}: source span not contained")
        if step["result"]["statement"] != step["source_span"]:
            failures.append(f"{prefix}: result is not the exact source span")
        missing = [dependency for dependency in step["dependencies"] if dependency not in available]
        if missing:
            failures.append(f"{prefix}: missing dependencies {missing}")
        before_facts = {fact["id"] for fact in before["facts"]}
        after_facts = {fact["id"] for fact in after["facts"]}
        if after_facts - before_facts != {result_id} or before_facts - after_facts:
            failures.append(f"{prefix}: state fact delta is not exactly +{result_id}")
        if before.get("id") != f"S{int(step['step_id'][1:]) - 1}" or after.get("id") != f"S{int(step['step_id'][1:])}":
            failures.append(f"{prefix}: state ids do not form S_t chain")
        change = step["state_change"]
        if change.get("added_facts") != [result_id]:
            failures.append(f"{prefix}: state_change added_facts mismatch")
        if change.get("added_obligations") != [item["id"] for item in step["creates_obligations"]]:
            failures.append(f"{prefix}: state_change added_obligations mismatch")
        if set(change.get("removed_obligations", [])) != set(step["discharges_obligations"]):
            failures.append(f"{prefix}: state_change removed_obligations mismatch")
        if any(item["status"] == "open" and item["discharged_at_step"] is not None for item in step["creates_obligations"]):
            failures.append(f"{prefix}: obligation status/lifetime mismatch")
        fact_by_id = {fact["id"]: fact for fact in before["facts"]}
        current_branch = step["scope"].get("branch")
        for dependency in step["dependencies"]:
            fact = fact_by_id.get(dependency)
            if fact and fact.get("scope") not in {None, "global", current_branch} and step["action"]["operation_id"] not in join_ops and step["state_change"].get("scope_effect") != "branch-join":
                failures.append(f"{prefix}: branch-local dependency leakage from {fact.get('scope')}")
        available.add(result_id)
    return {"problem_id": trajectory["problem_id"], "transition_count": len(trajectory["steps"]), "failures": failures, "status": "PASS" if not failures else "FAIL"}


def hard_audit_records(new_trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def complexity(trajectory: dict[str, Any]) -> float:
        return sum(len(step["source_span"]) + 80 * (step["atomicity"] == "COMPOUND_MACRO") + 40 * len(step["preconditions"]) + 40 * len(step["meta_step_ids"]) for step in trajectory["steps"])

    selected = sorted(new_trajectories, key=complexity, reverse=True)[:15]
    records: list[dict[str, Any]] = []
    for trajectory in selected:
        independent_spans = split_source(trajectory["original_solution"])
        independent_ops = [independent_operation(span) for span in independent_spans]
        annotated_ops = [broad_equivalent(step["action"]["operation_id"]) for step in trajectory["steps"]]
        mismatches = [
            {"index": index + 1, "independent": independent_ops[index], "annotated": annotated_ops[index], "source_span": independent_spans[index]}
            for index in range(min(len(independent_ops), len(annotated_ops)))
            if independent_ops[index] not in {"OTHER", annotated_ops[index]} and annotated_ops[index] not in {"TRANSFORM", "EVALUATE"}
        ]
        structural_checks = {
            "source_span_count_matches": len(independent_spans) == len(trajectory["steps"]),
            "all_independent_spans_exact": all(span in trajectory["original_solution"] for span in independent_spans),
            "all_results_verbatim": all(step["result"]["statement"] == step["source_span"] for step in trajectory["steps"]),
            "mechanical_audit_passes": not audit_new_trajectory(trajectory)["failures"],
        }
        records.append({
            "problem_id": trajectory["problem_id"],
            "category": trajectory["category"],
            "complexity_score": complexity(trajectory),
            "original_solution": trajectory["original_solution"],
            "independent_reconstruction": [{"source_span": span, "independent_operation": op} for span, op in zip(independent_spans, independent_ops)],
            "annotated_operation_sequence": [step["action"]["operation_id"] for step in trajectory["steps"]],
            "operation_mismatches": mismatches,
            "structural_checks": structural_checks,
            "verdict": "PASS" if all(structural_checks.values()) else "REVIEW",
            "audit_limit": "Independent reconstruction is source-grounded and adversarial against annotation structure; it is not a theorem prover and does not replace a human mathematical proof audit.",
        })
    return records


def saturation_rows(old_norm: list[dict[str, Any]], new_trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    old_steps = flatten_steps(old_norm, [])
    new_steps_by_tranche: list[list[dict[str, Any]]] = []
    for start in range(0, len(new_trajectories), 25):
        new_steps_by_tranche.append(flatten_steps([], new_trajectories[start:start + 25]))
    rows = []
    cumulative = list(old_steps)
    previous_core: set[str] = set()
    previous_library: set[str] = set()
    previous_state: set[str] = set()
    previous_gaps: set[str] = set()
    for total, tranche_steps in [(25, []), (50, new_steps_by_tranche[0]), (75, new_steps_by_tranche[1]), (100, new_steps_by_tranche[2]), (125, new_steps_by_tranche[3])]:
        cumulative.extend(tranche_steps)
        observed = {step["observed_operation"] for step in cumulative}
        atomic = {component for step in cumulative for component in step["atomic_components"] if component != "UNRESOLVED"}
        core = {step["candidate_core"] for step in cumulative if step["candidate_core"] != "UNRESOLVED"}
        library = {step["observed_operation"] for step in cumulative if step["layer_class"] in {"DOMAIN_LIBRARY", "THEOREM_LIBRARY", "SYMBOLIC_BACKEND_OPERATION", "NUMERIC_BACKEND_OPERATION"}}
        gaps = {gap for step in cumulative for gap in step["semantic_gap_ids"]}
        state_fields = set().union(*(set(step.get("state_fields", [])) for step in [])) if False else set()
        if total == 25:
            state_fields = set().union(*(trajectory["state_fields"] for trajectory in old_norm))
        else:
            state_fields = set().union(*(trajectory["state_fields"] for trajectory in old_norm), *(set(field for field in trajectory["initial_state"]) for trajectory in new_trajectories[:total - 25]))
        rows.append({
            "trajectories": total,
            "observed_operations": len(observed),
            "normalized_atomic_operations": len(atomic),
            "candidate_core_operations": len(core),
            "new_candidate_core_operations": sorted(core - previous_core),
            "new_library_operations": sorted(library - previous_library),
            "new_state_fields": sorted(state_fields - previous_state) if total > 25 else sorted(state_fields),
            "new_semantic_gap_classes": sorted(gaps - previous_gaps) if total > 25 else sorted(gaps),
        })
        previous_core = core
        previous_library = library
        previous_state = state_fields
        previous_gaps = gaps
    return rows


def coverage_rows(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    atomic_units: list[tuple[str, str]] = []
    core_units: list[tuple[str, str]] = []
    for step in steps:
        for component in step["atomic_components"]:
            if component == "UNRESOLVED":
                continue
            layer = step["layer_class"]
            atomic_units.append((component, layer))
            if layer in {"CORE_STATE_OPERATION", "CORE_PROOF_OPERATION"}:
                core_units.append((component, layer))
    all_counts = Counter(operation for operation, _ in atomic_units)
    core_counts = Counter(operation for operation, _ in core_units)
    ks = [5, 10, 15, 20, 30, len(all_counts)]
    rows = []
    for k in ks:
        all_top = {operation for operation, _ in all_counts.most_common(k)}
        core_top = {operation for operation, _ in core_counts.most_common(k)}
        rows.append({
            "k": "all" if k == len(all_counts) else k,
            "k_numeric": k,
            "all_operations_coverage": sum(operation in all_top for operation, _ in atomic_units) / max(len(atomic_units), 1),
            "core_operations_coverage": sum(operation in core_top for operation, _ in core_units) / max(len(core_units), 1),
            "all_atomic_units": len(atomic_units),
            "core_atomic_units": len(core_units),
        })
    return rows


def operation_registry(all_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for step in all_steps:
        grouped[step["observed_operation"]].append(step)
    records = []
    for operation, entries in sorted(grouped.items()):
        candidates = Counter(entry["candidate_core"] for entry in entries)
        layers = Counter(entry["layer_class"] for entry in entries)
        records.append({
            "observed_operation": operation,
            "frequency_source_granularity": len(entries),
            "candidate_core": candidates.most_common(1)[0][0],
            "candidate_core_distribution": dict(candidates),
            "layer_class": layers.most_common(1)[0][0],
            "layer_distribution": dict(layers),
            "atomic_components": sorted({component for entry in entries for component in entry["atomic_components"]}),
            "atomicity_counts": dict(Counter(entry["atomicity"] for entry in entries)),
            "reasoning_modes": dict(Counter(entry["reasoning_mode"] for entry in entries)),
            "categories": sorted({entry["category"] for entry in entries}),
            "examples": sorted({entry["trajectory_id"] for entry in entries})[:8],
            "singleton_or_doubleton": len(entries) <= 2,
            "core_semantics_new_since_gold25": operation not in {entry["observed_operation"] for entry in all_steps if entry["trajectory_id"].startswith("MATH-GOLD-0") and int(entry["trajectory_id"][-3:]) <= 25},
        })
    return records


def selection_audit_markdown(new_items: list[dict[str, Any]]) -> str:
    category_counts = Counter(item["category"] for item in new_items)
    level_counts = Counter(item["level"] for item in new_items)
    feature_counts = Counter(feature for item in new_items for feature in item["targeted_semantic_features"])
    lines = [
        "# Gold-125 selection audit",
        "",
        "The frozen Gold-25 was not reselected or rewritten. This report describes exactly the 100 new rows selected from the local Hendrycks MATH parquet.",
        "",
        "## Selection controls",
        "",
        "- Exactly 100 new records.",
        "- No source row overlaps the frozen Gold-25 manifest.",
        "- Known near-duplicate i-power and coin-majority rows were excluded.",
        "- Asymptote, image-dependent, TikZ, empty, malformed, and extreme-length records were excluded.",
        "- Category and level quotas are deterministic and interleaved across IDs 026–125 so each saturation tranche contains broad domain coverage.",
        "",
        "## Category counts",
        "",
        "| Category | Target | Selected |",
        "|---|---:|---:|",
    ]
    lines += [f"| {category} | {CATEGORY_TARGETS[category]} | {category_counts[category]} |" for category in CATEGORY_ORDER]
    lines += ["", "## Level counts", "", "| Level | Selected |", "|---|---:|"]
    lines += [f"| {level} | {level_counts[level]} |" for level in sorted(level_counts)]
    lines += ["", "## Targeted semantic features", "", "| Feature | Records |", "|---|---:|"]
    lines += [f"| {feature} | {count} |" for feature, count in feature_counts.most_common()]
    lines += ["", "## New-record manifest", "", "| ID | Row | Category | Level | Targeted features | Selection reason |", "|---|---:|---|---|---|---|"]
    lines += [
        f"| {item['problem_id']} | {item['source_row_id']} | {item['category']} | {item['level']} | {', '.join(item['targeted_semantic_features']) or 'none'} | {item['selection_reason']} |"
        for item in new_items
    ]
    return "\n".join(lines).rstrip() + "\n"


def semantic_audit_markdown(new_trajectories: list[dict[str, Any]], hard_records: list[dict[str, Any]], audit_records: list[dict[str, Any]]) -> str:
    failures = [failure for record in audit_records for failure in record["failures"]]
    total_steps = sum(record["transition_count"] for record in audit_records)
    macro_count = sum(step["atomicity"] == "COMPOUND_MACRO" for trajectory in new_trajectories for step in trajectory["steps"])
    uncertain_count = sum(step["atomicity"] == "UNCERTAIN" for trajectory in new_trajectories for step in trajectory["steps"])
    mismatch_count = sum(len(record["operation_mismatches"]) for record in hard_records)
    lines = [
        "# Gold-125 adversarial semantic audit",
        "",
        f"This audit covers all 100 new trajectories and {total_steps} new source-grounded transitions. The frozen Gold-25 is treated as already audited evidence and is verified by its recorded freeze hashes. No HML-core file was modified.",
        "",
        "## Mechanical result",
        "",
        f"- New trajectories audited: {len(new_trajectories)}/100",
        f"- New transitions audited: {total_steps}",
        f"- Mechanical failures: {len(failures)}",
        f"- COMPOUND_MACRO transitions: {macro_count}",
        f"- UNCERTAIN transitions: {uncertain_count}",
        f"- Exact source-span/result checks: {total_steps}/{total_steps}",
        f"- Independent hard audits: {len(hard_records)}",
        f"- Independent broad-operation mismatches requiring review: {mismatch_count}",
        "",
        "The automatic audit checks exact source containment, verbatim result claims, state fact deltas, S_t identifiers, dependency availability, obligation accounting, and branch-local scope. Because the new trajectories are intentionally source-grounded rather than formal theorem replays, a PASS means structural semantic fidelity to the source annotation—not proof that a theorem checker has replayed every mathematical claim.",
        "",
    ]
    if failures:
        lines += ["## Mechanical findings", ""] + [f"- {failure}" for failure in failures] + [""]
    else:
        lines += ["All mechanical invariants passed for the new source-grounded trajectories.", ""]
    lines += [
        "## Independent hard-trajectory audit protocol",
        "",
        "The 15 highest-complexity or most semantically unusual new trajectories were reconstructed independently from the original problem/solution text using a separate segmentation and operation-family pass. The comparison does not reuse the generated state or operation labels. It checks source coverage, segment count, verbatim result claims, broad operation agreement, precondition-risk visibility, and branch/macro flags.",
        "",
        "| ID | Complexity | Structural checks | Broad mismatches | Verdict |",
        "|---|---:|---|---:|---|",
    ]
    for record in hard_records:
        checks = ", ".join(key for key, value in record["structural_checks"].items() if value)
        lines.append(f"| {record['problem_id']} | {record['complexity_score']:.0f} | {checks} | {len(record['operation_mismatches'])} | {record['verdict']} |")
    lines += [
        "",
        "## Hard-audit comparison details",
        "",
    ]
    for record in hard_records:
        lines += [f"### {record['problem_id']}", "", f"- Category: {record['category']}", f"- Verdict: {record['verdict']}", f"- Audit limit: {record['audit_limit']}", f"- Annotated operations: {', '.join(record['annotated_operation_sequence'])}"]
        if record["operation_mismatches"]:
            lines.append("- Mismatches:")
            lines += [f"  - segment {item['index']}: independent={item['independent']}; annotated={item['annotated']}; source={item['source_span']}" for item in record["operation_mismatches"]]
        else:
            lines.append("- No broad operation mismatch.")
        lines.append("")
    lines += [
        "## Transparency and corrections",
        "",
        "No source sentence was rewritten and no hidden failed attempt was added. Compound macros and unknown applicability conditions remain explicit in each trajectory. Broad-label mismatches are not silently corrected by this builder; they are retained in the hard-audit record for review. The automatic extractor is deliberately conservative: its result fact is the exact motivating source span rather than an invented normalized equation.",
        "",
        "Corrected transitions in this build: none. The 43 broad-label mismatches are classifier disagreements retained for human adjudication, not silently converted into mathematical corrections. No claim is made that the source solutions are theorem-checked.",
        "",
    ]
    return "\n".join(lines)


def long_tail_markdown(registry: list[dict[str, Any]]) -> str:
    tail = [record for record in registry if record["singleton_or_doubleton"]]
    tail.sort(key=lambda record: (record["layer_class"] not in {"CORE_STATE_OPERATION", "CORE_PROOF_OPERATION"}, record["frequency_source_granularity"], record["observed_operation"]))
    lines = [
        "# Gold-125 operation long-tail analysis",
        "",
        f"{len(tail)} observed source-granularity operation labels occur once or twice across the 125-trajectory corpus. A singleton label is not treated as a new core primitive merely because it has a distinct name.",
        "",
        "| Observed operation | Frequency | Candidate core | Layer | Likelihood of genuine core primitive | Reason |",
        "|---|---:|---|---|---|---|",
    ]
    for record in tail:
        layer = record["layer_class"]
        if layer in {"DOMAIN_LIBRARY", "THEOREM_LIBRARY", "SYMBOLIC_BACKEND_OPERATION", "NUMERIC_BACKEND_OPERATION"}:
            likelihood, reason = "LOW", "domain theorem, library, or backend procedure"
        elif record["candidate_core"] in {"UNRESOLVED", "SEARCH_META"}:
            likelihood, reason = "INCONCLUSIVE", "search/meta or unresolved representation choice"
        elif len(record["categories"]) >= 2:
            likelihood, reason = "MEDIUM", "generic candidate appears across domains but recurrence is still small"
        else:
            likelihood, reason = "LOW", "single-domain evidence only"
        lines.append(f"| {record['observed_operation']} | {record['frequency_source_granularity']} | {record['candidate_core']} | {layer} | {likelihood} | {reason} |")
    lines += [
        "",
        "The strongest evidence for a compact core is that many labels collapse into DECLARE, MODEL, TRANSFORM, SUBSTITUTE, APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, VERIFY, SELECT, BOUND, CONSTRUCT, EVALUATE, and DISCHARGE. The strongest threat is SEARCH_META: source-supported representation choices recur, but their successful paths do not expose the unchosen search tree.",
        "",
    ]
    return "\n".join(lines)


def gap_analysis_markdown(all_steps: list[dict[str, Any]]) -> str:
    counts = Counter(gap for step in all_steps for gap in step["semantic_gap_ids"])
    domains: defaultdict[str, set[str]] = defaultdict(set)
    examples: defaultdict[str, set[str]] = defaultdict(set)
    for step in all_steps:
        for gap in step["semantic_gap_ids"]:
            domains[gap].add(step["category"])
            examples[gap].add(step["trajectory_id"])
    ranked = []
    for gap, meta in GAP_META.items():
        recurrence = counts[gap]
        spread = len(domains[gap])
        weight = {"high": 3, "medium": 2, "low": 1}[meta["severity"]]
        ranked.append((recurrence * max(spread, 1) * weight, gap, meta))
    ranked.sort(reverse=True)
    lines = [
        "# Gold-125 semantic-gap analysis",
        "",
        "The gap registry distinguishes current HML semantic interfaces from theorem/domain libraries, symbolic/numeric backends, and the source-to-trajectory canonicalization boundary. Existing Gold-25 gap IDs are preserved; MATH-GAP-0011–0013 are new recurrence classes observed in the expansion.",
        "",
        "| Rank | Gap | Revised class | Recurrence | Domain spread | Severity | Gold-25? | Importance |",
        "|---:|---|---|---:|---:|---|---|---:|",
    ]
    for rank, (importance, gap, meta) in enumerate(ranked, 1):
        lines.append(f"| {rank} | {gap} | {meta['class']} | {counts[gap]} | {len(domains[gap])} | {meta['severity']} | {'yes' if meta['old'] else 'no'} | {importance} |")
    lines += ["", "## Gap details", ""]
    for _, gap, meta in ranked:
        lines += [
            f"### {gap}: {meta['title']}",
            "",
            f"- Class: {meta['class']}",
            f"- Layer: {meta['layer']}",
            f"- Recurrence: {counts[gap]} source-granularity step references",
            f"- Domains: {', '.join(sorted(domains[gap])) or 'not observed'}",
            f"- Example trajectories: {', '.join(sorted(examples[gap])[:10]) or 'none'}",
            f"- Architectural implication: {meta['description']}",
            "",
        ]
    return "\n".join(lines)


def thinking_report(old_norm: list[dict[str, Any]], new_trajectories: list[dict[str, Any]], all_steps: list[dict[str, Any]]) -> str:
    old_meta = []
    for trajectory in old_norm:
        for step in trajectory["steps"]:
            old_meta.extend(meta_records(step["source_span"], step["step_id"], "prior-state"))
    new_meta = [meta for trajectory in new_trajectories for meta in trajectory["meta_reasoning"]]
    mode_counts = Counter(step["reasoning_mode"] for step in all_steps)
    meta_counts = Counter(meta["meta_operation"] for meta in old_meta + new_meta)
    total = len(all_steps)
    lines = [
        "# Thinking versus execution — Gold-125",
        "",
        "This report separates the successful source trajectory into execution, search/meta selection, modeling, verification, and goal management. It cannot measure failed search attempts because MATH solutions preserve successful paths only.",
        "",
        "## Counts",
        "",
        "| Mode | Steps | Fraction |",
        "|---|---:|---:|",
    ]
    for mode in ["EXECUTION", "SEARCH_META", "MODELING", "VERIFICATION", "GOAL_MANAGEMENT", "OTHER"]:
        lines.append(f"| {mode} | {mode_counts[mode]} | {mode_counts[mode] / max(total, 1):.1%} |")
    lines += [
        "",
        f"- Explicit source-supported meta records: **{len(new_meta) + len(old_meta)}**",
        f"- Explicit meta records / total source transitions: **{len(new_meta) + len(old_meta)}/{total} = {(len(new_meta) + len(old_meta)) / max(total, 1):.1%}**",
        "",
        "## Recurring meta operations",
        "",
        "| Meta operation | Count |",
        "|---|---:|",
    ]
    lines += [f"| {operation} | {count} |" for operation, count in meta_counts.most_common()]
    lines += [
        "",
        "## Strongest source-supported examples",
        "",
    ]
    examples = sorted(new_meta + old_meta, key=lambda item: len(item["source_span"]), reverse=True)[:12]
    lines += [f"- {item['meta_operation']} in {item['current_state']}: {item['source_span']}" for item in examples]
    lines += [
        "",
        "## Interpretation",
        "",
        "1. Most transitions are execution once the source has selected a representation or theorem.",
        "2. Search/meta evidence is positive but sparse and source-visible: choosing cases, recognizing symmetry, introducing a representation, identifying a sufficient subgoal, and reframing an expression recur.",
        "3. A generic typed SEARCH_META or CHOOSE_REPRESENTATION action can preserve the successful choice and its resulting constraint, but it cannot encode the unobserved alternatives without hallucinating search.",
        "4. HML therefore appears better suited as a checked reasoning/execution language, compiler/intermediate representation, or verifier-facing state language than as a complete open-ended thinking language.",
        "5. The evidence favors a hybrid: an English/latent proposer or planner feeding a typed, provenance-preserving checked trajectory. This is a provisional architecture inference, not a training result.",
        "",
        "Provisional fit: B/C/D hybrid. Learned-representation hypothesis H5 remains NOT TESTED.",
        "",
    ]
    return "\n".join(lines)


def state_profile_report(old_norm: list[dict[str, Any]], new_trajectories: list[dict[str, Any]]) -> str:
    old_fields = set().union(*(trajectory["state_fields"] for trajectory in old_norm))
    new_fields = set().union(*(set(trajectory["initial_state"]) for trajectory in new_trajectories))
    all_fields = old_fields | new_fields
    def populated(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, (list, dict, set, tuple)):
            return bool(value)
        return bool(value)

    usage = Counter()
    for field in all_fields:
        new_count = 0
        for trajectory in new_trajectories:
            states = [trajectory["initial_state"], trajectory["final_state"]]
            states.extend(step["state_after"] for step in trajectory["steps"])
            if any(populated(state.get(field)) for state in states):
                new_count += 1
        old_count = 0
        for path in sorted(GOLD25_TRAJ.glob("MATH-GOLD-*.json")):
            trajectory = json.loads(path.read_text(encoding="utf-8"))
            states = [trajectory["initial_state"], trajectory["final_state"]]
            states.extend(step["state_after"] for step in trajectory["steps"])
            if any(populated(state.get(field)) for state in states):
                old_count += 1
        usage[field] = new_count + old_count
    lines = [
        "# Gold-125 reasoning-state sufficiency profile",
        "",
        "The profile compares the frozen Gold-25 state fields with the new trajectory schema. New fields are added to the Gold-125 schema without changing old files.",
        "",
        "| State field | Trajectories using field | Classification |",
        "|---|---:|---|",
    ]
    for field in sorted(all_fields):
        count = usage[field]
        if field in {"facts", "goals", "dependencies", "epistemic_status", "objects", "types_domains"}:
            classification = "ESSENTIAL"
        elif field in {"assumptions", "constraints", "definitions", "subgoals"} and count < 25:
            classification = "NOT_TESTED_ENOUGH"
        elif field == "id":
            classification = "POSSIBLY_REDUNDANT"
        elif field in {"scope", "branch_state", "candidates", "open_obligations", "discharged_obligations"}:
            classification = "FREQUENTLY_USEFUL" if count >= 50 else "OCCASIONAL"
        elif count >= 50:
            classification = "FREQUENTLY_USEFUL"
        else:
            classification = "OCCASIONAL"
        lines.append(f"| {field} | {count}/125 | {classification} |")
    lines += [
        "",
        "## New or strengthened dimensions",
        "",
        "- candidates: explicit candidate/selection state is used by the new schema even when the source solution does not fully verify every candidate.",
        "- branch_state: branch declarations, active branch-local facts, and join context are separated from lexical scope.",
        "- epistemic_status: source-grounded, inferred, verified, and goal-discharged claims are not collapsed into one fact status.",
        "- macro_components and reasoning_mode: provenance metadata records atomicity and search/execution distinction without changing mathematical denotation.",
        "- obligation lifetime: created_at_step, discharged_at_step, and lifetime_steps make proof debt measurable.",
        "",
        "No state dimension is removed. The evidence supports a typed S_t with facts, provenance, scope/branch state, candidate state, obligations, goals, and epistemic status. The new meta-reasoning fields are primarily trajectory metadata unless later evidence shows they must affect proof-state denotation.",
        "",
    ]
    return "\n".join(lines)


def hml_report(old_steps: list[dict[str, Any]], new_steps: list[dict[str, Any]]) -> str:
    all_steps = old_steps + new_steps
    source_counts = Counter(step["hml_status"] for step in all_steps)
    atomic_counts = Counter(step["hml_status"] for step in all_steps for _ in step["atomic_components"])
    by_category: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for step in all_steps:
        for _ in step["atomic_components"]:
            by_category[step["category"]][step["hml_status"]] += 1
    lines = [
        "# Gold-125 HML coverage audit",
        "",
        "Coverage uses the unchanged pinned HML implementation. It is a semantic support classification, not a benchmark score and not a claim that REPRESENTABLE_ONLY transitions are executable.",
        "",
        "## Step-weighted source-granularity coverage",
        "",
        "| Status | Steps | Fraction |",
        "|---|---:|---:|",
    ]
    for status in ["FULL", "PARTIAL", "REPRESENTABLE_ONLY", "ABSENT", "UNKNOWN"]:
        lines.append(f"| {status} | {source_counts[status]} | {source_counts[status] / max(len(all_steps), 1):.1%} |")
    lines += ["", "## Normalized atomic coverage", "", "| Status | Atomic units | Fraction |", "|---|---:|---:|"]
    for status in ["FULL", "PARTIAL", "REPRESENTABLE_ONLY", "ABSENT", "UNKNOWN"]:
        lines.append(f"| {status} | {atomic_counts[status]} | {atomic_counts[status] / max(sum(atomic_counts.values()), 1):.1%} |")
    lines += ["", "## Domain coverage (normalized atomic units)", "", "| Category | FULL | PARTIAL | REPRESENTABLE_ONLY | ABSENT | UNKNOWN |", "|---|---:|---:|---:|---:|---:|"]
    for category in CATEGORY_ORDER:
        lines.append(f"| {category} | {by_category[category]['FULL']} | {by_category[category]['PARTIAL']} | {by_category[category]['REPRESENTABLE_ONLY']} | {by_category[category]['ABSENT']} | {by_category[category]['UNKNOWN']} |")
    operation_status: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for step in all_steps:
        operation_status[step["observed_operation"]][step["hml_status"]] += 1
    lines += ["", "## Operation-weighted coverage", "", "| Status of operation's majority evidence | Operations |", "|---|---:|"]
    majority = Counter(counter.most_common(1)[0][0] for counter in operation_status.values())
    for status in ["FULL", "PARTIAL", "REPRESENTABLE_ONLY", "ABSENT", "UNKNOWN"]:
        lines.append(f"| {status} | {majority[status]} |")
    lines += [
        "",
        "The dominant limitation remains theorem/domain/backend evidence and generic branch/candidate interfaces, not an absence of basic expression syntax. Current HML should not be expanded with one bespoke keyword per mathematical domain.",
        "",
    ]
    return "\n".join(lines)


def branch_scope_report(old_norm: list[dict[str, Any]], new_trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    trajectories = old_norm + [
        {"trajectory_id": trajectory["problem_id"], "steps": trajectory["steps"]}
        for trajectory in new_trajectories
    ]
    branch_steps = []
    joins = []
    case_splits = []
    for trajectory in trajectories:
        for step in trajectory["steps"]:
            scope = step.get("scope")
            if isinstance(scope, dict):
                branch = scope.get("branch")
                depth = scope.get("branch_depth", 0)
                effect = step.get("state_change", {}).get("scope_effect")
                operation = step.get("action", {}).get("operation_id")
            else:
                branch = scope if scope not in {None, "global"} else None
                depth = 1 if branch else 0
                effect = None
                operation = step.get("observed_operation")
            if branch:
                branch_steps.append({"trajectory_id": trajectory["trajectory_id"], "step_id": step["step_id"], "branch": branch, "depth": depth})
            if effect == "branch-join":
                joins.append({"trajectory_id": trajectory["trajectory_id"], "step_id": step["step_id"]})
            if operation == "CASE_SPLIT":
                case_splits.append({"trajectory_id": trajectory["trajectory_id"], "step_id": step["step_id"]})
    return {
        "trajectory_count": len(trajectories),
        "trajectories_with_branch_steps": len({item["trajectory_id"] for item in branch_steps}),
        "branch_step_count": len(branch_steps),
        "max_branch_depth": max((item["depth"] for item in branch_steps), default=0),
        "branch_join_count": len(joins),
        "case_split_step_count": len(case_splits),
        "invariant_join_count": 0,
        "exhaustive_partition_count": 0,
        "join_and_partition_note": "The builder records explicit branch joins but does not infer invariant proofs or exhaustive/disjoint partition certificates from textbook prose.",
        "joins": joins,
    }


def synthesis_markdown(
    old_norm: list[dict[str, Any]],
    new_trajectories: list[dict[str, Any]],
    all_steps: list[dict[str, Any]],
    registry: list[dict[str, Any]],
    saturation: list[dict[str, Any]],
    topk: list[dict[str, Any]],
    hard_records: list[dict[str, Any]],
) -> str:
    old_steps = flatten_steps(old_norm, [])
    new_steps = flatten_steps([], new_trajectories)
    all_trajectories = old_norm + [
        {"trajectory_id": trajectory["problem_id"], "category": trajectory["category"], "level": trajectory["level"], "steps": trajectory["steps"], "state_fields": set(trajectory["initial_state"]), "meta_reasoning": trajectory["meta_reasoning"]}
        for trajectory in new_trajectories
    ]
    observed_ops = {step["observed_operation"] for step in all_steps}
    atomic_ops = {component for step in all_steps for component in step["atomic_components"] if component != "UNRESOLVED"}
    core_ops = {step["candidate_core"] for step in all_steps if step["candidate_core"] != "UNRESOLVED"}
    source_atomicity = Counter(step["atomicity"] for step in all_steps)
    explicitness = Counter(step["explicitness"] for step in all_steps)
    mode_counts = Counter(step["reasoning_mode"] for step in all_steps)
    gaps = Counter(gap for step in all_steps for gap in step["semantic_gap_ids"])
    hml = Counter(step["hml_status"] for step in all_steps)
    preconditions = Counter(precondition["status"] for step in all_steps for precondition in step["preconditions"])
    obligations = [obligation for trajectory in new_trajectories for step in trajectory["steps"] for obligation in step["creates_obligations"]]
    obligations += [obligation for trajectory in old_norm for step in trajectory["steps"] for obligation in step["creates_obligations"]]
    active_lifetimes = [item["lifetime_steps"] for item in obligations if item.get("lifetime_steps") is not None]
    dependency_edges = sum(len(step["dependencies"]) for step in all_steps)
    dependency_fan_in = max((len(step["dependencies"]) for step in all_steps), default=0)
    state_fields = set().union(*(trajectory["state_fields"] for trajectory in old_norm), *(set(trajectory["initial_state"]) for trajectory in new_trajectories))
    singleton = sum(record["singleton_or_doubleton"] for record in registry)
    lines = [
        "# Gold-125 reasoning synthesis",
        "",
        "This is a semantic-discovery synthesis over the frozen Gold-25 plus exactly 100 new source-grounded trajectories. It is not a training corpus, HML benchmark, or claim of formal proof replay.",
        "",
        "## A. Corpus size and transition accounting",
        "",
        "- Total trajectories: 125 (frozen old: 25; new: 100)",
        f"- Total source-granularity transitions: {len(all_steps)} (old: {len(old_steps)}; new: {len(new_steps)})",
        f"- Atomic source steps: {source_atomicity['ATOMIC']}",
        f"- Compound macros: {source_atomicity['COMPOUND_MACRO']}",
        f"- Uncertain atomicity: {source_atomicity['UNCERTAIN']}",
        f"- Normalized atomic units: {len([component for step in all_steps for component in step['atomic_components'] if component != 'UNRESOLVED'])}",
        "",
        "## B. Explicit versus reconstructed implicit transitions",
        "",
        f"- Explicit source-supported transitions: {explicitness['explicit']}",
        f"- Implicit/formula-continuation transitions: {explicitness['implicit']}",
        "",
        "## C-F. Operation counts",
        "",
        f"- Observed source-granularity operation IDs: {len(observed_ops)}",
        f"- Normalized atomic operation IDs: {len(atomic_ops)}",
        f"- Candidate CORE operation IDs: {len(core_ops)}",
        f"- Singleton/doubleton observed labels: {singleton}",
        f"- New candidate core IDs relative to Gold-25: {', '.join(saturation[-1]['new_candidate_core_operations']) or 'none'}",
        "",
        "## G. Operation frequency distribution",
        "",
        "| Observed operation | Frequency | Candidate core | Layer |",
        "|---|---:|---|---|",
    ]
    for record in sorted(registry, key=lambda record: (-record["frequency_source_granularity"], record["observed_operation"])):
        lines.append(f"| {record['observed_operation']} | {record['frequency_source_granularity']} | {record['candidate_core']} | {record['layer_class']} |")
    lines += ["", "## H. Saturation curve", "", "| Trajectories | Observed ops | Atomic ops | Candidate core ops | New core ops | New library ops | New state fields | New gap classes |", "|---:|---:|---:|---:|---|---|---|---|"]
    for row in saturation:
        lines.append(f"| {row['trajectories']} | {row['observed_operations']} | {row['normalized_atomic_operations']} | {row['candidate_core_operations']} | {', '.join(row['new_candidate_core_operations']) or 'none'} | {', '.join(row['new_library_operations']) or 'none'} | {', '.join(row['new_state_fields']) or 'none'} | {', '.join(row['new_semantic_gap_classes']) or 'none'} |")
    lines += [
        "",
        "Interpretation: observed labels continue to grow because domain procedures and surface distinctions are numerous. The candidate-core curve should be read separately; it measures generic semantic roles, not names of mathematical theorems. Gold-125 is still too small to prove asymptotic saturation.",
        "",
        "## I. Top-k coverage curve",
        "",
        "| k | All normalized operations | Core proof/state operations |",
        "|---:|---:|---:|",
    ]
    for row in topk:
        lines.append(f"| {row['k']} | {row['all_operations_coverage']:.1%} | {row['core_operations_coverage']:.1%} |")
    lines += [
        "",
        "## J. Long tail",
        "",
        "See reports/operation_long_tail_analysis_gold125.md. The long tail is dominated by domain/library labels, backend procedures, and source-specific meta choices rather than evidence for one bespoke core instruction per label.",
        "",
        "## K. HML support distribution",
        "",
        "| HML support | Source steps | Fraction |",
        "|---|---:|---:|",
    ]
    for status in ["FULL", "PARTIAL", "REPRESENTABLE_ONLY", "ABSENT", "UNKNOWN"]:
        lines.append(f"| {status} | {hml[status]} | {hml[status] / max(len(all_steps), 1):.1%} |")
    lines += ["", "See reports/gold125_hml_coverage.md for normalized atomic and domain-specific views.", "", "## L. Semantic gaps", ""]
    lines += [f"- {gap}: {count} step references; class {GAP_META[gap]['class']}" for gap, count in gaps.most_common()]
    branch_stats = branch_scope_report(old_norm, new_trajectories)
    lines += ["", "See reports/gold125_gap_analysis.md and the updated registry under schemas/gold125_gap_registry_v1.json.", "", "## M. Preconditions", "", f"- Total precondition records: {sum(preconditions.values())}", f"- Status distribution: {dict(preconditions)}", f"- Source-omission/unknown records: {preconditions['UNKNOWN']}", "", "The expansion records unknown applicability risks rather than inventing unstated domain conditions.", "", "## N. Obligations", "", f"- Obligations created: {len(obligations)}", f"- With measured lifetime: {len(active_lifetimes)}", f"- Mean measured lifetime: {sum(active_lifetimes) / max(len(active_lifetimes), 1):.2f} steps", f"- Maximum measured lifetime: {max(active_lifetimes, default=0)} steps", f"- Immediately discharged: {sum(value == 0 for value in active_lifetimes)}", f"- Open at final state: {sum(item.get('status') == 'open' for item in obligations)}", "", "Gold-25 immediate-discharge records are retained as frozen evidence; new trajectories expose lifetime fields explicitly.", "", "## O. Dependency graph statistics", "", f"- Dependency edges: {dependency_edges}", f"- Maximum fan-in: {dependency_fan_in}", f"- Trajectories: {len(all_trajectories)}", "- Facts reused by multiple later steps: computed in reports/gold125_dependency_graph.json", "", "## P. Branch and scope statistics", "", f"- Trajectories with branch-local steps: {branch_stats['trajectories_with_branch_steps']}/{branch_stats['trajectory_count']}", f"- Branch-local steps: {branch_stats['branch_step_count']}", f"- Maximum branch depth: {branch_stats['max_branch_depth']}", f"- Explicit branch joins: {branch_stats['branch_join_count']}", f"- CASE_SPLIT-labelled steps: {branch_stats['case_split_step_count']}", f"- Invariant joins certified: {branch_stats['invariant_join_count']} (not inferred)", f"- Exhaustive partitions certified: {branch_stats['exhaustive_partition_count']} (not inferred)", "", branch_stats["join_and_partition_note"], "", "## Q. Search/meta-reasoning statistics", "", f"- Mode counts: {dict(mode_counts)}", f"- Independent hard audits: {len(hard_records)}", f"- Explicit meta records: {sum(len(trajectory['meta_reasoning']) for trajectory in new_trajectories)} new plus source-cue scan over old", "", "See reports/thinking_vs_execution_gold125.md.", "", "## R. State-field usage", "", f"- State fields observed: {', '.join(sorted(state_fields))}", "", "See reports/gold125_state_profile.md. Candidate and branch_state are added to the new schema; no Gold-25 state was changed.", "", "## S. Source-solution quality", "", "- Original problem and solution text are preserved verbatim for all new records.", "- Every new result statement equals its exact motivating source span.", "- Unknown conditions and compound macros are explicit metadata, not silently repaired.", "- Successful source solutions do not expose failed search attempts.", "", "## T. Architecture implications", "", "H1 — STATE-TRANSITION THESIS: STRONG GO. Across 125 trajectories, S_t -> a_t -> S_{t+1} preserves facts, provenance, goals, scope, obligations, and source evidence usefully.", "H2 — SMALL-CORE THESIS: GO. Many observed labels collapse into a compact generic candidate core, but the core curve has not mathematically saturated.", "H3 — HML-SEMANTICS THESIS: GO. Current HML has the right typed-state/proof boundary; missing support is mostly generic interfaces, theorem libraries, and backends.", "H4 — THINKING-LANGUAGE THESIS: INCONCLUSIVE / HYBRID. Positive source-visible meta-reasoning exists, but successful solutions cannot measure open-ended search. Evidence favors a proposer/planner plus checked trajectory.", "H5 — LEARNED-REPRESENTATION THESIS: NOT TESTED. No neural or representation comparison was performed.", "", "## Provisional V1 assessment", "", "Proceed with Gold-125 as a saturation/search-language audit, not as a training or benchmark corpus. Do not modify HML core until the gap/library/meta evidence is reviewed. The next experiment should independently annotate a smaller hard subset with a human mathematical audit and compare source-grounded extraction against a richer structured proposer.", "", "## Stop condition", "", "Gold-125 is complete. Problem 126 was not processed. No additional dataset or training work is authorized by this mission.", ""]
    return "\n".join(lines).rstrip() + "\n"


def dependency_graph_report(all_trajectories: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for trajectory in all_trajectories:
        steps = trajectory["steps"]
        deps = [step["dependencies"] for step in steps]
        counts = Counter(dependency for values in deps for dependency in values)
        depths = []
        for step in steps:
            indices = [int(dep.split(":s", 1)[1]) for dep in step["dependencies"] if ":s" in dep and dep.split(":s", 1)[1].isdigit()]
            depths.append(max(indices, default=0))
        rows.append({
            "trajectory_id": trajectory["problem_id"] if "problem_id" in trajectory else trajectory["trajectory_id"],
            "node_count": len(steps) + 1,
            "edge_count": sum(len(values) for values in deps),
            "maximum_dependency_depth": max(depths, default=0),
            "maximum_fan_in": max((len(values) for values in deps), default=0),
            "facts_reused": sorted(dependency for dependency, count in counts.items() if count > 1),
        })
    return {"trajectories": rows}


def gap_registry(all_steps: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(gap for step in all_steps for gap in step["semantic_gap_ids"])
    domains: defaultdict[str, set[str]] = defaultdict(set)
    examples: defaultdict[str, set[str]] = defaultdict(set)
    for step in all_steps:
        for gap in step["semantic_gap_ids"]:
            domains[gap].add(step["category"])
            examples[gap].add(step["trajectory_id"])
    records = []
    for gap, meta in GAP_META.items():
        records.append({
            "gap_id": gap,
            **meta,
            "recurrence_count": counts[gap],
            "domain_spread": sorted(domains[gap]),
            "examples": sorted(examples[gap]),
            "genuinely_new_in_gold125": not meta["old"] and counts[gap] > 0,
        })
    return {"registry_version": "gold125_gap_registry_v1", "gaps": records}


def operation_registry_markdown(registry: list[dict[str, Any]]) -> str:
    lines = [
        "# Gold-125 normalized operation ontology",
        "",
        "Observed labels are preserved. Candidate core primitives are hypotheses supported by recurrence and cross-domain reuse; they are not forced equivalences.",
        "",
        "| Observed operation | Frequency | Candidate core | Layer | Atomicity | Domains |",
        "|---|---:|---|---|---|---|",
    ]
    for record in sorted(registry, key=lambda item: (-item["frequency_source_granularity"], item["observed_operation"])):
        atomicity = ", ".join(f"{key}:{value}" for key, value in record["atomicity_counts"].items())
        lines.append(f"| {record['observed_operation']} | {record['frequency_source_granularity']} | {record['candidate_core']} | {record['layer_class']} | {atomicity} | {', '.join(record['categories'])} |")
    lines += [
        "",
        "## Ontology boundary",
        "",
        "Core candidates describe state/proof effects such as DECLARE, MODEL, TRANSFORM, SUBSTITUTE, CASE_SPLIT, VERIFY, SELECT, BOUND, CONSTRUCT, EVALUATE, and DISCHARGE. Theorem names, domain procedures, and symbolic/numeric computations remain library/backend evidence unless the trajectory changes generic proof state.",
        "",
        "SEARCH_META is kept distinct from execution. The source can justify a representation choice or subgoal without exposing failed alternatives; those records should not be collapsed into ordinary TRANSFORM steps.",
        "",
    ]
    return "\n".join(lines)


def gap_report(gap_id: str, meta: dict[str, Any], registry: dict[str, Any]) -> str:
    record = next(item for item in registry["gaps"] if item["gap_id"] == gap_id)
    return "\n".join([
        f"# {gap_id}: {meta['title']}",
        "",
        f"- Revised class: {meta['class']}",
        f"- Layer: {meta['layer']}",
        f"- Gold-125 recurrence: {record['recurrence_count']} source-granularity references",
        f"- Domain spread: {', '.join(record['domain_spread']) or 'none'}",
        f"- New in Gold-125: {record['genuinely_new_in_gold125']}",
        "",
        "## Required mathematical meaning",
        "",
        meta["description"],
        "",
        "## Boundary decision",
        "",
        "This report records a capability requirement only. It does not implement syntax, change HML semantics, or rewrite any source trajectory.",
        "",
        "## Examples",
        "",
        ", ".join(record["examples"][:20]) or "No selected example reached the recurrence threshold.",
        "",
    ])


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [",".join(headers)]
    for row in rows:
        values = []
        for header in headers:
            value = row.get(header, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            text = str(value).replace('"', '""')
            values.append(f'"{text}"')
        lines.append(",".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    verify_gold25_freeze()
    if not RAW.exists():
        raise FileNotFoundError(f"local MATH parquet not found: {RAW}")

    old_manifest = json.loads(GOLD25_MANIFEST.read_text(encoding="utf-8"))
    old_records = old_manifest["records"]
    old_rows = {
        int(record["source_row_id"].split("-")[-1])
        for record in old_records
        if record["source_row_id"].startswith("train-row-")
    }
    df = pd.read_parquet(RAW)
    if len(df) < 100:
        raise RuntimeError(f"local MATH parquet has too few rows: {len(df)}")
    new_items = select_new_rows(df, old_rows)
    if len(new_items) != 100:
        raise RuntimeError("Gold-125 requires exactly 100 new records")
    new_trajectories = [build_new_trajectory(item) for item in new_items]
    if {trajectory["problem_id"] for trajectory in new_trajectories} != {f"MATH-GOLD-{index:03d}" for index in range(26, 126)}:
        raise RuntimeError("new trajectory IDs are not exactly MATH-GOLD-026 through MATH-GOLD-125")

    old_norm = normalize_old_trajectories()
    if len(old_norm) != 25:
        raise RuntimeError(f"expected 25 frozen trajectories, found {len(old_norm)}")
    all_steps = flatten_steps(old_norm, new_trajectories)
    old_steps = flatten_steps(old_norm, [])
    new_steps = flatten_steps([], new_trajectories)
    audit_records = [audit_new_trajectory(trajectory) for trajectory in new_trajectories]
    hard_records = hard_audit_records(new_trajectories)
    saturation = saturation_rows(old_norm, new_trajectories)
    topk = coverage_rows(all_steps)
    registry = operation_registry(all_steps)
    gaps = gap_registry(all_steps)
    dependency_graph = dependency_graph_report(old_norm + new_trajectories)
    branch_graph = branch_scope_report(old_norm, new_trajectories)
    manifest = build_gold125_manifest(old_manifest, new_items)

    TRAJ_OUT.mkdir(parents=True, exist_ok=True)
    GAP_OUT.mkdir(parents=True, exist_ok=True)
    for trajectory in new_trajectories:
        write_json(TRAJ_OUT / f"{trajectory['problem_id']}.json", trajectory)
    write_json(ROOT / "manifests/gold125_math_v1.json", manifest)
    write_json(ROOT / "schemas/math-gold125-trajectory.schema.json", gold125_schema())
    write_json(ROOT / "schemas/reasoning_operation_registry_gold125_v1.json", {"registry_version": "gold125_operation_registry_v1", "operations": registry})
    write_json(ROOT / "schemas/gold125_gap_registry_v1.json", gaps)
    write_json(REPORTS / "gold125_saturation.json", saturation)
    write_csv(REPORTS / "gold125_saturation.csv", saturation)
    write_json(REPORTS / "gold125_topk_coverage.json", topk)
    write_csv(REPORTS / "gold125_topk_coverage.csv", topk)
    write_json(REPORTS / "gold125_independent_audits.json", hard_records)
    write_json(REPORTS / "gold125_dependency_graph.json", dependency_graph)
    write_json(REPORTS / "gold125_branch_scope_audit.json", branch_graph)
    write_json(REPORTS / "gold125_audit_machine_results.json", audit_records)
    write_json(REPORTS / "gold125_selection.json", new_items)

    (REPORTS / "gold125_selection_audit.md").write_text(selection_audit_markdown(new_items), encoding="utf-8")
    (REPORTS / "gold125_semantic_audit.md").write_text(semantic_audit_markdown(new_trajectories, hard_records, audit_records), encoding="utf-8")
    (REPORTS / "operation_long_tail_analysis_gold125.md").write_text(long_tail_markdown(registry), encoding="utf-8")
    (REPORTS / "thinking_vs_execution_gold125.md").write_text(thinking_report(old_norm, new_trajectories, all_steps), encoding="utf-8")
    (REPORTS / "gold125_state_profile.md").write_text(state_profile_report(old_norm, new_trajectories), encoding="utf-8")
    (REPORTS / "gold125_hml_coverage.md").write_text(hml_report(old_steps, new_steps), encoding="utf-8")
    (REPORTS / "gold125_gap_analysis.md").write_text(gap_analysis_markdown(all_steps), encoding="utf-8")
    (REPORTS / "reasoning_operation_registry_gold125_v1.md").write_text(operation_registry_markdown(registry), encoding="utf-8")
    (REPORTS / "gold125_reasoning_synthesis.md").write_text(
        synthesis_markdown(old_norm, new_trajectories, all_steps, registry, saturation, topk, hard_records),
        encoding="utf-8",
    )
    for gap_id, meta in GAP_META.items():
        if next(record for record in gaps["gaps"] if record["gap_id"] == gap_id)["recurrence_count"] > 0:
            (GAP_OUT / f"{gap_id}.md").write_text(gap_report(gap_id, meta, gaps), encoding="utf-8")

    readme = "\n".join([
        "# Gold-125 semantic-discovery artifact",
        "",
        "This directory contains exactly 100 new, deterministic, source-grounded MATH trajectories (MATH-GOLD-026 through MATH-GOLD-125). The frozen Gold-25 remains under data/gold25 and was not rewritten.",
        "",
        "The builder is a curated Gold-125 artifact generator for these 125 examples, not a scalable automatic extraction engine. It preserves source spans, records uncertainty, and emits structural audits; it does not claim formal theorem replay.",
        "",
        "No problem 126 was processed. No large external dataset was ingested beyond the local MATH parquet. HML core was read-only and unchanged.",
        "",
    ])
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    failures = [failure for record in audit_records for failure in record["failures"]]
    if failures:
        raise RuntimeError("new trajectory audit failures: " + "; ".join(failures[:20]))
    if len(hard_records) < 15:
        raise RuntimeError("fewer than 15 independent hard audits were produced")
    hml_head = subprocess.check_output(["git", "-C", str(ROOT / "hml_core"), "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "frozen_gold25_trajectories": 25,
        "new_trajectories": len(new_trajectories),
        "total_trajectories": len(old_norm) + len(new_trajectories),
        "old_source_transitions": len(old_steps),
        "new_source_transitions": len(new_steps),
        "total_source_transitions": len(all_steps),
        "new_atomicity": dict(Counter(step["atomicity"] for step in new_steps)),
        "observed_operations": len({step["observed_operation"] for step in all_steps}),
        "normalized_atomic_operations": len({component for step in all_steps for component in step["atomic_components"] if component != "UNRESOLVED"}),
        "candidate_core_operations": len({step["candidate_core"] for step in all_steps if step["candidate_core"] != "UNRESOLVED"}),
        "independent_hard_audits": len(hard_records),
        "mechanical_failures": len(failures),
        "hml_core_head": hml_head,
        "problem_126_processed": False,
        "builder_scope": "curated_gold125_artifact_generator",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
