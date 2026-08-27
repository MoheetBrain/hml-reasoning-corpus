"""Verified synthetic hard negatives by single causal mutation (mission §7).

How a label is produced
-----------------------
Never by an LLM judge, and never by assumption. A mutation is applied to a canonical
:class:`Transition` that already verifies ``VALID``, the **frozen verifier** is re-run on the
result, and whatever it returns is the label. A mutation whose verdict does not change is
discarded rather than relabelled: the point is a *causal* counterfactual, and a mutation that
did not alter admissibility is not one.

Why one mutation at a time
--------------------------
Two simultaneous defects make the item unattributable -- you cannot say which property the
model failed to read. Every child differs from its parent in exactly one recorded respect,
so a per-mutation-family breakdown is a statement about a specific semantic capability.

Why the family name never reaches the model
-------------------------------------------
``mutation_type`` is recorded in the audit record and excluded from every rendered surface.
It is the answer; carrying it in the input would make the task a string-matching exercise
with a near-perfect ceiling. The leakage audit checks the exclusion held rather than trusting
it.

Balance is structural, not incidental
-------------------------------------
Every family is applied to the *same* parent pool, and the parent's operation, domain and
source are unchanged by mutation. So within a family of siblings the operation name carries
no information about the label -- which matters here, because the natural verdict
distribution of this corpus is almost perfectly predicted by the operation name alone, and a
dataset built from it directly would measure that and nothing else.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from hamiltonian_lang.semantic_state.model import (
    Claim,
    ClaimStatus,
    EvidenceRecord,
    Goal,
    GoalStatus,
    SemanticState,
    Transition,
)
from hamiltonian_lang.semantic_state.verify import verify_replay

__all__ = [
    "MUTATIONS",
    "MutationResult",
    "GENERATOR_VERSION",
    "apply_mutation",
    "mutate_all",
]

GENERATOR_VERSION = "max-ev-mutations-1.0.0"


class NotApplicable(Exception):
    """This parent has no site for this mutation. Not an error; the family simply skips it."""


@dataclass(frozen=True)
class MutationResult:
    parent_id: str
    mutation_type: str
    mutation_seed: int
    semantic_diff: dict[str, Any]
    verifier_expected: str
    verifier_actual: str
    error_class: str | None
    transition: Transition
    generator_version: str = GENERATOR_VERSION

    @property
    def as_expected(self) -> bool:
        return self.verifier_actual == self.verifier_expected

    def audit_record(self) -> dict:
        return {
            "parent_id": self.parent_id,
            "mutation_type": self.mutation_type,
            "mutation_seed": self.mutation_seed,
            "semantic_diff": self.semantic_diff,
            "verifier_expected": self.verifier_expected,
            "verifier_actual": self.verifier_actual,
            "error_class": self.error_class,
            "generator_version": self.generator_version,
        }


def _rng(parent_id: str, family: str) -> tuple[random.Random, int]:
    """Deterministic per (parent, family). Reproducing an item never needs a stored blob."""
    seed = int(hashlib.sha256(f"{parent_id}|{family}".encode()).hexdigest()[:12], 16)
    return random.Random(seed), seed


def _cited(t: Transition) -> tuple[str, ...]:
    return t.action.dependencies


def _with_before(t: Transition, **kw) -> SemanticState:
    return replace(t.state_before, **kw)


def _absent_evidence_id(t: Transition) -> str:
    """A plausible evidence id the bundle does not contain. Ordinary-looking on purpose."""
    return next(f"e{i}" for i in range(1, 40) if f"e{i}" not in t.evidence)


# --------------------------------------------------------------------------- families
# Each returns (mutated transition, semantic_diff, expected verdict).


def m_remove_required_premise(t: Transition, rng: random.Random):
    """Delete a claim the action declares it depends on. -> DEPENDENCY_VIOLATION."""
    cited = [c for c in _cited(t) if c in t.state_before.claims]
    if not cited:
        raise NotApplicable("action cites nothing present")
    victim = rng.choice(cited)
    before = {k: v for k, v in t.state_before.claims.items() if k != victim}
    after = {k: v for k, v in t.state_after.claims.items() if k != victim}
    return (
        replace(
            t,
            state_before=_with_before(t, claims=before),
            state_after=replace(t.state_after, claims=after),
        ),
        {"removed_claim": victim, "still_cited_by_action": True},
        "INVALID",
    )


def m_dependency_ancestry_drift(t: Transition, rng: random.Random):
    """Give the produced claim ancestry the action never declared. -> DEPENDENCY_VIOLATION."""
    out = t.action.output_id
    produced = t.state_after.claims.get(out)
    if produced is None:
        raise NotApplicable("no produced claim")
    others = [k for k in t.state_before.claims if k not in produced.dependencies]
    if not others:
        raise NotApplicable("no unused claim to graft")
    extra = rng.choice(others)
    claims = dict(t.state_after.claims)
    claims[out] = replace(produced, dependencies=tuple(produced.dependencies) + (extra,))
    return (
        replace(t, state_after=replace(t.state_after, claims=claims)),
        {"claim": out, "grafted_dependency": extra},
        "INVALID",
    )


def m_branch_local_fact_leaks_global(t: Transition, rng: random.Random):
    """Re-scope a branch-local premise to global while the conclusion stays inside.

    The mirror of the real defect: a fact established under a case assumption is not
    available outside it, and the verifier reads containment off the scope tree.
    """
    if not t.state_before.branches:
        raise NotApplicable("no branch frame")
    inner = [k for k, c in t.state_before.claims.items() if c.scope.startswith("branch:")]
    if not inner:
        raise NotApplicable("no branch-scoped claim")
    out = t.action.output_id
    produced = t.state_after.claims.get(out)
    if produced is None:
        raise NotApplicable("no produced claim")
    claims_after = dict(t.state_after.claims)
    claims_after[out] = replace(produced, scope="global")
    return (
        replace(t, state_after=replace(t.state_after, claims=claims_after)),
        {"claim": out, "scope_before": produced.scope, "scope_after": "global"},
        "INVALID",
    )


def m_alter_binder_identity(t: Transition, rng: random.Random):
    """Rename one binder in the dependency edge only, so the reference dangles.

    Binder identity is the property that makes a dependency graph mean anything: two
    occurrences of a name are the same object or the graph is decoration.
    """
    cited = [c for c in _cited(t) if c in t.state_before.claims]
    if not cited:
        raise NotApplicable("action cites nothing present")
    victim = rng.choice(cited)
    # An ordinary unused name, not a decorated one: the defect is that the reference
    # dangles, and a distinctive glyph would let a probe spot it without following the edge.
    taken = set(t.state_before.claims) | set(t.state_after.claims)
    renamed = next(f"h{i}" for i in range(1, 90) if f"h{i}" not in taken)
    claims = dict(t.state_before.claims)
    claims[renamed] = replace(claims.pop(victim), id=renamed)
    after = dict(t.state_after.claims)
    if victim in after:
        after[renamed] = replace(after.pop(victim), id=renamed)
    return (
        replace(
            t,
            state_before=_with_before(t, claims=claims),
            state_after=replace(t.state_after, claims=after),
        ),
        {"renamed": victim, "to": renamed, "action_still_cites": victim},
        "INVALID",
    )


def m_false_goal_discharge(t: Transition, rng: random.Random):
    """Declare the goal discharged by a claim that does not state it. -> GOAL_DISCHARGE."""
    if not t.state_before.goals:
        raise NotApplicable("no goal")
    gid = next(iter(t.state_before.goals))
    out = t.action.output_id
    produced = t.state_after.claims.get(out)
    if produced is None:
        raise NotApplicable("no produced claim")
    goal = t.state_before.goals[gid]
    if produced.proposition == goal.proposition:
        # Already a genuine discharge: perturb the produced claim so it no longer states it.
        claims = dict(t.state_after.claims)
        claims[out] = replace(produced, proposition=produced.proposition + " ∧ True")
        return (
            replace(t, state_after=replace(t.state_after, claims=claims)),
            {"goal": gid, "produced_no_longer_states_goal": True},
            "INVALID",
        )
    action = replace(
        t.action,
        goal_effect={"goal_id": gid, "kind": "DISCHARGE", "evidence_id": next(iter(t.evidence), None)},
    )
    goals_after = dict(t.state_after.goals)
    goals_after[gid] = replace(goals_after[gid], status=GoalStatus.DISCHARGED)
    return (
        replace(t, action=action, state_after=replace(t.state_after, goals=goals_after)),
        {"goal": gid, "declared_discharge_without_stating_goal": True},
        "INVALID",
    )


def m_goal_vanishes(t: Transition, rng: random.Random):
    """Delete the goal from the resulting state. A goal is discharged, not deleted."""
    if not t.state_after.goals:
        raise NotApplicable("no goal")
    gid = next(iter(t.state_after.goals))
    goals = {k: v for k, v in t.state_after.goals.items() if k != gid}
    return (
        replace(t, state_after=replace(t.state_after, goals=goals)),
        {"deleted_goal": gid},
        "INVALID",
    )


def m_unlicensed_premise_rewrite(t: Transition, rng: random.Random):
    """Rewrite an existing premise in the resulting state with no declared effect. -> FRAME."""
    keys = [k for k in t.state_before.claims if k in t.state_after.claims]
    if not keys:
        raise NotApplicable("no persisting claim")
    victim = rng.choice(keys)
    claims = dict(t.state_after.claims)
    original = claims[victim]
    claims[victim] = replace(original, status=ClaimStatus.VERIFIED)
    return (
        replace(t, state_after=replace(t.state_after, claims=claims)),
        {"claim": victim, "status_before": str(original.status), "status_after": "VERIFIED"},
        "INVALID",
    )


def m_claim_appears_unproduced(t: Transition, rng: random.Random):
    """A claim materialises in the resulting state that the action does not produce."""
    claims = dict(t.state_after.claims)
    model_on = next(iter(t.state_before.claims.values()), None)
    if model_on is None:
        raise NotApplicable("empty prior state")
    ghost = next(
        (f"h{i}" for i in range(1, 60) if f"h{i}" not in claims and f"h{i}" not in t.state_before.claims),
        None,
    )
    if ghost is None:
        raise NotApplicable("no free identifier")
    # Copied from a real hypothesis in this state, with an ordinary name. The violation is
    # that it materialises unproduced -- it must not also be recognisable by its wording.
    claims[ghost] = Claim(
        id=ghost,
        proposition=model_on.proposition,
        status=ClaimStatus.DERIVED,
        scope=model_on.scope,
        domain=model_on.domain,
    )
    return (
        replace(t, state_after=replace(t.state_after, claims=claims)),
        {"injected_claim": ghost, "status": "DERIVED", "not_the_action_output": True},
        "INVALID",
    )


def m_warrant_evidence_dangles(t: Transition, rng: random.Random):
    """Point the warrant at evidence that is not in the bundle. -> WARRANT_MISMATCH."""
    warrant = dict(t.action.warrant)
    if not warrant.get("evidence_id"):
        raise NotApplicable("action has no cited evidence")
    warrant["evidence_id"] = _absent_evidence_id(t)
    return (
        replace(t, action=replace(t.action, warrant=warrant)),
        {"warrant_points_at": warrant["evidence_id"], "present_evidence": sorted(t.evidence)},
        "INVALID",
    )


def m_evidence_supports_other_rule(t: Transition, rng: random.Random):
    """The cited record exists but attests a different rule. -> WARRANT_MISMATCH."""
    if not t.evidence:
        raise NotApplicable("no evidence")
    eid = next(iter(t.evidence))
    rec = t.evidence[eid]
    # A real operation name from the corpus vocabulary, not an invented marker. An attested
    # rule that simply is not the rule being applied is the realistic failure; a token that
    # appears nowhere else would be a keyword the probe could memorise.
    other = "APPLY_THEOREM" if rec.supports_rule != "APPLY_THEOREM" else "PROCEDURAL_TRANSFORM"
    return (
        replace(t, evidence={**t.evidence, eid: replace(rec, supports_rule=other)}),
        {"evidence": eid, "supports_before": rec.supports_rule, "supports_after": other},
        "INVALID",
    )


def m_epistemic_promotion(t: Transition, rng: random.Random):
    """Declare a promotion to VERIFIED backed by evidence that does not exist.

    ``_check_epistemic`` only engages when the action *declares* an epistemic effect, so a
    silent status bump is a frame violation rather than an epistemic one and is already
    covered by ``UNLICENSED_PREMISE_REWRITE``. The distinctively epistemic failure is
    generation certifying itself: announcing the upgrade and citing nothing that supports it.
    """
    out = t.action.output_id
    produced = t.state_after.claims.get(out)
    if produced is None:
        raise NotApplicable("no produced claim")
    claims = dict(t.state_after.claims)
    claims[out] = replace(produced, status=ClaimStatus.VERIFIED)
    action = replace(
        t.action,
        epistemic_effect={"claim_id": out, "to_status": "VERIFIED",
                          "evidence_id": _absent_evidence_id(t)},
    )
    return (
        replace(t, action=action, state_after=replace(t.state_after, claims=claims)),
        {
            "claim": out,
            "status_before": str(produced.status),
            "status_after": "VERIFIED",
            "cited_evidence": _absent_evidence_id(t),
        },
        "INVALID",
    )


def m_type_domain_mismatch(t: Transition, rng: random.Random):
    """Declare an input domain that contradicts the state's annotation. -> TYPE_DOMAIN."""
    typing = dict(t.action.typing)
    inputs = dict(typing.get("input_domains") or {})
    candidates = [c for c in inputs if c in t.state_before.claims]
    if not candidates:
        raise NotApplicable("action types nothing")
    victim = rng.choice(candidates)
    declared = t.state_before.claims[victim].domain
    wrong = "Universe" if declared != "Universe" else "Proposition"
    inputs[victim] = wrong
    typing["input_domains"] = inputs
    return (
        replace(t, action=replace(t.action, typing=typing)),
        {"claim": victim, "state_domain": declared, "action_declares": wrong},
        "INVALID",
    )


