from __future__ import annotations

import copy
import itertools
from collections import defaultdict
from typing import Any

from .canonical import digest, learner_hash
from .constants import CORPUS_SHA, HML_SHA, PROTOCOL, SCHEMA_VERSION, SENTINELS
from .verifier import verify


DOMAINS = ["Number", "Real", "Integer", "Natural", "Rational", "Probability", "NonNegativeReal", "PositiveReal", "Boolean", "Proposition"]
PARENT = {
    "Number": None, "Real": "Number", "Integer": "Real", "Natural": "Integer",
    "Rational": "Real", "Probability": "Real", "NonNegativeReal": "Real",
    "PositiveReal": "NonNegativeReal", "Boolean": None, "Proposition": None,
}


def inhabits(actual: str, required: str) -> bool:
    current: str | None = actual
    seen: set[str] = set()
    while current is not None and current not in seen:
        if current == required:
            return True
        seen.add(current)
        current = PARENT[current]
    return False


def _empty_state() -> dict[str, Any]:
    return {"active_scopes": ["global"], "branches": {}, "candidates": {}, "goals": {}, "obligations": {}, "claims": {}}


def _action(required: str | None = None, summary: str = "q") -> dict[str, Any]:
    typing = {"output_domain": "Proposition"}
    if required is not None:
        typing["input_domains"] = {"p0": required}
    return {
        "id": "a0", "operation": "DERIVE", "summary": summary,
        "dependencies": ["p0"], "preconditions": [], "obligations_created": [],
        "obligations_discharged": [], "typing": typing, "warrant": {},
        "goal_effect": {}, "scope_effect": {}, "branch_effect": {},
        "candidate_effect": {}, "epistemic_effect": {}, "output_id": "c1",
    }


def domain_transition(actual: str, required: str, context: int) -> dict[str, Any]:
    before = _empty_state()
    claim = {"id": "p0", "proposition": f"typed value v{context}", "status": "GIVEN", "scope": "global", "dependencies": [], "domain": actual}
    before["claims"] = {"p0": claim}
    after = copy.deepcopy(before)
    after["claims"]["c1"] = {"id": "c1", "proposition": f"property q{context}", "status": "DERIVED", "scope": "global", "dependencies": ["p0"], "domain": "Proposition"}
    return {"schema_version": "semantic-firewall-case-0.1.0", "case_id": f"V2-DOM-{context}-{actual}-{required}", "pair_id": f"V2-DOM-{context}-{required}", "split": "CHALLENGE", "semantic_focus": "TYPE_DOMAIN", "source": {"origin": "synthetic", "rationale": "domain-lattice applicability derived from frozen HML data"}, "state_before": before, "action": _action(required, f"property q{context}"), "state_after": after, "evidence": {}}


TREE = {"global": None, "branch:a": "global", "branch:b": "branch:a", "branch:c": "branch:a", "branch:d": "branch:b"}


def contains(outer: str, inner: str) -> bool:
    current: str | None = inner
    while current is not None:
        if current == outer:
            return True
        current = TREE[current]
    return False


def scope_transition(premise_scope: str, output_scope: str, context: int) -> dict[str, Any]:
    branches = {
        "a": {"id": "a", "predicate": f"case a{context}", "status": "OPEN"},
        "b": {"id": "b", "predicate": f"case b{context}", "status": "OPEN", "scope": "branch:a"},
        "c": {"id": "c", "predicate": f"case c{context}", "status": "OPEN", "scope": "branch:a"},
        "d": {"id": "d", "predicate": f"case d{context}", "status": "OPEN", "scope": "branch:b"},
    }
    before = _empty_state()
    before["active_scopes"] = list(TREE)
    before["branches"] = branches
    before["claims"] = {"p0": {"id": "p0", "proposition": f"branch fact p{context}", "status": "ASSUMED", "scope": premise_scope, "dependencies": [], "domain": "Proposition"}}
    after = copy.deepcopy(before)
    after["claims"]["c1"] = {"id": "c1", "proposition": f"branch conclusion q{context}", "status": "DERIVED", "scope": output_scope, "dependencies": ["p0"], "domain": "Proposition"}
    return {"schema_version": "semantic-firewall-case-0.1.0", "case_id": f"V2-SCP-{context}-{premise_scope}-{output_scope}", "pair_id": f"V2-SCP-{context}-{output_scope}", "split": "CHALLENGE", "semantic_focus": "SCOPE", "source": {"origin": "synthetic", "rationale": "scope-tree applicability derived from frozen HML contract"}, "state_before": before, "action": _action(summary=f"branch conclusion q{context}"), "state_after": after, "evidence": {}}


