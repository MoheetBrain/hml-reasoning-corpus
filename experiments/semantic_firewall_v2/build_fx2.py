"""Build the second-generation Semantic Firewall acceptance suite (FX2).

What this is, and what it is NOT
--------------------------------
The original thirty fixtures are **external criteria**: authored on the corpus side against
a frozen reference checker, before the implementation existed. They are the strongest
evidence in this project and they are not touched here.

FX2 is weaker evidence and must never be cited as if it were not. It is authored by the
**integrator**, after the defects it covers were already known, so it cannot demonstrate
that the implementation was right — only that a defect which was found once cannot return
unnoticed. Every fixture records ``authored_by`` and the boundary it guards.

Why a second suite exists at all
--------------------------------
Four consecutive audits found real defects that the frozen thirty could not detect, because
every one of them has at most one branch scope active, mapping keys equal to record ids,
well-typed fields, and branch conclusions already present. The thirty are a good sample of
*well-formed* transitions and no sample at all of hostile ones.

Expectations are hand-written, not measured
-------------------------------------------
Each fixture's expected verdict is stated here **from the semantic contract**, before any
implementation is run. Generating expectations by executing the verifier would make the
suite a record of what the code does rather than of what it should do — the precise
self-validation the project now forbids. Where production and the frozen reference checker
disagree, the disagreement is recorded per fixture with its reason; it is not smoothed away.

Regenerate with::

    python3 experiments/semantic_firewall_v2/build_fx2.py
"""

from __future__ import annotations

import hashlib
import json
import pathlib

SCHEMA_VERSION = "semantic-firewall-case-0.1.0"
SUITE_VERSION = "semantic-firewall-fx2-1.0.0"

HERE = pathlib.Path(__file__).resolve().parent

_EMPTY = {
    "active_scopes": ["global"],
    "branches": {}, "candidates": {}, "goals": {}, "obligations": {}, "claims": {},
}
_ACTION = {
    "id": "a0", "operation": "DERIVE", "summary": "", "dependencies": [],
    "preconditions": [], "obligations_created": [], "obligations_discharged": [],
    "typing": {}, "warrant": {}, "goal_effect": {}, "scope_effect": {},
    "branch_effect": {}, "candidate_effect": {}, "epistemic_effect": {},
    "output_id": "c1",
}

FIXTURES: list[dict] = []


def fx(fixture_id, family, boundary, invariant, verdict, error_class, rationale,
       case, *, trust_mode="OFFLINE_REPLAY", reference="AGREES", reference_note="",
       materialise=None, schema_valid=True,
       provenance="integrator-authored, HMLTN Phase I hardening 2026-08-11"):
    """Register one fixture. ``verdict``/``error_class`` are the CONTRACT's answer."""
    FIXTURES.append({
        "fixture_id": fixture_id,
        "family": family,
        "boundary": boundary,
        "invariant": invariant,
        "trust_mode": trust_mode,
        "expected_result": verdict,
        "expected_error_class": error_class,
        "rationale": rationale,
        "frozen_reference_checker": reference,
        "frozen_reference_note": reference_note,
        "authored_by": "integrator",
        # Values RFC 8259 cannot express, applied by the runner before verification. Keeps
        # the artifact readable by any conforming JSON parser.
        "materialise": materialise or [],
        # Declared per fixture, NOT derived from the family, because the three MAL cases
        # differ and the differences are the interesting part. Two are schema-invalid. One
        # carries its bad value as a `materialise` instruction, so its case JSON is
        # well-formed by construction. And one is SCHEMA-VALID YET SEMANTICALLY MALFORMED --
        # the schema types obligations_created as `array` with no item constraint, so a
        # list-of-lists passes validation and is still refused by the verifier. That case is
        # the suite's own demonstration that passing the schema is not the same as being a
        # well-formed transition.
        "schema_valid": schema_valid,
        "provenance": provenance,
        "case": case,
    })


#: Sentinel meaning "emit no domain key at all", as distinct from ``domain: null``. Only
#: FX2-DOM-ABSENT-UNKNOWN uses it, because that is the one fixture testing the absence.
OMIT = object()


def claim(cid, prop="p", status="GIVEN", scope="global", deps=(), domain="Proposition"):
    rec = {"id": cid, "proposition": prop, "status": status, "scope": scope,
           "dependencies": list(deps)}
    if domain is not OMIT:
        rec["domain"] = domain
    return rec


def state(**over):
    out = json.loads(json.dumps(_EMPTY))
    out.update(over)
    return out


