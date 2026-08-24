#!/usr/bin/env python3
"""Deterministic, pre-action reasoning-state extraction for LeanDojo traces.

The extractor is intentionally representation-neutral.  It consumes only the
current raw Lean state and a bounded prefix of the successful source trajectory.
It never consumes the current/gold tactic or any future transition.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any, Iterable


SCHEMA_VERSION = "reasoning-state-v1.0.0"
HISTORY_WINDOW = 4

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_\u0080-\uffff\u2070-\u209f\u00b2\u00b3\u00b9]*")
_CASE = re.compile(r"^case\s+(.+?)\s*$")
_HYP = re.compile(r"^\s*([^:\n]+?)\s*:\s*(.+)$")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def tactic_family(tactic: str) -> str:
    """Return a conservative syntactic tactic head without interpreting it."""
    text = tactic.strip()
    while text.startswith(("·", "<;>", ";")):
        text = text.lstrip("·;<> ")
    if not text:
        return "EMPTY"
    match = re.match(r"(?:first\s*\||all_goals\s+|any_goals\s+)?([A-Za-z_][A-Za-z0-9_']*)", text)
    return match.group(1) if match else text.split(maxsplit=1)[0][:48]


def _target_shape(target: str) -> str:
    """Coarse, deterministic outer logical form; no theorem-specific labels."""
    compact = " ".join(target.split())
    if not compact:
        return "EMPTY"
    rules = (
        ("∀", "FORALL"), ("∃", "EXISTS"), ("↔", "IFF"), ("→", "IMPLIES"),
        ("¬", "NOT"), ("=", "EQUALITY"), ("≤", "ORDER"), ("<", "ORDER"),
        ("∈", "MEMBERSHIP"), ("⊆", "SUBSET"), ("∧", "AND"), ("∨", "OR"),
    )
    for marker, name in rules:
        if marker in compact:
            return name
    return "APPLICATION"


def parse_lean_state(raw_state: str) -> dict[str, Any]:
    """Parse only surface facts explicitly present in a Lean pretty-printed state."""
    if raw_state.strip() == "no goals":
        return {"goals": [], "open_goal_count": 0}

    goals: list[dict[str, Any]] = []
    case_label: str | None = None
    hypotheses: list[dict[str, str]] = []
    target_lines: list[str] = []
    in_target = False

    def finish() -> None:
        nonlocal case_label, hypotheses, target_lines, in_target
        if not target_lines and not hypotheses and case_label is None:
            return
        target = "\n".join(target_lines).strip()
        goals.append({
            "case_label": case_label,
            "hypotheses": hypotheses,
            "target": target,
            "target_shape": _target_shape(target),
            "goal_hash": digest_text(canonical({
                "case_label": case_label,
                "hypothesis_types": [h["type"] for h in hypotheses],
                "target": target,
            })),
        })
        case_label = None
        hypotheses = []
        target_lines = []
        in_target = False

    for line in raw_state.splitlines():
        if not line.strip():
            if in_target:
                finish()
            continue
        case_match = _CASE.match(line)
        if case_match and not in_target and (hypotheses or case_label is not None):
            finish()
        if case_match and not in_target:
            case_label = case_match.group(1)
            continue
        if "⊢" in line:
            if in_target:
                finish()
            in_target = True
            target_lines.append(line.split("⊢", 1)[1].strip())
            continue
        if in_target:
            # A new case line begins the next goal; otherwise Lean may wrap a target.
            if case_match:
                finish()
                case_label = case_match.group(1)
            else:
                target_lines.append(line.strip())
            continue
        hyp_match = _HYP.match(line)
        if hyp_match:
            hypotheses.append({"name": hyp_match.group(1).strip(), "type": hyp_match.group(2).strip()})
        elif hypotheses:
            hypotheses[-1]["type"] += " " + line.strip()
    finish()
    return {"goals": goals, "open_goal_count": len(goals)}


def dependency_edges(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive local declaration references from names appearing in later types/targets."""
    edges: set[tuple[int, str, str]] = set()
    for goal_index, goal in enumerate(parsed["goals"]):
        declarations = goal["hypotheses"]
        names = [item["name"] for item in declarations]
        for index, item in enumerate(declarations):
            tokens = set(_IDENTIFIER.findall(item["type"]))
            for prior in names[:index]:
                if prior in tokens:
                    edges.add((goal_index, prior, item["name"]))
        target_tokens = set(_IDENTIFIER.findall(goal["target"]))
        for name in names:
            if name in target_tokens:
                edges.add((goal_index, name, "@goal"))
    return [
        {"goal_index": goal_index, "from": source, "to": target}
        for goal_index, source, target in sorted(edges)
    ]


