"""R_LEANLIKE: the canonical state in a proof-assistant tactic-state idiom.

The contrast this arm supplies is **familiarity**. A model pretrained on public
mathematics has seen millions of tokens shaped like a Lean or Coq goal state -- a typed
context, a turnstile, a target -- and none shaped like HML. If representation effects are
really familiarity effects, this is the arm that should win, and saying so in advance is
what makes the result interpretable either way (§16).

It is a Lean *idiom*, not Lean. The surface carries status, domain, scope, dependency and
effect information that a real tactic state does not print, because the experiment requires
every arm to carry identical information (§5). Annotations are therefore compact and
postfix, so the mathematics stays where a Lean reader expects it and the metadata sits out
of the way.

Line grammar
------------
Each record is one line. Optional fields are **omitted when absent**, which is what keeps
the surface sparse; a present-but-empty string is written ``""`` and so stays distinct from
an omitted field.
"""

from __future__ import annotations

import json

from .scalars import JSON, read_atom, read_text, write_atom, write_text

__all__ = ["render", "parse", "NAME"]

NAME = "R_LEANLIKE"

_ACTION_JSON = (
    "typing", "warrant", "goal_effect", "scope_effect", "branch_effect",
    "candidate_effect", "epistemic_effect", "preconditions", "obligations_created",
    "obligations_discharged",
)


def _atoms(values) -> str:
    return ", ".join(write_atom(v) for v in values)


def _split_atoms(rest: str) -> list[str]:
    """Comma-separated atoms, respecting JSON quoting so a quoted comma cannot split."""
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
    return [o for o in out if o != "" or True]


def _opt(flag: str, value) -> str:
    """``None`` disappears; anything else is written, so absence and emptiness differ."""
    return "" if value is None else f" {flag}{write_atom(str(value))}"


def _head(rec: dict) -> str:
    head = write_atom(rec["key"])
    if rec["id"] != rec["key"]:
        head += f"={write_atom(rec['id'])}"
    return head


def _render_state(ir: dict, label: str) -> list[str]:
    st = ir[f"state_{label}"]
    out = [f"section {label}", "  open " + _atoms(st["active_scopes"])]
    for b in st["branches"]:
        line = f"  case {_head(b)} @{b['status']} in {write_atom(b['scope'])}"
        line += _opt(">>", b["conclusion"]) + _opt("part=", b["partition_id"])
        out.append(f"{line} : {write_text(b['predicate'])}")
    for c in st["claims"]:
        line = f"  {_head(c)} @{c['status']}"
        line += _opt("#", c["domain"]) + f" in {write_atom(c['scope'])}"
        if c["dependencies"]:
            line += " <-" + _atoms(c["dependencies"])
        out.append(f"{line} : {write_text(c['proposition'])}")
    for k in st["candidates"]:
        line = f"  ? {_head(k)} @{k['status']} in {write_atom(k['scope'])}"
        if k["constraint_ids"]:
            line += " !" + _atoms(k["constraint_ids"])
        if k["dependencies"]:
            line += " <-" + _atoms(k["dependencies"])
        line += _opt("src=", k["origin"]) + _opt("ev=", k["evidence_id"])
        line += _opt("res=", k["verification_result"])
        out.append(f"{line} : {write_text(k['proposition'])}")
    for o in st["obligations"]:
        line = f"  ! {_head(o)} @{o['status']}"
        line += " *mandatory" if o["mandatory"] else " *optional"
        if o["dependencies"]:
            line += " <-" + _atoms(o["dependencies"])
        line += _opt("src=", o["origin"]) + _opt("ev=", o["discharge_evidence_id"])
        out.append(f"{line} : {write_text(o['proposition'])}")
    for g in st["goals"]:
        line = f"  |- {_head(g)} @{g['status']} in {write_atom(g['scope'])}"
        out.append(f"{line} : {write_text(g['proposition'])}")
    out.append(f"end {label}")
    return out