def case(action=None, before=None, after=None, evidence=None, case_id="FX2"):
    act = json.loads(json.dumps(_ACTION))
    act.update(action or {})
    return {
        "schema_version": SCHEMA_VERSION, "case_id": case_id, "action": act,
        # Record-level provenance, same shape the frozen thirty carry. `split` is FX2 so a
        # reader can never mistake one of these for an ACCEPTANCE record.
        "pair_id": "", "split": "FX2", "semantic_focus": "",
        "state_before": before if before is not None else state(),
        "state_after": after if after is not None else state(),
        "evidence": evidence or {},
        "source": {"origin": "synthetic", "rationale": ""},
    }


# ---------------------------------------------------------------------------
# DOM — domain subtyping. Production and the reference agree here.
# ---------------------------------------------------------------------------

def _typed(claim_domain, required, out_domain="Proposition", produced_domain="Proposition"):
    p = claim(cid="p0", prop="n > 0", domain=OMIT if claim_domain is None else claim_domain)
    c = claim(cid="c1", prop="q", status="DERIVED", deps=["p0"], domain=produced_domain)
    typing = {"input_domains": {"p0": required}, "output_domain": out_domain}
    return case(
        action={"dependencies": ["p0"], "typing": typing, "summary": "q"},
        before=state(claims={"p0": p}),
        after=state(claims={"p0": p, "c1": c}),
    )


fx("FX2-DOM-SUBTYPE-LEGAL", "DOM", "LEGAL", "TYPE_DOMAIN", "VALID", None,
   "A Natural inhabits Integer. Containment, not equality: the pre-repair verifier compared "
   "declared domains with != and returned a FALSE INVALID on sound reasoning.",
   _typed("Natural", "Integer"))
fx("FX2-DOM-MULTIHOP-LEGAL", "DOM", "LEGAL", "TYPE_DOMAIN", "VALID", None,
   "Natural -> Integer -> Real -> Number. The walk is transitive, not one step.",
   _typed("Natural", "Number"))
fx("FX2-DOM-REVERSE-ILLEGAL", "DOM", "ILLEGAL", "TYPE_DOMAIN", "INVALID",
   "TYPE_OR_DOMAIN_MISMATCH",
   "Containment runs one way. Not every Integer is a Natural.",
   _typed("Integer", "Natural"))
fx("FX2-DOM-UNRELATED-ILLEGAL", "DOM", "ILLEGAL", "TYPE_DOMAIN", "INVALID",
   "TYPE_OR_DOMAIN_MISMATCH",
   "Boolean and Integer stand in no containment relation, so neither inhabits the other.",
   _typed("Boolean", "Integer"))
fx("FX2-DOM-ZERO-ILLEGAL", "DOM", "ILLEGAL", "TYPE_DOMAIN", "INVALID",
   "TYPE_OR_DOMAIN_MISMATCH",
   "NonNegativeReal does not inhabit PositiveReal; zero is the counterexample, and it is "
   "why these are separate nodes rather than one.",
   _typed("NonNegativeReal", "PositiveReal"))
fx("FX2-DOM-UNKNOWN", "DOM", "BOUNDARY_UNKNOWN", "TYPE_DOMAIN", "UNRESOLVED", None,
   "An UNKNOWN domain is unavailable evidence. SF-R13: return unresolved rather than guess.",
   _typed("UNKNOWN", "Integer"))
fx("FX2-DOM-ABSENT-UNKNOWN", "DOM", "BOUNDARY_UNKNOWN", "TYPE_DOMAIN", "UNRESOLVED", None,
   "An ABSENT annotation is also unavailability, not a violation (D-048). Production once "
   "returned INVALID here, rejecting a transition for carrying no domain.",
   _typed(None, "Integer"),
   reference="AGREES",
   reference_note="The reference treats None and 'UNKNOWN' alike in _type_domain.")


# ---------------------------------------------------------------------------
# WAR — the warrant premise envelope
# ---------------------------------------------------------------------------

def _warranted(premise_ids, dependencies):
    claims = {d: claim(cid=d, prop=f"prop {d}") for d in dependencies}
    produced = claim(cid="c1", prop="q", status="DERIVED", deps=dependencies)
    ev = {"e1": {"id": "e1", "kind": "SOURCE_REVIEW", "status": "VALID",
                 "supports_rule": "R", "trusted": True, "premise_ids": list(premise_ids)}}
    return case(
        action={"dependencies": list(dependencies), "summary": "q",
                "warrant": {"kind": "EVIDENCE_ADAPTER", "rule": "R", "evidence_id": "e1"}},
        before=state(claims=claims),
        after=state(claims={**claims, "c1": produced}),
        evidence=ev,
    )


