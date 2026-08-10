#!/usr/bin/env python3
"""Build and freeze the Semantic Firewall DEV/FINAL benchmark.

Selection is deterministic and source-grounded, but the transition records are
curated invariant probes rather than an automatic reconstruction of full MATH
solutions.  Run with a Python environment providing pandas and pyarrow, for example:

    uv run --no-project --with pandas --with pyarrow python \
        experiments/semantic_firewall/build_benchmark.py

The raw parquet is read only.  Gold-125 records may seed DEV; FINAL excludes every
Gold-125 source row and source hash.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/semantic_firewall"
RAW = ROOT / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet"
GOLD125 = ROOT / "manifests/gold125_math_v1.json"
DATA = HERE / "data"
FIXTURES = HERE / "acceptance/fixtures.json"
RENDERINGS = HERE / "renderings"
PROMPTS = HERE / "prompts"
FREEZE = HERE / "freeze_manifest.json"
FREEZE_SHA = HERE / "freeze_manifest.sha256"

SCHEMA_VERSION = "semantic-firewall-case-0.1.0"
HML_SHA = "5688aba18632b65a8709aa1d85577d31a67dba6a"
SOURCE_NAME = "Hendrycks MATH train parquet"
ERROR_CLASSES = (
    "DEPENDENCY_VIOLATION",
    "SCOPE_LEAK",
    "PRECONDITION_VIOLATION",
    "OBLIGATION_DROP",
    "CANDIDATE_PROMOTION",
    "INVALID_BRANCH_JOIN",
    "WARRANT_MISMATCH",
    "EPISTEMIC_PROMOTION",
    "FALSE_GOAL_DISCHARGE",
    "TYPE_OR_DOMAIN_MISMATCH",
)
INVARIANT_FOR = {
    "DEPENDENCY_VIOLATION": "DEPENDENCY",
    "SCOPE_LEAK": "SCOPE",
    "PRECONDITION_VIOLATION": "PRECONDITIONS",
    "OBLIGATION_DROP": "OBLIGATIONS",
    "CANDIDATE_PROMOTION": "CANDIDATES",
    "INVALID_BRANCH_JOIN": "BRANCH_JOIN",
    "WARRANT_MISMATCH": "WARRANT",
    "EPISTEMIC_PROMOTION": "EPISTEMIC_STATUS",
    "FALSE_GOAL_DISCHARGE": "GOAL_DISCHARGE",
    "TYPE_OR_DOMAIN_MISMATCH": "TYPE_DOMAIN",
}
CODE = {
    "DEPENDENCY_VIOLATION": "DEP",
    "SCOPE_LEAK": "SCP",
    "PRECONDITION_VIOLATION": "PRE",
    "OBLIGATION_DROP": "OBL",
    "CANDIDATE_PROMOTION": "CAN",
    "INVALID_BRANCH_JOIN": "BRN",
    "WARRANT_MISMATCH": "WAR",
    "EPISTEMIC_PROMOTION": "EPI",
    "FALSE_GOAL_DISCHARGE": "GOL",
    "TYPE_OR_DOMAIN_MISMATCH": "TYP",
}

PATTERNS = {
    "DEPENDENCY_VIOLATION": r"\b(?:since|therefore|thus|hence|using|substitut)",
    "SCOPE_LEAK": r"\b(?:first case|second case|case\s+[12ab]|in this case|if\b.{0,80}\bthen)",
    "PRECONDITION_VIOLATION": r"\b(?:divide|dividing|denominator|cancel|cross[- ]?multiply|logarithm|square root|radical|inequality)",
    "OBLIGATION_DROP": r"\b(?:must check|we check|checking|plug.{0,60}back|verify|extraneous|must satisfy)",
    "CANDIDATE_PROMOTION": r"\b(?:candidate|solutions?|roots?|possible values?|valid solution)",
    "INVALID_BRANCH_JOIN": r"\b(?:two cases|cases to consider|first case|second case|case\s+[12ab])",
    "WARRANT_MISMATCH": r"\b(?:theorem|formula|identity|am-gm|pigeonhole|complementary principle|pascal)",
    "EPISTEMIC_PROMOTION": r"\b(?:verify|check|true|valid solution|accept|satisf(?:y|ies))",
    "FALSE_GOAL_DISCHARGE": r"\\boxed\{",
    "TYPE_OR_DOMAIN_MISMATCH": r"\b(?:positive integers?|real numbers?|probability|integers?|divisible|domain|natural numbers?)",
}

# The final set intentionally favours Intermediate Algebra and Number Theory, with
# Counting & Probability concentrated where branch/case structure is most useful.
FINAL_CATEGORY_QUOTAS = {
    "DEPENDENCY_VIOLATION": {"Intermediate Algebra": 3, "Number Theory": 3, "Counting & Probability": 2},
    "SCOPE_LEAK": {"Intermediate Algebra": 2, "Number Theory": 2, "Counting & Probability": 4},
    "PRECONDITION_VIOLATION": {"Intermediate Algebra": 4, "Number Theory": 3, "Counting & Probability": 1},
    "OBLIGATION_DROP": {"Intermediate Algebra": 5, "Number Theory": 2, "Counting & Probability": 1},
    "CANDIDATE_PROMOTION": {"Intermediate Algebra": 5, "Number Theory": 2, "Counting & Probability": 1},
    "INVALID_BRANCH_JOIN": {"Intermediate Algebra": 2, "Number Theory": 2, "Counting & Probability": 4},
    "WARRANT_MISMATCH": {"Intermediate Algebra": 3, "Number Theory": 3, "Counting & Probability": 2},
    "EPISTEMIC_PROMOTION": {"Intermediate Algebra": 4, "Number Theory": 3, "Counting & Probability": 1},
    "FALSE_GOAL_DISCHARGE": {"Intermediate Algebra": 3, "Number Theory": 3, "Counting & Probability": 2},
    "TYPE_OR_DOMAIN_MISMATCH": {"Intermediate Algebra": 3, "Number Theory": 3, "Counting & Probability": 2},
}

CURRENT_HML_SUPPORT = {
    "DEPENDENCY": "CURRENT_HML_PASS",
    "SCOPE": "CURRENT_HML_PARTIAL",
    "PRECONDITIONS": "CURRENT_HML_PARTIAL",
    "OBLIGATIONS": "CURRENT_HML_PARTIAL",
    "CANDIDATES": "CURRENT_HML_NOT_EXPRESSIBLE",
    "BRANCH_JOIN": "CURRENT_HML_NOT_EXPRESSIBLE",
    "WARRANT": "CURRENT_HML_PARTIAL",
    "EPISTEMIC_STATUS": "CURRENT_HML_PARTIAL",
    "GOAL_DISCHARGE": "CURRENT_HML_PASS",
    "TYPE_DOMAIN": "CURRENT_HML_PARTIAL",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any, *, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        path.write_bytes(canonical_bytes(value))
    else:
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def source_hash(problem: str, solution: str) -> str:
    return sha256_bytes((problem + "\n" + solution).encode("utf-8"))


def split_source(solution: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+|\n{2,}|(?<=\\)\\\s*", solution)
    return [part.strip() for part in raw if part.strip()] or [solution.strip()]


def matching_span(solution: str, error_class: str) -> str | None:
    matches = [span for span in split_source(solution) if re.search(PATTERNS[error_class], span, re.I | re.S)]
    if not matches:
        return None
    return matches[-1] if error_class == "FALSE_GOAL_DISCHARGE" else matches[0]


def clean_nonvisual(problem: str, solution: str) -> bool:
    text = problem + "\n" + solution
    return not re.search(r"\b(?:diagram|figure|pictured|shown below|asy\b|drawn below)", text, re.I)


def select_dev(gold_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    preferred = {"Intermediate Algebra": 0, "Number Theory": 1, "Counting & Probability": 2}
    ordered = sorted(
        gold_records,
        key=lambda record: (
            0 if record.get("level") in {"Level 4", "Level 5"} else 1,
            preferred.get(record.get("category"), 3),
            record["source_row_id"],
        ),
    )
    for error_class in ERROR_CLASSES:
        matches = []
        for record in ordered:
            if record["source_row_id"] in used or not clean_nonvisual(record["problem"], record["original_solution"]):
                continue
            span = matching_span(record["original_solution"], error_class)
            if span:
                matches.append((record, span))
            if len(matches) == 2:
                break
        if len(matches) != 2:
            raise RuntimeError(f"could not select two DEV sources for {error_class}")
        for record, span in matches:
            used.add(record["source_row_id"])
            selected.append(
                {
                    "error_class": error_class,
                    "source_row_id": record["source_row_id"],
                    "source_hash": record["source_hash"],
                    "category": record["category"],
                    "level": record["level"],
                    "problem": record["problem"],
                    "solution": record["original_solution"],
                    "solution_span": span,
                    "gold125_overlap": True,
                }
            )
    return selected


def select_final(rows: Iterable[tuple[int, dict[str, Any]]], excluded_rows: set[int], excluded_hashes: set[str]) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for index, row in rows:
        problem = str(row["problem"])
        solution = str(row["solution"])
        digest = source_hash(problem, solution)
        if index in excluded_rows or digest in excluded_hashes:
            continue
        if row["level"] not in {"Level 4", "Level 5"} or row["type"] not in {
            "Intermediate Algebra", "Number Theory", "Counting & Probability"
        }:
            continue
        if not clean_nonvisual(problem, solution):
            continue
        pool.append(
            {
                "source_row_id": f"train-row-{index:05d}",
                "source_hash": digest,
                "category": str(row["type"]),
                "level": str(row["level"]),
                "problem": problem,
                "solution": solution,
                "gold125_overlap": False,
            }
        )

    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    for error_class in ERROR_CLASSES:
        for category, count in FINAL_CATEGORY_QUOTAS[error_class].items():
            candidates = []
            for record in pool:
                if record["source_row_id"] in used or record["category"] != category:
                    continue
                span = matching_span(record["solution"], error_class)
                if span:
                    candidates.append((record, span))
                if len(candidates) == count:
                    break
            if len(candidates) != count:
                raise RuntimeError(f"could not select {count} FINAL {category} sources for {error_class}")
            for record, span in candidates:
                item = dict(record)
                item["error_class"] = error_class
                item["solution_span"] = span
                selected.append(item)
                used.add(item["source_row_id"])
    if len(selected) != 80 or len(used) != 80:
        raise RuntimeError(f"FINAL selection must contain 80 unique source rows, found {len(selected)}")
    return selected


def claim(
    claim_id: str,
    proposition: str,
    *,
    status: str,
    scope: str = "global",
    dependencies: list[str] | None = None,
    domain: str = "Proposition",
) -> dict[str, Any]:
    return {
        "id": claim_id,
        "proposition": proposition,
        "status": status,
        "scope": scope,
        "dependencies": dependencies or [],
        "domain": domain,
    }


def source_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset": SOURCE_NAME,
        "source_row_id": item["source_row_id"],
        "source_hash": item["source_hash"],
        "category": item["category"],
        "level": item["level"],
        "problem": item["problem"],
        "solution_span": item["solution_span"],
        "solution_span_hash": sha256_bytes(item["solution_span"].encode("utf-8")),
        "gold125_overlap": item["gold125_overlap"],
        "source_role": "MATH context and exact worked-solution assertion anchoring an invariant-level transition probe",
    }


def valid_case(item: dict[str, Any], pair_id: str, case_id: str, split: str) -> dict[str, Any]:
    error_class = item["error_class"]
    invariant = INVARIANT_FOR[error_class]
    p0_scope = "branch:b1" if invariant == "SCOPE" else "global"
    p0_domain = "Integer" if invariant == "TYPE_DOMAIN" else "Proposition"
    before = {
        "active_scopes": ["global", "branch:b1"] if invariant == "SCOPE" else ["global"],
        "claims": {
            "p0": claim("p0", item["problem"], status="GIVEN", scope=p0_scope, domain=p0_domain),
        },
        "obligations": {},
        "candidates": {},
        "branches": {},
        "goals": {},
    }
    dependencies = ["p0"]
    if invariant == "DEPENDENCY":
        before["claims"]["p1"] = claim(
            "p1",
            "A prior source-supported intermediate fact needed by this transition.",
            status="DERIVED",
            dependencies=["p0"],
        )
        dependencies.append("p1")

    evidence: dict[str, Any] = {
        "e_source": {
            "id": "e_source",
            "kind": "SOURCE_REVIEW",
            "status": "VALID",
            "trusted": True,
            "supports_rule": "SOURCE_REVIEWED_DERIVATION",
            "premise_ids": dependencies,
            "source_span_hash": sha256_bytes(item["solution_span"].encode("utf-8")),
        }
    }
    action = {
        "id": "a0",
        "operation": "DERIVE",
        "summary": item["solution_span"],
        "dependencies": dependencies,
        "output_id": "c1",
        "warrant": {
            "kind": "EVIDENCE_ADAPTER",
            "rule": "SOURCE_REVIEWED_DERIVATION",
            "evidence_id": "e_source",
        },
        "preconditions": [],
        "obligations_created": [],
        "obligations_discharged": [],
        "scope_effect": {"kind": "NONE", "discharge_evidence_id": None},
        "candidate_effect": {"kind": "NONE", "candidate_id": None, "evidence_id": None},
        "branch_effect": {"kind": "NONE", "branch_ids": [], "coverage_evidence_id": None},
        "epistemic_effect": {"to_status": "DERIVED", "evidence_id": None},
        "goal_effect": {"kind": "NONE", "goal_id": None},
        "typing": {"input_domains": {dependency: before["claims"][dependency]["domain"] for dependency in dependencies}, "output_domain": "Proposition"},
    }
    output_status = "DERIVED"

    if invariant == "PRECONDITIONS":
        evidence["e_pre"] = {
            "id": "e_pre",
            "kind": "PRECONDITION_CHECK",
            "status": "VALID",
            "trusted": True,
            "supports_rule": "DOMAIN_CHECK",
            "premise_ids": ["p0"],
        }
        action["preconditions"] = [{
            "id": "pre0",
            "proposition": "The source operation's denominator/domain/sign condition holds.",
            "required": True,
            "status": "SATISFIED",
            "evidence_id": "e_pre",
            "deferable": False,
            "obligation_id": None,
        }]
    elif invariant == "OBLIGATIONS":
        action["obligations_created"] = [{
            "id": "o1",
            "proposition": "Check the source operation against its original constraints.",
            "mandatory": True,
            "dependencies": ["c1"],
        }]
    elif invariant == "CANDIDATES":
        before["candidates"]["cand1"] = {
            "id": "cand1",
            "proposition": item["solution_span"],
            "status": "PROPOSED",
            "constraint_ids": ["p0"],
            "scope": "global",
        }
        evidence["e_candidate"] = {
            "id": "e_candidate",
            "kind": "CANDIDATE_CHECK",
            "status": "VALID",
            "trusted": True,
            "candidate_id": "cand1",
            "checked_constraints": ["p0"],
            "supports_rule": "VERIFY_CANDIDATE",
            "premise_ids": dependencies,
        }
        action["operation"] = "VERIFY_CANDIDATE"
        action["candidate_effect"] = {"kind": "PROMOTE", "candidate_id": "cand1", "evidence_id": "e_candidate"}
    elif invariant == "BRANCH_JOIN":
        before["branches"] = {
            "b1": {"id": "b1", "status": "CLOSED", "predicate": "case one", "conclusion": item["solution_span"]},
            "b2": {"id": "b2", "status": "CLOSED", "predicate": "case two", "conclusion": item["solution_span"]},
        }
        evidence["e_coverage"] = {
            "id": "e_coverage",
            "kind": "EXHAUSTIVE_PARTITION",
            "status": "VALID",
            "trusted": True,
            "branch_ids": ["b1", "b2"],
            "supports_rule": "JOIN_BRANCHES",
            "premise_ids": dependencies,
        }
        action["operation"] = "JOIN_BRANCHES"
        action["branch_effect"] = {"kind": "JOIN", "branch_ids": ["b1", "b2"], "coverage_evidence_id": "e_coverage"}
    elif invariant == "EPISTEMIC_STATUS":
        output_status = "VERIFIED"
        evidence["e_verify"] = {
            "id": "e_verify",
            "kind": "TRANSITION_CHECK",
            "status": "VALID",
            "trusted": True,
            "supports_rule": "VERIFY_TRANSITION",
            "premise_ids": dependencies,
        }
        action["epistemic_effect"] = {"to_status": "VERIFIED", "evidence_id": "e_verify"}
    elif invariant == "GOAL_DISCHARGE":
        output_status = "VERIFIED"
        before["goals"]["g1"] = {"id": "g1", "proposition": item["solution_span"], "status": "OPEN", "scope": "global"}
        evidence["e_verify"] = {
            "id": "e_verify",
            "kind": "TRANSITION_CHECK",
            "status": "VALID",
            "trusted": True,
            "supports_rule": "VERIFY_TRANSITION",
            "premise_ids": dependencies,
        }
        action["epistemic_effect"] = {"to_status": "VERIFIED", "evidence_id": "e_verify"}
        action["goal_effect"] = {"kind": "DISCHARGE", "goal_id": "g1"}

    after = copy.deepcopy(before)
    after["claims"]["c1"] = claim(
        "c1",
        item["solution_span"],
        status=output_status,
        scope=p0_scope if invariant == "SCOPE" else "global",
        dependencies=dependencies,
        domain="Proposition",
    )
    if invariant == "OBLIGATIONS":
        after["obligations"]["o1"] = {
            "id": "o1",
            "proposition": action["obligations_created"][0]["proposition"],
            "status": "OPEN",
            "mandatory": True,
            "dependencies": ["c1"],
        }
    elif invariant == "CANDIDATES":
        after["candidates"]["cand1"]["status"] = "VERIFIED"
    elif invariant == "GOAL_DISCHARGE":
        after["goals"]["g1"]["status"] = "DISCHARGED"

    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "pair_id": pair_id,
        "split": split,
        "semantic_focus": invariant,
        "source": source_record(item),
        "state_before": before,
        "action": action,
        "state_after": after,
        "evidence": evidence,
    }


def corrupt(case: dict[str, Any], error_class: str) -> tuple[dict[str, Any], list[str], str]:
    bad = copy.deepcopy(case)
    if error_class == "DEPENDENCY_VIOLATION":
        bad["action"]["dependencies"].append("future_claim")
        bad["state_after"]["claims"]["c1"]["dependencies"].append("future_claim")
        paths = ["action.dependencies", "state_after.claims.c1.dependencies", "evidence.e_source.premise_ids"]
        description = "replace complete ancestry with an unavailable future dependency"
    elif error_class == "SCOPE_LEAK":
        bad["state_after"]["claims"]["c1"]["scope"] = "global"
        paths = ["state_after.claims.c1.scope"]
        description = "promote a branch-local conclusion to global scope without discharge"
    elif error_class == "PRECONDITION_VIOLATION":
        bad["action"]["preconditions"][0]["status"] = "FAILED"
        paths = ["action.preconditions[0].status"]
        description = "execute despite a failed mandatory applicability condition"
    elif error_class == "OBLIGATION_DROP":
        del bad["state_after"]["obligations"]["o1"]
        paths = ["state_after.obligations.o1"]
        description = "silently delete newly created proof debt"
    elif error_class == "CANDIDATE_PROMOTION":
        bad["action"]["candidate_effect"]["evidence_id"] = "missing_candidate_check"
        paths = ["action.candidate_effect.evidence_id"]
        description = "promote a candidate without independent original-constraint evidence"
    elif error_class == "INVALID_BRANCH_JOIN":
        bad["action"]["branch_effect"]["coverage_evidence_id"] = "missing_coverage"
        paths = ["action.branch_effect.coverage_evidence_id"]
        description = "join closed branches without an exhaustive partition certificate"
    elif error_class == "WARRANT_MISMATCH":
        bad["action"]["warrant"]["rule"] = "UNRELATED_RULE"
        paths = ["action.warrant.rule"]
        description = "name a rule not supported by the attached evidence envelope"
    elif error_class == "EPISTEMIC_PROMOTION":
        bad["evidence"]["e_verify"]["status"] = "PROPOSED"
        paths = ["evidence.e_verify.status"]
        description = "assert VERIFIED while the checking evidence is only proposed"
    elif error_class == "FALSE_GOAL_DISCHARGE":
        bad["state_after"]["claims"]["c1"]["proposition"] = "A different conclusion than the active goal."
        paths = ["state_after.claims.c1.proposition"]
        description = "close a goal with a verified claim about a different proposition"
    elif error_class == "TYPE_OR_DOMAIN_MISMATCH":
        bad["state_before"]["claims"]["p0"]["domain"] = "Boolean"
        bad["state_after"]["claims"]["p0"]["domain"] = "Boolean"
        paths = ["state_before.claims.p0.domain", "state_after.claims.p0.domain"]
        description = "supply a Boolean where the operation contract requires an Integer"
    else:
        raise ValueError(error_class)
    return bad, paths, description


def assign_twins(item: dict[str, Any], pair_id: str, split: str, ordinal: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    suffixes = ("A", "B")
    valid_suffix = suffixes[int(sha256_bytes(pair_id.encode("utf-8")), 16) % 2]
    invalid_suffix = "B" if valid_suffix == "A" else "A"
    valid_id = f"{pair_id}-{valid_suffix}"
    invalid_id = f"{pair_id}-{invalid_suffix}"
    valid = valid_case(item, pair_id, valid_id, split)
    invalid, paths, description = corrupt(valid_case(item, pair_id, invalid_id, split), item["error_class"])
    cases = sorted([valid, invalid], key=lambda case: case["case_id"])
    labels = {
        valid_id: {"expected": "VALID", "error_class": None, "pair_id": pair_id, "corruption": None},
        invalid_id: {
            "expected": "INVALID",
            "error_class": item["error_class"],
            "pair_id": pair_id,
            "corruption": {"target_paths": paths, "description": description, "ordinal": ordinal},
        },
    }
    return cases, labels


def unknown_fixture(valid: dict[str, Any], invariant: str) -> dict[str, Any]:
    fixture = copy.deepcopy(valid)
    if invariant == "DEPENDENCY":
        fixture["state_before"]["claims"]["p0"]["status"] = "UNKNOWN"
        fixture["state_after"]["claims"]["p0"]["status"] = "UNKNOWN"
    elif invariant == "SCOPE":
        fixture["state_after"]["claims"]["c1"]["scope"] = "UNKNOWN"
    elif invariant == "PRECONDITIONS":
        fixture["action"]["preconditions"][0]["status"] = "UNKNOWN"
    elif invariant == "OBLIGATIONS":
        fixture["state_before"]["obligations"]["o_prev"] = {"id": "o_prev", "proposition": "prior debt", "status": "OPEN", "mandatory": True, "dependencies": ["p0"]}
        fixture["action"]["obligations_discharged"] = [{"id": "o_prev", "evidence_id": "e_unknown"}]
        fixture["evidence"]["e_unknown"] = {"id": "e_unknown", "kind": "OBLIGATION_CHECK", "status": "UNKNOWN", "trusted": False, "supports_rule": "DISCHARGE", "premise_ids": ["p0"]}
    elif invariant == "CANDIDATES":
        fixture["evidence"]["e_candidate"]["status"] = "UNKNOWN"
    elif invariant == "BRANCH_JOIN":
        fixture["evidence"]["e_coverage"]["status"] = "UNKNOWN"
    elif invariant == "WARRANT":
        fixture["evidence"]["e_source"]["status"] = "UNKNOWN"
    elif invariant == "EPISTEMIC_STATUS":
        fixture["evidence"]["e_verify"]["status"] = "UNKNOWN"
    elif invariant == "GOAL_DISCHARGE":
        fixture["state_after"]["claims"]["c1"]["status"] = "UNKNOWN"
    elif invariant == "TYPE_DOMAIN":
        fixture["state_before"]["claims"]["p0"]["domain"] = "UNKNOWN"
        fixture["state_after"]["claims"]["p0"]["domain"] = "UNKNOWN"
    return fixture


def build_acceptance(seed_items: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    fixtures = []
    for error_class in ERROR_CLASSES:
        invariant = INVARIANT_FOR[error_class]
        item = seed_items[error_class]
        pair_id = f"FX-{CODE[error_class]}"
        legal = valid_case(item, pair_id, f"{pair_id}-LEGAL", "ACCEPTANCE")
        illegal, paths, description = corrupt(
            valid_case(item, pair_id, f"{pair_id}-ILLEGAL", "ACCEPTANCE"), error_class
        )
        unknown = unknown_fixture(
            valid_case(item, pair_id, f"{pair_id}-UNKNOWN", "ACCEPTANCE"), invariant
        )
        for fixture, expected, boundary in (
            (legal, "VALID", "LEGAL"),
            (illegal, "INVALID", "ILLEGAL"),
            (unknown, "UNRESOLVED", "BOUNDARY_UNKNOWN"),
        ):
            fixtures.append(
                {
                    "fixture_id": fixture["case_id"],
                    "invariant": invariant,
                    "boundary": boundary,
                    "expected_reference_result": expected,
                    "expected_error_class": error_class if expected == "INVALID" else None,
                    "current_hml_support": CURRENT_HML_SUPPORT[invariant],
                    "current_hml_note": "Assessment is against pinned HML 5688aba; neutral fixture remains authoritative.",
                    "corruption": {"target_paths": paths, "description": description} if expected == "INVALID" else None,
                    "case": fixture,
                }
            )
    return fixtures


def structured_english(case: dict[str, Any]) -> str:
    before = case["state_before"]
    after = case["state_after"]
    action = case["action"]
    lines = [
        f"Case {case['case_id']} (pair {case['pair_id']}).",
        f"Source row: {case['source']['source_row_id']} ({case['source']['category']}, {case['source']['level']}).",
        f"Source problem: {case['source']['problem']}",
        f"Proposed action: {action['summary']}",
        f"Operation: {action['operation']}.",
        f"Dependencies: {', '.join(action['dependencies']) or 'none'}.",
        f"Warrant: {action['warrant']['rule']} using {action['warrant']['evidence_id']}.",
        "State before: " + json.dumps(before, sort_keys=True, ensure_ascii=False),
        "Preconditions: " + json.dumps(action["preconditions"], sort_keys=True, ensure_ascii=False),
        "Obligation effects: " + json.dumps({"created": action["obligations_created"], "discharged": action["obligations_discharged"]}, sort_keys=True, ensure_ascii=False),
        "Candidate effect: " + json.dumps(action["candidate_effect"], sort_keys=True, ensure_ascii=False),
        "Branch effect: " + json.dumps(action["branch_effect"], sort_keys=True, ensure_ascii=False),
        "Scope effect: " + json.dumps(action["scope_effect"], sort_keys=True, ensure_ascii=False),
        "Epistemic effect: " + json.dumps(action["epistemic_effect"], sort_keys=True, ensure_ascii=False),
        "Goal effect: " + json.dumps(action["goal_effect"], sort_keys=True, ensure_ascii=False),
        "Typing: " + json.dumps(action["typing"], sort_keys=True, ensure_ascii=False),
        "Evidence: " + json.dumps(case["evidence"], sort_keys=True, ensure_ascii=False),
        "State after: " + json.dumps(after, sort_keys=True, ensure_ascii=False),
        "Question: Is this semantic transition VALID, INVALID, or UNRESOLVED?",
    ]
    return "\n".join(lines) + "\n"


def render_case(case: dict[str, Any]) -> dict[str, Any]:
    semantic_sha = sha256_bytes(canonical_bytes(case))
    return {
        "case_id": case["case_id"],
        "semantic_sha256": semantic_sha,
        "structured_english": structured_english(case),
        "generic_typed_ast": {
            "node_type": "SemanticTransition",
            "schema_version": case["schema_version"],
            "fields": case,
        },
        "hml": {
            "format": "CURRENT_HML_PLUS_LOSSLESS_ADAPTER_ENVELOPE_V0",
            "pure_current_hml_equivalent": False,
            "hml_core_sha": HML_SHA,
            "executable_projection": f"module SemanticFirewall_{case['case_id'].replace('-', '_')}\n",
            "unsupported_semantic_fields": ["candidates", "branch_join", "generic_state_delta", "arbitrary_source_proposition"],
            "adapter_envelope": case,
            "warning": "The envelope preserves matched information but is not new HML syntax and must not be scored as pure-HML support.",
        },
    }


def write_cases(split: str, items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    labels: dict[str, Any] = {}
    per_class = Counter()
    for ordinal, item in enumerate(items, start=1):
        per_class[item["error_class"]] += 1
        pair_id = f"SF-{split}-{CODE[item['error_class']]}-{per_class[item['error_class']]:03d}"
        pair_cases, pair_labels = assign_twins(item, pair_id, split, ordinal)
        cases.extend(pair_cases)
        labels.update(pair_labels)
    split_dir = DATA / split.lower()
    for case in cases:
        write_json(split_dir / "cases" / f"{case['case_id']}.json", case)
        write_json(RENDERINGS / split.lower() / f"{case['case_id']}.json", render_case(case))
    write_json(split_dir / "labels.json", labels)
    return cases, labels


def write_prompt_spec() -> None:
    prompt = {
        "prompt_version": "semantic-firewall-classification-0.1.0",
        "system": "Judge only whether the proposed semantic transition preserves the supplied state, evidence, scope, obligations, candidates, branches, epistemic status, goal, and type/domain contracts.",
        "task": "Return exactly VALID, INVALID, or UNRESOLVED, followed by the violated invariant and supporting fields. Do not infer missing evidence as true.",
        "representations": ["STRUCTURED_ENGLISH", "GENERIC_TYPED_AST", "HML"],
        "matching_rule": "Every representation must be generated from the identical neutral case and expose no label or corruption metadata.",
        "hml_caveat": "Current HML requires a transparent adapter envelope for fields it cannot express; pure-HML comparison is blocked until a production adapter exists.",
    }
    write_json(PROMPTS / "classification_prompt.json", prompt)


def main() -> None:
    import pandas as pd

    if not RAW.exists():
        raise FileNotFoundError(RAW)
    gold = json.loads(GOLD125.read_text(encoding="utf-8"))
    gold_records = gold["records"]
    excluded_rows = {int(record["source_row_id"].split("-")[-1]) for record in gold_records}
    excluded_hashes = {record["source_hash"] for record in gold_records}
    table = pd.read_parquet(RAW)
    rows = ((int(index), row.to_dict()) for index, row in table.iterrows())

    dev_items = select_dev(gold_records)
    final_items = select_final(rows, excluded_rows, excluded_hashes)
    dev_cases, dev_labels = write_cases("DEV", dev_items)
    final_cases, final_labels = write_cases("FINAL", final_items)
    seed_items = {error_class: next(item for item in dev_items if item["error_class"] == error_class) for error_class in ERROR_CLASSES}
    fixtures = build_acceptance(seed_items)
    write_json(FIXTURES, {"fixture_version": "semantic-firewall-acceptance-0.1.0", "hml_core_sha": HML_SHA, "fixtures": fixtures})
    write_prompt_spec()

    tracked_files = []
    for base in (DATA, RENDERINGS, PROMPTS):
        tracked_files.extend(sorted(path for path in base.rglob("*") if path.is_file()))
    tracked_files.append(FIXTURES)
    tracked_files.extend(
        [
            HERE / "README.md",
            HERE / "build_benchmark.py",
            HERE / "current_hml_probe.py",
            HERE / "reference_checker.py",
            HERE / "score_benchmark.py",
            HERE / "schemas/semantic_case.schema.json",
            HERE / "results/current_hml_probe.json",
            ROOT / "tests/test_semantic_firewall.py",
        ]
    )
    records = []
    for path in sorted(set(tracked_files)):
        records.append({"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "bytes": path.stat().st_size})

    all_labels = {**dev_labels, **final_labels}
    counts = Counter(label["expected"] for label in all_labels.values())
    manifest = {
        "manifest_version": "semantic-firewall-freeze-0.1.0",
        "frozen_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "corpus_start_commit": "23f06b9ff91dd7ac8632af99c0582591d621b15d",
        "hml_core_sha": HML_SHA,
        "source_file": str(RAW.relative_to(ROOT)),
        "source_file_sha256": sha256_file(RAW),
        "gold125_manifest_sha256": sha256_file(GOLD125),
        "selection_policy": "20 DEV pairs may overlap Gold-125; 80 FINAL pairs are unique MATH Level 4/5 rows excluding every Gold-125 row and hash, with fixed class/category quotas.",
        "benchmark_scope": "Controlled invariant-level semantic corruptions; not open theorem proving and not full source-solution replay.",
        "counts": {
            "dev_cases": len(dev_cases),
            "final_cases": len(final_cases),
            "valid": counts["VALID"],
            "invalid": counts["INVALID"],
            "pairs": len(all_labels) // 2,
            "acceptance_fixtures": len(fixtures),
            "final_gold125_overlap": sum(case["source"]["gold125_overlap"] for case in final_cases),
        },
        "error_classes": list(ERROR_CLASSES),
        "files": records,
    }
    write_json(FREEZE, manifest)
    FREEZE_SHA.write_text(f"{sha256_file(FREEZE)}  {FREEZE.name}\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
