"""Decompose a recorded Lean tactic state into its actual semantic components.

Why this exists
---------------
The 50K corpus wraps each Lean proof step as a transition whose ``state_before`` holds
exactly **one** claim: a single string containing the whole tactic state. Measured over
20,000 canonical records, every state has 1 claim, 0 candidates, 0 branches, 0 goals,
0 obligations and 1 scope. Eight of the verifier's ten invariants have nothing to check
there, and a representation comparison over it degenerates into four ways of wrapping one
opaque string.

The structure is not missing from the data -- it is missing from the *wrapper*. A Lean
tactic state already is a typed context plus a goal::

    case neg
    α : Type u_1
    r : α → α → Prop
    bad : Set ℕ := {m | ∀ (n : ℕ), m < n → ¬r (f m) (f n)}
    hbad : bad.Finite
    ⊢ ∃ m, ∀ (n : ℕ), m ≤ n → n ∉ bad

That is a branch label, four typed declarations (one of them a local definition), and a
goal. Recovering them is parsing, not invention: every identifier, type and proposition
below comes verbatim from the recorded state. Measured over 20,000 records the contexts
average 12.6 declarations and 100% carry an explicit goal, so the structure recovered here
is the corpus's own.

What is deliberately not done
-----------------------------
No attempt is made to parse Lean *terms*. A declaration's type is kept as its exact source
text. Parsing type expressions would mean adopting a Lean grammar this repository does not
own, and every downstream claim would then rest on that grammar being right.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

__all__ = ["Declaration", "GoalBlock", "LeanState", "parse_lean_state", "classify_domain"]

#: Lean marks inaccessible names with a dagger, often followed by a superscript index.
INACCESSIBLE = "✝"
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"

#: A declaration line: one or more binder names, a colon, a type. The name group refuses
#: anything containing the tokens that would make it a term rather than a binder list, so a
#: continuation line such as ``  (h : p) → q`` is not mistaken for a declaration.
_DECL = re.compile(
    r"^(?P<names>[^\s:(){}\[\],→←↔⊢=<>|]+(?:[ \t]+[^\s:(){}\[\],→←↔⊢=<>|]+)*)[ \t]*:[ \t]?(?P<rest>.*)$"
)

_TURNSTILE = "⊢"


@dataclass(frozen=True)
class Declaration:
    """One binder group from a tactic context: ``names : type`` or ``name : type := value``."""

    names: tuple[str, ...]
    type_text: str
    value_text: str | None = None
    #: 0-based position in the context. Binder order is real information: a later binder may
    #: depend on an earlier one, never the reverse.
    index: int = 0

    @property
    def is_definition(self) -> bool:
        return self.value_text is not None

    @property
    def inaccessible(self) -> bool:
        return any(INACCESSIBLE in n for n in self.names)


@dataclass(frozen=True)
class GoalBlock:
    """One focused goal: its optional case label, its context, and its target."""

    case_label: str | None
    declarations: tuple[Declaration, ...]
    goal_text: str

    @property
    def binder_names(self) -> tuple[str, ...]:
        return tuple(n for d in self.declarations for n in d.names)


@dataclass(frozen=True)
class LeanState:
    blocks: tuple[GoalBlock, ...]
    #: True for the literal terminal state Lean prints when a proof is complete.
    no_goals: bool = False
    #: Lines the parser could not classify. Non-empty means the decomposition is partial and
    #: the record must not be used as a canonical source.
    unparsed: tuple[str, ...] = field(default_factory=tuple)

    @property
    def primary(self) -> GoalBlock | None:
        return self.blocks[0] if self.blocks else None

    @property
    def clean(self) -> bool:
        return not self.unparsed and (self.no_goals or bool(self.blocks))


def _strip_index(name: str) -> str:
    """``inst✝⁵`` -> ``inst✝``. The superscript is a disambiguator, not part of the name."""
    return name.rstrip(_SUPERSCRIPTS)


def classify_domain(type_text: str) -> str:
    """A coarse, purely syntactic domain label for a declaration's type.

    Deliberately coarse. The verifier's ``TYPE_DOMAIN`` invariant compares declared domains
    for agreement; it does not need a Lean typechecker, and pretending to more precision
    than the surface supports would put unearned confidence into every record.
    """
    t = type_text.strip()
    if t.startswith("Type") or t.startswith("Sort") or t == "Prop":
        return "Universe"
    if t.startswith("Prop"):
        return "Proposition"
    # A type whose head is an arrow into Prop, or which reads as a statement, is a
    # proposition; anything else is treated as data. Both are recorded as *declared*
    # domains, never as verified ones.
    if re.match(r"^[∀∃¬]", t) or _TURNSTILE in t:
        return "Proposition"
    if re.search(r"(?:^|\s)(?:→|->)\s*Prop\s*$", t):
        return "Predicate"
    head = re.split(r"[\s(]", t, 1)[0]
    if head and head[0].isupper():
        return "Data"
    if head and (head[0].islower() or unicodedata.category(head[0]) == "Ll"):
        # A lowercase head is usually a bound type variable applied to arguments.
        return "Data"
    return "Data"


def _split_value(rest: str) -> tuple[str, str | None]:
    """Split ``T := v`` into type and value, respecting bracket depth."""
    depth = 0
    i = 0
    while i < len(rest) - 1:
        ch = rest[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and rest.startswith(":=", i):
            return rest[:i].strip(), rest[i + 2 :].strip()
        i += 1
    return rest.strip(), None


def _parse_block(lines: list[str]) -> tuple[GoalBlock | None, list[str]]:
    case_label: str | None = None
    decls: list[Declaration] = []
    goal_lines: list[str] = []
    unparsed: list[str] = []
    in_goal = False
    pending: list[str] | None = None  # continuation buffer for the current declaration

    def flush() -> None:
        nonlocal pending
        if pending is None:
            return
        head, *tail = pending
        m = _DECL.match(head)
        if m:
            body = " ".join([m.group("rest").strip(), *[t.strip() for t in tail]]).strip()
            type_text, value_text = _split_value(body)
            names = tuple(_strip_index(n) for n in m.group("names").split())
            decls.append(
                Declaration(names=names, type_text=type_text, value_text=value_text, index=len(decls))
            )
        pending = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if in_goal:
            goal_lines.append(line.strip())
            continue
        if line.startswith("case "):
            flush()
            case_label = line[5:].strip()
            continue
        if line.lstrip().startswith(_TURNSTILE):
            flush()
            in_goal = True
            goal_lines.append(line.lstrip()[1:].strip())
            continue
        # A continuation line is indented and does not itself open a declaration.
        if raw.startswith((" ", "\t")) and pending is not None:
            pending.append(line)
            continue
        if _DECL.match(line):
            flush()
            pending = [line]
            continue
        if pending is not None:
            pending.append(line)
            continue
        unparsed.append(line)
    flush()

    goal_text = " ".join(goal_lines).strip()
    if not goal_text:
        return None, unparsed + [l for l in lines if l.strip()]
    return GoalBlock(case_label=case_label, declarations=tuple(decls), goal_text=goal_text), unparsed


def parse_lean_state(text: str) -> LeanState:
    """Decompose a recorded Lean tactic state. Never raises; partial results are flagged."""
    stripped = text.strip()
    if stripped in ("no goals", "") or stripped.startswith("no goals"):
        return LeanState(blocks=(), no_goals=True)

    blocks: list[GoalBlock] = []
    unparsed: list[str] = []
    # Lean separates independent goals with a blank line.
    for chunk in re.split(r"\n[ \t]*\n", stripped):
        lines = chunk.split("\n")
        block, bad = _parse_block(lines)
        unparsed.extend(bad)
        if block is not None:
            blocks.append(block)
    return LeanState(blocks=tuple(blocks), no_goals=False, unparsed=tuple(unparsed))