fx("FX2-WAR-EXACT-LEGAL", "WAR", "LEGAL", "WARRANT", "VALID", None,
   "The envelope names exactly the declared premises.",
   _warranted(["p1", "p2"], ["p1", "p2"]))
fx("FX2-WAR-SUBSET-ILLEGAL", "WAR", "ILLEGAL", "WARRANT", "INVALID", "WARRANT_MISMATCH",
   "SF-R09 binds the EXACT premise list. The old subset test failed in the dangerous "
   "direction: evidence checked against fewer premises than the action declared was "
   "accepted, so a conclusion acquired ancestry its warrant never covered.",
   _warranted(["p1"], ["p1", "p2"]))
fx("FX2-WAR-SUPERSET-ILLEGAL", "WAR", "ILLEGAL", "WARRANT", "INVALID", "WARRANT_MISMATCH",
   "Evidence resting on a premise the action never declared is equally a mismatch.",
   _warranted(["p1", "p2"], ["p1"]))
fx("FX2-WAR-ORDER-ILLEGAL", "WAR", "ILLEGAL", "WARRANT", "INVALID", "WARRANT_MISMATCH",
   "Order is significant because the frozen reference compares the lists outright. "
   "Recorded as a decision: neither implementation contains an independent argument that a "
   "premise envelope is a sequence rather than a set, and this fixture freezes the answer.",
   _warranted(["p2", "p1"], ["p1", "p2"]))


# ---------------------------------------------------------------------------
# FRM — the frame condition. The reference frames CLAIMS only, so it diverges on three.
# ---------------------------------------------------------------------------

_REF_FRAME_NOTE = ("The frozen reference's _exact_state_change frames claims only, so it "
                   "accepts this. Production extends the frame to candidates, branches and "
                   "obligations (D-049); the divergence is deliberate and recorded.")

fx("FX2-FRM-LEGAL", "FRM", "LEGAL", "FRAME", "VALID", None,
   "The declared output is the one permitted addition; everything else is carried forward.",
   case(action={"dependencies": ["p0"], "summary": "q"},
        before=state(claims={"p0": claim("p0")}),
        after=state(claims={"p0": claim("p0"),
                            "c1": claim("c1", "q", "DERIVED", deps=["p0"])})))

fx("FX2-FRM-CREATE-ILLEGAL", "FRM", "ILLEGAL", "FRAME", "INVALID", "DEPENDENCY_VIOLATION",
   "A claim asserting 0 = 1, status VERIFIED, materialising with no evidence, no warrant "
   "and no epistemic effect. No forgery is required; the state is simply asserted.",
   case(action={"output_id": None},
        before=state(),
        after=state(claims={"x": claim("x", "0 = 1", "VERIFIED")})))

fx("FX2-FRM-MUTATE-ILLEGAL", "FRM", "ILLEGAL", "FRAME", "INVALID", "DEPENDENCY_VIOLATION",
   "An existing premise rewritten ASSUMED -> VERIFIED with its proposition changed.",
   case(action={"output_id": None},
        before=state(claims={"p": claim("p", "n > 0", "ASSUMED")}),
        after=state(claims={"p": claim("p", "n < 0", "VERIFIED")})))

fx("FX2-FRM-CANDPROMO-ILLEGAL", "FRM", "ILLEGAL", "FRAME", "INVALID",
   "DEPENDENCY_VIOLATION",
   "A candidate walked PROPOSED -> VERIFIED with candidate_effect kind NONE and zero "
   "constraints checked. The promotion protocol is keyed on the declaration, so declining "
   "to declare it skipped the entire rule including the constraint-subset check.",
   case(action={"output_id": None},
        before=state(candidates={"k": {"id": "k", "proposition": "x = 2",
                                       "status": "PROPOSED", "scope": "global",
                                       "constraint_ids": ["c1", "c2"]}}),
        after=state(candidates={"k": {"id": "k", "proposition": "x = 2",
                                      "status": "VERIFIED", "scope": "global",
                                      "constraint_ids": ["c1", "c2"]}})),
   reference="DIVERGES", reference_note=_REF_FRAME_NOTE)

