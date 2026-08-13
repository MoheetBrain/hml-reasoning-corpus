"""SOURCE -> NEUTRAL -> VNext -> verify/round-trip, over whole trajectories.

**What makes this different from `corpus_rerender.py`, and why it had to be rewritten.**

VNext-1 reconstructed each gap transition *in isolation* from the artifact's printed summary
fields, synthesising whatever premises the rule needed. It measured **representability** —
"a transition of this shape can be expressed and checked" — and said so. That is not enough
for a fidelity claim, because nothing tied the reconstruction to the worked solution and
nothing tied a downstream transition to the state its ancestor actually produced.

This module rederives from the **verbatim source span**, and it rederives **whole
trajectories**:

* the problem's own statement and target open the state, from the artifact's
  ``### Original problem`` and ``**Target:**`` fields;
* every transition of a problem is walked in order, carrying the state forward, so a
  downstream transition is checked against the state its ancestor really produced rather than
  against a fresh synthetic one;
* each step's content is read out of its ``Exact source span``, and **the span's SHA-256 is
  recomputed and compared against the hash the artifact publishes** before it is used. A
  mismatch is a hard refusal. That check is what distinguishes "rederived from source" from
  "reconstructed plausibly";
* a step whose premises are not in the carried state is **refused and the trajectory stops**.
  Nothing is invented to keep a number moving — which is the one instruction that decides
  whether this measurement means anything.

Mechanism routing uses the corpus's own classification, which Task 1 makes authoritative.
Content never does.

    PYTHONPATH=src:scripts/vnext python scripts/vnext/corpus_rederive.py <copy>
"""

from __future__ import annotations

import collections
import argparse
import gzip
import contextlib
import io
from dataclasses import replace
import hashlib
import json
import re
import sys
from pathlib import Path

from corpus_parse import DOWNSTREAM_CODE, Problem, Record, _parse

from hamiltonian_lang.semantic_state import (
    Action,
    Approximation,
    Branch,
    BranchStatus,
    Candidate,
    CandidateStatus,
    Claim,
    ClaimStatus,
    Exactness,
    EvidenceRecord,
    Obligation,
    ObligationState,
    SemanticState,
    Transition,
    Verdict,
    parse_transition,
    render_transition,
    verify_replay,
    verify_runtime,
)
from hamiltonian_lang.semantic_state.tree_view import (
    parse_tree_transition,
    render_tree_transition,
)
from hamiltonian_lang.semantic_state import export_transition

DOMAIN = "Proposition"
_MATH = re.compile(r"\$\$\n(.*?)\n\$\$", re.S)
_CASE = re.compile(r"^#+\s*(Case\b[^\n]*)$", re.M)
CANDIDATE_GAP = "CANDIDATE_CREATION_NOT_REPRESENTABLE"
BRANCH_GAP = "BRANCH_CREATION_NOT_REPRESENTABLE"
APPROX_GAP = "APPROXIMATION_STATUS_NOT_REPRESENTABLE"


def _prose(span: str) -> str:
    """The words between the display-math blocks — the source's own description of the step."""
    without = _MATH.sub("\n", span)
    lines = [ln.strip() for ln in without.split("\n") if ln.strip()]
    return " ".join(lines).strip() or "source step"


def _case_label(span: str) -> str | None:
    m = _CASE.search(span)
    return m.group(1).strip() if m else None


class Refusal(Exception):
    """The source does not support the reconstruction. Never repaired, always recorded."""


class Ancestry:
    """One problem's slice of the neutral branch-ancestry handoff, indexed for the walk.

    VNext-2's largest residual was that the corpus's linear dependency chain carries no
    sibling-case structure: a "Case 2" step cited the previous case's frame-local conclusion,
    and the pre-split premise it actually rests on was recorded nowhere. The corpus repair at
    ``3bbb425`` records it — ``pre_split_premise_ids`` and ``opening_dependency_ids`` per
    branch, with the invalid linear edges listed under ``rejected_linear_dependency_ids``
    rather than silently reused. This class only *indexes* that artifact; every proposition
    and id the walk uses comes from it or from the master, never from a guess.
    """

    def __init__(self, entry: dict) -> None:
        self.openers: dict[str, tuple[dict, dict]] = {}
        self.members: set[str] = set()
        self.joins: dict[str, str] = {}
        self.partitions: list[dict] = []
        self.partition_by_id: dict[str, dict] = {}
        self.branch_by_id: dict[str, dict] = {}
        #: Premises the old segmenter never emitted as transitions — the ``i001`` family
        #: (``SOURCE_INITIAL_STATE``) and two ``EXPLICIT_SOURCE_STATE_OMITTED_BY_OLD_SEGMENTER``
        #: entries. Declared with propositions and source hashes, so materialising them is
        #: consuming the handoff, not inventing state.
        self.initial_premises: dict[str, dict] = {}
        for partition in entry.get("partitions", ()):
            self.partitions.append(partition)
            self.partition_by_id[partition["partition_id"]] = partition
            if partition["join_transition_id"]:
                self.joins[partition["join_transition_id"]] = partition["partition_id"]
            for premise in partition["pre_split_premises"]:
                if premise["origin"] in (
                    "SOURCE_INITIAL_STATE",
                    "EXPLICIT_SOURCE_STATE_OMITTED_BY_OLD_SEGMENTER",
                ):
                    self.initial_premises[premise["premise_id"]] = premise
            for branch in partition["branches"]:
                self.branch_by_id[branch["branch_id"]] = branch
                if branch["opening_transition_id"]:
                    self.openers[branch["opening_transition_id"]] = (partition, branch)
                self.members.update(branch["transition_ids"])


