#!/usr/bin/env python3
"""Fail-closed reference semantics for neutral mathematical transitions.

The checker deliberately accepts only a small protocol.  It validates state and
evidence invariants; it is not a theorem prover and does not inspect benchmark
labels, corruption metadata, MATH answers, or HML concrete syntax.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


VALID = "VALID"
INVALID = "INVALID"
UNRESOLVED = "UNRESOLVED"

INVARIANTS = (
    "DEPENDENCY",
    "SCOPE",
    "PRECONDITIONS",
    "OBLIGATIONS",
    "CANDIDATES",
    "BRANCH_JOIN",
    "WARRANT",
    "EPISTEMIC_STATUS",
    "GOAL_DISCHARGE",
    "TYPE_DOMAIN",
)

ERROR_CLASS_FOR = {
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

_ESTABLISHED = {"GIVEN", "ASSUMED", "DERIVED", "VERIFIED"}
_DOMAIN_PARENTS = {
    "Natural": "Integer",
    "Integer": "Real",
    "Rational": "Real",
    "Probability": "Real",
    "PositiveReal": "NonNegativeReal",
    "NonNegativeReal": "Real",
    "Real": "Number",
}


@dataclass(frozen=True)
class Finding:
    invariant: str
    message: str
    path: str
    observed: Any = None
    required: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant": self.invariant,
            "message": self.message,
            "path": self.path,
            "observed": self.observed,
            "required": self.required,
        }


@dataclass
class CheckResult:
    verdict: str
    error_class: str | None = None
    violated_invariant: str | None = None
    supporting_evidence: list[Finding] = field(default_factory=list)
    unresolved_evidence: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "error_class": self.error_class,
            "violated_invariant": self.violated_invariant,
            "supporting_evidence": [item.to_dict() for item in self.supporting_evidence],
            "unresolved_evidence": [item.to_dict() for item in self.unresolved_evidence],
        }


class ReferenceChecker:
    """Check one representation-neutral transition without consulting its label."""

    def __init__(self) -> None:
        self.invalid: list[Finding] = []
        self.unknown: list[Finding] = []

    def check(self, case: dict[str, Any]) -> CheckResult:
        self.invalid = []
        self.unknown = []
        before = case.get("state_before", {})
        after = case.get("state_after", {})
        action = case.get("action", {})
        evidence = case.get("evidence", {})

        self._dependency(before, after, action)
        self._scope(before, after, action, evidence)
        self._preconditions(before, after, action, evidence)
        self._obligations(before, after, action, evidence)
        self._candidates(before, after, action, evidence)
        self._branch_join(before, after, action, evidence)
        self._warrant(before, action, evidence)
        self._epistemic(before, after, action, evidence)
        self._goal_discharge(before, after, action)
        self._type_domain(before, action)
        self._exact_state_change(before, after, action)

        if self.invalid:
            first = self.invalid[0]
            return CheckResult(
                verdict=INVALID,
                error_class=ERROR_CLASS_FOR[first.invariant],
                violated_invariant=first.invariant,
                supporting_evidence=self.invalid,
                unresolved_evidence=self.unknown,
            )
        if self.unknown:
            first = self.unknown[0]
            return CheckResult(
                verdict=UNRESOLVED,
                violated_invariant=first.invariant,
                unresolved_evidence=self.unknown,
            )
        return CheckResult(verdict=VALID)

    def _bad(
        self,
        invariant: str,
        message: str,
        path: str,
        observed: Any = None,
        required: Any = None,
    ) -> None:
        self.invalid.append(Finding(invariant, message, path, observed, required))

    def _unk(
        self,
        invariant: str,
        message: str,
        path: str,
        observed: Any = None,
        required: Any = None,
    ) -> None:
        self.unknown.append(Finding(invariant, message, path, observed, required))

    @staticmethod
    def _claims(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return state.get("claims", {}) if isinstance(state.get("claims", {}), dict) else {}

    @staticmethod
    def _valid_evidence(evidence: dict[str, Any], evidence_id: str | None) -> bool | None:
        if not evidence_id or evidence_id not in evidence:
            return False
        status = evidence[evidence_id].get("status")
        if status == "VALID":
            return True
        if status in {"UNKNOWN", "UNRESOLVED"}:
            return None
        return False

    def _dependency(self, before: dict[str, Any], after: dict[str, Any], action: dict[str, Any]) -> None:
        claims_before = self._claims(before)
        claims_after = self._claims(after)
        dependencies = action.get("dependencies", [])
        output_id = action.get("output_id")
        for index, dependency in enumerate(dependencies):
            claim = claims_before.get(dependency)
            if claim is None:
                self._bad(
                    "DEPENDENCY",
                    "a dependency is unavailable in state_before (unknown and future references are illegal)",
                    f"action.dependencies[{index}]",
                    dependency,
                    "an established claim in state_before",
                )
            elif claim.get("status") in {"UNKNOWN", "UNRESOLVED"}:
                self._unk(
                    "DEPENDENCY",
                    "dependency availability is unresolved",
                    f"state_before.claims.{dependency}.status",
                    claim.get("status"),
                    sorted(_ESTABLISHED),
                )
            elif claim.get("status") not in _ESTABLISHED:
                self._bad(
                    "DEPENDENCY",
                    "a non-evidence claim is used as a dependency",
                    f"state_before.claims.{dependency}.status",
                    claim.get("status"),
                    sorted(_ESTABLISHED),
                )
        if output_id:
            output = claims_after.get(output_id)
            if output is None:
                self._bad("DEPENDENCY", "the action output is absent from state_after", "action.output_id", output_id, "present")
            elif output.get("dependencies") != dependencies:
                self._bad(
                    "DEPENDENCY",
                    "output ancestry does not exactly match the action dependencies",
                    f"state_after.claims.{output_id}.dependencies",
                    output.get("dependencies"),
                    dependencies,
                )

    def _scope(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        claims_before = self._claims(before)
        output = self._claims(after).get(action.get("output_id"), {})
        output_scope = output.get("scope")
        active = set(before.get("active_scopes", []))
        if output_scope in {"UNKNOWN", None}:
            self._unk("SCOPE", "output scope is unresolved", "state_after.claims.<output>.scope", output_scope, "an active scope")
            return
        if output_scope != "global" and output_scope not in active:
            self._bad("SCOPE", "output is assigned to an inactive scope", "state_after.claims.<output>.scope", output_scope, sorted(active))
        local_dependencies = [
            dep
            for dep in action.get("dependencies", [])
            if claims_before.get(dep, {}).get("scope") not in {None, "global"}
        ]
        if local_dependencies and output_scope == "global":
            effect = action.get("scope_effect", {})
            discharge = self._valid_evidence(evidence, effect.get("discharge_evidence_id"))
            if effect.get("kind") != "DISCHARGE" or discharge is False:
                self._bad(
                    "SCOPE",
                    "branch- or assumption-local evidence leaked into global state without discharge",
                    "action.scope_effect",
                    effect,
                    "a valid discharge preserving the exact assumption context",
                )
            elif discharge is None:
                self._unk("SCOPE", "scope-discharge evidence is unresolved", "action.scope_effect.discharge_evidence_id")

    def _preconditions(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        created = {item.get("id") for item in action.get("obligations_created", [])}
        after_obligations = after.get("obligations", {})
        for index, precondition in enumerate(action.get("preconditions", [])):
            if not precondition.get("required", True):
                continue
            status = precondition.get("status")
            path = f"action.preconditions[{index}]"
            if status == "SATISFIED":
                valid = self._valid_evidence(evidence, precondition.get("evidence_id"))
                if valid is False:
                    self._bad("PRECONDITIONS", "a required precondition lacks valid evidence", path + ".evidence_id")
                elif valid is None:
                    self._unk("PRECONDITIONS", "precondition evidence is unresolved", path + ".evidence_id")
            elif status == "DEFERRED":
                obligation_id = precondition.get("obligation_id")
                if not precondition.get("deferable") or obligation_id not in created or obligation_id not in after_obligations:
                    self._bad("PRECONDITIONS", "a precondition was deferred without explicit persistent debt", path, precondition, "a declared open obligation")
            elif status in {"UNKNOWN", "UNRESOLVED"}:
                self._unk("PRECONDITIONS", "required applicability is unresolved", path + ".status", status, "SATISFIED or explicitly DEFERRED")
            else:
                self._bad("PRECONDITIONS", "a failed or missing required precondition does not license execution", path + ".status", status, "SATISFIED or explicitly DEFERRED")

    def _obligations(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        before_obs = before.get("obligations", {})
        after_obs = after.get("obligations", {})
        discharged = {item.get("id"): item for item in action.get("obligations_discharged", [])}
        for obligation_id, obligation in before_obs.items():
            if obligation.get("status") != "OPEN":
                continue
            if obligation_id in after_obs and after_obs[obligation_id].get("status") == "OPEN":
                continue
            discharge = discharged.get(obligation_id)
            if discharge is None:
                self._bad("OBLIGATIONS", "an open obligation disappeared silently", f"state_after.obligations.{obligation_id}", None, "OPEN or explicitly discharged")
                continue
            valid = self._valid_evidence(evidence, discharge.get("evidence_id"))
            if valid is False:
                self._bad("OBLIGATIONS", "obligation discharge lacks valid evidence", "action.obligations_discharged")
            elif valid is None:
                self._unk("OBLIGATIONS", "obligation-discharge evidence is unresolved", "action.obligations_discharged")
        for index, created in enumerate(action.get("obligations_created", [])):
            obligation_id = created.get("id")
            after_obligation = after_obs.get(obligation_id)
            if after_obligation is None or after_obligation.get("status") != "OPEN":
                self._bad("OBLIGATIONS", "new proof debt is not persisted as OPEN", f"action.obligations_created[{index}]", obligation_id, "an OPEN state_after obligation")

    def _candidates(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        candidates_before = before.get("candidates", {})
        candidates_after = after.get("candidates", {})
        effect = action.get("candidate_effect", {})
        candidate_id = effect.get("candidate_id")
        if not candidate_id:
            return
        old = candidates_before.get(candidate_id)
        new = candidates_after.get(candidate_id)
        if old is None or new is None:
            self._bad("CANDIDATES", "candidate transition does not preserve candidate identity", "action.candidate_effect.candidate_id", candidate_id, "candidate present before and after")
            return
        if old.get("status") in {"UNKNOWN", "UNRESOLVED"} or new.get("status") in {"UNKNOWN", "UNRESOLVED"}:
            self._unk("CANDIDATES", "candidate lifecycle status is unresolved", "state_after.candidates.<id>.status")
            return
        if new.get("status") == "VERIFIED" and old.get("status") != "VERIFIED":
            valid = self._valid_evidence(evidence, effect.get("evidence_id"))
            record = evidence.get(effect.get("evidence_id"), {})
            constraints = set(old.get("constraint_ids", []))
            checked = set(record.get("checked_constraints", []))
            legal = (
                action.get("operation") == "VERIFY_CANDIDATE"
                and valid is True
                and record.get("kind") == "CANDIDATE_CHECK"
                and record.get("candidate_id") == candidate_id
                and constraints <= checked
            )
            if valid is None:
                self._unk("CANDIDATES", "candidate verification evidence is unresolved", "action.candidate_effect.evidence_id")
            elif not legal:
                self._bad("CANDIDATES", "a candidate was promoted without an independent check of every original constraint", "action.candidate_effect", effect, "VERIFY_CANDIDATE plus valid matching evidence")

    def _branch_join(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        effect = action.get("branch_effect", {})
        if effect.get("kind") != "JOIN":
            return
        required = effect.get("branch_ids", [])
        branches = before.get("branches", {})
        output = self._claims(after).get(action.get("output_id"), {})
        if any(branches.get(branch_id, {}).get("status") in {"UNKNOWN", "UNRESOLVED"} for branch_id in required):
            self._unk("BRANCH_JOIN", "branch completion is unresolved", "state_before.branches")
            return
        incomplete = [branch_id for branch_id in required if branches.get(branch_id, {}).get("status") != "CLOSED"]
        valid_coverage = self._valid_evidence(evidence, effect.get("coverage_evidence_id"))
        conclusions = [branches.get(branch_id, {}).get("conclusion") for branch_id in required]
        if valid_coverage is None:
            self._unk("BRANCH_JOIN", "partition coverage is unresolved", "action.branch_effect.coverage_evidence_id")
        elif incomplete or valid_coverage is False or not required or any(value != output.get("proposition") for value in conclusions):
            self._bad(
                "BRANCH_JOIN",
                "global join requires certified coverage, every branch closed, and the same licensed conclusion in each branch",
                "action.branch_effect",
                {"incomplete": incomplete, "coverage": valid_coverage, "conclusions": conclusions},
                output.get("proposition"),
            )

    def _warrant(self, before: dict[str, Any], action: dict[str, Any], evidence: dict[str, Any]) -> None:
        warrant = action.get("warrant", {})
        evidence_id = warrant.get("evidence_id")
        valid = self._valid_evidence(evidence, evidence_id)
        record = evidence.get(evidence_id, {})
        dependencies = action.get("dependencies", [])
        if valid is None:
            self._unk("WARRANT", "warrant evidence is unresolved", "action.warrant.evidence_id")
        elif valid is False:
            self._bad("WARRANT", "the named warrant has no valid evidence", "action.warrant.evidence_id", evidence_id, "VALID evidence")
        elif record.get("supports_rule") != warrant.get("rule") or record.get("premise_ids", []) != dependencies:
            self._bad(
                "WARRANT",
                "warrant identity or premise envelope does not match its evidence",
                "action.warrant",
                {"rule": warrant.get("rule"), "premises": dependencies},
                {"rule": record.get("supports_rule"), "premises": record.get("premise_ids", [])},
            )

    def _epistemic(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        action: dict[str, Any],
        evidence: dict[str, Any],
    ) -> None:
        output = self._claims(after).get(action.get("output_id"), {})
        if output.get("status") != "VERIFIED":
            return
        effect = action.get("epistemic_effect", {})
        valid = self._valid_evidence(evidence, effect.get("evidence_id"))
        record = evidence.get(effect.get("evidence_id"), {})
        open_mandatory = [
            obligation_id
            for obligation_id, obligation in after.get("obligations", {}).items()
            if obligation.get("status") == "OPEN" and obligation.get("mandatory", True)
            and action.get("output_id") in obligation.get("dependencies", [])
        ]
        if valid is None:
            self._unk("EPISTEMIC_STATUS", "verification evidence is unresolved", "action.epistemic_effect.evidence_id")
        elif valid is False or not record.get("trusted") or effect.get("to_status") != "VERIFIED" or open_mandatory:
            self._bad(
                "EPISTEMIC_STATUS",
                "VERIFIED is not licensed by trusted checked evidence with all mandatory debt closed",
                "action.epistemic_effect",
                {"evidence_valid": valid, "trusted": record.get("trusted"), "open_mandatory": open_mandatory},
                "trusted VALID evidence and no open mandatory obligations",
            )

    def _goal_discharge(self, before: dict[str, Any], after: dict[str, Any], action: dict[str, Any]) -> None:
        effect = action.get("goal_effect", {})
        if effect.get("kind") != "DISCHARGE":
            return
        goal_id = effect.get("goal_id")
        goal_before = before.get("goals", {}).get(goal_id)
        goal_after = after.get("goals", {}).get(goal_id)
        output = self._claims(after).get(action.get("output_id"), {})
        if goal_before is None or goal_after is None:
            self._bad("GOAL_DISCHARGE", "goal identity is not preserved", "action.goal_effect.goal_id", goal_id, "an existing goal")
            return
        if goal_before.get("status") in {"UNKNOWN", "UNRESOLVED"} or output.get("status") in {"UNKNOWN", "UNRESOLVED"}:
            self._unk("GOAL_DISCHARGE", "goal support is unresolved", "action.goal_effect")
            return
        if (
            goal_before.get("status") != "OPEN"
            or goal_after.get("status") != "DISCHARGED"
            or output.get("status") != "VERIFIED"
            or output.get("proposition") != goal_before.get("proposition")
        ):
            self._bad(
                "GOAL_DISCHARGE",
                "a goal may close only from a VERIFIED claim of the exact target",
                "action.goal_effect",
                {"goal_before": goal_before, "goal_after": goal_after, "output": output},
                "OPEN -> DISCHARGED with exact VERIFIED support",
            )

    @staticmethod
    def _is_subtype(actual: str, expected: str) -> bool:
        if actual == expected:
            return True
        seen: set[str] = set()
        current = actual
        while current in _DOMAIN_PARENTS and current not in seen:
            seen.add(current)
            current = _DOMAIN_PARENTS[current]
            if current == expected:
                return True
        return False

    def _type_domain(self, before: dict[str, Any], action: dict[str, Any]) -> None:
        claims = self._claims(before)
        expected = action.get("typing", {}).get("input_domains", {})
        for claim_id, wanted in expected.items():
            actual = claims.get(claim_id, {}).get("domain")
            if actual in {None, "UNKNOWN", "UNRESOLVED"}:
                self._unk("TYPE_DOMAIN", "input domain is unresolved", f"state_before.claims.{claim_id}.domain", actual, wanted)
            elif not self._is_subtype(actual, wanted):
                self._bad("TYPE_DOMAIN", "input does not inhabit the operation's required domain", f"state_before.claims.{claim_id}.domain", actual, wanted)

    def _exact_state_change(self, before: dict[str, Any], after: dict[str, Any], action: dict[str, Any]) -> None:
        """Reject unrelated mutations; classify them by the affected semantic axis."""
        output_id = action.get("output_id")
        before_claims = self._claims(before)
        after_claims = self._claims(after)
        for claim_id, claim in before_claims.items():
            if after_claims.get(claim_id) != claim:
                self._bad("DEPENDENCY", "an existing claim changed without a licensed state effect", f"state_after.claims.{claim_id}")
        additions = set(after_claims) - set(before_claims)
        allowed = {output_id} if output_id else set()
        if additions != allowed:
            self._bad("DEPENDENCY", "state_after contains unrelated claim additions", "state_after.claims", sorted(additions), sorted(allowed))


def check_case(case: dict[str, Any]) -> dict[str, Any]:
    """Convenience API used by tests, scorers, and future builder comparisons."""

    return ReferenceChecker().check(case).to_dict()

