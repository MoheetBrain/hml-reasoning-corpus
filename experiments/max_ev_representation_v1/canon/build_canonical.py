"""Build ONE canonical semantic object per item (mission §4).

Every experimental item originates here. The four representation arms are renderings of the
:class:`Transition` this module produces -- none is separately authored, and none can carry
information the others lack, because none of them is the source.

Fidelity rules
--------------
Every identifier, type and proposition is copied verbatim from the recorded Lean state.
Nothing is invented. What this module *adds* is structure the corpus always implied but the
50K wrapper flattened: which declarations exist, what each one's type is, which earlier
binders it mentions, which case frame it sits in, and what the goal is.

Satisfying the frame condition
------------------------------
``verify._check_frame`` is strict, and correctly so: a claim may not appear in
``state_after`` unless it is the action's declared output, may not vanish, and may not
change without a declared effect. So the construction is:

* the context declarations become claims that **persist unchanged** into ``state_after``;
* the action's single declared output ``c1`` records the resulting proof state;
* the goal is carried as a real :class:`Goal`, and is only touched when the action declares
  a ``goal_effect`` naming it.

That is the honest shape of a Lean step: the hypotheses were already established, the tactic
produces a new proof state, and the goal is discharged only when Lean says ``no goals``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from hamiltonian_lang.semantic_state.model import (
    Action,
    Branch,
    BranchStatus,
    Claim,
    ClaimStatus,
    EvidenceRecord,
    Goal,
    GoalStatus,
    SemanticState,
    Transition,
)

from .lean_state import Declaration, GoalBlock, classify_domain, parse_lean_state

__all__ = ["CanonicalItem", "BuildError", "build_canonical", "IDENT"]

#: Lean identifier-ish runs. Used only to ask "does this text mention that binder?", never
#: to parse a term.
IDENT = re.compile(r"[A-Za-z_À-ɏͰ-Ͽᴀ-ᶿ⁰-₟✝'][\w'À-ɏͰ-Ͽ⁰-₟✝.]*")

GENERATOR_VERSION = "max-ev-canonical-1.0.0"


class BuildError(Exception):
    """The record cannot be decomposed faithfully. Always a refusal, never a partial item."""


@dataclass(frozen=True)
class CanonicalItem:
    """One canonical semantic object plus the provenance needed to reproduce it."""

    semantic_id: str
    transition: Transition
    #: Structural facts used for complexity strata and OOD splits (§9, §19).
    features: dict[str, Any]
    provenance: dict[str, Any]


def _unique_ids(block: GoalBlock) -> list[tuple[str, Declaration, str]]:
    """(claim_id, declaration, binder_name) with collisions disambiguated.

    Lean reuses inaccessible names such as ``inst✝``; the printed superscript is the
    disambiguator. Names are kept verbatim, and a genuine repeat gets a positional suffix so
    two distinct binders never collapse into one claim.
    """
    seen: dict[str, int] = {}
    out: list[tuple[str, Declaration, str]] = []
    for decl in block.declarations:
        for name in decl.names:
            if name in seen:
                seen[name] += 1
                cid = f"{name}#{seen[name]}"
            else:
                seen[name] = 0
                cid = name
            out.append((cid, decl, name))
    return out


def _mentions(text: str, names: set[str]) -> set[str]:
    """Which of ``names`` occur as identifier tokens in ``text``."""
    return {tok for tok in IDENT.findall(text) if tok in names} | {
        tok.split(".")[0] for tok in IDENT.findall(text) if tok.split(".")[0] in names
    }


def build_canonical(record: dict, *, semantic_id: str) -> CanonicalItem:
    """Decompose one 50K canonical record into a structured :class:`Transition`."""
    nt = record["neutral_transition"]
    claims_in = nt["state_before"]["claims"]
    if len(claims_in) != 1:
        raise BuildError(f"expected exactly one wrapped claim, got {len(claims_in)}")
    before_key, before_raw = next(iter(claims_in.items()))
    after_raw = None
    for key, val in nt["state_after"]["claims"].items():
        if key != before_key:
            after_raw = val
    if after_raw is None:
        raise BuildError("no produced claim in state_after")

    st = parse_lean_state(before_raw["proposition"])
    if not st.clean or st.primary is None:
        raise BuildError("prior state did not decompose cleanly")
    block = st.primary
    if not block.declarations:
        raise BuildError("prior state has an empty context")

    scope = f"branch:{block.case_label}" if block.case_label else "global"
    active = ("global", scope) if block.case_label else ("global",)

    entries = _unique_ids(block)
    names = {cid for cid, _, _ in entries}
    claims: dict[str, Claim] = {}
    prior_names: set[str] = set()
    for cid, decl, _name in entries:
        body = decl.type_text + (f" := {decl.value_text}" if decl.value_text else "")
        deps = tuple(sorted(_mentions(body, prior_names)))
        claims[cid] = Claim(
            id=cid,
            proposition=body,
            status=ClaimStatus.GIVEN,
            scope=scope,
            domain=classify_domain(decl.type_text),
            dependencies=deps,
        )
        prior_names.add(cid)

    goals = {
        "g0": Goal(id="g0", proposition=block.goal_text, status=GoalStatus.OPEN, scope=scope)
    }
    branches: dict[str, Branch] = {}
    if block.case_label:
        branches[block.case_label] = Branch(
            id=block.case_label,
            predicate=block.case_label,
            status=BranchStatus.OPEN,
            scope="global",
        )

    state_before = SemanticState(
        claims=claims, goals=goals, branches=branches, active_scopes=active
    )

    # ---- action -------------------------------------------------------------------
    ev_in = nt["evidence"]
    eid, ev_raw = next(iter(ev_in.items()))

    # What the action depends on: the binders the **goal it acts on** actually mentions.
    #
    # The obvious source would be the tactic text, and it is deliberately unavailable: the
    # 50K model-safe envelope records only ``tactic_sha256``, because the tactic is the
    # answer to the corpus's other tasks and carrying it would leak. Falling back to it
    # would also be wrong here for a second reason -- ``premises_used`` names Mathlib lemmas,
    # not local hypotheses, so it cannot express a dependency on anything in this state.
    #
    # Free variables of the goal is the honest reading and a mechanical one: to transform a
    # goal you must be able to see every binder it refers to, so those binders are exactly
    # the premises the step rests on. It is also the reading that makes the dependency graph
    # non-trivial, which is what the SCOPE, DEPENDENCY and TYPE_DOMAIN invariants need in
    # order to have anything to check.
    goal_mentions = _mentions(block.goal_text, names)
    cited = tuple(sorted(goal_mentions))
    typing = {
        "input_domains": {c: claims[c].domain for c in cited},
        "output_domain": "Proposition",
    }
    after_state = parse_lean_state(after_raw["proposition"])
    discharged = after_state.no_goals

    action = Action(
        id="a1",
        operation="LEAN_TACTIC",
        summary="",
        output_id="c1",
        dependencies=cited,
        typing=typing,
        warrant={"kind": "FORMAL_TRACE", "rule": "LEAN_TACTIC", "evidence_id": eid},
        goal_effect=(
            {"goal_id": "g0", "kind": "DISCHARGE", "evidence_id": eid}
            if discharged
            else {}
        ),
    )

    # A discharged goal is proved *by its own statement*: the claim the action produces is
    # the goal proposition, now DERIVED. ``verify._check_goal_discharge`` requires exactly
    # that identity, and it is the correct reading -- Lean printing "no goals" is a report
    # that the proof closed, not the proposition that was established.
    if discharged:
        produced_text = block.goal_text
    else:
        # The resulting *goal*, not the whole printed tactic state. Two reasons, and the
        # second is the load-bearing one.
        #
        # Semantically it is the more honest reading: the hypotheses were already
        # established and persist as claims, so what this action produces is the new proof
        # obligation, not a fresh copy of the context.
        #
        # Instrumentally it keeps every proposition in the corpus **single-line**. A printed
        # tactic state contains newlines, and the frozen HML view is line-oriented, so it
        # would have to emit them as ``\n`` escape text while a free-form surface showed
        # them literally -- reintroducing, in miniature, exactly the asymmetric escaping
        # confound that invalidated the previous 50K run (§24). Holding the arms to
        # single-line propositions removes the asymmetry at the source instead of auditing
        # for it afterwards.
        nxt = after_state.primary
        if nxt is None:
            raise BuildError("resulting state did not decompose cleanly")
        produced_text = nxt.goal_text
    c1 = Claim(
        id="c1",
        proposition=produced_text,
        status=ClaimStatus.DERIVED,
        scope=scope,
        domain="Proposition",
        dependencies=cited,
    )
    after_goals = {
        "g0": Goal(
            id="g0",
            proposition=block.goal_text,
            status=GoalStatus.DISCHARGED if discharged else GoalStatus.OPEN,
            scope=scope,
        )
    }
    state_after = SemanticState(
        claims={**claims, "c1": c1},
        goals=after_goals,
        branches=branches,
        active_scopes=active,
    )

    evidence = {
        eid: EvidenceRecord(
            id=eid,
            kind="FORMAL_TRACE",
            status="VALID",
            trusted=True,
            supports_rule="LEAN_TACTIC",
            premise_ids=cited,
            payload={
                "source_kind": "LEAN_DOJO_RECORDED_TRACE",
                "tactic_sha256": ev_raw.get("payload", {}).get("tactic_sha256"),
                "mathlib_revision": nt["source"].get("mathlib_revision"),
            },
        )
    }

    transition = Transition(
        case_id=semantic_id,
        action=action,
        state_before=state_before,
        state_after=state_after,
        evidence=evidence,
        source={
            "file_path": nt["source"].get("file_path"),
            "theorem_id": nt["source"].get("theorem_id"),
            "official_split": nt["source"].get("official_split"),
        },
    )

    dep_edges = sum(len(c.dependencies) for c in claims.values())
    features = {
        "n_claims": len(claims),
        "n_dependency_edges": dep_edges,
        "max_dependency_depth": _depth(claims),
        "binder_depth": _binder_depth(block),
        "has_branch": bool(block.case_label),
        "case_label": block.case_label,
        "n_cited": len(cited),
        "goal_chars": len(block.goal_text),
        "state_chars": sum(len(c.proposition) for c in claims.values()),
        "discharges_goal": discharged,
        "domain_area": (nt["source"].get("file_path") or "/").split("/")[1]
        if "/" in (nt["source"].get("file_path") or "")
        else "unknown",
        "quantifiers": sum(block.goal_text.count(q) for q in ("∀", "∃")),
        "after_n_declarations": len(after_state.primary.declarations) if after_state.primary else 0,
        "after_n_goal_blocks": len(after_state.blocks),
    }
    provenance = {
        "generator_version": GENERATOR_VERSION,
        "source_record_id": record.get("record_id"),
        "canonical_transition_sha256": record.get("canonical_transition_sha256"),
        "parent_id": record.get("parent_id"),
        "official_split": nt["source"].get("official_split"),
    }
    return CanonicalItem(semantic_id, transition, features, provenance)


def _depth(claims: dict[str, Claim]) -> int:
    memo: dict[str, int] = {}

    def d(cid: str, seen: frozenset[str] = frozenset()) -> int:
        if cid in memo:
            return memo[cid]
        if cid in seen:
            return 0
        c = claims.get(cid)
        if c is None or not c.dependencies:
            return 0
        val = 1 + max(d(p, seen | {cid}) for p in c.dependencies)
        memo[cid] = val
        return val

    return max((d(k) for k in claims), default=0)


def _binder_depth(block: GoalBlock) -> int:
    """Binder complexity of the goal: bracket nesting plus explicit quantifiers.

    Bracket nesting alone is too coarse to stratify on -- measured over 6,000 accepted
    parents it takes only ten distinct values and sits at 1 for half of them. Adding the
    quantifier count separates goals that bind variables from goals that merely nest
    applications, which is the distinction the OOD split is meant to probe.
    """
    text = block.goal_text
    depth = best = 0
    for ch in text:
        if ch in "([{":
            depth += 1
            best = max(best, depth)
        elif ch in ")]}":
            depth -= 1
    return best + sum(text.count(q) for q in ("∀", "∃", "λ", "Σ", "Π"))