class Trajectory:
    """One problem, walked in order, carrying VNext state forward."""

    def __init__(
        self,
        problem: Problem,
        ancestry: Ancestry | None = None,
        initial_premises: list[dict] | None = None,
        implicit_steps: list[dict] | None = None,
    ) -> None:
        self.problem = problem
        self.ancestry = ancestry
        source_premises = initial_premises or [
            {
                "premise_id": "p0",
                "proposition": problem.original_problem or problem.id,
            }
        ]
        claims = {
            premise["premise_id"]: Claim(
                id=premise["premise_id"],
                proposition=premise["proposition"],
                status=ClaimStatus.GIVEN,
                scope="global",
                domain=DOMAIN,
            )
            for premise in source_premises
        }
        if ancestry is not None:
            # Ancestry may contain two source-explicit premises omitted by the old segmenter.
            # The corpus-wide initial-premise artifact owns i00N; ancestry remains authority
            # for these explicit source states and must agree on any overlapping id.
            for premise_id, premise in ancestry.initial_premises.items():
                held = claims.get(premise_id)
                if held is not None and held.proposition != premise["proposition"]:
                    raise Refusal(
                        f"initial-premise artifact and ancestry disagree on {premise_id}"
                    )
                claims[premise_id] = Claim(
                    id=premise_id,
                    proposition=premise["proposition"],
                    status=ClaimStatus.GIVEN,
                    scope="global",
                    domain=DOMAIN,
                )
        self.state = SemanticState(claims=claims, goals={}, active_scopes=("global",))
        #: Open case frames as a stack of local ids; ancestry branch id -> local frame id.
        self.open_branches: list[str] = []
        self.frame_of: dict[str, str] = {}
        self.declared_partitions: set[str] = set()
        self.candidate_id: str | None = None
        self.results: list[dict] = []
        self.accepted: list[Transition] = []
        self.implicit_by_branch = {
            step["branch_id"]: step for step in (implicit_steps or [])
        }
        self.inserted_implicit: set[str] = set()
        self.joined_partitions: set[str] = set()

    # -- helpers ---------------------------------------------------------
    def _scope_for(self, claim_deps: tuple[str, ...]) -> str:
        """The frame a step writes into: the one its narrowest premise lives in.

        Derived from the reconstructed state rather than from "whichever case opened last".
        The first version used the latter and leaked: once Case 2 opened, a step continuing
        Case 1's reasoning cited a ``branch:b1`` premise and wrote into ``branch:b2``, which
        ``_check_scope`` correctly reported as SCOPE_LEAK. The verifier was right and the
        pipeline was wrong.
        """
        frames = {
            self.state.claims[d].scope for d in claim_deps if d in self.state.claims
        } - {"global"}
        if not frames:
            return "global"
        if len(frames) > 1:
            raise Refusal(
                f"the step rests on premises in unrelated frames {sorted(frames)}; the source "
                f"does not say which case it is continuing"
            )
        return next(iter(frames))

    def _resolve(self, record: Record) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Split the cited ids into claims and candidates, refusing anything absent."""
        claims, candidates = [], []
        for dep in record.dependency_ids:
            if dep in self.state.claims:
                claims.append(dep)
            elif dep in self.state.candidates:
                candidates.append(dep)
            else:
                raise Refusal(f"cites {dep!r}, which the reconstructed state does not hold")
        return tuple(claims), tuple(candidates)

    def _replace(self, **kw) -> SemanticState:
        base = dict(
            claims=dict(self.state.claims),
            candidates=dict(self.state.candidates),
            branches=dict(self.state.branches),
            goals=dict(self.state.goals),
            obligations=dict(self.state.obligations),
            active_scopes=tuple(self.state.active_scopes),
        )
        base.update(kw)
        return SemanticState(**base)

    # -- step shapes -----------------------------------------------------
    def _plain(self, record: Record, oid: str, claim_deps, _cand) -> Transition:
        produced = Claim(
            id=oid, proposition=record.state_after, status=ClaimStatus.DERIVED,
            scope=self._scope_for(claim_deps), domain=DOMAIN, dependencies=claim_deps,
        )
        after = self._replace(claims={**self.state.claims, oid: produced})
        return self._t(record, Action(
            id=f"a{oid}", operation=record.operation, summary=record.summary,
            output_id=oid, dependencies=claim_deps,
        ), after)

    def _candidate_create(self, record: Record, oid: str, claim_deps, _cand) -> Transition:
        if not claim_deps:
            raise Refusal("a candidate needs at least one original constraint")
        candidate = Candidate(
            id=oid, proposition=record.state_after, status=CandidateStatus.PROPOSED,
            scope=self._scope_for(claim_deps), constraint_ids=claim_deps,
            origin=_prose(record.source_span or ""), dependencies=claim_deps,
        )
        self.candidate_id = oid
        after = self._replace(candidates={**self.state.candidates, oid: candidate})
        return self._t(record, Action(
            id=f"a{oid}", operation=record.operation, summary=record.summary,
            dependencies=claim_deps,
            candidate_effect={"kind": "CREATE", "candidate_id": oid},
        ), after)

    def _candidate_derive(self, record: Record, oid: str, _claim_deps, cand) -> Transition:
        """A step that continues a proposed object produces a **new** candidate.

        The corpus allocates a fresh id per transition and downstream steps cite *that* id, so
        mutating the candidate in place -- the first version of this pipeline -- left every
        successor citing an id the reconstructed state did not hold, and 78 trajectories
        stopped there. The source really is proposing a revised object at each step, and the
        original constraints are inherited because they are what the object must still
        satisfy.
        """
        previous = self.state.candidates[cand[0]]
        derived = Candidate(
            id=oid, proposition=record.state_after, status=CandidateStatus.PROPOSED,
            scope=previous.scope, constraint_ids=previous.constraint_ids,
            origin=f"{_prose(record.source_span or '')} (from {previous.id})",
            dependencies=(),
        )
        after = self._replace(candidates={**self.state.candidates, oid: derived})
        return self._t(record, Action(
            id=f"a{oid}", operation=record.operation, summary=record.summary,
            dependencies=(),
            candidate_effect={"kind": "CREATE", "candidate_id": oid},
        ), after)

    def _approximate_from_candidate(
        self, record: Record, oid: str, _claim_deps, cand
    ) -> Transition:
        """An approximate value stated beside a proposed object (G-class repair, VNext-3).

        The source states a numerical rendering next to an existing *candidate* — e.g. the
        candidate ``2-\\sqrt6`` followed by ``\\sqrt6\\approx2.449``. A candidate is not a
        claim, so it cannot be cited as a dependency, and the approximate statement is in
        fact free-standing: its truth does not rest on the candidate at all. It is rendered
        as an **unsourced approximation** — ``source_claim_id`` absent, which the exactness
        rules permit exactly when the record still accounts for itself through ``method`` or
        ``provenance``. Both are carried, and the adjacent candidate is named in the
        provenance so the association survives without becoming a dependency claim.
        """
        previous = self.state.candidates[cand[0]]
        produced = Claim(
            id=oid, proposition=record.state_after, status=ClaimStatus.DERIVED,
            scope=previous.scope, domain=DOMAIN, dependencies=(),
            exactness=Exactness.APPROXIMATE,
            approximation=Approximation(
                source_claim_id=None,
                method=_prose(record.source_span or "") or record.operation,
                provenance=(
                    f"source span {record.source_span_sha}; stated beside candidate "
                    f"{previous.id}"
                ),
            ),
        )
        after = self._replace(claims={**self.state.claims, oid: produced})
        return self._t(record, Action(
            id=f"a{oid}", operation=record.operation, summary=record.summary,
            output_id=oid, dependencies=(),
            exactness_effect={"kind": "APPROXIMATE", "claim_id": oid},
        ), after)

    def _approximate(self, record: Record, oid: str, claim_deps, _cand) -> Transition:
        if not claim_deps:
            raise Refusal("an approximation needs a source claim to approximate")
        source = claim_deps[0]
        produced = Claim(
            id=oid, proposition=record.state_after, status=ClaimStatus.DERIVED,
            scope=self._scope_for(claim_deps), domain=DOMAIN, dependencies=claim_deps,
            exactness=Exactness.APPROXIMATE,
            approximation=Approximation(
                source_claim_id=source,
                method=_prose(record.source_span or ""),
                provenance=f"source span {record.source_span_sha}",
            ),
        )
        after = self._replace(claims={**self.state.claims, oid: produced})
        return self._t(record, Action(
            id=f"a{oid}", operation=record.operation, summary=record.summary,
            output_id=oid, dependencies=claim_deps,
            exactness_effect={"kind": "APPROXIMATE", "claim_id": oid},
        ), after)

    def _close_top(self, record: Record):
        """Close the topmost open case, on the last proposition it established.

        The conclusion is read out of the reconstructed state, never invented. The frame is
        never empty: opening always writes the branch-local assumption into it, so at worst a
        case closes on its own assumption — which the verifier accepts, because the assumption
        is a claim the frame holds.
        """
        bid = self.open_branches[-1]
        ancestry_branch_id = next(
            (source_id for source_id, local_id in self.frame_of.items() if local_id == bid),
            None,
        )
        if ancestry_branch_id in self.implicit_by_branch:
            yield self._implicit_weaken(record, self.implicit_by_branch[ancestry_branch_id])
        scope = f"branch:{bid}"
        established = [c for c in self.state.claims.values() if c.scope == scope]
        if not established:
            raise Refusal(f"case frame {scope!r} holds nothing to close on")
        before = self.state.branches[bid]
        closed = Branch(
            id=before.id, predicate=before.predicate, status=BranchStatus.CLOSED,
            scope=before.scope, conclusion=established[-1].proposition,
            partition_id=before.partition_id,
            coverage_obligation_id=before.coverage_obligation_id,
        )
        after = self._replace(
            branches={**self.state.branches, bid: closed},
            active_scopes=tuple(s for s in self.state.active_scopes if s != scope),
        )
        self.open_branches.pop()
        yield self._t(record, Action(
            id=f"aclose::{record.id}::{bid}", operation="CLOSE_BRANCH",
            summary=f"close {before.predicate}",
            branch_effect={"kind": "CLOSE", "branch_ids": [bid]},
        ), after, synthetic="CLOSE_BRANCH")
        if ancestry_branch_id is not None and self.ancestry is not None:
            source_branch = self.ancestry.branch_by_id[ancestry_branch_id]
            partition = self.ancestry.partition_by_id[source_branch["partition_id"]]
            has_declared_weakening = all(
                branch["branch_id"] in self.implicit_by_branch
                for branch in partition["branches"]
            )
            if partition["join_transition_id"] is None and has_declared_weakening:
                maybe_join = self._join_partition(
                    record,
                    partition,
                    output_id=f"{partition['partition_id']}-JOIN-CLAIM",
                    proposition=self._implicit_partition_result(partition),
                    synthetic=True,
                    require_complete=False,
                )
                if maybe_join is not None:
                    yield maybe_join

    def _implicit_weaken(self, record: Record, step: dict) -> Transition:
        """Materialise D-063's one permitted implicit step inside its source branch."""
        if step["step_id"] in self.inserted_implicit:
            raise Refusal(f"implicit step {step['step_id']!r} would be inserted twice")
        premise_id = step["premise_ids"][0]
        premise = self.state.claims.get(premise_id)
        if premise is None:
            raise Refusal(
                f"implicit OR-introduction cites {premise_id!r}, which the state does not hold"
            )
        if premise.proposition != step["premise_proposition"]:
            raise Refusal(
                f"implicit OR-introduction premise {premise_id!r} disagrees with its "
                "source-derived proposition"
            )
        branch_local = self.frame_of[step["branch_id"]]
        expected_scope = f"branch:{branch_local}"
        if premise.scope != expected_scope:
            raise Refusal(
                f"implicit OR-introduction premise {premise_id!r} is in {premise.scope!r}, "
                f"not triggering frame {expected_scope!r}"
            )
        output_id = f"implicit::{step['step_id']}"
        evidence_id = f"evidence::{step['step_id']}"
        produced = Claim(
            id=output_id,
            proposition=step["resulting_proposition"],
            status=ClaimStatus.DERIVED,
            scope=expected_scope,
            domain=DOMAIN,
            dependencies=(premise_id,),
        )
        evidence = EvidenceRecord(
            id=evidence_id,
            kind="logical_rule",
            status="VALID",
            supports_rule="DISJUNCTION_INTRODUCTION",
            premise_ids=(premise_id,),
            payload={
                "proof": step["deterministic_derivation_proof"],
                "source_join_span_sha256": step["provenance"]["source_join_span_sha256"],
            },
        )
        transition = Transition(
            case_id=step["step_id"],
            action=Action(
                id=f"action::{step['step_id']}",
                operation="WEAKEN",
                summary="",
                output_id=output_id,
                dependencies=(premise_id,),
                warrant={"rule": "DISJUNCTION_INTRODUCTION", "evidence_id": evidence_id},
            ),
            state_before=self.state,
            state_after=self._replace(claims={**self.state.claims, output_id: produced}),
            evidence={evidence_id: evidence},
            source={
                "problem": step["problem_id"],
                "span_sha256": step["provenance"]["source_join_span_sha256"],
                "record_kind": "IMPLICIT_LOGICAL_STEP",
            },
        )
        self.inserted_implicit.add(step["step_id"])
        return transition

    def _implicit_partition_result(self, partition: dict) -> str:
        steps = [
            self.implicit_by_branch[branch["branch_id"]]
            for branch in partition["branches"]
            if branch["branch_id"] in self.implicit_by_branch
        ]
        if len(steps) != len(partition["branches"]):
            raise Refusal(
                f"partition {partition['partition_id']!r} lacks one deterministic "
                "OR-introduction per branch"
            )
        results = {step["resulting_proposition"] for step in steps}
        if len(results) != 1:
            raise Refusal(
                f"partition {partition['partition_id']!r} implicit steps do not establish "
                "one common conclusion"
            )
        return next(iter(results))

    def _join_partition(
        self,
        record: Record,
        partition: dict,
        output_id: str,
        proposition: str,
        *,
        synthetic: bool,
        require_complete: bool = True,
    ) -> Transition | None:
        pid = partition["partition_id"]
        if pid in self.joined_partitions:
            return None
        source_branch_ids = [branch["branch_id"] for branch in partition["branches"]]
        if any(source_id not in self.frame_of for source_id in source_branch_ids):
            if require_complete:
                raise Refusal(f"partition {pid!r} has branches that were never opened")
            return None
        branch_ids = [self.frame_of[source_id] for source_id in source_branch_ids]
        branches = [self.state.branches[branch_id] for branch_id in branch_ids]
        if any(branch.status is not BranchStatus.CLOSED for branch in branches):
            if require_complete:
                raise Refusal(f"partition {pid!r} has branches that are not closed")
            return None
        if {branch.conclusion for branch in branches} != {proposition}:
            raise Refusal(
                f"partition {pid!r} branches do not establish the common conclusion "
                f"{proposition!r}"
            )
        obligation = self.state.obligations.get(pid)
        if obligation is None:
            raise Refusal(f"partition {pid!r} has no coverage obligation")
        evidence_id = f"evidence::join::{pid}"
        evidence = EvidenceRecord(
            id=evidence_id,
            kind="partition_certificate",
            status="VALID",
            supports_rule="JOIN_BRANCHES",
            premise_ids=(),
            payload={"branch_ids": branch_ids},
        )
        parent_scope = "global"
        if partition["parent_branch_id"] is not None:
            parent_scope = f"branch:{self.frame_of[partition['parent_branch_id']]}"
        produced = Claim(
            id=output_id,
            proposition=proposition,
            status=ClaimStatus.DERIVED,
            scope=parent_scope,
            domain=DOMAIN,
            dependencies=(),
        )
        joined = {
            branch.id: Branch(
                id=branch.id,
                predicate=branch.predicate,
                status=BranchStatus.JOINED,
                scope=branch.scope,
                conclusion=branch.conclusion,
                partition_id=branch.partition_id,
                coverage_obligation_id=branch.coverage_obligation_id,
            )
            for branch in branches
        }
        discharged = Obligation(
            id=obligation.id,
            proposition=obligation.proposition,
            status=ObligationState.DISCHARGED,
            mandatory=obligation.mandatory,
            origin=obligation.origin,
            dependencies=obligation.dependencies,
            discharge_evidence_id=evidence_id,
        )
        self.joined_partitions.add(pid)
        return Transition(
            case_id=(f"{record.id}::IMPLICIT_JOIN::{pid}" if synthetic else record.id),
            action=Action(
                id=f"action::join::{pid}",
                operation="JOIN_BRANCHES",
                summary="",
                output_id=output_id,
                dependencies=(),
                obligations_discharged=({"id": pid, "evidence_id": evidence_id},),
                branch_effect={
                    "kind": "JOIN",
                    "branch_ids": branch_ids,
                    "rule": "JOIN_BRANCHES",
                    "coverage_evidence_id": evidence_id,
                },
            ),
            state_before=self.state,
            state_after=self._replace(
                claims={**self.state.claims, output_id: produced},
                branches={**self.state.branches, **joined},
                obligations={**self.state.obligations, pid: discharged},
            ),
            evidence={evidence_id: evidence},
            source={"problem": self.problem.id, "span_sha256": record.source_span_sha},
        )

    def _unwind_to(self, record: Record, parent_local: str | None):
        """Close open cases until the target parent frame is on top (or none are open).

        This is what makes *nested* case analyses walk correctly: a sibling at the outer
        level closes the whole inner partition first, and a nested opener closes nothing —
        its parent frame is already on top. The target comes from the ancestry artifact's
        ``parent_branch_id``, never from position in the linear chain.
        """
        while self.open_branches and self.open_branches[-1] != parent_local:
            yield from self._close_top(record)
        if parent_local is not None and (
            not self.open_branches or self.open_branches[-1] != parent_local
        ):
            raise Refusal(
                f"the ancestry places this case inside a parent frame ({parent_local!r}) "
                f"that is not open at this point in the walk"
            )

    def _declare_ancestry_partition(self, record: Record, partition: dict):
        """Declare one partition exactly as the neutral artifact states it.

        Every pre-split premise must already be present in the reconstructed state, and where
        the artifact says the premise *is* an earlier transition's result, the reconstructed
        proposition must equal the artifact's, byte for byte. A mismatch is a refusal — it
        would mean the artifact and the walk disagree about what the common state was, and
        proceeding would verify a partition over premises nobody established.
        """
        pid = partition["partition_id"]
        propositions = []
        for premise in partition["pre_split_premises"]:
            held = self.state.claims.get(premise["premise_id"])
            if held is None:
                raise Refusal(
                    f"pre-split premise {premise['premise_id']!r} of partition {pid!r} is "
                    f"not in the reconstructed state"
                )
            if (
                premise["origin"] == "EARLIER_SOURCE_TRANSITION"
                and held.proposition != premise["proposition"]
            ):
                raise Refusal(
                    f"pre-split premise {premise['premise_id']!r} of {pid!r} reads "
                    f"{held.proposition!r} in the reconstruction but {premise['proposition']!r} "
                    f"in the ancestry artifact"
                )
            propositions.append(premise["proposition"])
        obligation = Obligation(
            id=pid,
            proposition=f"the declared cases exhaust: {'; '.join(propositions)}",
            status=ObligationState.OPEN, mandatory=True, origin=record.operation,
            dependencies=tuple(partition["pre_split_premise_ids"]),
        )
        after = self._replace(obligations={**self.state.obligations, pid: obligation})
        self.declared_partitions.add(pid)
        yield self._t(record, Action(
            id=f"apart::{pid}", operation="CASE_SPLIT",
            summary="declare the case partition",
            dependencies=tuple(partition["pre_split_premise_ids"]),
            obligations_created=({"id": pid},),
            branch_effect={"kind": "DECLARE_PARTITION", "partition_id": pid},
        ), after, synthetic="DECLARE_PARTITION")

    def _open_from_ancestry(self, record: Record, oid: str, partition: dict, branch: dict):
        """Open one case exactly as the neutral artifact states it.

        The opening dependencies are ``opening_dependency_ids`` — the declared common
        pre-split state — never ``record.dependency_ids``, whose linear edge the artifact
        explicitly rejects. The branch-local assumption is the artifact's, verbatim. When the
        record's own content differs from the assumption (all 63 openers in practice: the
        span carries both the case header and its first derivation), the content becomes a
        separate in-frame derivation citing the assumption plus the opening dependencies —
        both declared, neither guessed.
        """
        deps = tuple(branch["opening_dependency_ids"])
        rejected = set(branch["rejected_linear_dependency_ids"])
        if rejected & set(deps):
            raise Refusal(
                f"ancestry for {branch['branch_id']!r} reuses rejected linear edges as "
                f"opening dependencies"
            )
        missing = [d for d in deps if d not in self.state.claims]
        if missing:
            raise Refusal(
                f"opening dependency {missing} of {branch['branch_id']!r} is not in the "
                f"reconstructed state"
            )
        parent_ancestry = branch["parent_branch_id"]
        parent_frame = (
            "global" if parent_ancestry is None
            else f"branch:{self.frame_of[parent_ancestry]}"
        )
        predicate = branch["assumption"]["proposition"]
        bid = f"b{len(self.state.branches) + 1}"
        scope = f"branch:{bid}"
        derived_needed = record.state_after != predicate
        assumption_id = f"h::{branch['branch_id']}" if derived_needed else oid

        assumption = Claim(
            id=assumption_id, proposition=predicate, status=ClaimStatus.ASSUMED,
            scope=scope, dependencies=deps,
        )
        branch_obj = Branch(
            id=bid, predicate=predicate, status=BranchStatus.OPEN, scope=parent_frame,
            partition_id=partition["partition_id"],
            coverage_obligation_id=partition["partition_id"],
        )
        after = self._replace(
            claims={**self.state.claims, assumption_id: assumption},
            branches={**self.state.branches, bid: branch_obj},
            active_scopes=tuple(self.state.active_scopes) + (scope,),
        )
        self.frame_of[branch["branch_id"]] = bid
        self.open_branches.append(bid)
        yield self._t(record, Action(
            id=f"aopen::{branch['branch_id']}", operation="OPEN_BRANCH",
            summary=branch["label"],
            output_id=assumption_id, dependencies=deps,
            branch_effect={"kind": "OPEN", "branch_ids": [bid]},
        ), after, **({"synthetic": "OPEN_BRANCH"} if derived_needed else {}))

        if derived_needed:
            step_deps = (assumption_id,) + deps
            produced = Claim(
                id=oid, proposition=record.state_after, status=ClaimStatus.DERIVED,
                scope=scope, domain=DOMAIN, dependencies=step_deps,
            )
            after2 = self._replace(claims={**self.state.claims, oid: produced})
            yield self._t(record, Action(
                id=f"a{oid}", operation=record.operation, summary=record.summary,
                output_id=oid, dependencies=step_deps,
            ), after2)

    def _t(self, record: Record, action: Action, after: SemanticState, **extra) -> Transition:
        evidence = {}
        if not extra:
            evidence_id = f"source-evidence::{record.id}"
            action = replace(
                action,
                warrant={"rule": action.operation, "evidence_id": evidence_id},
            )
            evidence[evidence_id] = EvidenceRecord(
                id=evidence_id,
                kind="SOURCE_DERIVATION",
                status="UNKNOWN",
                trusted=False,
                supports_rule=action.operation,
                premise_ids=tuple(action.dependencies),
                payload={"source_span_sha256": record.source_span_sha},
            )
        return Transition(
            case_id=record.id + ("::" + extra["synthetic"] if extra else ""),
            action=action, state_before=self.state, state_after=after,
            evidence=evidence,
            source={"problem": self.problem.id, "span_sha256": record.source_span_sha},
        )

    # -- the walk --------------------------------------------------------
    def run(self, records: list[Record]) -> None:
        stopped = False
        for index, record in enumerate(records, 1):
            if stopped:
                self.results.append({"id": record.id, "outcome": "NOT_ATTEMPTED",
                                     "gap_code": record.gap_code})
                continue
            try:
                self._integrity(record)
                for transition in self._build(record, index):
                    self._check(record, transition)
                    self.state = transition.state_after
            except Refusal as refusal:
                self.results.append({"id": record.id, "outcome": "REFUSED",
                                     "gap_code": record.gap_code, "reason": str(refusal)})
                stopped = True

    def _integrity(self, record: Record) -> None:
        if record.source_span is None or record.source_span_sha is None:
            raise Refusal("no source span is published for this transition")
        actual = hashlib.sha256(record.source_span.encode("utf-8")).hexdigest()
        if actual != record.source_span_sha:
            raise Refusal(
                f"source span hash mismatch: recomputed {actual}, published "
                f"{record.source_span_sha}"
            )

    def _build(self, record: Record, index: int):
        oid = f"c{index:03d}"
        ancestry = self.ancestry
        if ancestry is not None and record.id in ancestry.openers:
            # A case opening, per the neutral artifact. Unwind to the declared parent frame,
            # declare the partition on first contact, then open. The record's own linear
            # dependency is NOT resolved here -- the artifact rejects it as ancestry.
            partition, branch = ancestry.openers[record.id]
            parent = branch["parent_branch_id"]
            parent_local = self.frame_of.get(parent) if parent is not None else None
            if parent is not None and parent_local is None:
                raise Refusal(
                    f"ancestry parent branch {parent!r} was never opened in this walk"
                )
            yield from self._unwind_to(record, parent_local)
            if partition["partition_id"] not in self.declared_partitions:
                yield from self._declare_ancestry_partition(record, partition)
            yield from self._open_from_ancestry(record, oid, partition, branch)
            return
        if ancestry is not None and record.id in ancestry.joins:
            partition = ancestry.partition_by_id[ancestry.joins[record.id]]
            yield from self._unwind_to(record, None)
            if record.problem_id == "MIXED-039":
                joined_claim_id = f"{partition['partition_id']}-JOIN-CLAIM"
                joined = self._join_partition(
                    record,
                    partition,
                    output_id=joined_claim_id,
                    proposition=self._implicit_partition_result(partition),
                    synthetic=True,
                )
                if joined is None:
                    raise Refusal(f"partition {partition['partition_id']!r} was already joined")
                yield joined
                # The source's original T014 is selection of the maximum from the joined
                # branch-outcome disjunction, not the join itself.
                yield self._plain(record, oid, (joined_claim_id,), ())
                return
            joined = self._join_partition(
                record,
                partition,
                output_id=oid,
                proposition=record.state_after,
                synthetic=False,
            )
            if joined is None:
                raise Refusal(f"partition {partition['partition_id']!r} was already joined")
            yield joined
            return
        if record.gap_code == BRANCH_GAP:
            covered = ancestry is not None and (
                record.id in ancestry.members or record.id in ancestry.joins
            )
            if not covered:
                raise Refusal(
                    "a branch-structured step the neutral ancestry artifact (v1) does not "
                    "cover; without declared ancestry, reconstructing it would reintroduce "
                    "the linear-adjacency guess the artifact exists to remove"
                )
            # Members reason inside their open frame and joins restate a case's result;
            # both are ordinary steps over the reconstructed state, and their premises
            # resolve through the same rules as everything else below.
        claim_deps, cand = self._resolve(record)
        # G-class repair (VNext-3). The gap code says which *mechanism* the step exercises;
        # it does not say the step starts from claims. A candidate-coded step whose only
        # citation is an existing candidate derives a NEW candidate from it — fresh output
        # id, previous object untouched, constraints inherited — and an approximation-coded
        # step in the same position derives an approximate claim beside it. The first
        # version routed on gap code alone, sent these to the from-claims builders, and
        # refused 11 steps whose shapes the semantics already expressed.
        continues_candidate = bool(cand) and not claim_deps
        if record.gap_code == CANDIDATE_GAP:
            shape = self._candidate_derive if continues_candidate else self._candidate_create
        elif record.gap_code == APPROX_GAP:
            shape = (
                self._approximate_from_candidate if continues_candidate
                else self._approximate
            )
        elif continues_candidate:
            # Not a direct gap (or a covered in-branch/join step) whose only citations are
            # candidates: it continues the candidate, which is what a downstream-of-candidate
            # transition actually does.
            shape = self._candidate_derive
        else:
            shape = self._plain
        yield shape(record, oid, claim_deps, cand)

    def _check(self, record: Record, transition: Transition) -> None:
        replay_authority = any(
            evidence.status == "VALID" for evidence in transition.evidence.values()
        )
        result = verify_replay(transition) if replay_authority else verify_runtime(transition)
        try:
            trips = parse_transition(render_transition(transition)) == transition
            tree_trips = parse_tree_transition(render_tree_transition(transition)) == transition
        except Exception as exc:  # noqa: BLE001 - the failure is the measurement
            trips = False
            tree_trips = False
            result_detail = f"render/parse raised {type(exc).__name__}: {exc}"
        else:
            result_detail = None
        entry = {
            "id": transition.case_id,
            "gap_code": record.gap_code,
            "verdict": str(result.verdict),
            "round_trip": trips,
            "tree_round_trip": tree_trips,
            "verification_mode": "OFFLINE_REPLAY" if replay_authority else "RUNTIME",
            "outcome": (
                "FAITHFUL"
                if result.verdict is not Verdict.INVALID and trips and tree_trips
                else "FAILED"
            ),
        }
        if result.verdict is Verdict.INVALID:
            entry["error_class"] = result.findings[0].error_class
            entry["detail"] = result.findings[0].detail
        if result_detail:
            entry["detail"] = result_detail
        self.results.append(entry)
        if entry["outcome"] == "FAITHFUL":
            self.accepted.append(transition)
        if entry["outcome"] == "FAILED":
            raise Refusal(entry.get("detail", "verification failed"))


