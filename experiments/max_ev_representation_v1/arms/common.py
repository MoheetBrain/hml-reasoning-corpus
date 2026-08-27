"""The model-facing projection and its intermediate representation (mission §4, §5).

Two jobs, both of which exist to make the experiment mean something.

**Scrubbing.** A canonical :class:`Transition` carries provenance -- the Mathlib file, the
theorem name, the tactic hash, the record id. None of it is mathematics, and all of it would
let a model identify the source instead of reading the state. :func:`project` removes it
before any arm renders anything, so source-ID leakage is impossible by construction rather
than by audit.

**One information set, four syntaxes.** The scientific claim under test is that *syntax*
changes how readable a mathematical state is. That claim is only testable if the four arms
carry identical information, so the arms are defined as four surfaces over one intermediate
representation: :func:`to_ir` states exactly what there is to say, and each arm decides only
how to say it. An arm cannot accidentally carry more or less than another, because none of
them is the source of what is carried.

The HML arm is the exception in one respect, deliberately: it renders through the **frozen**
``semantic_state.view`` at ``b011511``, not through this IR. The mission fixes that renderer,
and re-implementing it here would be measuring a copy. Parity is still proved the same way --
its output is parsed back and compared as an IR like every other arm.
"""

from __future__ import annotations

from typing import Any

from hamiltonian_lang.semantic_state.model import (
    Action,
    Branch,
    BranchStatus,
    Candidate,
    CandidateStatus,
    Claim,
    ClaimStatus,
    EvidenceRecord,
    Goal,
    GoalStatus,
    Obligation,
    ObligationState,
    SemanticState,
    Transition,
)

__all__ = ["project", "to_ir", "from_ir", "ir_equal", "SEMANTIC_PAYLOAD_KEYS"]

#: Evidence-payload keys that carry semantics rather than provenance. Everything else is
#: dropped before rendering: ``tactic_sha256`` and ``mathlib_revision`` identify the source
#: row, which is precisely what the model must not be given.
SEMANTIC_PAYLOAD_KEYS = frozenset(
    {"checked_constraints", "branch_ids", "premises_used", "constraint_ids", "cases"}
)


def project(t: Transition) -> Transition:
    """Strip provenance, keep mathematics. The result is what every arm renders."""
    evidence = {
        k: EvidenceRecord(
            id=v.id,
            kind=v.kind,
            status=v.status,
            trusted=v.trusted,
            supports_rule=v.supports_rule,
            premise_ids=v.premise_ids,
            payload={
                pk: pv for pk, pv in sorted(v.payload.items()) if pk in SEMANTIC_PAYLOAD_KEYS
            },
        )
        for k, v in sorted(t.evidence.items())
    }
    return Transition(
        case_id="",
        action=t.action,
        state_before=t.state_before,
        state_after=t.state_after,
        evidence=evidence,
        schema_version="",
        source={},
    )


# --------------------------------------------------------------------------- IR

def _claim(c: Claim) -> dict:
    return {
        "id": c.id, "proposition": c.proposition, "status": str(c.status),
        "scope": c.scope, "domain": c.domain, "dependencies": list(c.dependencies),
    }


def _candidate(c: Candidate) -> dict:
    return {
        "id": c.id, "proposition": c.proposition, "status": str(c.status), "scope": c.scope,
        "constraint_ids": list(c.constraint_ids), "origin": c.origin,
        "dependencies": list(c.dependencies), "evidence_id": c.evidence_id,
        "verification_result": c.verification_result,
    }


def _branch(b: Branch) -> dict:
    return {
        "id": b.id, "predicate": b.predicate, "status": str(b.status), "scope": b.scope,
        "conclusion": b.conclusion, "partition_id": b.partition_id,
    }


def _goal(g: Goal) -> dict:
    return {"id": g.id, "proposition": g.proposition, "status": str(g.status), "scope": g.scope}


def _obligation(o: Obligation) -> dict:
    return {
        "id": o.id, "proposition": o.proposition, "status": str(o.status),
        "mandatory": o.mandatory, "origin": o.origin,
        "dependencies": list(o.dependencies), "discharge_evidence_id": o.discharge_evidence_id,
    }


_KINDS = (
    ("claims", _claim), ("candidates", _candidate), ("branches", _branch),
    ("goals", _goal), ("obligations", _obligation),
)


def _state(s: SemanticState) -> dict:
    out: dict[str, Any] = {}
    for name, fn in _KINDS:
        recs = getattr(s, name)
        # Keyed by dictionary key, which is what an action cites; ``record.id`` may differ
        # and is carried separately so the distinction survives the round trip.
        out[name] = [{"key": k, **fn(v)} for k, v in recs.items()]
    out["active_scopes"] = list(s.active_scopes)
    return out


