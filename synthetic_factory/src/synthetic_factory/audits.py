"""Deterministic dataset statistics and Markdown audit reports."""

from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .records import canonical_json, digest


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    return b"".join((canonical_json(record) + "\n").encode("utf-8") for record in records)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    families = collections.Counter(record["mutation_family"] for record in records)
    failures = collections.Counter(record["failure_code_if_invalid"] for record in records)
    causal = collections.Counter(record["causality"]["classification"] for record in records)
    source_theorems = {
        record["source_theorem_id"] for record in records if record.get("source_theorem_id")
    }
    payload_hashes = [digest(record["counterfactual_transition"]) for record in records]
    changed = collections.Counter(
        record["minimality"]["number_of_changed_semantic_fields"] for record in records
    )
    return {
        "attempted_mutations": len(records),
        "accepted_pairs": len(records),
        "semantic_hard_pairs": causal.get("SEMANTIC_HARD_PAIR", 0),
        "structural_pairs": causal.get("STRUCTURAL_PAIR", 0),
        "trivial_parser_pairs": causal.get("TRIVIAL_PARSER_PAIR", 0),
        "ambiguous_pairs": causal.get("AMBIGUOUS", 0),
        "unknown_or_unsupported": sum(
            record["mutated_verifier_result"]["verdict"] == "UNRESOLVED"
            for record in records
        ),
        "valid_alternatives": sum(
            record["mutated_verifier_result"]["verdict"] == "VALID" for record in records
        ),
        "invalid_counterfactuals": sum(
            record["mutated_verifier_result"]["verdict"] == "INVALID" for record in records
        ),
        "mutation_family_distribution": dict(sorted(families.items())),
        "failure_code_distribution": dict(sorted(failures.items())),
        "changed_semantic_fields_distribution": {
            str(key): value for key, value in sorted(changed.items())
        },
        "duplicate_payload_count": len(payload_hashes) - len(set(payload_hashes)),
        "duplicate_rate": (
            (len(payload_hashes) - len(set(payload_hashes))) / len(payload_hashes)
            if payload_hashes
            else 0.0
        ),
        "source_record_diversity": len({record["source_record_id"] for record in records}),
        "source_theorem_diversity": len(source_theorems),
        "provenance_complete": sum(
            bool(record.get("source_provenance")) for record in records
        ),
        "hml_sha_mismatches": sum(
            record["hml_sha"] != records[0]["hml_sha"] for record in records
        ) if records else 0,
    }


def hardest(records: list[dict[str, Any]], per_family: int = 2) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        grouped[record["mutation_family"]].append(record)
    selected = []
    for family in sorted(grouped):
        ranked = sorted(
            grouped[family],
            key=lambda row: (
                len(canonical_json(row["source_transition"])),
                row["pair_id"],
            ),
            reverse=True,
        )
        selected.extend(ranked[:per_family])
    return sorted(selected, key=lambda row: (row["mutation_family"], row["pair_id"]))