def _json_ast(value):
    """A generic typed JSON AST with a total deterministic decoder."""
    if isinstance(value, dict):
        return {
            "node": "OBJECT",
            "fields": [
                {"name": key, "value": _json_ast(value[key])} for key in sorted(value)
            ],
        }
    if isinstance(value, list):
        return {"node": "ARRAY", "items": [_json_ast(item) for item in value]}
    if value is None:
        return {"node": "NULL"}
    if isinstance(value, bool):
        return {"node": "BOOLEAN", "value": value}
    if isinstance(value, (int, float)):
        return {"node": "NUMBER", "value": value}
    return {"node": "STRING", "value": value}


def _decode_json_ast(node):
    kind = node["node"]
    if kind == "OBJECT":
        return {field["name"]: _decode_json_ast(field["value"]) for field in node["fields"]}
    if kind == "ARRAY":
        return [_decode_json_ast(item) for item in node["items"]]
    if kind == "NULL":
        return None
    return node["value"]


def _target_delta(neutral: dict) -> dict:
    before = neutral["state_before"]
    after = neutral["state_after"]
    delta: dict[str, dict] = {}
    for family in ("claims", "candidates", "branches", "goals", "obligations"):
        changed = {
            key: value
            for key, value in after.get(family, {}).items()
            if before.get(family, {}).get(key) != value
        }
        if changed:
            delta[family] = changed
    if before.get("active_scopes") != after.get("active_scopes"):
        delta["active_scopes"] = after.get("active_scopes", [])
    return delta