fx("FX2-FRM-REOPEN-ILLEGAL", "FRM", "ILLEGAL", "FRAME", "INVALID", "DEPENDENCY_VIOLATION",
   "REJECTED is documented as terminal. Reopening it would let a refuted object be retried "
   "until some evidence happened to accept it.",
   case(action={"output_id": None},
        before=state(candidates={"k": {"id": "k", "proposition": "x = 2",
                                       "status": "REJECTED", "scope": "global",
                                       "constraint_ids": ["c1"]}}),
        after=state(candidates={"k": {"id": "k", "proposition": "x = 2",
                                      "status": "VERIFIED", "scope": "global",
                                      "constraint_ids": ["c1"]}})),
   reference="DIVERGES", reference_note=_REF_FRAME_NOTE)

fx("FX2-FRM-OBLDEL-ILLEGAL", "FRM", "ILLEGAL", "FRAME", "INVALID", "DEPENDENCY_VIOLATION",
   "A mandatory OPEN obligation deleted outright. Proof debt does not lapse by being "
   "dropped from the resulting state.",
   case(action={"output_id": None},
        before=state(obligations={"o": {"id": "o", "proposition": "d != 0",
                                        "status": "OPEN", "mandatory": True,
                                        "dependencies": []}}),
        after=state()),
   reference="DIVERGES", reference_note=_REF_FRAME_NOTE)


# ---------------------------------------------------------------------------
# SCP — scope containment. The reference has no scope tree, so it diverges throughout.
# ---------------------------------------------------------------------------

_REF_SCOPE_NOTE = ("The frozen reference derives scope depth from active_scopes position "
                   "and has no containment tree, so it cannot distinguish these. The "
                   "divergence is the point of the fixture (D-053).")


def _scoped(scopes, premise_scope, conclusion_scope, branches):
    p = claim("p", "q", "ASSUMED", scope=premise_scope)
    c = claim("c1", "q", "DERIVED", scope=conclusion_scope, deps=["p"])
    st = lambda claims: {"active_scopes": list(scopes), "branches": branches,  # noqa: E731
                         "candidates": {}, "goals": {}, "obligations": {}, "claims": claims}
    return case(action={"dependencies": ["p"], "summary": "q"},
                before=st({"p": p}), after=st({"p": p, "c1": c}))


def _br(**parents):
    return {k: {"id": k, "predicate": "case", "status": "OPEN",
                **({"scope": v} if v else {})} for k, v in parents.items()}


_SIB = _br(a=None, b=None)
fx("FX2-SCP-SIBLING-AB-ILLEGAL", "SCP", "ILLEGAL", "SCOPE", "INVALID", "SCOPE_LEAK",
   "branch:a and branch:b are both children of global. Neither contains the other, so a "
   "conclusion may not cross between them. Before D-053 this direction was VALID and only "
   "the mirror was refused, decided by list position alone.",
   _scoped(["global", "branch:a", "branch:b"], "branch:a", "branch:b", _SIB),
   reference="DIVERGES", reference_note=_REF_SCOPE_NOTE)
fx("FX2-SCP-SIBLING-BA-ILLEGAL", "SCP", "ILLEGAL", "SCOPE", "INVALID", "SCOPE_LEAK",
   "The mirror of the above. These two fixtures exist as a PAIR: their verdicts must be "
   "identical, and a suite containing only one of them would not detect the asymmetry.",
   _scoped(["global", "branch:a", "branch:b"], "branch:b", "branch:a", _SIB),
   reference="DIVERGES", reference_note=_REF_SCOPE_NOTE)

_NEST = _br(a=None, b="branch:a")
fx("FX2-SCP-NARROWING-LEGAL", "SCP", "LEGAL", "SCOPE", "VALID", None,
   "branch:b sits inside branch:a, so a premise in a may conclude into b. Containment must "
   "still WORK, not merely refuse everything.",
   _scoped(["global", "branch:a", "branch:b"], "branch:a", "branch:b", _NEST),
   reference="DIVERGES", reference_note=_REF_SCOPE_NOTE)
fx("FX2-SCP-WIDENING-ILLEGAL", "SCP", "ILLEGAL", "SCOPE", "INVALID", "SCOPE_LEAK",
   "The reverse of the above, on the same tree: a fact local to the inner frame does not "
   "become true in the outer one by being restated there.",
   _scoped(["global", "branch:a", "branch:b"], "branch:b", "branch:a", _NEST),
   reference="DIVERGES", reference_note=_REF_SCOPE_NOTE)