def state_delta(before: str, after: str) -> dict[str, Any]:
    b = parse_lean_state(before)
    a = parse_lean_state(after)
    b_hyp = Counter(h["name"] for g in b["goals"] for h in g["hypotheses"])
    a_hyp = Counter(h["name"] for g in a["goals"] for h in g["hypotheses"])
    added = list((a_hyp - b_hyp).elements())
    removed = list((b_hyp - a_hyp).elements())
    common = set(b_hyp) & set(a_hyp)
    b_types = {h["name"]: h["type"] for g in b["goals"] for h in g["hypotheses"]}
    a_types = {h["name"]: h["type"] for g in a["goals"] for h in g["hypotheses"]}
    rebound = sorted(name for name in common if b_types.get(name) != a_types.get(name))
    b_targets = [g["target"] for g in b["goals"]]
    a_targets = [g["target"] for g in a["goals"]]
    return {
        "open_goal_delta": a["open_goal_count"] - b["open_goal_count"],
        "target_changed": b_targets != a_targets,
        "hypotheses_added": sorted(added),
        "hypotheses_removed": sorted(removed),
        "hypotheses_rebound": rebound,
    }


def extract_reasoning_state(
    current_state: str,
    prior_events: Iterable[dict[str, str]],
) -> dict[str, Any]:
    """Extract V1 from information available strictly before the next action."""
    parsed = parse_lean_state(current_state)
    goals = parsed["goals"]
    all_events = list(prior_events)
    events = all_events[-HISTORY_WINDOW:]
    recent_actions = [
        {"offset": index - len(events), "family": tactic_family(event["action"])}
        for index, event in enumerate(events)
    ]
    recent_deltas = [
        {"offset": index - len(events), **state_delta(event["state_before"], event["state_after"])}
        for index, event in enumerate(events)
    ]
    active = goals[0] if goals else None
    dependencies = dependency_edges(parsed)
    families = [item["family"] for item in recent_actions]
    repeated = families[-1] if len(families) >= 2 and families[-1] == families[-2] else None
    return {
        "schema_version": SCHEMA_VERSION,
        "active_goal": None if active is None else {
            "position": 0,
            "goal_hash": active["goal_hash"],
            "target": active["target"],
            "target_shape": active["target_shape"],
            "hypothesis_count": len(active["hypotheses"]),
        },
        "open_goals": [
            {
                "position": index,
                "goal_hash": goal["goal_hash"],
                "case_label": goal["case_label"],
                "target_shape": goal["target_shape"],
                "hypothesis_count": len(goal["hypotheses"]),
            }
            for index, goal in enumerate(goals)
        ],
        "local_dependencies": dependencies,
        "active_scope": {
            "case_label": None if active is None else active["case_label"],
            "source_explicit": bool(active and active["case_label"]),
        },
        "trajectory_position": {"steps_completed": len(all_events)},
        "recent_actions": recent_actions,
        "recent_deltas": recent_deltas,
        "progress_summary": {
            "open_goal_count": len(goals),
            "recent_net_goal_delta": sum(item["open_goal_delta"] for item in recent_deltas),
            "repeated_recent_action_family": repeated,
        },
    }


def raw_history_payload(prior_events: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Neutral chronological control containing the exact bounded source history."""
    events = list(prior_events)[-HISTORY_WINDOW:]
    return [
        {
            "state_before": event["state_before"],
            "action": event["action"],
            "state_after": event["state_after"],
        }
        for event in events
    ]
