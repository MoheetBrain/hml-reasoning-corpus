from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical import learner_hash
from .constants import CORPUS_SHA, HML_SHA, PROTOCOL, SCHEMA_VERSION, SENTINELS


CONTRACT_BY_FAMILY = {
    "DEPENDENCY": "ACTION_APPLICABILITY",
    "SCOPE": "ACTION_APPLICABILITY",
    "PRECONDITIONS": "ACTION_APPLICABILITY",
    "TYPE_DOMAIN": "ACTION_APPLICABILITY",
    "OBLIGATIONS": "TRANSITION_CONFORMANCE",
    "GOAL_DISCHARGE": "TRANSITION_CONFORMANCE",
    "CANDIDATES": "EVIDENCE_SUFFICIENCY",
    "BRANCH_JOIN": "EVIDENCE_SUFFICIENCY",
    "WARRANT": "EVIDENCE_SUFFICIENCY",
    "EPISTEMIC_STATUS": "EVIDENCE_SUFFICIENCY",
}


def _record(pair: dict[str, Any], *, variant: str, partition: str) -> dict[str, Any]:
    transition = pair["source_transition"] if variant == "ORIGINAL" else pair["counterfactual_transition"]
    result = pair["original_verifier_result"] if variant == "ORIGINAL" else pair["mutated_verifier_result"]
    family = pair["mutation_family"]
    contract = CONTRACT_BY_FAMILY[family]
    accepted = result["verdict"] == "VALID"
    split = transition.get("split", "UNKNOWN").upper()
    label = "HML_TRANSITION_ACCEPTED" if accepted else "HML_TRANSITION_REJECTED"
    row = {
        "schema_version": SCHEMA_VERSION,
        "protocol": PROTOCOL,
        "factory": "A",
        "partition": partition,
        "record_id": f"V2-A-{partition}-{pair['pair_id']}-{variant}",
        "pair_id": pair["pair_id"],
        "variant_role": variant,
        "prediction_contract": contract,
        "learner_input_hash": learner_hash(contract, transition),
        "label": label,
        "failure_stage": None if accepted else family,
        "failure_code": result.get("error_class"),
        "invariant_family": None if accepted else result["findings"][0]["invariant"],
        "secondary_findings": max(0, len(result.get("findings", [])) - 1),
        "source_split": split,
        "source_theorem_id": pair.get("source_theorem_id"),
        "ancestor_record_id": pair["source_record_id"],
        "source_provenance": pair["source_provenance"],
        "oracle": {"authority": "FROZEN_HML_REPLAY", "hml_sha": HML_SHA, "result": result},
        "transition": transition,
        "shortcut_flags": {
            "contains_sentinel": any(token in json.dumps(transition).lower() for token in SENTINELS),
            "direct_status_or_effect_contradiction": family in {"PRECONDITIONS", "OBLIGATIONS", "GOAL_DISCHARGE"} and variant != "ORIGINAL",
        },
        "corpus_sha": CORPUS_SHA,
    }
    return row


def generate(factory_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = factory_root / "synthetic_factory" / "data" / "stage100" / "canonical_pairs.jsonl"
    pairs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(pairs) != 100:
        raise RuntimeError("V1 Stage100 is not the expected 100-pair checkpoint")
    a1 = [_record(pair, variant=variant, partition="A1_REGRESSION_PROBES") for pair in pairs for variant in ("ORIGINAL", "COUNTERFACTUAL")]
    clean_pairs = [pair for pair in pairs if pair["mutation_family"] in {"CANDIDATES", "BRANCH_JOIN"}]
    a2 = [_record(pair, variant=variant, partition="A2_LEARNING_CONFORMANCE") for pair in clean_pairs for variant in ("ORIGINAL", "COUNTERFACTUAL")]
    for row in a2:
        if row["shortcut_flags"]["contains_sentinel"] or row["secondary_findings"]:
            raise RuntimeError(f"A2 shortcut/multi-failure leak: {row['record_id']}")
        if row["prediction_contract"] != "EVIDENCE_SUFFICIENCY":
            raise RuntimeError("A2 contract drift")
    return a1, a2
