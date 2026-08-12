from __future__ import annotations

import collections
import json
import time
from pathlib import Path
from typing import Any

from .constants import LEAN_RECORDS, LEAN_SHA256


RECOVERABILITY_FIELDS = (
    "state_before", "candidate_action", "state_after", "formal_backend_trace",
    "dependencies", "typed_action_arguments", "evidence", "preconditions",
    "obligations", "scope",
)


def qualify(path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    theorem_split = json.loads((path.parent / "theorem_split.json").read_text(encoding="utf-8"))
    split_manifest = json.loads((path.parent / "split_manifest.json").read_text(encoding="utf-8"))
    counts = collections.Counter()
    split_counts = collections.Counter()
    reasons = {contract: collections.Counter() for contract in ("ACTION_APPLICABILITY", "TRANSITION_CONFORMANCE", "EVIDENCE_SUFFICIENCY")}
    theorem_splits: dict[str, set[str]] = collections.defaultdict(set)
    effect_classes = collections.Counter()
    field_recoverable = collections.Counter()
    field_origins = {
        "state_before": "DIRECT_SOURCE",
        "candidate_action": "DIRECT_SOURCE",
        "state_after": "DIRECT_SOURCE",
        "formal_backend_trace": "FORMAL_BACKEND",
        "dependencies": "NOT_RECOVERABLE",
        "typed_action_arguments": "NOT_RECOVERABLE",
        "evidence": "NOT_RECOVERABLE",
        "preconditions": "NOT_RECOVERABLE",
        "obligations": "NOT_RECOVERABLE",
        "scope": "NOT_RECOVERABLE",
    }
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            counts["total"] += 1
            official_split = row.get("lean_official_split")
            theorem = row.get("theorem_id")
            split = theorem_split.get(theorem)
            if split and theorem:
                split_counts[split.upper()] += 1
                theorem_splits[theorem].add(split.upper())
            action = row.get("observed_action") or {}
            lean = row.get("lean") or {}
            effect_classes[action.get("effect_class", "MISSING")] += 1
            direct_before = isinstance(row.get("state_before"), dict) and bool(lean.get("raw_state_before"))
            direct_action = bool(lean.get("raw_tactic")) and isinstance(action, dict)
            direct_after = isinstance(row.get("state_after"), dict) and bool(lean.get("raw_state_after"))
            formal = row.get("compatibility", {}).get("frozen_hml_representable") is True
            for field, present in {
                "state_before": direct_before, "candidate_action": direct_action,
                "state_after": direct_after, "formal_backend_trace": formal,
            }.items():
                field_recoverable[field] += int(present)

            applicable = direct_before and direct_action and formal
            conforming = applicable and direct_after
            evidence = False  # No certificate/evidence envelope exists in this artifact.
            counts["ACTION_APPLICABILITY"] += int(applicable)
            counts["TRANSITION_CONFORMANCE"] += int(conforming)
            counts["EVIDENCE_SUFFICIENCY"] += int(evidence)
            if not applicable:
                reasons["ACTION_APPLICABILITY"]["MISSING_DIRECT_STATE_ACTION_OR_FORMAL_TRACE"] += 1
            if not conforming:
                reasons["TRANSITION_CONFORMANCE"]["MISSING_DIRECT_AFTER_STATE"] += 1
            reasons["EVIDENCE_SUFFICIENCY"]["NO_EVIDENCE_OR_CERTIFICATE_ENVELOPE"] += 1
    elapsed = time.perf_counter() - started
    if counts["total"] != LEAN_RECORDS:
        raise RuntimeError(f"qualification count mismatch: {counts['total']}")
    overlaps = {theorem: sorted(splits) for theorem, splits in theorem_splits.items() if len(splits) > 1}
    return {
        "artifact_sha256": LEAN_SHA256,
        "records_scanned": counts["total"],
        "eligible": {contract: counts[contract] for contract in ("ACTION_APPLICABILITY", "TRANSITION_CONFORMANCE", "EVIDENCE_SUFFICIENCY")},
        "qualification_semantics": {
            "ACTION_APPLICABILITY": "positive observed Lean tactic only; does not provide counterfactual negatives or an HML SemanticState",
            "TRANSITION_CONFORMANCE": "Lean-native before/tactic/after trace only; not HML transition conformance",
            "EVIDENCE_SUFFICIENCY": "requires an explicit evidence/certificate learner input, absent here",
        },
        "not_recoverable_reasons": {key: dict(value) for key, value in reasons.items()},
        "field_provenance": field_origins,
        "field_recoverable_counts": {field: field_recoverable[field] for field in RECOVERABILITY_FIELDS},
        "split_record_counts": dict(sorted(split_counts.items())),
        "split_manifest": split_manifest,
        "split_policy": "project theorem-level split, seed 20260811; raw LeanDojo train/val/test retained as source metadata only",
        "theorems": len(theorem_splits),
        "theorem_split_overlap_count": len(overlaps),
        "theorem_split_overlap_examples": dict(list(overlaps.items())[:20]),
        "effect_class_counts": dict(sorted(effect_classes.items())),
        "performance": {"wall_seconds": elapsed, "records_per_second": counts["total"] / elapsed, "workers": 1, "peak_memory_strategy": "streaming_one_record"},
        "gold_prohibited_provenance": {"LLM_GUESS": 0, "HEURISTIC_GUESS": 0},
    }