fx("FX2-SCP-DUPLICATE-ILLEGAL", "SCP", "ILLEGAL", "SCOPE", "INVALID", "SCOPE_LEAK",
   "The duplicate-frame attack: active_scopes.index returns the FIRST occurrence, so "
   "prepending a copy of an inner frame made it look outermost and let any premise escape "
   "to global. One extra list element defeated the invariant, with no forged evidence.",
   _scoped(["branch:x", "global", "branch:x"], "branch:x", "global", _br(x=None)),
   reference="DIVERGES", reference_note=_REF_SCOPE_NOTE)


# ---------------------------------------------------------------------------
# BRN — branch/join
# ---------------------------------------------------------------------------

def _join(conclusions, published="n is even or n is odd", statuses=None, covered=None):
    statuses = statuses or dict.fromkeys(conclusions, "CLOSED")
    branches = {b: {"id": b, "predicate": f"case {b}", "status": statuses[b],
                    "partition_id": "p1",
                    **({"conclusion": c} if c is not None else {})}
                for b, c in conclusions.items()}
    cov = list(conclusions) if covered is None else list(covered)
    st = lambda claims: {"active_scopes": ["global"], "branches": branches,  # noqa: E731
                         "candidates": {}, "goals": {}, "obligations": {}, "claims": claims}
    return case(
        action={"operation": "JOIN_BRANCHES", "summary": published,
                "branch_effect": {"kind": "JOIN", "branch_ids": list(conclusions),
                                  "coverage_evidence_id": "e1"}},
        before=st({}),
        after=st({"c1": claim("c1", published, "DERIVED")}),
        evidence={"e1": {"id": "e1", "kind": "EXHAUSTIVE_PARTITION", "status": "VALID",
                         "supports_rule": "JOIN_BRANCHES", "trusted": True,
                         "premise_ids": [], "branch_ids": cov}},
    )


_Q = "n is even or n is odd"
fx("FX2-BRN-LEGAL", "BRN", "LEGAL", "BRANCH_JOIN", "VALID", None,
   "Every branch CLOSED, every conclusion equal to the published claim, coverage certified.",
   _join({"b1": _Q, "b2": _Q}))
fx("FX2-BRN-NULLCONC-ILLEGAL", "BRN", "ILLEGAL", "BRANCH_JOIN", "INVALID",
   "INVALID_BRANCH_JOIN",
   "Coverage without conclusions is not a proof. Before D-053 three null branches could "
   "publish '0 = 1' as VALID, because the conclusion check was skipped whenever the "
   "conclusion was null. Note the asymmetry that made it indefensible: '' and 'UNKNOWN' "
   "were both refused while null was accepted.",
   _join({"b1": None, "b2": None, "b3": None}, published="0 = 1"),
   reference="DIVERGES",
   reference_note="The reference applies the same skip-when-null reading.")
fx("FX2-BRN-PARTIAL-NULL-ILLEGAL", "BRN", "ILLEGAL", "BRANCH_JOIN", "INVALID",
   "INVALID_BRANCH_JOIN",
   "One unconcluded branch is enough: the join would rest on a case that established "
   "nothing.",
   _join({"b1": _Q, "b2": None}),
   reference="DIVERGES", reference_note="Same skip-when-null reading.")
fx("FX2-BRN-MISMATCH-ILLEGAL", "BRN", "ILLEGAL", "BRANCH_JOIN", "INVALID",
   "INVALID_BRANCH_JOIN",
   "A join publishes what every branch established, not a new proposition.",
   _join({"b1": _Q, "b2": "n is prime"}))
fx("FX2-BRN-OPEN-ILLEGAL", "BRN", "ILLEGAL", "BRANCH_JOIN", "INVALID",
   "INVALID_BRANCH_JOIN",
   "An OPEN branch has not concluded, whatever its recorded conclusion says.",
   _join({"b1": _Q, "b2": _Q}, statuses={"b1": "CLOSED", "b2": "OPEN"}))
fx("FX2-BRN-NOCOVER-ILLEGAL", "BRN", "ILLEGAL", "BRANCH_JOIN", "INVALID",
   "INVALID_BRANCH_JOIN",
   "The partition certificate omits a branch. Branches that agree are not evidence that "
   "they exhaust the cases.",
   _join({"b1": _Q, "b2": _Q}, covered=["b1"]))
fx("FX2-BRN-OVERLAP-LEGAL", "BRN", "LEGAL", "BRANCH_JOIN", "VALID", None,
   "Coverage is required; DISJOINTNESS DELIBERATELY IS NOT. Disjunction elimination is "
   "sound for overlapping cases, so a checker demanding disjointness would reject valid "
   "reasoning. Frozen here because a later reader is likely to think the missing check is "
   "an oversight and add it.",
   _join({"b1": _Q, "b2": _Q}))
