"""R_TYPED_AST: the canonical state as a typed s-expression tree.

The contrast this arm supplies is **explicit structure with no natural-language cues**.
Every record is a tagged node, every field is a named slot, and nesting is carried by
parentheses rather than by indentation or prose. It is the representation a compiler would
choose, and the one closest to the machine object itself.

It is not "HML with different brackets". HML's surface is indentation-scoped, uses bare
keywords, and gives each record kind a fixed field order with optional fields omitted
entirely. This is a uniform tagged tree in which every slot is named and always present.
A reader that can follow one is not thereby able to follow the other, which is what makes
the pair a usable contrast.
"""

from __future__ import annotations

import json

from .scalars import JSON, read_atom, write_atom

__all__ = ["render", "parse", "NAME"]

NAME = "R_TYPED_AST"

_STATE_KINDS = ("claims", "candidates", "branches", "goals", "obligations")

#: Field order per record kind. Fixed so the render is deterministic; the *reader* is
#: order-independent, so a hand-edited tree still loads.
_FIELDS = {
    "claims": ("id", "proposition", "status", "scope", "domain", "dependencies"),
    "candidates": (
        "id", "proposition", "status", "scope", "constraint_ids", "origin",
        "dependencies", "evidence_id", "verification_result",
    ),
    "branches": ("id", "predicate", "status", "scope", "conclusion", "partition_id"),
    "goals": ("id", "proposition", "status", "scope"),
    "obligations": (
        "id", "proposition", "status", "mandatory", "origin", "dependencies",
        "discharge_evidence_id",
    ),
}
_SINGULAR = {
    "claims": "claim", "candidates": "candidate", "branches": "branch",
    "goals": "goal", "obligations": "obligation",
}
_TAG_TO_KIND = {v: k for k, v in _SINGULAR.items()}

_ACTION_FIELDS = (
    "id", "operation", "summary", "output_id", "dependencies", "preconditions",
    "obligations_created", "obligations_discharged", "typing", "warrant", "goal_effect",
    "scope_effect", "branch_effect", "candidate_effect", "epistemic_effect",
)
_EVIDENCE_FIELDS = (
    "id", "kind", "status", "trusted", "supports_rule", "premise_ids", "payload",
)

#: Fields whose value is a list of identifiers rather than one opaque JSON value. They are
#: emitted as nested atom lists so binder names stay visible instead of becoming JSON arrays.
_ID_LISTS = frozenset({"dependencies", "constraint_ids", "premise_ids"})


def _val(name: str, value) -> str:
    if name in _ID_LISTS:
        return "(" + " ".join(write_atom(v) for v in value) + ")"
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _record(kind: str, rec: dict) -> str:
    body = " ".join(f"({f} {_val(f, rec[f])})" for f in _FIELDS[kind])
    return f"  ({_SINGULAR[kind]} {write_atom(rec['key'])} {body})"


def render(ir: dict) -> str:
    out = ["(transition"]
    for label in ("before", "after"):
        st = ir[f"state_{label}"]
        out.append(f" (state {label}")
        out.append("  (scopes " + " ".join(write_atom(s) for s in st["active_scopes"]) + ")")
        for kind in _STATE_KINDS:
            out.extend(_record(kind, rec) for rec in st[kind])
        out.append(" )")
    a = ir["action"]
    out.append(" (action " + " ".join(f"({f} {_val(f, a[f])})" for f in _ACTION_FIELDS) + ")")
    for ev in ir["evidence"]:
        body = " ".join(f"({f} {_val(f, ev[f])})" for f in _EVIDENCE_FIELDS)
        out.append(f" (evidence {write_atom(ev['key'])} {body})")
    out.append(")")
    return "\n".join(out)


# --------------------------------------------------------------------------- reader


def _tokenize(text: str) -> list:
    """Parens and values. A JSON literal is consumed whole; anything else is a bare symbol."""
    toks: list = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            toks.append(ch)
            i += 1
            continue
        if ch in '"{[' or ch == "-" or ch.isdigit():
            try:
                value, end = JSON.raw_decode(text, i)
            except json.JSONDecodeError:
                pass
            else:
                toks.append(("json", value))
                i = end
                continue
        j = i
        while j < n and not text[j].isspace() and text[j] not in "()":
            j += 1
        raw = text[i:j]
        toks.append(
            ("json", True) if raw == "true"
            else ("json", False) if raw == "false"
            else ("json", None) if raw == "null"
            else ("sym", raw)
        )
        i = j
    return toks


def _tree(toks: list, pos: int = 0):
    if pos >= len(toks) or toks[pos] != "(":
        raise ValueError(f"expected '(' at token {pos}")
    node: list = []
    pos += 1
    while pos < len(toks):
        t = toks[pos]
        if t == ")":
            return node, pos + 1
        if t == "(":
            child, pos = _tree(toks, pos)
            node.append(child)
        else:
            node.append(t)
            pos += 1
    raise ValueError("unterminated node")


def _tag(node) -> str:
    head = node[0] if isinstance(node, list) else node
    if isinstance(head, tuple):
        return head[1] if head[0] == "sym" else str(head[1])
    raise ValueError(f"expected a tag, got {head!r}")


def _plain(node):
    if isinstance(node, tuple):
        return node[1] if node[0] == "json" else read_atom(node[1])
    raise ValueError(f"expected a leaf, got {node!r}")


def _slots(node: list, start: int) -> dict:
    out: dict = {}
    for child in node[start:]:
        if not isinstance(child, list) or not child:
            raise ValueError(f"expected a field node, got {child!r}")
        name = _tag(child)
        if name in _ID_LISTS:
            # ``(dependencies (a b))`` -- the atoms live in a nested node, not as siblings,
            # so an identifier that happens to read as a field name cannot be mistaken for
            # one. An empty list renders as ``()`` and parses to the empty node.
            inner = child[1] if len(child) > 1 else []
            out[name] = [_plain(c) for c in inner]
        elif len(child) == 1:
            out[name] = None
        else:
            out[name] = _plain(child[1])
    return out


def parse(text: str) -> dict:
    tree, _ = _tree(_tokenize(text))
    if _tag(tree) != "transition":
        raise ValueError("not a transition tree")
    ir: dict = {"evidence": []}
    for node in tree[1:]:
        tag = _tag(node)
        if tag == "state":
            label = _plain(node[1])
            st: dict = {k: [] for k in _STATE_KINDS}
            st["active_scopes"] = []
            for child in node[2:]:
                ctag = _tag(child)
                if ctag == "scopes":
                    st["active_scopes"] = [_plain(c) for c in child[1:]]
                    continue
                kind = _TAG_TO_KIND[ctag]
                slots = _slots(child, 2)
                rec = {"key": _plain(child[1])}
                rec.update({f: slots[f] for f in _FIELDS[kind]})
                st[kind].append(rec)
            ir[f"state_{label}"] = st
        elif tag == "action":
            slots = _slots(node, 1)
            ir["action"] = {f: slots[f] for f in _ACTION_FIELDS}
        elif tag == "evidence":
            slots = _slots(node, 2)
            rec = {"key": _plain(node[1])}
            rec.update({f: slots[f] for f in _EVIDENCE_FIELDS})
            ir["evidence"].append(rec)
        else:
            raise ValueError(f"unknown node {tag!r}")
    return ir
