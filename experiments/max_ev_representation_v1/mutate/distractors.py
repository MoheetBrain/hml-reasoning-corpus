"""Uncited distractor records, so the task cannot be solved by keyword spotting.

The defect this repairs
-----------------------
Measured on the first build of DATASET_V1, the token ``UNKNOWN`` carried **0.918 bits** of
the 1.585-bit label entropy in all four arms. The reason is structural: the UNRESOLVED class
is produced by setting some status to ``UNKNOWN``, so its mere presence almost determined the
answer. A probe scoring well on that is detecting a string, and a representation comparison
run on it would measure which arm makes that string easiest to spot.

The repair is not to hide the word -- it is load-bearing mathematics -- but to make its mere
presence uninformative, so that the model has to read *where* it appears.

Why that is the correct semantics, not a trick
----------------------------------------------
The verifier's unknown collection is **dependency-scoped** (D-049): only records the action
actually cites can make a transition UNRESOLVED. An unrelated ``UNKNOWN`` claim sitting in
the state is explicitly *not* a reason to refuse a transition that never cites it -- and the
frozen verifier's own docstring records that before that scoping existed, one unrelated
unknown appended anywhere turned all ten ILLEGAL fixtures from INVALID to UNRESOLVED, "a
complete detection bypass".

So injecting uncited unknowns tests exactly the rule the verifier implements. A model that
answers UNRESOLVED because it saw the word is wrong for the same reason the pre-D-049 checker
was wrong, and the dataset should be able to tell the difference.

The same argument applies to ``VERIFIED``, which otherwise appears only in items mutated by
epistemic promotion.

Every distractor is re-verified: if adding one changes the verdict, it is discarded rather
than kept with a corrected label. A distractor that changes admissibility is not a distractor.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import replace

from hamiltonian_lang.semantic_state.model import (
    Claim,
    ClaimStatus,
    EvidenceRecord,
    Transition,
)
from hamiltonian_lang.semantic_state.verify import verify_replay

__all__ = ["add_distractors", "DISTRACTOR_STATUSES", "GENERATOR_VERSION"]

GENERATOR_VERSION = "max-ev-distractors-1.0.0"

#: Statuses whose bare presence would otherwise correlate with a label. Drawn uniformly, so
#: each appears in roughly the same share of VALID, INVALID and UNRESOLVED items.
DISTRACTOR_STATUSES = (
    ClaimStatus.UNKNOWN,
    ClaimStatus.VERIFIED,
    ClaimStatus.ASSUMED,
    ClaimStatus.REFUTED,
)


def _fresh_id(existing: set[str], rng: random.Random) -> str:
    """A plausible Lean-ish hypothesis name that the context does not already bind."""
    for _ in range(64):
        candidate = f"h{rng.randint(1, 40)}"
        if candidate not in existing:
            return candidate
    return "h_aux"


#: Rule names an uncited attestation may claim to support. Includes the names the mutation
#: families use, so no rule name is unique to a mutated item.
DISTRACTOR_RULES = ("LEAN_TACTIC", "APPLY_THEOREM", "PROCEDURAL_TRANSFORM", "VERIFY")


def add_distractors(
    t: Transition, item_id: str, *, extra_probability: float = 0.6, max_extra: int = 2
) -> tuple[Transition, list[dict]]:
    """Give every item an uncited UNKNOWN claim and an uncited VALID attestation, plus extras.

    The first two are **unconditional**, and that is the point. UNRESOLVED items necessarily
    contain the word ``UNKNOWN`` and lose the word ``VALID`` from their evidence status; if
    those words appeared nowhere else, their presence would answer the question. Measured on
    the first build, ``UNKNOWN`` alone carried 0.918 of the 1.585 available bits. Putting one
    of each into *every* item makes their presence constant, so the only way left to use them
    is to check **which record** carries them -- which is the dependency-scoping rule the
    verifier actually implements (D-049).

    Deterministic in ``item_id``, so a row can be regenerated without stored state.
    """
    seed = int(hashlib.sha256(f"distract|{item_id}".encode()).hexdigest()[:12], 16)
    rng = random.Random(seed)
    cited = set(t.action.dependencies)
    added: list[dict] = []
    current = t

    current, rec = _inject_claim(current, cited, rng, forced_status=ClaimStatus.UNKNOWN)
    if rec:
        added.append(rec)
    current, rec = _inject_evidence(current, rng)
    if rec:
        added.append(rec)

    current, rec = _benign_epistemic_effect(current, rng)
    if rec:
        added.append(rec)

    count = rng.randint(1, max_extra) if rng.random() <= extra_probability else 0
    for _ in range(count):
        current, rec = _inject_claim(current, cited, rng)
        if rec:
            added.append(rec)

    return current, added


def _inject_claim(t: Transition, cited: set[str], rng: random.Random, *, forced_status=None):
    """One uncited claim, present identically in both states. Discarded if it changes the verdict."""
    before = dict(t.state_before.claims)
    after = dict(t.state_after.claims)
    pool = [k for k in before if k not in cited]
    if not pool:
        return t, None
    model_on = before[rng.choice(pool)]
    new_id = _fresh_id(set(before) | set(after), rng)
    status = forced_status or rng.choice(DISTRACTOR_STATUSES)
    # The proposition is copied from a real hypothesis in this very state, so the distractor
    # is genuine mathematics rather than filler a model could learn to ignore.
    claim = Claim(
        id=new_id,
        proposition=model_on.proposition,
        status=status,
        scope=model_on.scope,
        domain=model_on.domain,
        dependencies=(),
    )
    # Present identically in both states: the frame condition forbids a claim appearing in
    # the resulting state unless the action produced it.
    candidate = replace(
        t,
        state_before=replace(t.state_before, claims={**before, new_id: claim}),
        state_after=replace(t.state_after, claims={**after, new_id: claim}),
    )
    if str(verify_replay(candidate).verdict) != str(verify_replay(t).verdict):
        return t, None
    return candidate, {"kind": "claim", "id": new_id, "status": str(status), "cited_by_action": False}


def _benign_epistemic_effect(t: Transition, rng: random.Random):
    """Declare a no-op epistemic effect on some items.

    ``_check_epistemic`` returns early for ``to_status`` in ``(None, PROPOSED, UNRESOLVED)``,
    so declaring ``PROPOSED`` asserts nothing and licenses nothing. Without this, the keys
    ``epistemic_effect``, ``to_status`` and ``claim_id`` appeared *only* in items mutated by
    epistemic promotion and each carried 0.049 bits -- structure of the record rather than
    content of the mathematics.
    """
    if t.action.epistemic_effect or rng.random() > 0.5 or not t.action.output_id:
        return t, None
    candidate = replace(
        t,
        action=replace(
            t.action,
            epistemic_effect={"claim_id": t.action.output_id, "to_status": "PROPOSED"},
        ),
    )
    if str(verify_replay(candidate).verdict) != str(verify_replay(t).verdict):
        return t, None
    return candidate, {"kind": "epistemic_effect", "to_status": "PROPOSED", "no_op": True}


def _inject_evidence(t: Transition, rng: random.Random):
    """One uncited attestation with status VALID, so that word is not a UNRESOLVED tell."""
    new_id = next((f"e{i}" for i in range(2, 40) if f"e{i}" not in t.evidence), None)
    if new_id is None:
        return t, None
    record = EvidenceRecord(
        id=new_id,
        kind="FORMAL_TRACE",
        status="VALID",
        trusted=bool(rng.getrandbits(1)),
        supports_rule=rng.choice(DISTRACTOR_RULES),
        premise_ids=(),
        payload={},
    )
    candidate = replace(t, evidence={**t.evidence, new_id: record})
    if str(verify_replay(candidate).verdict) != str(verify_replay(t).verdict):
        return t, None
    return candidate, {
        "kind": "evidence", "id": new_id, "status": "VALID",
        "supports_rule": record.supports_rule, "cited_by_action": False,
    }
