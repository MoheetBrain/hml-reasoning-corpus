"""Validation helpers for the small, canonical Gold-10 corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SUPPORT_CLASSES = {
    "EXPRESSIBLE_CURRENT_HML",
    "EXPRESSIBLE_WITH_LIBRARY",
    "REQUIRES_MINOR_SURFACE_EXTENSION",
    "REQUIRES_NEW_CORE_SEMANTIC",
    "AMBIGUOUS_OR_HUMAN_IMPLICIT",
    "NOT_MACHINE_VERIFIABLE",
}
STAGE_IDS = set(range(1, 17))
EXPECTED_IDS = {f"G{i:02d}" for i in range(1, 11)}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(obj: dict[str, Any], keys: list[str], where: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{where}: missing {key}")


def validate_trajectory(doc: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    _require(
        doc,
        [
            "schema_version", "example_id", "dataset_split", "title", "problem",
            "gold_status", "hml_status", "reasoning_stages_used", "semantic_gap_ids",
            "states", "actions", "goal_discharged", "renderings", "verification",
        ],
        "trajectory",
        errors,
    )
    example_id = doc.get("example_id", "?")
    if example_id not in EXPECTED_IDS:
        errors.append(f"{example_id}: invalid example id")
    if doc.get("dataset_split") != "GOLD-10":
        errors.append(f"{example_id}: dataset_split is not GOLD-10")
    if doc.get("gold_status") != "GOLD_CANONICAL_VERIFIED":
        errors.append(f"{example_id}: canonical trajectory is not marked verified")
    if doc.get("hml_status") == "FAITHFUL" and doc.get("semantic_gap_ids"):
        errors.append(f"{example_id}: semantic-gap example silently marked FAITHFUL")
    if not set(doc.get("reasoning_stages_used", [])) <= STAGE_IDS:
        errors.append(f"{example_id}: reasoning_stages_used contains an invalid stage")

    states = doc.get("states", [])
    actions = doc.get("actions", [])
    state_ids = [s.get("id") for s in states if isinstance(s, dict)]
    action_ids = [a.get("id") for a in actions if isinstance(a, dict)]
    if len(state_ids) != len(set(state_ids)):
        errors.append(f"{example_id}: duplicate state id")
    if len(action_ids) != len(set(action_ids)):
        errors.append(f"{example_id}: duplicate action id")
    if not states or states[0].get("id") != "S0":
        errors.append(f"{example_id}: trajectory does not begin at S0")

    known_claims: set[str] = set()
    for index, state in enumerate(states):
        where = f"{example_id}/{state.get('id', '?')}"
        _require(
            state,
            [
                "id", "declarations", "objects", "types_domains", "facts", "assumptions",
                "goals", "subgoals", "unresolved_obligations", "epistemic_status",
                "dependencies", "provenance",
            ],
            where,
            errors,
        )
        provenance = state.get("provenance", {})
        if provenance.get("source_problem") != example_id:
            errors.append(f"{where}: provenance points at another problem")
        for field in ("facts", "assumptions", "goals", "subgoals", "unresolved_obligations", "epistemic_status"):
            for claim in state.get(field, []):
                if not isinstance(claim, dict) or not claim.get("id"):
                    errors.append(f"{where}: malformed claim in {field}")
                else:
                    known_claims.add(claim["id"])
        if index and state.get("id") == "S0":
            errors.append(f"{where}: S0 appears more than once")

    for index, action in enumerate(actions):
        where = f"{example_id}/{action.get('id', '?')}"
        _require(
            action,
            [
                "id", "from_state", "to_state", "inputs", "operation", "dependencies",
                "warrant", "preconditions", "resulting_fact", "state_change", "verification",
                "reasoning_stages", "hml_support", "semantic_gap_ids", "provenance",
            ],
            where,
            errors,
        )
        if action.get("from_state") not in state_ids or action.get("to_state") not in state_ids:
            errors.append(f"{where}: state reference does not resolve")
        if index == 0 and action.get("from_state") != "S0":
            errors.append(f"{where}: first action does not start at S0")
        if index and action.get("from_state") != actions[index - 1].get("to_state"):
            errors.append(f"{where}: action chain is not contiguous")
        if action.get("from_state") not in action.get("inputs", []):
            errors.append(f"{where}: inputs omit from_state")
        if action.get("hml_support") not in SUPPORT_CLASSES:
            errors.append(f"{where}: invalid HML support class")
        if not set(action.get("reasoning_stages", [])) <= STAGE_IDS:
            errors.append(f"{where}: invalid reasoning stage")
        if not action.get("provenance", {}).get("source_step"):
            errors.append(f"{where}: action has no provenance")
        result = action.get("resulting_fact", {})
        if result.get("id"):
            known_claims.add(result["id"])
        for dependency in action.get("dependencies", []):
            if dependency.startswith("fact:") and dependency not in known_claims:
                errors.append(f"{where}: dependency {dependency} does not resolve")
        if set(action.get("semantic_gap_ids", [])) - set(doc.get("semantic_gap_ids", [])):
            errors.append(f"{where}: action references an undeclared trajectory gap")
        if action.get("hml_support") == "EXPRESSIBLE_CURRENT_HML" and action.get("semantic_gap_ids"):
            errors.append(f"{where}: current-HML action has a semantic gap")

    renderings = doc.get("renderings", {})
    for key in ("hml", "structured_english", "structured_control"):
        rendering = renderings.get(key, {})
        path_text = rendering.get("path")
        if not path_text:
            errors.append(f"{example_id}: rendering {key} has no path")
        elif not (root / path_text).is_file():
            errors.append(f"{example_id}: rendering path missing: {path_text}")
    hml = renderings.get("hml", {})
    if hml.get("hml_core_sha") != doc.get("verification", {}).get("hml_core_sha"):
        errors.append(f"{example_id}: HML rendering and verification SHA disagree")
    if doc.get("verification", {}).get("canonical_status") != "VERIFIED":
        errors.append(f"{example_id}: canonical verification is not VERIFIED")
    return errors

def gold_paths(root: Path) -> list[Path]:
    return sorted((root / "data" / "gold_10").glob("G[0-9][0-9].json"))


def validate_gold10(root: Path) -> list[str]:
    errors: list[str] = []
    paths = gold_paths(root)
    if len(paths) != 10:
        errors.append(f"expected exactly 10 Gold trajectory files, found {len(paths)}")
    found: set[str] = set()
    for path in paths:
        try:
            doc = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot load JSON: {exc}")
            continue
        found.add(doc.get("example_id", ""))
        errors.extend(validate_trajectory(doc, root))
    if found != EXPECTED_IDS:
        errors.append(f"Gold ids are {sorted(found)}, expected {sorted(EXPECTED_IDS)}")
    return errors