def to_ir(t: Transition) -> dict:
    """A plain, ordered, JSON-able statement of everything the arms must carry."""
    a = t.action
    return {
        "state_before": _state(t.state_before),
        "action": {
            "id": a.id, "operation": a.operation, "summary": a.summary,
            "output_id": a.output_id, "dependencies": list(a.dependencies),
            "preconditions": [dict(p) for p in a.preconditions],
            "obligations_created": [dict(p) for p in a.obligations_created],
            "obligations_discharged": [dict(p) for p in a.obligations_discharged],
            "typing": dict(a.typing), "warrant": dict(a.warrant),
            "goal_effect": dict(a.goal_effect), "scope_effect": dict(a.scope_effect),
            "branch_effect": dict(a.branch_effect), "candidate_effect": dict(a.candidate_effect),
            "epistemic_effect": dict(a.epistemic_effect),
        },
        "state_after": _state(t.state_after),
        "evidence": [
            {
                "key": k, "id": v.id, "kind": v.kind, "status": v.status,
                "trusted": v.trusted, "supports_rule": v.supports_rule,
                "premise_ids": list(v.premise_ids), "payload": dict(v.payload),
            }
            for k, v in t.evidence.items()
        ],
    }


def _enum(cls, value, fallback):
    try:
        return cls(value)
    except ValueError:
        return fallback


def _un_state(d: dict) -> SemanticState:
    claims = {
        r["key"]: Claim(
            id=r["id"], proposition=r["proposition"],
            status=_enum(ClaimStatus, r["status"], ClaimStatus.UNKNOWN),
            scope=r["scope"], domain=r["domain"], dependencies=tuple(r["dependencies"]),
        )
        for r in d["claims"]
    }
    candidates = {
        r["key"]: Candidate(
            id=r["id"], proposition=r["proposition"],
            status=_enum(CandidateStatus, r["status"], CandidateStatus.UNKNOWN),
            scope=r["scope"], constraint_ids=tuple(r["constraint_ids"]), origin=r["origin"],
            dependencies=tuple(r["dependencies"]), evidence_id=r["evidence_id"],
            verification_result=r["verification_result"],
        )
        for r in d["candidates"]
    }
    branches = {
        r["key"]: Branch(
            id=r["id"], predicate=r["predicate"],
            status=_enum(BranchStatus, r["status"], BranchStatus.UNKNOWN),
            scope=r["scope"], conclusion=r["conclusion"], partition_id=r["partition_id"],
        )
        for r in d["branches"]
    }
    goals = {
        r["key"]: Goal(
            id=r["id"], proposition=r["proposition"],
            status=_enum(GoalStatus, r["status"], GoalStatus.UNKNOWN), scope=r["scope"],
        )
        for r in d["goals"]
    }
    obligations = {
        r["key"]: Obligation(
            id=r["id"], proposition=r["proposition"],
            status=_enum(ObligationState, r["status"], ObligationState.UNKNOWN),
            mandatory=r["mandatory"], origin=r["origin"],
            dependencies=tuple(r["dependencies"]),
            discharge_evidence_id=r["discharge_evidence_id"],
        )
        for r in d["obligations"]
    }
    return SemanticState(
        claims=claims, candidates=candidates, branches=branches, goals=goals,
        obligations=obligations, active_scopes=tuple(d["active_scopes"]),
    )


def from_ir(d: dict) -> Transition:
    a = d["action"]
    return Transition(
        case_id="",
        action=Action(
            id=a["id"], operation=a["operation"], summary=a["summary"],
            output_id=a["output_id"], dependencies=tuple(a["dependencies"]),
            preconditions=tuple(dict(p) for p in a["preconditions"]),
            obligations_created=tuple(dict(p) for p in a["obligations_created"]),
            obligations_discharged=tuple(dict(p) for p in a["obligations_discharged"]),
            typing=dict(a["typing"]), warrant=dict(a["warrant"]),
            goal_effect=dict(a["goal_effect"]), scope_effect=dict(a["scope_effect"]),
            branch_effect=dict(a["branch_effect"]),
            candidate_effect=dict(a["candidate_effect"]),
            epistemic_effect=dict(a["epistemic_effect"]),
        ),
        state_before=_un_state(d["state_before"]),
        state_after=_un_state(d["state_after"]),
        evidence={
            r["key"]: EvidenceRecord(
                id=r["id"], kind=r["kind"], status=r["status"], trusted=r["trusted"],
                supports_rule=r["supports_rule"], premise_ids=tuple(r["premise_ids"]),
                payload=dict(r["payload"]),
            )
            for r in d["evidence"]
        },
        schema_version="",
        source={},
    )


def ir_equal(a: dict, b: dict) -> bool:
    """Structural equality of two IRs, insensitive to nothing. Used by the parity gate."""
    return a == b