# ---- UNRESOLVED families: the third verdict, reached only through genuine unknowns -----


def m_unknown_premise_status(t: Transition, rng: random.Random):
    """A cited premise's status cannot be read. Not a violation -- an unanswerable question."""
    cited = [c for c in _cited(t) if c in t.state_before.claims]
    if not cited:
        raise NotApplicable("action cites nothing present")
    victim = rng.choice(cited)
    claims = dict(t.state_before.claims)
    claims[victim] = replace(claims[victim], status=ClaimStatus.UNKNOWN)
    after = dict(t.state_after.claims)
    if victim in after:
        after[victim] = replace(after[victim], status=ClaimStatus.UNKNOWN)
    return (
        replace(
            t,
            state_before=_with_before(t, claims=claims),
            state_after=replace(t.state_after, claims=after),
        ),
        {"claim": victim, "status_after": "UNKNOWN"},
        "UNRESOLVED",
    )


def m_unknown_evidence_status(t: Transition, rng: random.Random):
    """The cited evidence record's own status is unreadable."""
    if not t.evidence:
        raise NotApplicable("no evidence")
    eid = next(iter(t.evidence))
    rec = t.evidence[eid]
    if rec.status == "UNKNOWN":
        raise NotApplicable("already unknown")
    return (
        replace(t, evidence={**t.evidence, eid: replace(rec, status="UNKNOWN")}),
        {"evidence": eid, "status_before": rec.status, "status_after": "UNKNOWN"},
        "UNRESOLVED",
    )


