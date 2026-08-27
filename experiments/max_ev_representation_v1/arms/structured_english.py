"""R_STRUCTURED_ENGLISH: the canonical state as generated English sentences.

The contrast this arm supplies is **natural-language framing with no formal syntax**. It is
the control that answers the obvious objection to any "our notation helps" result: perhaps
the model simply needs the state spelled out, and any explicit rendering would do. If plain
English carries the state as well as HML does, the interesting variable was explicitness,
not notation.

It is template English, deliberately. Sentences are generated from fixed patterns so the
surface is unambiguous and readable back; the arm is a *representation*, not a writing
sample, and varying the prose would confound the comparison with fluency.

Mathematical content is never paraphrased. A proposition is emitted verbatim after the
sentence's colon, so the mathematics is identical in every arm and only the framing differs.
"""

from __future__ import annotations

import json
import re

from .scalars import JSON, read_atom, read_text, write_atom, write_text

__all__ = ["render", "parse", "NAME"]

NAME = "R_STRUCTURED_ENGLISH"

_STATES = "it states: "
_PREDICATE = "its predicate is: "
_SUMMARY = "It is summarised as: "

_ACTION_LINES = (
    ("typing", "Its typing is "),
    ("warrant", "Its warrant is "),
    ("goal_effect", "Its goal effect is "),
    ("scope_effect", "Its scope effect is "),
    ("branch_effect", "Its branch effect is "),
    ("candidate_effect", "Its candidate effect is "),
    ("epistemic_effect", "Its epistemic effect is "),
    ("preconditions", "Its preconditions are "),
    ("obligations_created", "Its created obligations are "),
    ("obligations_discharged", "Its discharged obligations are "),
)
_ACTION_BY_PREFIX = {prefix: name for name, prefix in _ACTION_LINES}


def _atoms(values) -> str:
    return ", ".join(write_atom(v) for v in values)


def _split_atoms(rest: str) -> list[str]:
    rest = rest.strip()
    out: list[str] = []
    i = 0
    while i < len(rest):
        if rest[i].isspace() or rest[i] == ",":
            i += 1
            continue
        if rest[i] == '"':
            value, end = JSON.raw_decode(rest, i)
            out.append(value)
            i = end
            continue
        j = i
        while j < len(rest) and rest[j] != ",":
            j += 1
        out.append(rest[i:j].strip())
        i = j
    return out


def _name(rec: dict) -> str:
    if rec["id"] != rec["key"]:
        return f"{write_atom(rec['key'])} (recorded as {write_atom(rec['id'])})"
    return write_atom(rec["key"])


def _clause(text: str, value) -> str:
    return "" if value is None else f" {text} {write_atom(str(value))}"


def _deps(values, phrase: str = "depending on") -> str:
    return f" {phrase} {_atoms(values)}" if values else ""


def _render_state(ir: dict, label: str) -> list[str]:
    st = ir[f"state_{label}"]
    out = ["Prior state." if label == "before" else "Resulting state."]
    out.append("The active scopes are " + _atoms(st["active_scopes"]) + ".")
    for b in st["branches"]:
        head = (
            f"Case {_name(b)} has status {b['status']} in scope {write_atom(b['scope'])}"
            + _clause("concluding", b["conclusion"])
            + _clause("in partition", b["partition_id"])
        )
        out.append(f"{head}; {_PREDICATE}{write_text(b['predicate'])}")
    for c in st["claims"]:
        head = (
            f"Fact {_name(c)} has status {c['status']} in scope {write_atom(c['scope'])}"
            + _clause("with domain", c["domain"])
            + _deps(c["dependencies"])
        )
        out.append(f"{head}; {_STATES}{write_text(c['proposition'])}")
    for k in st["candidates"]:
        head = (
            f"Candidate {_name(k)} has status {k['status']} in scope {write_atom(k['scope'])}"
            + _deps(k["constraint_ids"], "constrained by")
            + _deps(k["dependencies"])
            + _clause("originating from", k["origin"])
            + _clause("with evidence", k["evidence_id"])
            + _clause("recorded result", k["verification_result"])
        )
        out.append(f"{head}; {_STATES}{write_text(k['proposition'])}")
    for o in st["obligations"]:
        head = (
            f"Obligation {_name(o)} has status {o['status']} and is "
            + ("mandatory" if o["mandatory"] else "optional")
            + _deps(o["dependencies"])
            + _clause("originating from", o["origin"])
            + _clause("discharged by", o["discharge_evidence_id"])
        )
        out.append(f"{head}; {_STATES}{write_text(o['proposition'])}")
    for g in st["goals"]:
        head = f"Goal {_name(g)} has status {g['status']} in scope {write_atom(g['scope'])}"
        out.append(f"{head}; {_STATES}{write_text(g['proposition'])}")
    return out


