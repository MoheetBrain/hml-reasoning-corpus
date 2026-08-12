from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def verify(transition: dict[str, Any]) -> dict[str, Any]:
    source = str(Path(os.environ["HML_FROZEN_PATH"]).resolve() / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    from hamiltonian_lang.semantic_state import import_transition, verify_replay
    return verify_replay(import_transition(transition)).to_dict()