fx("FX2-BRN-UNKNOWNCONC-UNKNOWN", "BRN", "BOUNDARY_UNKNOWN", "BRANCH_JOIN", "UNRESOLVED",
   None,
   "An UNKNOWN conclusion is unavailable evidence, not a disagreement. It was previously "
   "reported as a detected violation, contradicting the three-valued discipline used "
   "everywhere else in the verifier.",
   _join({"b1": _Q, "b2": "UNKNOWN"}),
   reference="DIVERGES", reference_note="The reference reports this as a mismatch.")


# ---------------------------------------------------------------------------
# UNK — an unrelated unknown must not mask an independent violation
# ---------------------------------------------------------------------------

_junk = claim("junk_zzz", "entirely unrelated", "UNKNOWN")
_bad_before = state(claims={"p0": claim("p0"), "junk_zzz": _junk})
_bad_after = state(claims={"p0": claim("p0"), "junk_zzz": _junk,
                           "c1": claim("c1", "q", "DERIVED", deps=["p0", "p9"])})
fx("FX2-UNK-MASK-ILLEGAL", "UNK", "ILLEGAL", "DEPENDENCY", "INVALID",
   "DEPENDENCY_VIOLATION",
   "The produced claim records an ancestor the action never declared -- an independent "
   "violation -- while an UNRELATED claim carries status UNKNOWN. Before D-049 the unknown "
   "sweep was unscoped, so appending three lines of JSON turned 10/10 ILLEGAL fixtures into "
   "UNRESOLVED. UNRESOLVED counts as neither accepted nor detected, so that was a complete "
   "detection bypass available to anyone who could append a record nothing cites.",
   case(action={"dependencies": ["p0"], "summary": "q"},
        before=_bad_before, after=_bad_after),
   reference="DIVERGES",
   reference_note="The reference records unknowns per-check rather than sweeping the state, "
                  "so it is not susceptible; it reports INVALID for its own reasons.")

_rel_before = state(claims={"p0": claim("p0", "n > 0", "UNKNOWN")})
_rel_after = state(claims={"p0": claim("p0", "n > 0", "UNKNOWN"),
                           "c1": claim("c1", "q", "DERIVED", deps=["p0"])})
fx("FX2-UNK-RELEVANT-UNKNOWN", "UNK", "BOUNDARY_UNKNOWN", "DEPENDENCY", "UNRESOLVED", None,
   "Scoping the sweep must not switch the rule off: an unknown on a record the action "
   "actually cites still suspends the verdict.",
   case(action={"dependencies": ["p0"], "summary": "q"},
        before=_rel_before, after=_rel_after))


# ---------------------------------------------------------------------------
# TRU — trust. These are the only fixtures whose verdict depends on the mode.
# ---------------------------------------------------------------------------

def _self_asserted():
    cand = lambda s: {"id": "k1", "proposition": "x = 2", "status": s,  # noqa: E731
                      "scope": "global", "constraint_ids": ["c1"]}
    return case(
        action={"operation": "VERIFY_CANDIDATE", "output_id": None,
                "candidate_effect": {"kind": "PROMOTE", "candidate_id": "k1",
                                     "evidence_id": "e_self"}},
        before=state(candidates={"k1": cand("PROPOSED")}),
        after=state(candidates={"k1": cand("VERIFIED")}),
        evidence={"e_self": {"id": "e_self", "kind": "CANDIDATE_CHECK", "status": "VALID",
                             "supports_rule": "VERIFY_CANDIDATE", "trusted": True,
                             "premise_ids": [], "checked_constraints": ["c1"]}},
    )


fx("FX2-TRU-SELFVALID-REPLAY-LEGAL", "TRU", "LEGAL", "TRUST", "VALID", None,
   "Replaying a frozen corpus, a recorded status is observed reference data produced by an "
   "external process. This fixture DOCUMENTS the replay mode rather than endorsing it, and "
   "exists so that the runtime fixture below is a contrast rather than an assertion.",
   _self_asserted(), trust_mode="OFFLINE_REPLAY")
fx("FX2-TRU-SELFVALID-RUNTIME-ILLEGAL", "TRU", "ILLEGAL", "TRUST", "INVALID",
   "CANDIDATE_PROMOTION",
   "The same bytes, authored by a model. status VALID and trusted true are both fields the "
   "producer sets, so they buy NOTHING: acceptance requires an attestation carrying a "
   "CheckedEvidence that only reasoning.certificates.check can mint (D-050/D-052).",
   _self_asserted(), trust_mode="RUNTIME",
   reference="DIVERGES",
   reference_note="The frozen reference has no trust mode; it reads status as authority "
                  "unconditionally, which is the design this fixture guards against.")


