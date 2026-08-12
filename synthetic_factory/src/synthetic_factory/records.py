"""Canonical JSON, structural diffs, and minimal-pair record construction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import CORPUS_SHA, HML_SHA, HML_TAG, PROTOCOL_VERSION, SCHEMA_VERSION


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def source_bundle_sha(factory_root: Path) -> str:
    candidates = [factory_root / "protocol.yaml", factory_root / "schemas"]
    files = [factory_root / "src" / "synthetic_factory" / "constants.py"]
    for candidate in candidates:
        if candidate.is_file():
            files.append(candidate)
        elif candidate.is_dir():
            files.extend(path for path in candidate.rglob("*") if path.is_file())
    files.extend(
        path
        for path in (factory_root / "src" / "synthetic_factory").rglob("*.py")
        if path not in files
    )
    h = hashlib.sha256()
    for path in sorted(set(files)):
        h.update(str(path.relative_to(factory_root)).encode())
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


@dataclass(frozen=True)
class Difference:
    path: str
    before: Any
    after: Any


def differences(before: Any, after: Any, path: str = "$") -> list[Difference]:
    if type(before) is not type(after):
        return [Difference(path, before, after)]
    if isinstance(before, dict):
        out: list[Difference] = []
        for key in sorted(set(before) | set(after)):
            child = f"{path}.{key}"
            if key not in before:
                out.append(Difference(child, None, after[key]))
            elif key not in after:
                out.append(Difference(child, before[key], None))
            else:
                out.extend(differences(before[key], after[key], child))
        return out
    if isinstance(before, list):
        out = []
        for index in range(max(len(before), len(after))):
            child = f"{path}[{index}]"
            if index >= len(before):
                out.append(Difference(child, None, after[index]))
            elif index >= len(after):
                out.append(Difference(child, before[index], None))
            else:
                out.extend(differences(before[index], after[index], child))
        return out
    return [] if before == after else [Difference(path, before, after)]


def node_count(value: Any) -> int:
    if isinstance(value, dict):
        return 1 + sum(node_count(v) for v in value.values())
    if isinstance(value, list):
        return 1 + sum(node_count(v) for v in value)
    return 1


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(
                min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b))
            )
        previous = current
    return previous[-1]


def changed_value_edit_distance(diff: Difference) -> int:
    left = canonical_json(diff.before)
    right = canonical_json(diff.after)
    return levenshtein(left, right)


def build_pair(
    *,
    source: dict[str, Any],
    mutated: dict[str, Any],
    mutation_family: str,
    mutation_description: str,
    expected_error_class: str,
    original_result: dict[str, Any],
    mutated_result: dict[str, Any],
    original_runtime_result: dict[str, Any],
    mutated_runtime_result: dict[str, Any],
    generator_sha: str,
    source_path: str,
    source_file_sha256: str,
) -> dict[str, Any]:
    diff = differences(source, mutated)
    if len(diff) != 1:
        raise ValueError(f"minimal-pair contract requires one changed field, got {len(diff)}")
    change = diff[0]
    if mutated_result.get("error_class") != expected_error_class:
        raise ValueError(
            f"mutation expected {expected_error_class}, got {mutated_result.get('error_class')}"
        )
    source_meta = source.get("source") or {}
    cid = source["case_id"]
    action = source["action"]
    mutated_action = mutated["action"]
    proposed_after = mutated["state_after"]
    causal_classification = {
        "BRANCH_JOIN": "SEMANTIC_HARD_PAIR",
        "CANDIDATES": "SEMANTIC_HARD_PAIR",
        "SCOPE": "AMBIGUOUS",
        "TYPE_DOMAIN": "AMBIGUOUS",
    }.get(mutation_family, "STRUCTURAL_PAIR")
    causal_note = {
        "SEMANTIC_HARD_PAIR": (
            "The changed certificate content is well formed and the target invariant, "
            "rather than parsing or frame drift, explains rejection."
        ),
        "STRUCTURAL_PAIR": (
            "This is a useful verifier-harness probe, but its missing identity or direct "
            "status/effect inconsistency is too easy to count as a hard mathematical negative."
        ),
        "AMBIGUOUS": (
            "The intended invariant fires, but the one-sided prior-state mutation also "
            "causes a frame finding; causal isolation is therefore incomplete."
        ),
    }[causal_classification]
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol": PROTOCOL_VERSION,
        "pair_id": f"CF-{cid}",
        "source_record_id": cid,
        "source_theorem_id": source_meta.get("source_row_id") or source_meta.get("problem"),
        "source_transition_id": cid,
        "original_state": source["state_before"],
        "mutated_state": mutated["state_before"],
        "original_candidate_action": action,
        "mutated_candidate_action": mutated_action,
        "mutation_family": mutation_family,
        "exact_changed_field": change.path,
        "change_count": 1,
        "original_verifier_result": original_result,
        "mutated_verifier_result": mutated_result,
        "runtime_diagnostic": {
            "original": original_runtime_result,
            "mutated": mutated_runtime_result,
            "note": (
                "Runtime ignores imported evidence status and requires checker attestations. "
                "The primary counterfactual label is source-evidence-preserving replay; no "
                "generated positive is accepted from this diagnostic."
            ),
        },
        "original_state_after": source["state_after"],
        "mutated_state_after_if_valid": None,
        "proposed_mutated_state_after": proposed_after,
        "failure_code_if_invalid": mutated_result.get("error_class"),
        "preconditions": mutated_action.get("preconditions") or [],
        "obligations": {
            "created": mutated_action.get("obligations_created") or [],
            "discharged": mutated_action.get("obligations_discharged") or [],
            "state_before": mutated["state_before"].get("obligations") or {},
            "state_after": proposed_after.get("obligations") or {},
        },
        "dependencies": mutated_action.get("dependencies") or [],
        "scope": {
            "active_before": mutated["state_before"].get("active_scopes") or [],
            "active_after": proposed_after.get("active_scopes") or [],
            "scope_effect": mutated_action.get("scope_effect") or {},
        },
        "hml_sha": HML_SHA,
        "corpus_sha": CORPUS_SHA,
        "generator_sha": generator_sha,
        "verifier_version": HML_TAG,
        "verifier_trust_mode": "OFFLINE_REPLAY",
        "source_provenance": {
            "corpus_path": source_path,
            "source_file_sha256": source_file_sha256,
            "source_payload_sha256": digest(source),
            "source": source_meta,
        },
        "minimality": {
            "number_of_changed_semantic_fields": 1,
            "number_of_changed_ast_nodes": 1,
            "changed_value_ast_nodes_before": node_count(change.before),
            "changed_value_ast_nodes_after": node_count(change.after),
            "changed_value_character_edit_distance": changed_value_edit_distance(change),
            "text_edit_distance_is_diagnostic_only": True,
            "before_value": change.before,
            "after_value": change.after,
        },
        "causality": {
            "classification": causal_classification,
            "explanation": f"{mutation_description} {causal_note}",
            "parser_or_serialization_artifact": False,
            "verifier_error_matches_target_invariant": True,
            "independently_hard_enough_for_production": causal_classification
            == "SEMANTIC_HARD_PAIR",
        },
        "source_transition": source,
        "counterfactual_transition": mutated,
    }