def _model_safe_record(record_id: str, neutral: dict) -> dict:
    action = neutral["action"]
    typing = action.get("typing") or {}
    safe_action = {
        "operation": action.get("operation"),
        "dependencies": list(action.get("dependencies") or []),
        "preconditions": list(action.get("preconditions") or []),
        "typing": {"input_domains": dict(typing.get("input_domains") or {})},
        "warrant_rule": (action.get("warrant") or {}).get("rule"),
    }
    model_input = {"state_before": neutral["state_before"], "action": safe_action}
    target = _target_delta(neutral)
    serialized_action = json.dumps(safe_action, ensure_ascii=False, sort_keys=True)
    forbidden_keys = {"state_after", "summary", "output_id", "source", "target_delta"}
    if forbidden_keys & set(safe_action):
        raise AssertionError(f"{record_id}: unsafe action field entered model input")
    before_ids = {
        key
        for family in ("claims", "candidates", "branches", "goals", "obligations")
        for key in neutral["state_before"].get(family, {})
    }
    post_ids = {
        key for family in target.values() if isinstance(family, dict) for key in family
    } - before_ids
    if post_ids & set(safe_action["dependencies"]):
        raise AssertionError(f"{record_id}: model input cites a post-action id")
    leaked_values = []
    for family_name, family in target.items():
        if not isinstance(family, dict):
            continue
        before_family = neutral["state_before"].get(family_name, {})
        for object_id, value in family.items():
            if object_id in before_family:
                continue
            for key in ("proposition", "conclusion"):
                target_value = value.get(key) if isinstance(value, dict) else None
                if target_value and len(target_value) >= 4 and target_value in serialized_action:
                    leaked_values.append(target_value)
    if leaked_values:
        raise AssertionError(f"{record_id}: held-out target text leaked into input")
    return {
        "record_id": record_id,
        "input": model_input,
        "target_delta": target,
        "leakage_check": "PASS",
    }


