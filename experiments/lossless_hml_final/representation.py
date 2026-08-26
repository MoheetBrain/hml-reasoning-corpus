#!/usr/bin/env python3
"""Deterministic RAW and lossless-overlay views for generative Lean tactics."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable


IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_'\u0080-\uffff\u2070-\u209f\u00b2\u00b3\u00b9]*")
CASE = re.compile(r"^case\s+(.+?)\s*$", re.MULTILINE)
PROMPT_PREFIX = (
    "Generate the single most useful next Lean 4 tactic for the current proof state.\n"
    "Return exactly one executable raw Lean tactic and nothing else.\n\n"
    "<REASONING_CONTEXT>\n"
)
PROMPT_SUFFIX = "\n</REASONING_CONTEXT>\n\nOnly the next raw Lean tactic:"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def tactic_family(tactic: str) -> str:
    text = tactic.strip().lstrip("·;<> ")
    match = re.match(r"(?:first\s*\||all_goals\s+|any_goals\s+)?([A-Za-z_][A-Za-z0-9_']*)", text)
    return match.group(1) if match else (text.split(maxsplit=1)[0][:48] if text else "EMPTY")


def identifiers(tactic: str) -> list[str]:
    return sorted(set(IDENTIFIER.findall(tactic)))


def case_labels(state: str) -> list[str]:
    return CASE.findall(state)


def exact_event(event: dict[str, str], step: int) -> dict[str, Any]:
    return {
        "step_number": step,
        "state_before_exact": event["state_before"],
        "tactic_exact": event["action"],
        "state_after_exact": event["state_after"],
    }


def raw_payload(current_state: str, history: Iterable[dict[str, str]]) -> dict[str, Any]:
    events = list(history)
    return {
        "representation": "RAW_HISTORY",
        "current_lean_state_exact": current_state,
        "completed_history_exact": [exact_event(event, index) for index, event in enumerate(events)],
        "completed_steps": len(events),
    }


def overlay_payload(current_state: str, history: Iterable[dict[str, str]]) -> dict[str, Any]:
    events = list(history)
    organized = []
    for index, event in enumerate(events):
        item = exact_event(event, index)
        item["semantic_index"] = {
            "case_labels_after": case_labels(event["state_after"]),
            "case_labels_before": case_labels(event["state_before"]),
            "identifiers_referenced_exact": identifiers(event["action"]),
            "state_after_id": digest(event["state_after"]),
            "state_before_id": digest(event["state_before"]),
            "tactic_family": tactic_family(event["action"]),
            "transition_id": digest(canonical({
                "state_before": event["state_before"],
                "action": event["action"],
                "state_after": event["state_after"],
            })),
        }
        organized.append(item)
    return {
        "representation": "LOSSLESS_HML_OVERLAY_V1",
        "current": {"state_exact": current_state},
        "history": organized,
        "semantic_index": {
            "current_case_labels": case_labels(current_state),
            "current_state_id": digest(current_state),
            "current_step_number": len(events),
            "history_order": list(range(len(events))),
        },
    }


def prompt(arm: str, current_state: str, history: Iterable[dict[str, str]]) -> str:
    payload = raw_payload(current_state, history) if arm == "raw" else overlay_payload(current_state, history)
    return PROMPT_PREFIX + canonical(payload) + PROMPT_SUFFIX