# ---------------------------------------------------------------------------
# CAN — candidate rejection, grounded in AMPS-Khan
# ---------------------------------------------------------------------------

_AMPS_PROV = (
    "Derived from AMPS-Khan row 22728, topic 'find-the-area-between-two-curves', in which a "
    "radical equation is squared and the resulting candidate roots are checked against the "
    "original equation, rejecting the extraneous one. Source: /Users/moheet/Desktop/"
    "0000.parquet, sha256 b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41. "
    "PROVENANCE CAVEAT: that file is a COMMUNITY MIRROR (HuggingFace XinyaoHu/AMPS_khan), "
    "traced one hop and NOT verified against Hendrycks' official release. The mathematical "
    "pattern is real and independently checkable; the corpus attribution is not fully "
    "verified. 248 rows contain this pattern but only 11 distinct solution skeletons."
)


def _extraneous(after_status, checked):
    cand = lambda s: {"id": "k_root", "proposition": "x = 18", "status": s,  # noqa: E731
                      "scope": "global",
                      "constraint_ids": ["c_radical", "c_domain"],
                      "origin": "squaring a radical equation"}
    return case(
        action={"operation": "VERIFY_CANDIDATE", "output_id": None,
                "candidate_effect": {"kind": "PROMOTE", "candidate_id": "k_root",
                                     "evidence_id": "e_check"}},
        before=state(candidates={"k_root": cand("PROPOSED")}),
        after=state(candidates={"k_root": cand(after_status)}),
        evidence={"e_check": {"id": "e_check", "kind": "CANDIDATE_CHECK", "status": "VALID",
                              "supports_rule": "VERIFY_CANDIDATE", "trusted": True,
                              "premise_ids": [], "checked_constraints": list(checked),
                              "candidate_id": "k_root"}},
    )


fx("FX2-CAN-EXTRANEOUS-REJECTED-LEGAL", "CAN", "LEGAL", "CANDIDATES", "VALID", None,
   "A candidate root that fails substitution into the ORIGINAL equation is REJECTED. This "
   "is the first externally grounded exercise of the REJECTED lifecycle state: the contract "
   "records that no frozen fixture reaches UNVERIFIED or REJECTED, so SF-R06 has never been "
   "demonstrated.",
   _extraneous("REJECTED", ["c_radical", "c_domain"]), provenance=_AMPS_PROV)
fx("FX2-CAN-SUBSET-ILLEGAL", "CAN", "ILLEGAL", "CANDIDATES", "INVALID",
   "CANDIDATE_PROMOTION",
   "Promotion checked the squared equation but not the original domain constraint -- which "
   "is exactly how an extraneous root gets promoted. Verifying a subset establishes a "
   "different claim than the one being made.",
   _extraneous("VERIFIED", ["c_radical"]), provenance=_AMPS_PROV)


# ---------------------------------------------------------------------------
# MAL — malformed input must be REFUSED at the boundary, never raised
# ---------------------------------------------------------------------------

def _malformed(mutate):
    c = case(action={"output_id": None})
    mutate(c)
    return c


def _set(path, value):
    def go(c):
        tgt = c
        for k in path[:-1]:
            tgt = tgt[k]
        tgt[path[-1]] = value
    return go


fx("FX2-MAL-TYPING-REFUSE", "MAL", "ILLEGAL", "MALFORMED", "REFUSED", None,
   "typing.input_domains as a list raised an uncaught AttributeError inside verify(). A "
   "verifier that may be handed model output must never throw.",
   _malformed(_set(["action", "typing"], ["p0", "p1"])), schema_valid=False)
fx("FX2-MAL-NAN-REFUSE", "MAL", "ILLEGAL", "MALFORMED", "REFUSED", None,
   "NaN != NaN, and the frame condition compares records structurally, so a record "
   "byte-identical in both states reported 'changed without a licensed state effect'. It "
   "failed safe, but it was a false INVALID on any float-bearing payload. "
   "NOTE: the artifact carries this as a `materialise` instruction rather than a literal, "
   "because RFC 8259 has no NaN and embedding one makes the whole file unreadable to a "
   "strict parser -- an independent Ruby parse rejected it, which is why this is an "
   "instruction and not a value.",
   _malformed(_set(["action", "typing"], {"weight": None})),
   materialise=[{"path": ["action", "typing", "weight"], "set_nonfinite": "nan"}])