def m_unknown_domain(t: Transition, rng: random.Random):
    """A cited premise's declared domain is unreadable."""
    cited = [c for c in _cited(t) if c in t.state_before.claims]
    if not cited:
        raise NotApplicable("action cites nothing present")
    victim = rng.choice(cited)
    claims = dict(t.state_before.claims)
    claims[victim] = replace(claims[victim], domain="UNKNOWN")
    after = dict(t.state_after.claims)
    if victim in after:
        after[victim] = replace(after[victim], domain="UNKNOWN")
    return (
        replace(
            t,
            state_before=_with_before(t, claims=claims),
            state_after=replace(t.state_after, claims=after),
        ),
        {"claim": victim, "domain_after": "UNKNOWN"},
        "UNRESOLVED",
    )


def m_unknown_goal_status(t: Transition, rng: random.Random):
    """The goal the action acts on has an unreadable status."""
    effect_goal = t.action.goal_effect.get("goal_id")
    if not effect_goal or effect_goal not in t.state_before.goals:
        raise NotApplicable("action does not name a goal")
    goals = dict(t.state_before.goals)
    goals[effect_goal] = replace(goals[effect_goal], status=GoalStatus.UNKNOWN)
    return (
        replace(t, state_before=_with_before(t, goals=goals)),
        {"goal": effect_goal, "status_after": "UNKNOWN"},
        "UNRESOLVED",
    )


