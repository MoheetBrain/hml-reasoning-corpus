"""Representation parity gate (mission §5). Training is blocked if this fails.

What is proved
--------------
Not "the arms look equivalent" -- that is prose. For every item in the dataset, each arm's
**rendered text is read back** and the recovered objects are compared. Three properties, in
increasing strength:

1. *Self-fidelity*: ``parse(render(x)) == x`` for each arm. An arm that cannot read its own
   output is lossy, and the loss is exactly the information the model was denied.
2. *Cross-arm identity*: all four arms recover the **same** object. This is the statement
   ``semantic_information(HML) = semantic_information(AST) = semantic_information(LeanLike)
   = semantic_information(StructuredEnglish)`` that §5 requires, made mechanical.
3. *Label preservation*: the recovered transition, re-verified by the frozen verifier, still
   carries the recorded label. A rendering that changed admissibility would be a rendering
   that changed the mathematics.

The per-property table demanded by §5 -- object identity, types, binder identity, scope,
assumptions, facts, constraints, goals, candidates, branches, dependencies, obligations,
epistemic state, warrants, preconditions, evidence references -- is checked field by field
rather than inferred from whole-object equality, so a report can say *which* property held.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from hamiltonian_lang.semantic_state.verify import verify_replay

from ..arms import ARM_NAMES, parse, render
from ..arms.common import from_ir

__all__ = ["PROPERTIES", "ParityReport", "check_file", "check_row"]

#: The §5 checklist. Each entry extracts one property from an IR, so a mismatch names the
#: property rather than dumping two objects and leaving the reader to diff them.
PROPERTIES = {
    "object_identity": lambda ir: sorted(
        (k, r["key"], r["id"])
        for k in ("claims", "candidates", "branches", "goals", "obligations")
        for st in ("state_before", "state_after")
        for r in ir[st][k]
    ),
    "types": lambda ir: sorted(
        (st, r["key"], r.get("domain"))
        for st in ("state_before", "state_after")
        for r in ir[st]["claims"]
    ),
    "binder_identity": lambda ir: sorted(
        (st, r["key"], r["proposition"])
        for st in ("state_before", "state_after")
        for r in ir[st]["claims"]
    ),
    "scope": lambda ir: (
        sorted(ir["state_before"]["active_scopes"]),
        sorted(ir["state_after"]["active_scopes"]),
        sorted(
            (st, k, r["key"], r.get("scope"))
            for st in ("state_before", "state_after")
            for k in ("claims", "candidates", "branches", "goals")
            for r in ir[st][k]
        ),
    ),
    "assumptions_and_facts": lambda ir: sorted(
        (st, r["key"], r["status"], r["proposition"])
        for st in ("state_before", "state_after")
        for r in ir[st]["claims"]
    ),
    "constraints": lambda ir: sorted(
        (st, r["key"], tuple(r["constraint_ids"]))
        for st in ("state_before", "state_after")
        for r in ir[st]["candidates"]
    ),
    "goals": lambda ir: sorted(
        (st, r["key"], r["proposition"], r["status"], r["scope"])
        for st in ("state_before", "state_after")
        for r in ir[st]["goals"]
    ),
    "candidates": lambda ir: sorted(
        (st, r["key"], r["proposition"], r["status"])
        for st in ("state_before", "state_after")
        for r in ir[st]["candidates"]
    ),
    "branches": lambda ir: sorted(
        (st, r["key"], r["predicate"], r["status"], r["scope"], r["conclusion"])
        for st in ("state_before", "state_after")
        for r in ir[st]["branches"]
    ),
    "dependencies": lambda ir: (
        sorted(
            (st, r["key"], tuple(r["dependencies"]))
            for st in ("state_before", "state_after")
            for r in ir[st]["claims"]
        ),
        tuple(ir["action"]["dependencies"]),
    ),
    "obligations": lambda ir: sorted(
        (st, r["key"], r["status"], r["mandatory"], r["proposition"])
        for st in ("state_before", "state_after")
        for r in ir[st]["obligations"]
    ),
    "epistemic_state": lambda ir: (
        ir["action"]["epistemic_effect"],
        sorted(
            (st, r["key"], r["status"])
            for st in ("state_before", "state_after")
            for r in ir[st]["claims"]
        ),
    ),
    "warrants": lambda ir: ir["action"]["warrant"],
    "preconditions": lambda ir: ir["action"]["preconditions"],
    "evidence_references": lambda ir: sorted(
        (e["key"], e["id"], e["kind"], e["status"], e["trusted"], e["supports_rule"],
         tuple(e["premise_ids"]))
        for e in ir["evidence"]
    ),
    "action_envelope": lambda ir: {
        k: ir["action"][k]
        for k in ("id", "operation", "summary", "output_id", "typing", "goal_effect",
                  "scope_effect", "branch_effect", "candidate_effect",
                  "obligations_created", "obligations_discharged")
    },
}


@dataclass
class ParityReport:
    rows: int = 0
    self_roundtrip_ok: Counter = field(default_factory=Counter)
    cross_arm_ok: int = 0
    label_preserved: int = 0
    property_ok: Counter = field(default_factory=Counter)
    property_fail: Counter = field(default_factory=Counter)
    failures: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.rows > 0
            and self.cross_arm_ok == self.rows
            and self.label_preserved == self.rows
            and all(self.self_roundtrip_ok[a] == self.rows for a in ARM_NAMES)
            and not self.property_fail
        )

    def to_dict(self) -> dict:
        return {
            "result": "PASS" if self.passed else "FAIL",
            "rows": self.rows,
            "self_roundtrip_ok": {a: self.self_roundtrip_ok[a] for a in ARM_NAMES},
            "cross_arm_identity_ok": self.cross_arm_ok,
            "label_preserved_after_reparse": self.label_preserved,
            "properties_checked": sorted(PROPERTIES),
            "property_ok": dict(sorted(self.property_ok.items())),
            "property_fail": dict(sorted(self.property_fail.items())),
            "failures": self.failures[:25],
        }


def canonical(ir: dict) -> dict:
    """Order-insensitive form, for comparing two arms.

    A :class:`SemanticState` maps id to record; the verifier never reads record order, and
    the frozen HML view emits its own order for readability. §5 admits exactly this class of
    difference -- "up to representation-only differences" -- so the comparison sorts record
    lists by key rather than pretending order is content. Everything that *is* content, down
    to each field of each record, still has to match exactly.
    """
    out = {"action": ir["action"], "evidence": sorted(ir["evidence"], key=lambda e: e["key"])}
    for st in ("state_before", "state_after"):
        block = dict(ir[st])
        for kind in ("claims", "candidates", "branches", "goals", "obligations"):
            block[kind] = sorted(block[kind], key=lambda r: r["key"])
        block["active_scopes"] = sorted(block["active_scopes"])
        out[st] = block
    return out


def check_row(row: dict, report: ParityReport) -> None:
    report.rows += 1
    recovered: dict[str, dict] = {}
    for arm in ARM_NAMES:
        text = row["renders"][arm]
        try:
            ir = parse(arm, text)
        except Exception as exc:  # noqa: BLE001 -- any failure is a parity failure
            report.failures.append(
                {"item": row["item_id"], "arm": arm, "error": f"{type(exc).__name__}: {exc}"}
            )
            continue
        recovered[arm] = ir
        # Real self-fidelity: if the reader lost anything, the writer cannot reproduce the
        # exact text it was given. Comparing the re-render to the stored bytes is the
        # strongest losslessness statement available from the row alone.
        try:
            if render(arm, ir) == text:
                report.self_roundtrip_ok[arm] += 1
            else:
                report.failures.append(
                    {"item": row["item_id"], "arm": arm, "error": "re-render differs"}
                )
        except Exception as exc:  # noqa: BLE001
            report.failures.append(
                {"item": row["item_id"], "arm": arm,
                 "error": f"re-render {type(exc).__name__}: {exc}"}
            )

    if len(recovered) != len(ARM_NAMES):
        return

    recovered = {a: canonical(ir) for a, ir in recovered.items()}
    reference = recovered[ARM_NAMES[0]]
    identical = True
    for name, extract in PROPERTIES.items():
        ref = extract(reference)
        if all(extract(recovered[a]) == ref for a in ARM_NAMES[1:]):
            report.property_ok[name] += 1
        else:
            report.property_fail[name] += 1
            identical = False
            offenders = [a for a in ARM_NAMES[1:] if extract(recovered[a]) != ref]
            report.failures.append(
                {"item": row["item_id"], "property": name, "arms_disagreeing": offenders}
            )
    if identical and all(recovered[a] == reference for a in ARM_NAMES[1:]):
        report.cross_arm_ok += 1

    try:
        verdict = str(verify_replay(from_ir(reference)).verdict)
    except Exception as exc:  # noqa: BLE001
        report.failures.append(
            {"item": row["item_id"], "error": f"reverify {type(exc).__name__}: {exc}"}
        )
        return
    if verdict == row["label"]:
        report.label_preserved += 1
    else:
        report.failures.append(
            {"item": row["item_id"], "recorded_label": row["label"], "reverified": verdict}
        )


def check_file(path: str | Path, report: ParityReport | None = None) -> ParityReport:
    report = report or ParityReport()
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            check_row(json.loads(line), report)
    return report
