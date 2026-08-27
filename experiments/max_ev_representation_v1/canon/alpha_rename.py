"""Consistent alpha-renaming of the bound names in a canonical transition (mission §9A).

Two jobs, and the second is the one that protects the whole experiment.

**An OOD axis.** Binder spellings the training split never contained test whether the model
learned the *structure* of a dependency graph or memorised particular names.

**A memorisation control.** Every state here is recorded Mathlib, and every model under test
has read Mathlib. An arm whose surface resembles the original source could retrieve rather
than reason, and the Lean-like arm resembles it most. Renaming every bound name breaks
verbatim retrieval while leaving the mathematical structure -- types, dependencies, scopes,
quantifiers -- exactly as it was. Without this, a Lean-like win would be uninterpretable.

Only *bound* names are renamed. A global constant such as ``Set`` or ``Finite`` is part of
the mathematics and is left alone; renaming it would change the statement rather than its
presentation.
"""

from __future__ import annotations

import re
from dataclasses import replace

from hamiltonian_lang.semantic_state.model import Transition

from .build_canonical import IDENT

__all__ = ["rename_transition", "fresh_names"]

#: Binder alphabets that do not occur as bound names anywhere in the source corpus, so a
#: renamed state cannot collide with a remembered one.
_STEMS = (
    "u", "v", "w", "q", "z", "aa", "bb", "cc", "dd", "ee", "ff", "gg", "hh",
    "kk", "mm", "nn", "pp", "qq", "rr", "ss", "tt", "vv", "ww", "xx", "yy", "zz",
)


def fresh_names(originals: list[str], salt: str = "") -> dict[str, str]:
    """A stable, collision-free renaming for one context.

    Deterministic in the order of ``originals``, so the same state always renames the same
    way and an item can be regenerated from its id alone.
    """
    taken = set(originals)
    mapping: dict[str, str] = {}
    i = 0
    for name in originals:
        while True:
            stem = _STEMS[i % len(_STEMS)]
            suffix = i // len(_STEMS)
            candidate = f"{stem}{suffix}" if suffix else stem
            i += 1
            if candidate not in taken and candidate not in mapping.values():
                mapping[name] = candidate
                break
    return mapping


def _sub(text: str, mapping: dict[str, str]) -> str:
    """Replace whole identifier tokens only.

    A plain string replacement would rewrite ``f`` inside ``Finite``. Matching the identifier
    grammar and substituting only complete tokens keeps ``Set``, ``Finite`` and every other
    global constant untouched, and also rewrites the head of a projection such as ``bad.Finite``
    without disturbing the projection itself.
    """

    def one(m: re.Match) -> str:
        tok = m.group(0)
        if tok in mapping:
            return mapping[tok]
        head, dot, rest = tok.partition(".")
        if dot and head in mapping:
            return mapping[head] + "." + rest
        return tok

    return IDENT.sub(one, text)


def rename_transition(t: Transition, salt: str = "") -> Transition:
    """Rename every bound name in ``t``, consistently, everywhere it occurs."""
    originals = list(t.state_before.claims)
    mapping = fresh_names(originals, salt)
    if not mapping:
        return t

    def ren(name: str) -> str:
        return mapping.get(name, name)

    def ren_claims(claims: dict) -> dict:
        out = {}
        for key, c in claims.items():
            new_key = ren(key)
            out[new_key] = replace(
                c,
                id=ren(c.id),
                proposition=_sub(c.proposition, mapping),
                dependencies=tuple(ren(d) for d in c.dependencies),
            )
        return out

    def ren_goals(goals: dict) -> dict:
        return {
            k: replace(g, proposition=_sub(g.proposition, mapping)) for k, g in goals.items()
        }

    typing = dict(t.action.typing)
    if typing.get("input_domains"):
        typing["input_domains"] = {
            ren(k): v for k, v in typing["input_domains"].items()
        }
    action = replace(
        t.action,
        dependencies=tuple(ren(d) for d in t.action.dependencies),
        typing=typing,
    )
    evidence = {
        k: replace(v, premise_ids=tuple(ren(p) for p in v.premise_ids))
        for k, v in t.evidence.items()
    }
    return replace(
        t,
        action=action,
        state_before=replace(
            t.state_before,
            claims=ren_claims(t.state_before.claims),
            goals=ren_goals(t.state_before.goals),
        ),
        state_after=replace(
            t.state_after,
            claims=ren_claims(t.state_after.claims),
            goals=ren_goals(t.state_after.goals),
        ),
        evidence=evidence,
    )