#: Family name -> implementation. Order fixes the reporting order everywhere downstream.
MUTATIONS: dict[str, Callable[[Transition, random.Random], tuple]] = {
    "REMOVE_REQUIRED_PREMISE": m_remove_required_premise,
    "DEPENDENCY_ANCESTRY_DRIFT": m_dependency_ancestry_drift,
    "BRANCH_LOCAL_FACT_LEAKS_GLOBAL": m_branch_local_fact_leaks_global,
    "ALTER_BINDER_IDENTITY": m_alter_binder_identity,
    "FALSE_GOAL_DISCHARGE": m_false_goal_discharge,
    "GOAL_VANISHES": m_goal_vanishes,
    "UNLICENSED_PREMISE_REWRITE": m_unlicensed_premise_rewrite,
    "CLAIM_APPEARS_UNPRODUCED": m_claim_appears_unproduced,
    "WARRANT_EVIDENCE_DANGLES": m_warrant_evidence_dangles,
    "EVIDENCE_SUPPORTS_OTHER_RULE": m_evidence_supports_other_rule,
    "EPISTEMIC_PROMOTION": m_epistemic_promotion,
    "TYPE_DOMAIN_MISMATCH": m_type_domain_mismatch,
    "UNKNOWN_PREMISE_STATUS": m_unknown_premise_status,
    "UNKNOWN_EVIDENCE_STATUS": m_unknown_evidence_status,
    "UNKNOWN_DOMAIN": m_unknown_domain,
    "UNKNOWN_GOAL_STATUS": m_unknown_goal_status,
}

