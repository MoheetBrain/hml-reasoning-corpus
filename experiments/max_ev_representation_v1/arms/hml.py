"""R_HML: the frozen shipped view, used exactly as frozen.

This arm does not implement a renderer. It calls ``semantic_state.view.render_transition``
at the frozen model-language commit ``b011511e72572608eb7836d3b8a1a6bb794c890d``
(``hml-model-language-v1-freeze-2026-08-27``), which the mission fixes as ``R6_SHIPPED_VIEW``.

Re-implementing it here would measure a copy, and a copy that drifted by one field would
make the entire comparison a comparison with something HML is not. The only code below is
the adapter that puts the frozen view on the same ``render(ir) -> str`` / ``parse(str) -> ir``
interface as the other three arms, so the parity gate can treat all four identically.
"""

from __future__ import annotations

from hamiltonian_lang.semantic_state import view

from .common import from_ir, to_ir

__all__ = ["render", "parse", "NAME", "FROZEN_COMMIT"]

NAME = "R_HML"
FROZEN_COMMIT = "b011511e72572608eb7836d3b8a1a6bb794c890d"


def render(ir: dict) -> str:
    """Render through the frozen view. The IR is rebuilt into the typed object it expects."""
    return view.render_transition(from_ir(ir))


def parse(text: str) -> dict:
    return to_ir(view.parse_transition(text))
