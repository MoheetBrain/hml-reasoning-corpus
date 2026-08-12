from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def learner_input(contract: str, transition: dict[str, Any]) -> dict[str, Any]:
    if contract == "ACTION_APPLICABILITY":
        return {"state_before": transition["state_before"], "action": transition["action"]}
    if contract == "TRANSITION_CONFORMANCE":
        return {
            "state_before": transition["state_before"],
            "action": transition["action"],
            "proposed_state_after": transition["state_after"],
        }
    if contract == "EVIDENCE_SUFFICIENCY":
        return {
            "state_before": transition["state_before"],
            "action": transition["action"],
            "proposed_state_after": transition["state_after"],
            "evidence": transition.get("evidence", {}),
        }
    raise ValueError(f"unknown prediction contract {contract}")


def learner_hash(contract: str, transition: dict[str, Any]) -> str:
    return digest(learner_input(contract, transition))


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join((canonical_json(row) + "\n").encode() for row in rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_bundle_sha(root: Path) -> str:
    h = hashlib.sha256()
    paths = list((root / "src").rglob("*.py")) + list((root / "schemas").glob("*.json"))
    paths.append(root / "protocol.json")
    for path in sorted(paths):
        h.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()