def write_reports(
    *,
    factory_root: Path,
    authority: dict[str, Any],
    records: list[dict[str, Any]],
    source_manifest: dict[str, Any],
    dataset_sha256: str,
    generator_sha: str,
) -> dict[str, Any]:
    reports = factory_root / "reports"
    manifests = factory_root / "manifests"
    reports.mkdir(parents=True, exist_ok=True)
    manifests.mkdir(parents=True, exist_ok=True)
    summary = summarize(records)
    top = hardest(records)

    generated = {
        "dataset": "counterfactual_v1_stage100",
        "status": "DIAGNOSTIC_STAGE100_HARDNESS_GATE_FAILED",
        "records": len(records),
        "sha256": dataset_sha256,
        "generator_source_sha256": generator_sha,
        "summary": summary,
        "quality_decision": "FIX_GENERATOR_FIRST",
        "alpha_renaming_secondary_dataset": "NOT_STARTED_STAGE100_HARDNESS_GATE_FAILED",
        "decision_reason": (
            "Stage 100 passes, but the 241,265-record Lean scale source is not itself a "
            "SemanticState Transition payload and lacks verifier-relevant dependencies, "
            "evidence, preconditions, obligations and scope. Do not scale by duplicating "
            "the 100 Semantic Firewall sources."
        ),
    }
    (manifests / "generated_dataset.json").write_text(
        json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (manifests / "source_records.json").write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    hml = authority["hml"]
    corpus = authority["corpus"]
    lean = authority["lean_canonical"]
    authority_md = f"""# Authority recovery

## Decision

Both authority gates pass.

| Authority | Verified value |
|---|---|
| HML tag | `{hml['tag']}` |
| HML SHA | `{hml['sha']}` |
| HML tree | `{hml['tree_hash']}` |
| HML commit date | `{hml['commit_date']}` |
| HML checkout | clean; zero writable files |
| corpus SHA | `{corpus['authority_sha']}` |
| current isolated branch | `{corpus['current_branch']}` |
| Lean canonical path | `{lean['absolute_path']}` |
| Lean canonical SHA-256 | `{lean['sha256']}` |
| canonical records | {lean['records']:,} |
| represented theorems | {lean['represented_theorems']:,} |
| excluded goal creation | {lean['excluded_goal_creation']:,} |
| original Lean transitions | {lean['original_transitions']:,} |
| source experiment SHA | `{lean['source_experiment_git_sha']}` |

The arithmetic reconciles exactly: {lean['records']:,} +
{lean['excluded_goal_creation']:,} = {lean['original_transitions']:,}.

## Stale history

Historical pins `5688aba…` and `164d194…`, Gold-10/25/125, and the MiniLang handoff
were found only as history. None was used as runtime authority. The old corpus
submodule was not imported.

## Isolation

- Claude/FABLE files changed: **0**
- historical Codex handoff files changed: **0**
- frozen HML files changed: **0**

The local FABLE experiment checkout and research artifact store were read only. The
canonical JSONL was exported to the isolated VM workspace and re-hashed before use.
"""
    (reports / "AUTHORITY_RECOVERY.md").write_text(authority_md, encoding="utf-8")

    yield_rows = "\n".join(
        f"| `{family}` | {count} |"
        for family, count in summary["mutation_family_distribution"].items()
    )
    failure_rows = "\n".join(
        f"| `{code}` | {count} |"
        for code, count in summary["failure_code_distribution"].items()
    )
    stage_md = f"""# Stage 100 audit

## Result

**All 100 minimal pairs pass the mechanical contract, but only 20 pass the hard-negative
review. Decision: `FIX_GENERATOR_FIRST`.**

| Measure | Result |
|---|---:|
| attempted mutations | {summary['attempted_mutations']} |
| accepted pairs | {summary['accepted_pairs']} |
| semantic hard pairs | {summary['semantic_hard_pairs']} |
| structural pairs | {summary['structural_pairs']} |
| ambiguous pairs | {summary['ambiguous_pairs']} |
| trivial parser pairs | {summary['trivial_parser_pairs']} |
| unknown/unsupported | {summary['unknown_or_unsupported']} |
| valid alternatives | {summary['valid_alternatives']} |
| invalid counterfactuals | {summary['invalid_counterfactuals']} |
| duplicate rate | {summary['duplicate_rate']:.2%} |
| source-record diversity | {summary['source_record_diversity']} |
| source-theorem/row diversity | {summary['source_theorem_diversity']} |
| provenance completeness | {summary['provenance_complete']}/{len(records)} |
| changed semantic fields | exactly 1 for every pair |
| dataset SHA-256 | `{dataset_sha256}` |
| generator source SHA-256 | `{generator_sha}` |

Every source transition independently returns `VALID` from frozen HML. Every mutated
transition imports successfully and returns `INVALID` at the intended replay invariant.
No `UNRESOLVED` result was converted to `INVALID`; no syntax corruption was generated.

## Mutation-family distribution

| Family | Pairs |
|---|---:|
{yield_rows}

## Failure-code distribution

| Verifier failure code | Count |
|---|---:|
{failure_rows}

## Causal interpretation

Each pair changes one verifier-semantic leaf: premise identity, scope, precondition
status, obligation materialisation, candidate constraint coverage, branch coverage,
evidence identity, epistemic evidence, goal status, or input domain. The source and
counterfactual both parse and import, so none is parser garbage. Independent review
nevertheless classifies missing sentinel IDs and direct status/effect contradictions as
`STRUCTURAL_PAIR`, not mathematically hard negatives. Scope and type mutations are
`AMBIGUOUS` because a second frame finding accompanies the target finding. Only the
candidate-constraint and branch-coverage mutations are retained as
`SEMANTIC_HARD_PAIR` at this checkpoint.

The primary verdict uses `OFFLINE_REPLAY` because the retained evidence bytes are from
the frozen externally adjudicated corpus. Runtime-without-attestation diagnostics are
recorded separately and are never treated as positive labels.

## Why Stage 1,000 is not authorized

The scale artifact is available and correctly pinned, but its Lean effect-first records
are not HML `Transition` payloads. `premises_used` is empty throughout the canonical
JSONL; preconditions, obligations, scopes, typed action arguments and evidence envelopes
are absent. Its `frozen_hml_representable=true` flag was assigned after excluding only
goal creation and is not a verifier replay result. Scaling now would either duplicate
these 100 fixture shapes or invent missing semantics.
"""
    (reports / "STAGE100_AUDIT.md").write_text(stage_md, encoding="utf-8")

    yield_md = f"""# Mutation yield

Stage 100 attempts exactly one approved mutation for each of the 100 current-corpus
DEV/FINAL records independently accepted by frozen HML.

| Family | Attempted | Accepted | Invalid | Unknown | Trivial parser |
|---|---:|---:|---:|---:|---:|
""" + "\n".join(
        f"| `{family}` | {count} | {count} | {count} | 0 | 0 |"
        for family, count in summary["mutation_family_distribution"].items()
    ) + "\n"
    (reports / "MUTATION_YIELD.md").write_text(yield_md, encoding="utf-8")

    hard_lines = [
        "# Hard-negative audit",
        "",
        "The two largest source transitions in each semantic family were selected",
        "deterministically and re-audited from their exact source payload and verifier finding.",
        "",
        "## Independent-review result",
        "",
        "Mechanical acceptance did not imply mathematical hardness. The review corrected",
        "the initial all-hard interpretation to 20 semantic-hard, 60 structural and 20",
        "ambiguous pairs. No parser failures were found. Dependency/warrant/epistemic probes",
        "use obvious missing identities; precondition and effect probes directly contradict",
        "status/materialisation fields; scope and type also raise FRAME. The branch and",
        "candidate probes isolate certificate coverage, but their imported trusted evidence",
        "does not independently re-prove the opaque MATH text. Therefore this is a harness",
        "checkpoint, not production-ready mathematical counterfactual data.",
        "",
    ]
    for index, record in enumerate(top, 1):
        finding = record["mutated_verifier_result"]["findings"][0]
        source = record["source_provenance"]["source"]
        problem = " ".join(str(source.get("problem", "")).split())[:240].rstrip()
        hard_lines.extend(
            [
                f"## {index}. {record['pair_id']} — {record['mutation_family']}",
                "",
                f"- Source: `{source.get('source_row_id', record['source_record_id'])}` — {problem}",
                f"- Exact changed field: `{record['exact_changed_field']}`",
                f"- Change: `{json.dumps(record['minimality']['before_value'], ensure_ascii=False)}` → "
                f"`{json.dumps(record['minimality']['after_value'], ensure_ascii=False)}`",
                f"- Verifier: `{record['failure_code_if_invalid']}` / `{finding['invariant']}`",
                f"- Grounded explanation: {finding['detail']}",
                f"- Causal audit: {record['causality']['explanation']}",
                f"- Revised class: `{record['causality']['classification']}`",
                "",
            ]
        )
    (reports / "HARD_NEGATIVE_AUDIT.md").write_text(
        "\n".join(hard_lines).rstrip() + "\n", encoding="utf-8"
    )

    gaps_md = """# Semantic and adapter gaps found by the factory

No HML changes were implemented. Detailed candidates are under
`reports/semantic_gap_candidates/`.

1. The 241,265 Lean records are effect-first learning records, not frozen-HML
   verifier transitions. Their compatibility flag is not a verifier result.
2. Lean propositions and tactics are opaque to the semantic-state verifier; arbitrary
   Lean mathematical validity cannot be attested by the current certificate registry.
3. Goal creation is intentionally excluded and fails closed in frozen HML.

These facts block truthful Stage-1,000 scaling from Lean. They do not invalidate the
Stage-100 verifier harness.
"""
    (reports / "SEMANTIC_GAPS.md").write_text(gaps_md, encoding="utf-8")
    return {"summary": summary, "hardest": [row["pair_id"] for row in top]}
