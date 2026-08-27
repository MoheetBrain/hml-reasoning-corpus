"""Coarse shortcut controls and paired minimal-pair evaluation (mission §4, §5).

Three diagnostics that together answer "could this score be achieved without reading the
mathematics", from three different directions.

**Length-only.** Size and formatting alone: tokens, characters, lines, fields. Per arm,
because the arms differ in length by up to 2x and the question is arm-specific.

**Structure-count.** Coarse record counts only -- how many facts, goals, branches,
candidates, obligations, dependency edges -- with **no mathematical content whatsoever**.
Derived from the typed-AST render because it is uniformly tagged, but the counts describe the
semantic object, so this control is shared across arms rather than computed per arm.

Both use the same head and schedule as the real probe, so a gap between them and the probe is
a gap in what the features carry, not in how they were fitted.

**Minimal pairs.** The strongest of the three, and the one that is not a baseline at all. For
each parent, its VALID item and one of its one-change counterfactuals differ in exactly one
semantic edit and share everything else -- the same theorem, the same context, nearly the same
tokens. Asking whether the classifier puts more VALID-probability on the genuine one is a
question global lexical statistics cannot answer by construction: the two members of a pair
have almost identical lexical statistics.

Reported per mutation family, because "which semantic property does the model fail to read"
is a more useful answer than a single number.
"""

from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

from .probe import ProbeConfig, train_probe

__all__ = [
    "length_only_features",
    "structure_count_features",
    "LENGTH_FEATURE_NAMES",
    "STRUCTURE_FEATURE_NAMES",
    "run_coarse_control",
    "minimal_pair_report",
]

LENGTH_FEATURE_NAMES = (
    "characters", "lines", "fields", "words", "digits", "punctuation",
    "mean_line_length", "max_line_length",
)

STRUCTURE_FEATURE_NAMES = (
    "n_claims_before", "n_claims_after", "n_goals_before", "n_goals_after",
    "n_branches", "n_candidates", "n_obligations", "n_evidence",
    "n_dependency_tokens", "n_scopes", "claims_delta",
)

_TAG = {
    "claim": re.compile(r"\(claim "),
    "goal": re.compile(r"\(goal "),
    "branch": re.compile(r"\(branch "),
    "candidate": re.compile(r"\(candidate "),
    "obligation": re.compile(r"\(obligation "),
    "evidence": re.compile(r"\(evidence "),
}
_STATE = re.compile(r"\(state (before|after)")
_DEPS = re.compile(r"\(dependencies \(([^)]*)\)\)")
_SCOPES = re.compile(r"\(scopes ([^)]*)\)")


def length_only_features(texts: list[str]) -> np.ndarray:
    """Size and formatting only. No token identities, so no lexical content at all."""
    out = np.zeros((len(texts), len(LENGTH_FEATURE_NAMES)), dtype=np.float32)
    for i, text in enumerate(texts):
        lines = text.split("\n")
        lengths = [len(line) for line in lines] or [0]
        out[i] = (
            len(text),
            len(lines),
            text.count("("),
            len(text.split()),
            sum(c.isdigit() for c in text),
            sum(not c.isalnum() and not c.isspace() for c in text),
            float(np.mean(lengths)),
            float(max(lengths)),
        )
    return np.log1p(out)


def structure_count_features(ast_texts: list[str]) -> np.ndarray:
    """Coarse record counts. Deliberately blind to every proposition in the state."""
    out = np.zeros((len(ast_texts), len(STRUCTURE_FEATURE_NAMES)), dtype=np.float32)
    for i, text in enumerate(ast_texts):
        halves = _STATE.split(text)
        before = halves[2] if len(halves) > 2 else ""
        after = halves[4] if len(halves) > 4 else ""
        n_claims_before = len(_TAG["claim"].findall(before))
        n_claims_after = len(_TAG["claim"].findall(after))
        dep_tokens = sum(len(m.split()) for m in _DEPS.findall(text))
        scopes = _SCOPES.search(text)
        out[i] = (
            n_claims_before,
            n_claims_after,
            len(_TAG["goal"].findall(before)),
            len(_TAG["goal"].findall(after)),
            len(_TAG["branch"].findall(text)),
            len(_TAG["candidate"].findall(text)),
            len(_TAG["obligation"].findall(text)),
            len(_TAG["evidence"].findall(text)),
            dep_tokens,
            len(scopes.group(1).split()) if scopes else 0,
            n_claims_after - n_claims_before,
        )
    return out


def run_coarse_control(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_dev: np.ndarray,
    y_dev: np.ndarray,
    evals: dict[str, np.ndarray],
    seed: int = 0,
) -> dict:
    """Fit a coarse control with the same head and schedule as the real probe."""
    return train_probe(
        x_train, y_train, x_dev, y_dev, evals,
        ProbeConfig(kind="linear", seed=seed, epochs=200, lr=5e-3),
    )


def minimal_pair_report(
    probs: np.ndarray,
    rows: list[dict],
    label_index: dict[str, int],
) -> dict:
    """Paired discrimination between a parent and each of its one-change counterfactuals.

    For a pair ``(valid, mutated)`` the test is whether the classifier assigns more
    probability to VALID on the genuine item than on the edited one. The margin is signed, so
    a family the model reads backwards is visible as a negative margin rather than as an
    accuracy near chance.
    """
    valid_i = label_index["VALID"]
    by_family: dict[str, dict[str, list]] = defaultdict(lambda: {"correct": [], "margin": []})

    parents: dict[str, int] = {}
    children: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        if row["label"] == "VALID":
            parents[row["semantic_id"]] = idx
        else:
            children[row["semantic_id"]].append(idx)

    all_correct: list[int] = []
    all_margin: list[float] = []
    for sem_id, parent_idx in parents.items():
        p_valid_parent = float(probs[parent_idx, valid_i])
        for child_idx in children[sem_id]:
            family = rows[child_idx]["audit"]["mutation_type"] or "UNKNOWN_FAMILY"
            margin = p_valid_parent - float(probs[child_idx, valid_i])
            correct = int(margin > 0)
            by_family[family]["correct"].append(correct)
            by_family[family]["margin"].append(margin)
            all_correct.append(correct)
            all_margin.append(margin)

    def block(correct: list[int], margin: list[float]) -> dict:
        if not correct:
            return {"n": 0}
        return {
            "n": len(correct),
            "pairwise_accuracy": round(float(np.mean(correct)), 4),
            "mean_probability_margin": round(float(np.mean(margin)), 4),
            "median_margin": round(float(np.median(margin)), 4),
        }

    return {
        "overall": block(all_correct, all_margin),
        "by_mutation_family": {
            fam: block(v["correct"], v["margin"])
            for fam, v in sorted(by_family.items())
        },
        "definition": "P(VALID | genuine) > P(VALID | one-change counterfactual)",
    }