def render(ir: dict) -> str:
    out = _render_state(ir, "before")
    a = ir["action"]
    out.append("")
    out.append(f"tactic {write_atom(a['id'])} : {write_atom(a['operation'])}")
    out.append(f"  summary {write_text(a['summary'])}")
    out.append("  yields " + (write_atom(a["output_id"]) if a["output_id"] else ""))
    out.append("  uses " + _atoms(a["dependencies"]))
    for f in _ACTION_JSON:
        out.append(f"  {f} " + json.dumps(a[f], ensure_ascii=False, sort_keys=True))
    for ev in ir["evidence"]:
        out.append("")
        out.append(f"trace {_head(ev)} : {write_atom(ev['kind'])}")
        out.append(f"  status {write_atom(ev['status'])}")
        out.append(f"  trusted {'true' if ev['trusted'] else 'false'}")
        out.append("  supports " + (write_atom(ev["supports_rule"]) if ev["supports_rule"] else ""))
        out.append("  premises " + _atoms(ev["premise_ids"]))
        out.append("  payload " + json.dumps(ev["payload"], ensure_ascii=False, sort_keys=True))
    out.append("")
    out.extend(_render_state(ir, "after"))
    return "\n".join(out)


# --------------------------------------------------------------------------- reader


def _split_head(line: str) -> tuple[str, str]:
    """Split a record line at the top-level ``" : "`` separating metadata from the text."""
    depth = 0
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            _, i = JSON.raw_decode(line, i)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and line.startswith(" : ", i):
            return line[:i], line[i + 3 :]
        i += 1
    raise ValueError(f"no top-level ' : ' in {line[:60]!r}")


def _tokens(head: str) -> list[str]:
    """Whitespace-separated tokens, keeping JSON strings whole."""
    out: list[str] = []
    i = 0
    while i < len(head):
        if head[i].isspace():
            i += 1
            continue
        if head[i] == '"':
            _, end = JSON.raw_decode(head, i)
            out.append(head[i:end])
            i = end
            continue
        j = i
        while j < len(head) and not head[j].isspace():
            j += 1
        out.append(head[i:j])
        i = j
    return out


def _key_id(token: str) -> tuple[str, str]:
    if token.startswith('"'):
        value, end = JSON.raw_decode(token)
        rest = token[end:]
        key = value
    else:
        key, _, rest = token.partition("=")
        rest = ("=" + rest) if rest else ""
    if rest.startswith("="):
        return key, read_atom(rest[1:])
    return key, key


def _flags(tokens: list[str]) -> dict:
    """Interpret the annotation tokens that follow the key."""
    out: dict = {
        "status": None, "domain": None, "scope": None, "dependencies": [],
        "constraint_ids": [], "origin": None, "evidence_id": None,
        "verification_result": None, "conclusion": None, "partition_id": None,
        "mandatory": None, "discharge_evidence_id": None,
    }
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("@"):
            out["status"] = read_atom(t[1:])
        elif t.startswith("#"):
            out["domain"] = read_atom(t[1:])
        elif t == "in":
            i += 1
            out["scope"] = read_atom(tokens[i])
        elif t.startswith("<-"):
            out["dependencies"] = _split_atoms(" ".join([t[2:], *tokens[i + 1 :]]))
            break
        elif t.startswith("!") and t != "!":
            rest = " ".join([t[1:], *tokens[i + 1 :]])
            stop = next(
                (
                    j
                    for j, tok in enumerate(tokens[i + 1 :], start=i + 1)
                    if tok.startswith(("<-", "src=", "ev=", "res="))
                ),
                len(tokens),
            )
            out["constraint_ids"] = _split_atoms(" ".join([t[1:], *tokens[i + 1 : stop]]))
            i = stop - 1
            del rest
        elif t.startswith(">>"):
            out["conclusion"] = read_atom(t[2:])
        elif t.startswith("part="):
            out["partition_id"] = read_atom(t[5:])
        elif t.startswith("src="):
            out["origin"] = read_atom(t[4:])
        elif t.startswith("ev="):
            out["evidence_id"] = read_atom(t[3:])
            out["discharge_evidence_id"] = out["evidence_id"]
        elif t.startswith("res="):
            out["verification_result"] = read_atom(t[4:])
        elif t == "*mandatory":
            out["mandatory"] = True
        elif t == "*optional":
            out["mandatory"] = False
        i += 1
    return out