#: Families whose intended verdict is UNRESOLVED rather than INVALID.
UNRESOLVED_FAMILIES = frozenset(
    {
        "UNKNOWN_PREMISE_STATUS",
        "UNKNOWN_EVIDENCE_STATUS",
        "UNKNOWN_DOMAIN",
        "UNKNOWN_GOAL_STATUS",
    }
)


def apply_mutation(parent: Transition, family: str, parent_id: str) -> MutationResult | None:
    """Apply one family and re-verify. ``None`` when the parent has no site for it."""
    rng, seed = _rng(parent_id, family)
    try:
        mutated, diff, expected = MUTATIONS[family](parent, rng)
    except NotApplicable:
        return None
    result = verify_replay(mutated)
    return MutationResult(
        parent_id=parent_id,
        mutation_type=family,
        mutation_seed=seed,
        semantic_diff=diff,
        verifier_expected=expected,
        verifier_actual=str(result.verdict),
        error_class=result.error_class,
        transition=mutated,
    )


def mutate_all(parent: Transition, parent_id: str) -> list[MutationResult]:
    """Every applicable family, in registry order. Callers filter on ``as_expected``."""
    out = []
    for family in MUTATIONS:
        res = apply_mutation(parent, family, parent_id)
        if res is not None:
            out.append(res)
    return out
