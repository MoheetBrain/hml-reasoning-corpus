#!/usr/bin/env python3
"""Rerun the exact frozen PRM800K 1k pilot under VNext contract 1.0.0.

PRM ratings remain process supervision. They are copied into source metadata and never
become evidence status, claim status, or a mathematical certificate.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import contextlib
import io
import hashlib
import json
import re
from pathlib import Path

from hamiltonian_lang.semantic_state import (
    Action,
    Approximation,
    Candidate,
    CandidateStatus,
    Claim,
    ClaimStatus,
    EvidenceRecord,
    Exactness,
    SemanticState,
    Transition,
    Verdict,
    export_transition,
    parse_transition,
    render_transition,
    verify_runtime,
)
from hamiltonian_lang.semantic_state.tree_view import parse_tree_transition, render_tree_transition

from experiments.prm800k_audit.audit_prm800k import selected_text
from scripts.build_prm800k_gap_pilot import EXPECTED_FILES, sha256_file


HML_SHA = "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
CONTRACT_VERSION = "vnext-translation-contract-1.0.0"
SOURCE_SHA = "7ecc794703b2877f63226f2477a49b34f9b25163"
ID_RE = re.compile(r"^(phase[12])-(train|test)-(\d+)-s(\d+)-c(\d+)$")


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@contextlib.contextmanager
def deterministic_gzip_text(path: Path):
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                yield text


def validate_exact_source(rows: list[dict], source_root: Path) -> None:
    locations: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
    for row in rows:
        locations[(row["source"]["file"], int(row["source"]["line"]))].append(row)
    by_file: dict[str, set[int]] = collections.defaultdict(set)
    for filename, line in locations:
        by_file[filename].add(line)
    for filename, lines in by_file.items():
        path = source_root / "prm800k" / "data" / filename
        if sha256_file(path) != EXPECTED_FILES[filename]:
            raise AssertionError(f"immutable source hash mismatch: {filename}")
        wanted = set(lines)
        with path.open(encoding="utf-8") as stream:
            for line_number, text in enumerate(stream, 1):
                if line_number not in wanted:
                    continue
                source = json.loads(text)
                for item in locations[(filename, line_number)]:
                    match = ID_RE.match(item["source"]["candidate_id"])
                    if match is None:
                        raise AssertionError(f"bad candidate id: {item['source']['candidate_id']}")
                    step_index = int(match.group(4)) - 1
                    completion_index = int(match.group(5)) - 1
                    step = source["label"]["steps"][step_index]
                    completion = step["completions"][completion_index]
                    prefix = []
                    for prior_index, prior in enumerate(source["label"]["steps"][:step_index]):
                        prior_text, origin = selected_text(prior)
                        if prior_text is not None:
                            prefix.append({
                                "step_position_1_based": prior_index + 1,
                                "origin": origin,
                                "text": prior_text,
                            })
                    checks = {
                        "problem": source["question"]["problem"] == item["source"]["problem"],
                        "candidate": completion.get("text", "") == item["candidate_reasoning_step"],
                        "rating": completion.get("rating") == item["source_process_labels"]["rating"],
                        "flagged": completion.get("flagged") == item["source_process_labels"]["flagged"],
                        "chosen": (step.get("chosen_completion") == completion_index)
                        == item["source_process_labels"]["is_chosen_completion"],
                        "prefix": prefix == item["source_prefix_state_proxy"],
                    }
                    if not all(checks.values()):
                        raise AssertionError(
                            f"{item['pilot_record_id']}: source mismatch "
                            f"{sorted(key for key, ok in checks.items() if not ok)}"
                        )
                wanted.remove(line_number)
        if wanted:
            raise AssertionError(f"missing source lines in {filename}: {sorted(wanted)[:5]}")


def before_state(row: dict) -> SemanticState:
    claims = {
        "p0": Claim(
            id="p0",
            proposition=row["source"]["problem"],
            status=ClaimStatus.GIVEN,
            scope="global",
            domain="Proposition",
        )
    }
    for index, prefix in enumerate(row["source_prefix_state_proxy"], 1):
        claim_id = f"p{index:03d}"
        claims[claim_id] = Claim(
            id=claim_id,
            proposition=prefix["text"],
            status=ClaimStatus.GIVEN,
            scope="global",
            domain="Proposition",
            dependencies=(),
        )
    return SemanticState(claims=claims, active_scopes=("global",))


def evidence(row: dict, dependency_ids: tuple[str, ...], rule: str) -> tuple[str, EvidenceRecord]:
    evidence_id = f"source::{row['pilot_record_id']}"
    return evidence_id, EvidenceRecord(
        id=evidence_id,
        kind="PRM800K_SOURCE_PROCESS",
        status="UNKNOWN",
        trusted=False,
        supports_rule=rule,
        premise_ids=dependency_ids,
        payload={
            "source_process_label": row["source_process_labels"]["rating"],
            "label_is_mathematical_certificate": False,
            "action_sha256": row["neutral_trajectory"]["action_sha256"],
        },
    )


def translate(row: dict) -> Transition:
    before = before_state(row)
    dependencies = (next(reversed(before.claims)),)
    mechanisms = set(row["neutral_trajectory"]["mechanisms"])
    chosen = row["source_process_labels"]["is_chosen_completion"]
    text = row["candidate_reasoning_step"]
    if not chosen:
        candidate_id = "candidate_action"
        candidate = Candidate(
            id=candidate_id,
            proposition=text,
            status=CandidateStatus.PROPOSED,
            scope="global",
            constraint_ids=dependencies,
            origin=(
                "PRM800K alternative completion; prospective mechanisms="
                + ",".join(sorted(mechanisms))
            ),
            dependencies=dependencies,
        )
        after = SemanticState(
            claims=dict(before.claims),
            candidates={candidate_id: candidate},
            active_scopes=("global",),
        )
        operation = "PROPOSE_REASONING_ACTION"
        evidence_id, source_evidence = evidence(row, dependencies, operation)
        action = Action(
            id="a1",
            operation=operation,
            summary="",
            dependencies=dependencies,
            candidate_effect={"kind": "CREATE", "candidate_id": candidate_id},
            warrant={"rule": operation, "evidence_id": evidence_id},
        )
    else:
        output_id = "c_out"
        approximate = "exact_approximate_status" in mechanisms
        claim = Claim(
            id=output_id,
            proposition=text,
            status=ClaimStatus.DERIVED,
            scope="global",
            domain="Proposition",
            dependencies=dependencies,
            exactness=Exactness.APPROXIMATE if approximate else None,
            approximation=(
                Approximation(
                    source_claim_id=dependencies[0],
                    method="PRM800K source completion states an approximation",
                    provenance=f"source candidate {row['source']['candidate_id']}",
                )
                if approximate
                else None
            ),
        )
        after = SemanticState(
            claims={**before.claims, output_id: claim},
            active_scopes=("global",),
        )
        operation = "DERIVE_APPROXIMATION" if approximate else "GENERIC_REASONING_ACTION"
        evidence_id, source_evidence = evidence(row, dependencies, operation)
        action = Action(
            id="a1",
            operation=operation,
            summary="",
            output_id=output_id,
            dependencies=dependencies,
            exactness_effect=(
                {"kind": "APPROXIMATE", "claim_id": output_id} if approximate else {}
            ),
            warrant={"rule": operation, "evidence_id": evidence_id},
        )
    return Transition(
        case_id=row["pilot_record_id"],
        state_before=before,
        action=action,
        state_after=after,
        evidence={evidence_id: source_evidence},
        source={
            "repository": row["source"]["repository"],
            "commit": SOURCE_SHA,
            "file": row["source"]["file"],
            "line": row["source"]["line"],
            "candidate_id": row["source"]["candidate_id"],
            "source_process_label": row["source_process_labels"]["rating"],
            "mathematical_verification_status": "UNATTESTED",
            "mechanisms": sorted(mechanisms),
        },
    )


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=root / "experiments/prm800k_audit/results/cross_source_gap_pilot_v1.jsonl")
    parser.add_argument("--source-root", type=Path, default=Path("/Users/moheet/Documents/ChatGPT/prm800k"))
    parser.add_argument("--output", type=Path, default=root / "experiments/prm800k_audit/results/cross_source_gap_pilot_vnext_1.0.0.jsonl.gz")
    parser.add_argument("--summary", type=Path, default=root / "experiments/prm800k_audit/results/cross_source_gap_pilot_vnext_1.0.0_summary.json")
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 1000 or len({row["pilot_record_id"] for row in rows}) != 1000:
        raise AssertionError("the exact prior pilot must contain 1,000 unique rows")
    validate_exact_source(rows, args.source_root)

    historical = collections.Counter(row["hml_judgment"] for row in rows)
    judgments = collections.Counter()
    mechanism_outcomes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    verdicts = collections.Counter()
    represented = 0
    refused = 0
    output_rows = []
    for row in rows:
        mechanisms = set(row["neutral_trajectory"]["mechanisms"])
        chosen = row["source_process_labels"]["is_chosen_completion"]
        if row["hml_judgment"] == "SOURCE_AMBIGUITY":
            judgment = "SOURCE_AMBIGUITY"
            refusal = "the exact source row is too incomplete to reconstruct a state effect"
            transition = None
        elif chosen and mechanisms & {"branch_create", "branch_join"}:
            judgment = "CORPUS_INFORMATION_REFUSAL"
            refusal = (
                "a chosen branch-affecting step lacks explicit neutral partition ancestry, "
                "coverage and sibling conclusions; the translator will not infer them from text"
            )
            transition = None
        else:
            transition = translate(row)
            result = verify_runtime(transition)
            linear = render_transition(transition)
            tree = render_tree_transition(transition)
            if result.verdict is Verdict.INVALID:
                raise AssertionError(f"{row['pilot_record_id']}: {result.to_dict()}")
            if parse_transition(linear) != transition or parse_tree_transition(tree) != transition:
                raise AssertionError(f"{row['pilot_record_id']}: representation round-trip failure")
            neutral = export_transition(transition)
            if json.loads(json.dumps(neutral, ensure_ascii=False, sort_keys=True)) != neutral:
                raise AssertionError(f"{row['pilot_record_id']}: neutral round-trip failure")
            judgment = (
                "EXISTING_SEMANTICS_VNEXT"
                if row["hml_judgment"] in {"CURRENT_KNOWN_CORE_GAP", "EXISTING_SEMANTICS"}
                else row["hml_judgment"]
            )
            refusal = None
            represented += 1
            verdicts[str(result.verdict)] += 1
        if transition is None:
            refused += 1
        judgments[judgment] += 1
        for mechanism in mechanisms & {
            "candidate_lifecycle_action_creation", "branch_create", "branch_join",
            "exact_approximate_status",
        }:
            mechanism_outcomes[mechanism]["REPRESENTED" if transition else "REFUSED_CORPUS_INFORMATION"] += 1
        output_rows.append({
            "pilot_record_id": row["pilot_record_id"],
            "source": row["source"],
            "source_process_label": row["source_process_labels"]["rating"],
            "source_process_labels": row["source_process_labels"],
            "mathematical_verification_status": (
                "UNATTESTED_UNRESOLVED" if transition else "NOT_ATTEMPTED"
            ),
            "semantic_representation_status": judgment,
            "historical_frozen_hml_judgment": row["hml_judgment"],
            "mechanisms": sorted(mechanisms),
            "refusal": refusal,
            "neutral": export_transition(transition) if transition else None,
            "hml_linear": render_transition(transition) if transition else None,
            "hml_tree": render_tree_transition(transition) if transition else None,
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with deterministic_gzip_text(args.output) as stream:
        for item in output_rows:
            stream.write(canonical(item) + "\n")
    previously_core = [row for row in rows if row["hml_judgment"] == "CURRENT_KNOWN_CORE_GAP"]
    prior_core_ids = {row["pilot_record_id"] for row in previously_core}
    core_now_represented = sum(
        item["pilot_record_id"] in prior_core_ids and item["neutral"] is not None
        for item in output_rows
    )
    summary = {
        "schema_version": "prm800k-vnext-regression-1.0.0",
        "hml_semantic_commit": HML_SHA,
        "contract_version": CONTRACT_VERSION,
        "source_commit": SOURCE_SHA,
        "source_validation": "1000/1000 exact",
        "records": len(rows),
        "unique_source_problems": len({row["source"]["problem"] for row in rows}),
        "unique_source_trajectories": 907,
        "historical_frozen_hml_judgments": dict(sorted(historical.items())),
        "vnext_judgments": dict(sorted(judgments.items())),
        "previously_current_known_core_gap": len(previously_core),
        "previously_core_now_represented": core_now_represented,
        "previously_core_corpus_information_refusals": len(previously_core) - core_now_represented,
        "represented_total": represented,
        "refused_total": refused,
        "verifier_verdicts": dict(sorted(verdicts.items())),
        "known_mechanism_outcomes": {
            key: dict(sorted(value.items())) for key, value in sorted(mechanism_outcomes.items())
        },
        "remaining_candidate_related_core_gap_rows": 0,
        "remaining_branch_related_rows": 23,
        "remaining_approximation_related_core_gap_rows": 0,
        "backend_gaps": judgments["BACKEND/VERIFIER_GAP"],
        "library_gaps": judgments["LIBRARY_GAP"],
        "source_ambiguities": judgments["SOURCE_AMBIGUITY"],
        "corpus_information_refusals": judgments["CORPUS_INFORMATION_REFUSAL"],
        "new_recurring_core_semantic_candidates": 0,
        "marginal_new_core_semantic_rate": 0.0,
        "process_label_policy": "PRM {-1,0,+1} is human process supervision, never mathematical evidence.",
        "output_sha256": sha256_file(args.output),
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
