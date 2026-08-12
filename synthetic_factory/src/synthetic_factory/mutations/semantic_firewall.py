"""One-field counterfactuals for the ten frozen verifier invariant families."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Mutation:
    payload: dict[str, Any]
    family: str
    expected_error_class: str
    description: str


EXPECTED = {
    "DEPENDENCY": "DEPENDENCY_VIOLATION",
    "SCOPE": "SCOPE_LEAK",
    "PRECONDITIONS": "PRECONDITION_VIOLATION",
    "OBLIGATIONS": "OBLIGATION_DROP",
    "CANDIDATES": "CANDIDATE_PROMOTION",
    "BRANCH_JOIN": "INVALID_BRANCH_JOIN",
    "WARRANT": "WARRANT_MISMATCH",
    "EPISTEMIC_STATUS": "EPISTEMIC_PROMOTION",
    "GOAL_DISCHARGE": "FALSE_GOAL_DISCHARGE",
    "TYPE_DOMAIN": "TYPE_OR_DOMAIN_MISMATCH",
}


def _first(mapping: dict[str, Any]) -> tuple[str, Any]:
    if not mapping:
        raise ValueError("mutation requires a non-empty mapping")
    return next(iter(mapping.items()))


def mutate_valid_case(source: dict[str, Any]) -> Mutation:
    """Change exactly one semantic leaf while preserving well-formed serialization."""
    payload = copy.deepcopy(source)
    focus = source.get("semantic_focus")
    action = payload["action"]

    if focus == "DEPENDENCY":
        action["dependencies"][0] = "__cf_missing_dependency__"
        description = (
            "The action now cites one unavailable premise; no mathematical conclusion may "
            "acquire ancestry from a fact absent from state_before."
        )
    elif focus == "SCOPE":
        dep = action["dependencies"][0]
        payload["state_before"]["claims"][dep]["scope"] = "branch:cf_inactive"
        description = (
            "A cited premise is moved to an inactive branch scope while the action is held "
            "fixed, so branch-local knowledge is unavailable at the transition."
        )
    elif focus == "PRECONDITIONS":
        action["preconditions"][0]["status"] = "FAILED"
        description = (
            "One required precondition changes from satisfied to failed; parsing and all "
            "other action/state fields remain identical."
        )
    elif focus == "OBLIGATIONS":
        if action.get("obligations_created"):
            action["obligations_created"][0]["id"] = "__cf_missing_obligation__"
            description = (
                "The action declares creation of an obligation that is absent from the "
                "resulting state, so proof debt is silently dropped."
            )
        else:
            oid = action["obligations_discharged"][0]["id"]
            payload["state_after"]["obligations"][oid]["status"] = "OPEN"
            description = (
                "The action claims to discharge one obligation but the resulting state "
                "leaves that exact obligation open."
            )
    elif focus == "CANDIDATES":
        eid = action["candidate_effect"]["evidence_id"]
        checked = payload["evidence"][eid]["checked_constraints"]
        if not checked:
            raise ValueError("candidate promotion has no checked constraint to remove")
        checked.pop()
        description = (
            "Promotion evidence checks a strict subset of the candidate's original "
            "constraints, so it certifies a different candidate claim."
        )
    elif focus == "BRANCH_JOIN":
        eid = action["branch_effect"]["coverage_evidence_id"]
        covered = payload["evidence"][eid]["branch_ids"]
        if not covered:
            raise ValueError("branch certificate has no covered branch to remove")
        covered.pop()
        description = (
            "The partition certificate no longer covers one joined branch; agreement among "
            "the remaining branches does not establish exhaustiveness."
        )
    elif focus == "WARRANT":
        action["warrant"]["evidence_id"] = "__cf_missing_evidence__"
        description = (
            "The mathematical claim and rule are unchanged, but the action now cites an "
            "evidence identity that does not exist in the transition envelope."
        )
    elif focus == "EPISTEMIC_STATUS":
        action["epistemic_effect"]["evidence_id"] = "__cf_missing_evidence__"
        description = (
            "The action still requests the same epistemic promotion but no longer points "
            "to existing evidence that can license that status increase."
        )
    elif focus == "GOAL_DISCHARGE":
        gid = action["goal_effect"]["goal_id"]
        payload["state_after"]["goals"][gid]["status"] = "OPEN"
        description = (
            "The action declares exact-goal discharge while the resulting state leaves the "
            "same goal open; a declared effect must materialise."
        )
    elif focus == "TYPE_DOMAIN":
        cid, required = _first(action["typing"]["input_domains"])
        payload["state_before"]["claims"][cid]["domain"] = (
            "Natural" if required == "Proposition" else "Proposition"
        )
        description = (
            "One cited claim is moved to a domain that does not inhabit the action's "
            "declared input domain; the proposition text and action are unchanged."
        )
    else:
        raise ValueError(f"no approved Stage-100 mutation for semantic focus {focus!r}")

    return Mutation(
        payload=payload,
        family=str(focus),
        expected_error_class=EXPECTED[str(focus)],
        description=description,
    )