def render(ir: dict) -> str:
    out = _render_state(ir, "before")
    a = ir["action"]
    out.append("Proposed action.")
    out.append(f"Action {write_atom(a['id'])} applies operation {write_atom(a['operation'])}.")
    out.append(_SUMMARY + write_text(a["summary"]))
    out.append(
        f"It produces {write_atom(a['output_id'])}."
        if a["output_id"]
        else "It produces no new record."
    )
    out.append(
        "It depends on " + _atoms(a["dependencies"]) + "."
        if a["dependencies"]
        else "It has no dependencies."
    )
    for name, prefix in _ACTION_LINES:
        out.append(prefix + json.dumps(a[name], ensure_ascii=False, sort_keys=True) + ".")
    out.append("Supporting evidence.")
    for ev in ir["evidence"]:
        out.append(f"Record {_name(ev)} is of kind {write_atom(ev['kind'])}.")
        out.append(f"Its status is {write_atom(ev['status'])}.")
        out.append("It is trusted." if ev["trusted"] else "It is not trusted.")
        out.append(
            f"It supports rule {write_atom(ev['supports_rule'])}."
            if ev["supports_rule"]
            else "It supports no rule."
        )
        out.append(
            "Its premises are " + _atoms(ev["premise_ids"]) + "."
            if ev["premise_ids"]
            else "It has no premises."
        )
        out.append("Its payload is " + json.dumps(ev["payload"], ensure_ascii=False, sort_keys=True) + ".")
    out.extend(_render_state(ir, "after"))
    return "\n".join(out)


# --------------------------------------------------------------------------- reader

_HEAD = re.compile(
    r"^(?P<kind>Fact|Goal|Case|Candidate|Obligation|Record) (?P<rest>.*)$", re.DOTALL
)
_NAMED = re.compile(r"^(?P<key>\"(?:[^\"\\]|\\.)*\"|\S+?)(?: \(recorded as (?P<id>.+?)\))?(?= has | is )")


def _clause_value(head: str, phrase: str):
    m = re.search(rf"(?<= ){re.escape(phrase)} (\"(?:[^\"\\]|\\.)*\"|\S+)", head)
    return read_atom(m.group(1)) if m else None


def _clause_list(head: str, phrase: str) -> list[str]:
    m = re.search(rf"(?<= ){re.escape(phrase)} (.+?)(?=(?: (?:depending on|constrained by|originating from|with evidence|recorded result|discharged by|with domain|in partition|concluding) )|$)", head)
    return _split_atoms(m.group(1)) if m else []


def _empty_state() -> dict:
    return {
        "claims": [], "candidates": [], "branches": [], "goals": [], "obligations": [],
        "active_scopes": [],
    }