def _dep_flags(tokens: list[str]) -> dict:
    """``<-`` consumes the rest of the line, so constraint lists are read before it."""
    return _flags(tokens)


def _empty_state() -> dict:
    return {
        "claims": [], "candidates": [], "branches": [], "goals": [], "obligations": [],
        "active_scopes": [],
    }


def parse(text: str) -> dict:
    ir: dict = {"evidence": []}
    state: dict | None = None
    label = ""
    action: dict | None = None
    evidence: dict | None = None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("section "):
            label = stripped[8:].strip()
            state = _empty_state()
            action = evidence = None
            continue
        if stripped.startswith("end "):
            ir[f"state_{stripped[4:].strip()}"] = state
            state = None
            continue
        if stripped.startswith("tactic "):
            head, op = _split_head(stripped[7:])
            action = {
                "id": read_atom(head.strip()), "operation": read_atom(op.strip()),
                "summary": "", "output_id": None, "dependencies": [],
            }
            ir["action"] = action
            evidence = None
            continue
        if stripped.startswith("trace "):
            head, kind = _split_head(stripped[6:])
            key, rid = _key_id(_tokens(head)[0])
            evidence = {"key": key, "id": rid, "kind": read_atom(kind.strip()), "payload": {}}
            ir["evidence"].append(evidence)
            action = None
            continue
        if action is not None:
            name, _, rest = stripped.partition(" ")
            if name == "summary":
                action["summary"] = read_text(rest)
            elif name == "yields":
                action["output_id"] = read_atom(rest.strip()) if rest.strip() else None
            elif name == "uses":
                action["dependencies"] = _split_atoms(rest)
            elif name in _ACTION_JSON:
                action[name] = json.loads(rest)
            continue
        if evidence is not None:
            name, _, rest = stripped.partition(" ")
            if name == "status":
                evidence["status"] = read_atom(rest.strip())
            elif name == "trusted":
                evidence["trusted"] = rest.strip() == "true"
            elif name == "supports":
                evidence["supports_rule"] = read_atom(rest.strip()) if rest.strip() else None
            elif name == "premises":
                evidence["premise_ids"] = _split_atoms(rest)
            elif name == "payload":
                evidence["payload"] = json.loads(rest)
            continue
        if state is None:
            raise ValueError(f"record outside a section: {stripped[:50]!r}")
        if stripped.startswith("open "):
            state["active_scopes"] = _split_atoms(stripped[5:])
            continue
        head, body = _split_head(stripped)
        toks = _tokens(head)
        kind = "claims"
        if toks[0] == "case":
            kind, toks = "branches", toks[1:]
        elif toks[0] == "|-":
            kind, toks = "goals", toks[1:]
        elif toks[0] == "?":
            kind, toks = "candidates", toks[1:]
        elif toks[0] == "!":
            kind, toks = "obligations", toks[1:]
        key, rid = _key_id(toks[0])
        f = _dep_flags(toks[1:])
        text_value = read_text(body)
        if kind == "claims":
            rec = {
                "key": key, "id": rid, "proposition": text_value, "status": f["status"],
                "scope": f["scope"], "domain": f["domain"],
                "dependencies": f["dependencies"],
            }
        elif kind == "goals":
            rec = {
                "key": key, "id": rid, "proposition": text_value,
                "status": f["status"], "scope": f["scope"],
            }
        elif kind == "branches":
            rec = {
                "key": key, "id": rid, "predicate": text_value, "status": f["status"],
                "scope": f["scope"], "conclusion": f["conclusion"],
                "partition_id": f["partition_id"],
            }
        elif kind == "candidates":
            rec = {
                "key": key, "id": rid, "proposition": text_value, "status": f["status"],
                "scope": f["scope"], "constraint_ids": f["constraint_ids"],
                "origin": f["origin"], "dependencies": f["dependencies"],
                "evidence_id": f["evidence_id"],
                "verification_result": f["verification_result"],
            }
        else:
            rec = {
                "key": key, "id": rid, "proposition": text_value, "status": f["status"],
                "mandatory": bool(f["mandatory"]), "origin": f["origin"],
                "dependencies": f["dependencies"],
                "discharge_evidence_id": f["discharge_evidence_id"],
            }
        state[kind].append(rec)
    return ir