def _select_domain() -> list[tuple[str, str, bool, int]]:
    valid = [(a, r, True, context) for context in (0, 1) for a, r in itertools.product(DOMAINS, repeat=2) if inhabits(a, r)]
    invalid_all = [(a, r, False, context) for context in (0, 1) for a, r in itertools.product(DOMAINS, repeat=2) if not inhabits(a, r)]
    invalid = sorted(invalid_all, key=lambda row: digest(row))[:50]
    if len(valid) != 50:
        raise RuntimeError(f"domain lattice changed: expected 50 valid context pairs, got {len(valid)}")
    return valid + invalid


def _select_scope() -> list[tuple[str, str, bool, int]]:
    selected: list[tuple[str, str, bool, int]] = []
    scopes = list(TREE)
    for context in (0, 1):
        selected.extend((p, out, contains(p, out), context) for p, out in itertools.product(scopes, repeat=2))
    positives = [row for row in selected if row[2]][:25]
    negatives = [row for row in selected if not row[2]]
    if len(negatives) < 25:
        for p, out in itertools.product(scopes, repeat=2):
            if not contains(p, out):
                negatives.append((p, out, False, 2))
                if len(negatives) == 25:
                    break
    return positives + negatives[:25]


def _wrap(transition: dict[str, Any], expected: bool, family: str, context: int, anchor: str) -> dict[str, Any]:
    result = verify(transition)
    label = "APPLICABLE" if expected else "NOT_APPLICABLE"
    expected_verdict = "VALID" if expected else "INVALID"
    target = "TYPE_DOMAIN" if family == "DOMAIN_LATTICE" else "SCOPE"
    if result["verdict"] != expected_verdict:
        raise RuntimeError(f"oracle mismatch {transition['case_id']}: {result}")
    if not expected and (len(result["findings"]) != 1 or result["findings"][0]["invariant"] != target):
        raise RuntimeError(f"secondary/wrong finding {transition['case_id']}: {result}")
    rendered = str(transition).lower()
    if any(token in rendered for token in SENTINELS):
        raise RuntimeError("sentinel leaked into Factory B")
    return {
        "schema_version": SCHEMA_VERSION, "protocol": PROTOCOL, "factory": "B",
        "partition": "GOLD_STAGE100_CHALLENGE_BALANCED", "record_id": f"V2-B-{transition['case_id']}",
        "neighborhood_id": anchor, "variant_role": "MEMBER", "prediction_contract": "ACTION_APPLICABILITY",
        "learner_input_hash": learner_hash("ACTION_APPLICABILITY", transition), "label": label,
        "applicability_family": family, "causal_class": "CAUSAL_HARD", "secondary_findings": 0,
        "source_split": "CHALLENGE", "source_theorem_id": None, "ancestor_record_id": anchor,
        "field_provenance": {"state_before": "FROZEN_HML_DERIVATION", "candidate_action": "FROZEN_HML_DERIVATION", "label": "FROZEN_HML_DERIVATION"},
        "source_provenance": {"corpus_sha": CORPUS_SHA, "hml_sha": HML_SHA, "basis": "semantic_state/domains.py" if family == "DOMAIN_LATTICE" else "semantic_state/verify.py scope tree"},
        "minimality": {"semantic_changes_within_neighborhood": 1, "learner_visible_changes": 1, "state_changes": 1, "action_changes": 0, "ast_node_changes": 1},
        "oracle": {"authority": "FROZEN_HML_REPLAY", "result": result, "transition": transition},
        "canonical_source": {"state_before": transition["state_before"], "candidate_action": transition["action"]},
        "renderings": {},
    }


def generate() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    domain_groups: dict[str, list[tuple[str, str, bool, int]]] = defaultdict(list)
    for row in _select_domain():
        domain_groups[f"{row[3]}:{row[1]}"].append(row)
    for actual, required, expected, context in _select_domain():
        positives = [row for row in domain_groups[f"{context}:{required}"] if row[2]]
        anchor_actual = positives[0][0] if positives else required
        anchor = f"DOM-{context}-{required}-{anchor_actual}"
        rows.append(_wrap(domain_transition(actual, required, context), expected, "DOMAIN_LATTICE", context, anchor))
    rows.sort(key=lambda row: row["record_id"])
    if len(rows) != 100 or sum(row["label"] == "APPLICABLE" for row in rows) != 50:
        raise RuntimeError("Factory B Stage100 must be 100 records balanced 50/50")
    return rows