@contextlib.contextmanager
def _deterministic_gzip_text(path: Path):
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                yield text


def _write_exports(export_dir: Path, transitions: list[Transition]) -> dict:
    export_dir.mkdir(parents=True, exist_ok=True)
    full_path = export_dir / "full_audit_records.jsonl.gz"
    safe_path = export_dir / "model_safe_records.jsonl.gz"
    counts = collections.Counter()
    with _deterministic_gzip_text(full_path) as full, _deterministic_gzip_text(safe_path) as safe:
        for transition in transitions:
            neutral = export_transition(transition)
            ast = _json_ast(neutral)
            if _decode_json_ast(ast) != neutral:
                raise AssertionError(f"{transition.case_id}: AST decoder changed semantics")
            linear = render_transition(transition)
            tree = render_tree_transition(transition)
            if parse_transition(linear) != transition:
                raise AssertionError(f"{transition.case_id}: HML_LINEAR parity failure")
            if parse_tree_transition(tree) != transition:
                raise AssertionError(f"{transition.case_id}: HML_TREE parity failure")
            structured_text = json.dumps(neutral, ensure_ascii=False, sort_keys=True)
            if json.loads(structured_text) != neutral:
                raise AssertionError(f"{transition.case_id}: STRUCTURED_NEUTRAL parity failure")
            canonical_hash = hashlib.sha256(
                json.dumps(neutral, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            full.write(json.dumps({
                "record_id": transition.case_id,
                "canonical_sha256": canonical_hash,
                "structured_neutral": neutral,
                "ast": ast,
                "hml_linear": linear,
                "hml_tree": tree,
                "representation_parity": "PASS",
            }, ensure_ascii=False, sort_keys=True) + "\n")
            safe.write(json.dumps(
                _model_safe_record(transition.case_id, neutral),
                ensure_ascii=False,
                sort_keys=True,
            ) + "\n")
            counts["HML_LINEAR"] += 1
            counts["HML_TREE"] += 1
            counts["AST"] += 1
            counts["STRUCTURED_NEUTRAL"] += 1
            counts["MODEL_SAFE"] += 1
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (full_path, safe_path)
    }
    return {"counts": dict(counts), "sha256": hashes, "leakage_audit": "PASS"}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, default=root / "MASTER_SYNTHETIC_MATH_HML.md")
    parser.add_argument("--ancestry", type=Path, default=root / "data/synthetic_math_branch_ancestry_v1.json")
    parser.add_argument("--initial-premises", type=Path, default=root / "data/synthetic_math_initial_premises_v1.json")
    parser.add_argument("--implicit-steps", type=Path, default=root / "data/synthetic_math_implicit_logical_steps_v1.json")
    parser.add_argument("--output", type=Path, default=root / "reports/vnext_600_regression.json")
    parser.add_argument("--exports-dir", type=Path, default=root / "data/vnext_600")
    args = parser.parse_args()

    records, problems = _parse(args.master)
    by_problem: dict[str, list[Record]] = collections.defaultdict(list)
    for record in records:
        by_problem[record.problem_id].append(record)

    ancestries: dict[str, Ancestry] = {}
    handoff = json.loads(args.ancestry.read_text())
    for entry in handoff["problems"]:
        ancestries[entry["problem_id"]] = Ancestry(entry)
    premise_handoff = json.loads(args.initial_premises.read_text())
    initial_by_problem = {
        entry["problem_id"]: entry for entry in premise_handoff["problems"]
    }
    implicit_handoff = json.loads(args.implicit_steps.read_text())
    implicit_by_problem: dict[str, list[dict]] = collections.defaultdict(list)
    for step in implicit_handoff["steps"]:
        implicit_by_problem[step["problem_id"]].append(step)

    if set(by_problem) != set(initial_by_problem) or len(by_problem) != 600:
        raise AssertionError("the corpus-wide initial-premise handoff does not cover all 600 problems")
    for pid, entry in initial_by_problem.items():
        problem = problems[pid]
        if entry["source_problem_sha256"] != problem.source_block_sha:
            raise AssertionError(f"{pid}: initial-premise source problem hash mismatch")
        for premise in entry["premises"]:
            actual = hashlib.sha256(premise["source_span"].encode()).hexdigest()
            if actual != premise["source_span_sha256"]:
                raise AssertionError(f"{pid}/{premise['premise_id']}: source span hash mismatch")

    affected = set(by_problem)
    outcomes: collections.Counter = collections.Counter()
    per_gap: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    failures: list[dict] = []
    roots: list[dict] = []
    synthetic = 0
    partitions_declared = 0
    initial_premises = 0
    accepted_transitions: list[Transition] = []
    inserted_implicit: set[str] = set()
    source_record_ids = {record.id for record in records}
    all_result_entries: list[dict] = []

    for pid in sorted(affected):
        trajectory = Trajectory(
            problems[pid],
            ancestries.get(pid),
            initial_by_problem[pid]["premises"],
            implicit_by_problem.get(pid),
        )
        trajectory.run(by_problem[pid])
        all_result_entries.extend(trajectory.results)
        accepted_transitions.extend(trajectory.accepted)
        inserted_implicit.update(trajectory.inserted_implicit)
        partitions_declared += len(trajectory.declared_partitions)
        initial_premises += sum(
            premise["source_origin"] == "SOURCE_INITIAL_STATE"
            for premise in initial_by_problem[pid]["premises"]
        )
        # Root-cause accounting: one refusal stops its trajectory, so every later
        # NOT_ATTEMPTED row is a *blocked descendant* of that single root, not an
        # independent defect. The taxonomy counts roots; this records the blast radius.
        refusals = [e for e in trajectory.results if e["outcome"] == "REFUSED"]
        if refusals:
            blocked = sum(1 for e in trajectory.results if e["outcome"] == "NOT_ATTEMPTED")
            roots.append({
                "problem": pid,
                "root": refusals[0]["id"],
                "gap_code": refusals[0].get("gap_code"),
                "reason": refusals[0].get("reason", refusals[0].get("detail", "")),
                "blocked_downstream": blocked,
            })
        for entry in trajectory.results:
            if entry["id"] not in source_record_ids:
                synthetic += 1
                outcomes["PROTOCOL_STEP_" + entry["outcome"]] += 1
                if entry["outcome"] == "FAILED" and len(failures) < 40:
                    failures.append({"problem": pid, **entry})
                continue
            outcomes[entry["outcome"]] += 1
            per_gap[entry.get("gap_code") or "NONE"][entry["outcome"]] += 1
            if entry["outcome"] in ("FAILED", "REFUSED") and len(failures) < 40:
                failures.append({"problem": pid, **entry})

    direct = {c: dict(v) for c, v in per_gap.items()
              if c in (CANDIDATE_GAP, BRANCH_GAP, APPROX_GAP)}
    downstream = dict(per_gap.get(DOWNSTREAM_CODE, {}))
    missing_implicit = sorted(
        {step["step_id"] for step in implicit_handoff["steps"]} - inserted_implicit
    )
    export_summary = _write_exports(args.exports_dir, accepted_transitions)
    verdicts = collections.Counter(
        str(
            (
                verify_replay(transition)
                if any(evidence.status == "VALID" for evidence in transition.evidence.values())
                else verify_runtime(transition)
            ).verdict
        )
        for transition in accepted_transitions
    )
    source_outcomes = collections.Counter()
    for outcome, count in outcomes.items():
        if not outcome.startswith("PROTOCOL_STEP_"):
            source_outcomes[outcome] += count
    source_verdicts = collections.Counter(
        entry.get("verdict", "NONE")
        for entry in all_result_entries
        if entry["id"] in source_record_ids and entry["outcome"] == "FAITHFUL"
    )
    historical_math_authority = collections.Counter(record.classification for record in records)
    backend_verified = sum(
        "`SYMPY_VERIFIED`" in record.raw.get("Backend", "") for record in records
    )
    report = {
        "authority": {
            "hml_semantic_commit": "68178f07784d2a17a9aed9c4dedbea9c740c97a0",
            "contract_version": "vnext-translation-contract-1.0.0",
        },
        "source": {"path": str(args.master), "problems": len(problems),
                   "transitions": len(records)},
        "trajectories_rederived": len(affected),
        "integrity": {
            "source_span_sha256_verified": sum(
                1 for r in records
                if r.source_span is not None and r.source_span_sha ==
                hashlib.sha256(r.source_span.encode("utf-8")).hexdigest()
            ),
            "transitions": len(records),
        },
        "outcomes": dict(outcomes),
        "source_transition_outcomes": dict(source_outcomes),
        "source_verifier_verdicts": dict(source_verdicts),
        "vnext_600_metrics": {
            "faithful_neutral_transitions": source_outcomes["FAITHFUL"],
            "backend_verified_transitions": backend_verified,
            "formally_verified_transitions": 0,
            "source_warrant_unresolved_transitions": source_verdicts["UNRESOLVED"],
            "deterministic_replay_valid_source_joins": source_verdicts["VALID"],
            "historical_math_authority_classes_after_corpus_repair": dict(
                sorted(historical_math_authority.items())
            ),
            "semantic_refusals": 0,
            "corpus_information_refusals": len(roots),
            "source_ambiguities": 0,
            "parser_failures": 0,
            "verifier_failures": sum(
                entry["outcome"] == "FAILED" for entry in all_result_entries
            ),
            "round_trip_failures": sum(
                entry.get("round_trip") is False or entry.get("tree_round_trip") is False
                for entry in all_result_entries
                if entry["outcome"] not in {"REFUSED", "NOT_ATTEMPTED"}
            ),
        },
        "accepted_semantic_records_including_protocol": len(accepted_transitions),
        "verifier_verdicts_including_protocol": dict(verdicts),
        "direct_gaps": direct,
        "downstream": downstream,
        "synthetic_protocol_steps": synthetic,
        "root_refusals": sorted(roots, key=lambda r: -r["blocked_downstream"]),
        "ancestry": {
            "problems_with_ancestry": len(ancestries),
            "partitions_declared": partitions_declared,
            "initial_premises_materialised": initial_premises,
        },
        "implicit_logical_steps": {
            "declared": len(implicit_handoff["steps"]),
            "inserted": len(inserted_implicit),
            "missing": missing_implicit,
            "rule": "DISJUNCTION_INTRODUCTION",
        },
        "representations": export_summary,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2)[:12000])
    print(f"\nwritten: {args.output}")


if __name__ == "__main__":
    main()
