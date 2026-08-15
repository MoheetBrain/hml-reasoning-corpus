"""Shared D1 action/target leakage policy for VNext model projections."""

from __future__ import annotations

import hashlib
import re
import unicodedata


TOKEN_PATTERN = r"\w+|[^\w\s]"
TOKEN_RE = re.compile(TOKEN_PATTERN, re.UNICODE)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    return re.sub(r"[^\w]+", "", value)


def comparison_tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(unicodedata.normalize("NFKC", value).lower()))


def delta_texts(neutral: dict) -> list[str]:
    before, after = neutral["state_before"], neutral["state_after"]
    values = []
    for collection in ("claims", "candidates", "goals", "obligations", "branches"):
        old = before.get(collection, {})
        for key, value in after.get(collection, {}).items():
            if key in old or not isinstance(value, dict):
                continue
            for field in ("proposition", "statement", "description", "target"):
                if isinstance(value.get(field), str):
                    values.append(value[field])
    return values


def action_leakage(row: dict, projected_action: dict) -> dict:
    action_text = projected_action.get("tactic_text") or projected_action.get("action_text") or ""
    action_norm = normalized(action_text)
    action_tokens = comparison_tokens(action_text)
    diagnostics = []
    direct = False
    ambiguous = False
    for target_delta in delta_texts(row["neutral"]):
        delta_norm = normalized(target_delta)
        delta_tokens = comparison_tokens(target_delta)
        union = action_tokens | delta_tokens
        overlap = len(action_tokens & delta_tokens) / len(union) if union else 0.0
        exact = bool(delta_norm) and action_norm == delta_norm
        delta_in_action = bool(delta_norm) and len(delta_norm) >= 8 and delta_norm in action_norm
        action_in_delta = bool(action_norm) and len(action_norm) >= 8 and action_norm in delta_norm
        if exact or delta_in_action:
            direct = True
        elif action_in_delta or (len(delta_tokens) >= 5 and overlap >= 0.80):
            ambiguous = True
        diagnostics.append({
            "action_equals_delta_normalized": exact,
            "action_normalized_substring_of_delta": action_in_delta,
            "delta_normalized_substring_of_action": delta_in_action,
            "delta_sha256": digest_text(target_delta),
            "token_jaccard": round(overlap, 6),
        })
    classification = "B_DIRECT_TARGET_REVEALING_ACTION" if direct else (
        "C_AMBIGUOUS" if ambiguous else "A_LEGITIMATE_ACTION_SEMANTICS"
    )
    return {
        "record_id": row["record_id"],
        "source_family": row["source_family"],
        "split": row["split"],
        "classification": classification,
        "action_field": "tactic_text" if "tactic_text" in projected_action else "action_text",
        "action_sha256": digest_text(action_text),
        "action_character_count": len(action_text),
        "diagnostics": diagnostics,
        "excluded_from_execute": classification == "B_DIRECT_TARGET_REVEALING_ACTION",
    }