def parse(text: str) -> dict:
    ir: dict = {"evidence": []}
    state = _empty_state()
    label = "before"
    action: dict = {}
    evidence: dict | None = None
    section = "state"

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line == "Prior state.":
            state, label, section = _empty_state(), "before", "state"
            continue
        if line == "Resulting state.":
            state, label, section = _empty_state(), "after", "state"
            continue
        if line == "Proposed action.":
            ir["state_before"] = state
            section = "action"
            continue
        if line == "Supporting evidence.":
            section = "evidence"
            evidence = None
            continue
        if line.startswith("The active scopes are "):
            state["active_scopes"] = _split_atoms(line[len("The active scopes are ") : -1])
            continue

        if section == "action":
            if line.startswith("Action "):
                m = re.match(r"^Action (\S+) applies operation (.+)\.$", line)
                action = {
                    "id": read_atom(m.group(1)), "operation": read_atom(m.group(2)),
                    "summary": "", "output_id": None, "dependencies": [],
                }
                ir["action"] = action
            elif line.startswith(_SUMMARY):
                action["summary"] = read_text(line[len(_SUMMARY) :])
            elif line == "It produces no new record.":
                action["output_id"] = None
            elif line.startswith("It produces "):
                action["output_id"] = read_atom(line[len("It produces ") : -1])
            elif line == "It has no dependencies.":
                action["dependencies"] = []
            elif line.startswith("It depends on "):
                action["dependencies"] = _split_atoms(line[len("It depends on ") : -1])
            else:
                for prefix, name in _ACTION_BY_PREFIX.items():
                    if line.startswith(prefix):
                        action[name] = json.loads(line[len(prefix) : -1])
                        break
            continue

        if section == "evidence" and not line.startswith("Record "):
            if line.startswith("Its status is "):
                evidence["status"] = read_atom(line[len("Its status is ") : -1])
            elif line == "It is trusted.":
                evidence["trusted"] = True
            elif line == "It is not trusted.":
                evidence["trusted"] = False
            elif line == "It supports no rule.":
                evidence["supports_rule"] = None
            elif line.startswith("It supports rule "):
                evidence["supports_rule"] = read_atom(line[len("It supports rule ") : -1])
            elif line == "It has no premises.":
                evidence["premise_ids"] = []
            elif line.startswith("Its premises are "):
                evidence["premise_ids"] = _split_atoms(line[len("Its premises are ") : -1])
            elif line.startswith("Its payload is "):
                evidence["payload"] = json.loads(line[len("Its payload is ") : -1])
            continue

        m = _HEAD.match(line)
        if m is None:
            raise ValueError(f"unrecognised sentence: {line[:60]!r}")
        kind = m.group("kind")
        rest = m.group("rest")
        nm = _NAMED.match(rest)
        if nm is None:
            raise ValueError(f"unnamed record: {line[:60]!r}")
        key = read_atom(nm.group("key"))
        rid = read_atom(nm.group("id")) if nm.group("id") else key

        if kind == "Record":
            evidence = {
                "key": key, "id": rid,
                "kind": read_atom(rest[rest.index(" is of kind ") + len(" is of kind ") : -1]),
                "payload": {},
            }
            ir["evidence"].append(evidence)
            continue

        marker = _PREDICATE if kind == "Case" else _STATES
        idx = rest.index("; " + marker)
        head, body = rest[:idx], rest[idx + len("; " + marker) :]
        value = read_text(body)
        status = re.search(r" has status (\S+)", head).group(1)
        scope_m = re.search(r" in scope (\"(?:[^\"\\]|\\.)*\"|\S+)", head)
        scope = read_atom(scope_m.group(1)) if scope_m else None

        if kind == "Fact":
            state["claims"].append({
                "key": key, "id": rid, "proposition": value, "status": status, "scope": scope,
                "domain": _clause_value(head, "with domain"),
                "dependencies": _clause_list(head, "depending on"),
            })
        elif kind == "Goal":
            state["goals"].append({
                "key": key, "id": rid, "proposition": value, "status": status, "scope": scope,
            })
        elif kind == "Case":
            state["branches"].append({
                "key": key, "id": rid, "predicate": value, "status": status, "scope": scope,
                "conclusion": _clause_value(head, "concluding"),
                "partition_id": _clause_value(head, "in partition"),
            })
        elif kind == "Candidate":
            state["candidates"].append({
                "key": key, "id": rid, "proposition": value, "status": status, "scope": scope,
                "constraint_ids": _clause_list(head, "constrained by"),
                "dependencies": _clause_list(head, "depending on"),
                "origin": _clause_value(head, "originating from"),
                "evidence_id": _clause_value(head, "with evidence"),
                "verification_result": _clause_value(head, "recorded result"),
            })
        else:
            state["obligations"].append({
                "key": key, "id": rid, "proposition": value, "status": status,
                "mandatory": " and is mandatory" in head,
                "dependencies": _clause_list(head, "depending on"),
                "origin": _clause_value(head, "originating from"),
                "discharge_evidence_id": _clause_value(head, "discharged by"),
            })
    ir[f"state_{label}"] = state
    return ir
