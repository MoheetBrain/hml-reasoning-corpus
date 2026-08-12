"""The only label seam: current frozen importer and verifier."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def _load_hml() -> tuple[Any, Any, Any]:
    root = os.environ.get("HML_FROZEN_PATH")
    if not root:
        raise RuntimeError("HML_FROZEN_PATH is required")
    source = str(Path(root).resolve() / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    from hamiltonian_lang.semantic_state import (  # type: ignore[import-not-found]
        import_transition,
        verify_replay,
        verify_runtime,
    )

    return import_transition, verify_replay, verify_runtime


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Import once, then record replay and no-attestation runtime results separately."""
    importer, replay, runtime = _load_hml()
    transition = importer(payload)
    return {
        "replay": replay(transition).to_dict(),
        "runtime_without_attestations": runtime(transition).to_dict(),
        "well_formed": True,
        "type_import_succeeded": True,
    }


def primary_result(payload: dict[str, Any]) -> dict[str, Any]:
    return verify_payload(payload)["replay"]