fx("FX2-MAL-UNHASHABLE-REFUSE", "MAL", "ILLEGAL", "MALFORMED", "REFUSED", None,
   "An unhashable value in obligations_created reached a dictionary lookup and raised. "
   "This fixture is SCHEMA-VALID and semantically malformed: the schema types "
   "obligations_created as `array` with no item constraint, so a list-of-lists passes "
   "validation. It is kept precisely for that contrast -- a case can satisfy the published "
   "schema and still be refused, so schema conformance is not a substitute for the "
   "verifier.",
   _malformed(_set(["action", "obligations_created"], [[1], [2]])), schema_valid=True)
fx("FX2-MAL-SCOPES-REFUSE", "MAL", "ILLEGAL", "MALFORMED", "REFUSED", None,
   "A non-string in active_scopes raised on a string join while rendering a diagnostic.",
   _malformed(_set(["state_before", "active_scopes"], [{"id": {}}])), schema_valid=False)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------

def main() -> None:
    # Fill the record-level provenance from the fixture's own metadata, so the case and the
    # fixture that wraps it cannot disagree about what is being tested.
    for f in FIXTURES:
        f["case"]["pair_id"] = f["fixture_id"].rsplit("-", 1)[0]
        f["case"]["semantic_focus"] = f["invariant"]
        f["case"]["case_id"] = f["fixture_id"]
        # Provenance travels with the case, not only with the fixture wrapper, so a case
        # lifted out of the suite still declares where it came from.
        src = f["case"]["source"]
        src["rationale"] = f["rationale"][:400]
        if f["provenance"].startswith("Derived from AMPS-Khan"):
            src["origin"] = "amps_khan"
            src["external_row_id"] = "0000.parquet:22728"
            src["external_file_sha256"] = (
                "b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41")
            src["provenance_caveat"] = (
                "COMMUNITY MIRROR, traced one hop to HuggingFace XinyaoHu/AMPS_khan and NOT "
                "verified against Hendrycks' official release. The mathematical pattern is "
                "independently checkable; the corpus attribution is not.")

    ids = [f["fixture_id"] for f in FIXTURES]
    assert len(ids) == len(set(ids)), "duplicate fixture id"
    assert all(i.startswith("FX2-") for i in ids), "id must not collide with the frozen 30"

    doc = {
        "suite_version": SUITE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_by": "experiments/semantic_firewall_v2/build_fx2.py",
        "authored_by": "integrator",
        "supersedes": None,
        "extends": "experiments/semantic_firewall/acceptance/fixtures.json",
        "status_of_evidence": (
            "SECOND-GENERATION AND WEAKER THAN THE FROZEN THIRTY. Those were authored on the "
            "corpus side against a reference checker before the implementation existed. "
            "These were authored by the integrator AFTER the defects they cover were known, "
            "so they cannot show the implementation was right -- only that a defect found "
            "once cannot return unnoticed. Never cite FX2 as external validation."
        ),
        "expectations_are_hand_written": (
            "Every expected verdict is stated from the semantic contract, not read off a "
            "verifier run. Generating expectations by execution would record what the code "
            "does rather than what it should do."
        ),
        "counts": {
            "total": len(FIXTURES),
            "by_family": {f: sum(1 for x in FIXTURES if x["family"] == f)
                          for f in sorted({x["family"] for x in FIXTURES})},
            "by_boundary": {b: sum(1 for x in FIXTURES if x["boundary"] == b)
                            for b in sorted({x["boundary"] for x in FIXTURES})},
            "diverges_from_frozen_reference": sum(
                1 for x in FIXTURES if x["frozen_reference_checker"] == "DIVERGES"),
            "schema_valid": sum(1 for x in FIXTURES if x["schema_valid"]),
            "deliberately_schema_invalid": sum(
                1 for x in FIXTURES if not x["schema_valid"]),
        },
        "fixtures": FIXTURES,
    }
    out = HERE / "fixtures_v2.json"
    # allow_nan=False is the gate: it makes emitting a non-standard literal an error here
    # rather than a file no independent parser can read.
    text = json.dumps(doc, indent=2, sort_keys=False, allow_nan=False) + "\n"
    out.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(f"{out.name}: {len(FIXTURES)} fixtures, sha256 {digest}")
    for fam, n in doc["counts"]["by_family"].items():
        print(f"  {fam}: {n}")
    print(f"  diverging from the frozen reference: "
          f"{doc['counts']['diverges_from_frozen_reference']}")


if __name__ == "__main__":
    main()
