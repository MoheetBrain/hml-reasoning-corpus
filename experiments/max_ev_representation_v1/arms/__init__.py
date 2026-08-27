"""The four representation arms (mission §4).

All four render the same model-facing projection of one canonical semantic object, and all
four read their own output back to an identical intermediate representation. No arm is
separately authored, so none can carry information another lacks; what differs between them
is syntax, vocabulary and framing, which is the variable under test.
"""

from __future__ import annotations

from . import hml, leanlike, structured_english, typed_ast

__all__ = ["ARMS", "ARM_NAMES", "render", "parse"]

#: Ordered so every report, table and tensor uses the same arm order.
ARMS = {
    hml.NAME: hml,
    typed_ast.NAME: typed_ast,
    leanlike.NAME: leanlike,
    structured_english.NAME: structured_english,
}
ARM_NAMES = tuple(ARMS)


def render(arm: str, ir: dict) -> str:
    return ARMS[arm].render(ir)


def parse(arm: str, text: str) -> dict:
    return ARMS[arm].parse(text)
