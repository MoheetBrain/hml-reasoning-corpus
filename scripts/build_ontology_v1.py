#!/usr/bin/env python3
"""Build ontology-v1 derived views and audit AMPS-Khan without touching HML."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OLD_TRAJ = ROOT / "data/gold25/trajectories"
NEW_TRAJ = ROOT / "data/gold125/trajectories"
OLD_REGISTRY = ROOT / "schemas/reasoning_operation_registry_gold25_v0.json"
NEW_REGISTRY = ROOT / "schemas/reasoning_operation_registry_gold125_v1.json"
HARD_AUDIT = ROOT / "reports/gold125_independent_audits.json"
OUT = ROOT / "data/derived/gold125_ontology_v1"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
AMPS_DESKTOP = Path("/Users/moheet/Desktop/0000.parquet")
AMPS_RAW = ROOT / "data/raw/amps_khan/0000.parquet"

DOMAIN_WARRANTS = {
    "MODULAR_REASONING": ("MODULAR_ARITHMETIC", "DOMAIN_LIBRARY"),
    "PROBABILITY": ("PROBABILITY_LAW", "DOMAIN_LIBRARY"),
    "SEQUENCE_RECURRENCE": ("SEQUENCE_RULE", "DOMAIN_LIBRARY"),
    "DIFFERENTIATE": ("CALCULUS_RULE", "DOMAIN_LIBRARY"),
    "INTEGRATE": ("CALCULUS_RULE", "DOMAIN_LIBRARY"),
    "TAKE_LIMIT": ("CALCULUS_RULE", "DOMAIN_LIBRARY"),
    "TRIG_IDENTITY": ("TRIGONOMETRY_IDENTITY", "DOMAIN_LIBRARY"),
    "COORDINATE_TRANSFORM": ("GEOMETRY_RULE", "DOMAIN_LIBRARY"),
    "PIGEONHOLE": ("THEOREM", "THEOREM_LIBRARY"),
    "INCLUSION_EXCLUSION": ("COUNTING_RULE", "THEOREM_LIBRARY"),
    "EXPECTATION": ("PROBABILITY_LAW", "DOMAIN_LIBRARY"),
}
BACKEND_WARRANTS = {
    "EVALUATE": ("NUMERIC_EVALUATION", "NUMERIC_BACKEND"),
    "APPLY_PRECEDENCE": ("NUMERIC_EVALUATION", "NUMERIC_BACKEND"),
    "EXPAND": ("SYMBOLIC_NORMALIZATION", "SYMBOLIC_BACKEND"),
    "FACTOR": ("SYMBOLIC_NORMALIZATION", "SYMBOLIC_BACKEND"),
    "RATIONALIZE": ("SYMBOLIC_NORMALIZATION", "SYMBOLIC_BACKEND"),
    "COMBINE_LIKE_TERMS": ("SYMBOLIC_NORMALIZATION", "SYMBOLIC_BACKEND"),
}
CORE_OPERATION_MAP = {
    "INTRODUCE_VARIABLE": "DECLARE", "RECORD_GIVEN": "RECORD",
    "FORMULATE_EQUATION": "MODEL", "FORMULATE_INEQUALITY": "MODEL",
    "APPLY_IDENTITY": "TRANSFORM", "CROSS_MULTIPLY": "TRANSFORM",
    "CLEAR_DENOMINATOR": "TRANSFORM", "ADD_BOTH_SIDES": "TRANSFORM",
    "SUBTRACT_BOTH_SIDES": "TRANSFORM", "DIVIDE_BOTH_SIDES": "TRANSFORM",
    "EXPAND": "TRANSFORM", "FACTOR": "TRANSFORM", "RATIONALIZE": "TRANSFORM",
    "COMBINE_LIKE_TERMS": "TRANSFORM", "SOLVE": "TRANSFORM",
    "SOLVE_CASE": "TRANSFORM", "CONSTRAINT_PROPAGATION": "TRANSFORM",
    "CANCEL_SYMMETRIC_TERMS": "TRANSFORM", "PARAMETERIZE_CONGRUENCE": "TRANSFORM",
    "INDEX_TRANSLATION": "TRANSFORM", "ADVANCE_SEQUENCE": "TRANSFORM",
    "PRIME_FACTORIZE": "TRANSFORM", "EXTRACT_ROOT": "TRANSFORM",
    "APPLY_PRECEDENCE": "EVALUATE", "APPLY_DEFINITION": "APPLY_DEFINITION",
    "APPLY_THEOREM": "APPLY_THEOREM", "SUBSTITUTE": "SUBSTITUTE",
    "CASE_SPLIT": "CASE_SPLIT", "ENUMERATE": "ENUMERATE",
    "COUNT": "COUNT", "COUNT_PERMUTATIONS": "COUNT", "COMPLEMENT_COUNT": "COUNT",
    "COMBINE_CASE_COUNTS": "COUNT", "COUNT_EXCLUDED": "COUNT",
    "MULTIPLY_COUNTS": "COUNT", "INCLUSION_EXCLUSION": "COUNT",
    "PIGEONHOLE": "COUNT", "PROBABILITY": "EVALUATE", "EVALUATE": "EVALUATE",
    "EVALUATE_PROBABILITY": "EVALUATE", "CONDITIONAL_PROBABILITY": "EVALUATE",
    "MULTIPLY_CONDITIONALS": "EVALUATE", "EXPECTATION": "EVALUATE",
    "VERIFY": "VERIFY", "VERIFY_CANDIDATE": "VERIFY", "SELECT": "SELECT",
    "SELECT_CANDIDATE": "SELECT", "SELECT_EXTREMUM": "SELECT",
    "BOUND": "BOUND", "BOUND_REASONING": "BOUND", "BOUND_SEARCH": "BOUND",
    "OPTIMIZE": "BOUND", "CONSTRUCT": "CONSTRUCT", "CONSTRUCTION": "CONSTRUCT",
    "DISCHARGE": "DISCHARGE", "DISCHARGE_GOAL": "DISCHARGE",
    "CONTRADICTION": "CONTRADICTION", "TRIG_IDENTITY": "TRANSFORM",
    "MODULAR_REASONING": "TRANSFORM", "SEQUENCE_RECURRENCE": "TRANSFORM",
    "DIFFERENTIATE": "TRANSFORM", "INTEGRATE": "TRANSFORM",
    "TAKE_LIMIT": "EVALUATE", "COORDINATE_TRANSFORM": "TRANSFORM",
    "SEARCH_META": "UNRESOLVED", "OTHER": "UNRESOLVED",
}
OLD_MODE = {
    "DISCHARGE_GOAL": "GOAL_MANAGEMENT", "SELECT_CANDIDATE": "GOAL_MANAGEMENT",
    "SELECT_EXTREMUM": "GOAL_MANAGEMENT", "BOUND_SEARCH": "SEARCH_META",
    "ENUMERATE": "SEARCH_META", "CONSTRUCT": "SEARCH_META",
    "CASE_SPLIT": "SEARCH_META", "VERIFY_CANDIDATE": "VERIFICATION",
}
KEEP_AS_CORE = {
    "DECLARE", "RECORD", "MODEL", "CONSTRUCT", "TRANSFORM", "SUBSTITUTE",
    "APPLY_DEFINITION", "APPLY_THEOREM", "CASE_SPLIT", "ENUMERATE", "COUNT",
    "EVALUATE", "BOUND", "SELECT", "VERIFY", "CONTRADICTION", "DISCHARGE",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text(value: Any) -> str:
    return str(value or "")


def registries() -> dict[str, dict[str, Any]]:
    result = {}
    for path in (OLD_REGISTRY, NEW_REGISTRY):
        for item in read_json(path)["operations"]:
            operation_id = item.get("operation_id", item.get("observed_operation"))
            if operation_id:
                result[operation_id] = item
    return result


def load_steps() -> list[dict[str, Any]]:
    registry = registries()
    result = []
    paths = sorted(OLD_TRAJ.glob("MATH-GOLD-*.json")) + sorted(NEW_TRAJ.glob("MATH-GOLD-*.json"))
    for path in paths:
        trajectory = read_json(path)
        is_new = int(trajectory["problem_id"].split("-")[-1]) > 25
        for step in trajectory["steps"]:
            observed = step["action"]["operation_id"]
            profile = registry.get(observed, {})
            result.append({
                "trajectory_id": trajectory["problem_id"],
                "category": trajectory.get("category"),
                "level": trajectory.get("level"),
                "step_id": step["step_id"],
                "source_span": step["source_span"],
                "observed_operation": observed,
                "original_reasoning_mode": step.get("reasoning_mode", OLD_MODE.get(observed, "EXECUTION")),
                "original_warrant": step.get("warrant", {}),
                "original_candidate_core": step["action"].get("candidate_core", profile.get("canonical_name", "UNRESOLVED")),
                "original_layer": step["action"].get("layer_class", "UNRESOLVED"),
                "preconditions": step.get("preconditions", []),
                "obligations_created": step.get("creates_obligations", []),
                "obligations_discharged": step.get("discharges_obligations", []),
                "dependencies": step.get("dependencies", []),
                "state_delta": step.get("state_change", {}),
                "scope": step.get("scope", step.get("branch")),
                "atomicity": step.get("atomicity", "ATOMIC"),
                "problem": trajectory.get("problem", ""),
                "original_solution": trajectory.get("original_solution", ""),
                "is_new_gold125": is_new,
            })
    return result


def meta_ops(span: str) -> list[str]:
    low = span.lower()
    patterns = [
        (r"it suffices|enough to|we seek|we want to", "CREATE_SUBGOAL"),
        (r"rather than|instead", "REFRAME"),
        (r"notice|observe|key observation|key is", "RECOGNIZE_STRUCTURE"),
        (r"by symmetry|without loss|wlog", "USE_SYMMETRY"),
        (r"\bconsider\b|\bcase\b", "CONSIDER_CASES"),
        (r"introduce|let .* be|define", "CHOOSE_REPRESENTATION"),
    ]
    return [name for pattern, name in patterns if re.search(pattern, low)]


def mode_for(record: dict[str, Any]) -> str:
    mode = record["original_reasoning_mode"]
    return mode if mode in {"SEARCH_META", "EXECUTION", "VERIFICATION", "MODELING", "GOAL_MANAGEMENT", "OTHER"} else OLD_MODE.get(record["observed_operation"], "OTHER")


def core_for(record: dict[str, Any]) -> tuple[str, str]:
    observed, low = record["observed_operation"], record["source_span"].lower()
    if observed == "SEARCH_META":
        if re.search(r"let .* be|introduce|choose|represent|parameter", low):
            return "CONSTRUCT", "SEARCH_META"
        if re.search(r"case|either|consider", low):
            return "CASE_SPLIT", "SEARCH_META"
        return "UNRESOLVED", "SEARCH_META"
    if observed == "OTHER":
        return "UNRESOLVED", "UNKNOWN"
    core = CORE_OPERATION_MAP.get(observed, record["original_candidate_core"]) or "UNRESOLVED"
    if observed in DOMAIN_WARRANTS:
        layer = DOMAIN_WARRANTS[observed][1]
    elif observed in BACKEND_WARRANTS:
        layer = BACKEND_WARRANTS[observed][1]
    elif observed in {"APPLY_IDENTITY", "APPLY_THEOREM", "PIGEONHOLE", "INCLUSION_EXCLUSION"}:
        layer = "THEOREM_LIBRARY"
    elif record["original_layer"] == "SEARCH_META_OPERATION":
        layer = "SEARCH_META"
    else:
        layer = "CORE"
    return core, layer


def warrant_for(record: dict[str, Any]) -> tuple[str, str]:
    observed = record["observed_operation"]
    if observed in DOMAIN_WARRANTS:
        return DOMAIN_WARRANTS[observed][0], "domain-operation-factored-to-warrant"
    if observed in BACKEND_WARRANTS:
        return BACKEND_WARRANTS[observed][0], "backend-operation-factored-to-warrant"
    if observed == "APPLY_IDENTITY":
        return "IDENTITY", "theorem-operation-factored-to-warrant"
    if observed in {"APPLY_THEOREM", "PIGEONHOLE", "INCLUSION_EXCLUSION"}:
        return "THEOREM", "theorem-operation-factored-to-warrant"
    if observed == "APPLY_DEFINITION":
        return "DEFINITION", "operation-registry"
    if observed in {"TRANSFORM", "SUBSTITUTE", "ADD_BOTH_SIDES", "SUBTRACT_BOTH_SIDES", "DIVIDE_BOTH_SIDES", "CROSS_MULTIPLY"}:
        return "ALGEBRAIC_PRESERVATION", "operation-registry"
    if observed in {"SEARCH_META", "CONSTRUCT"}:
        return "HEURISTIC_OR_REPRESENTATION_CHOICE", "source-meta-cue"
    if observed == "OTHER":
        return "UNKNOWN", "insufficient-source-evidence"
    return "SOURCE_GROUNDED", "source-span"


def goal_effect(record: dict[str, Any], core: str) -> str:
    observed, low = record["observed_operation"], record["source_span"].lower()
    if observed in {"DISCHARGE", "DISCHARGE_GOAL"} or re.search(r"\bboxed\b|final answer|total number .* seek", low):
        return "DISCHARGE"
    if re.search(r"it suffices|enough to|we seek|we want to|goal|show that", low):
        return "CREATE_SUBGOAL"
    if observed in {"SELECT", "SELECT_CANDIDATE", "SELECT_EXTREMUM", "BOUND", "BOUND_REASONING", "BOUND_SEARCH", "OPTIMIZE"}:
        return "ADVANCE"
    return "ADVANCE" if core != "UNRESOLVED" else "NONE"


def scope_effect(record: dict[str, Any]) -> str:
    scope = record["scope"]
    if isinstance(scope, dict):
        if scope.get("branch") and record["state_delta"].get("scope_effect") == "branch-join":
            return "JOIN_BRANCHES"
        if scope.get("branch"):
            return "OPEN_BRANCH"
    elif scope not in {None, "", "global"}:
        return "OPEN_BRANCH"
    return "OPEN_BRANCH" if record["observed_operation"] == "CASE_SPLIT" else "NONE"


def epistemic_effect(record: dict[str, Any], core: str) -> str:
    observed = record["observed_operation"]
    if observed in {"VERIFY", "VERIFY_CANDIDATE"}:
        return "VERIFY_CANDIDATE"
    if observed in {"SELECT", "SELECT_CANDIDATE", "SELECT_EXTREMUM"}:
        return "PROPOSE_CANDIDATE"
    if observed == "CONTRADICTION":
        return "REJECT_CANDIDATE"
    return "UNKNOWN" if core == "UNRESOLVED" else "DERIVE"


def classify_disagreement(record: dict[str, Any], independent: str, source_span: str) -> dict[str, Any]:
    existing = record["observed_operation"]
    low = source_span.lower()
    if existing == independent or (existing in {"BOUND", "BOUND_REASONING", "OPTIMIZE"} and independent == "BOUND"):
        return {"cause": "GRANULARITY_DISAGREEMENT", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The labels converge after broad normalization; the apparent difference is granularity or goal framing."}
    if existing in {"DISCHARGE", "DISCHARGE_GOAL"}:
        return {"cause": "OPERATION_VS_GOAL_EFFECT_COLLISION", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "DISCHARGE is a goal effect; the same span may also evaluate, transform, bound, or count."}
    if existing == "TRIG_IDENTITY" and independent == "TRANSFORM":
        return {"cause": "OPERATION_VS_WARRANT_COLLISION", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The trigonometric identity is a warrant for generic TRANSFORM, not a distinct core operation."}
    if existing == "SEARCH_META" and independent in {"CONSTRUCT", "CASE_SPLIT", "BOUND"}:
        return {"cause": "MODE_VS_OPERATION_COLLISION", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "SEARCH_META names the selection mode while the source still has an underlying operation."}
    if existing in {"MODULAR_REASONING", "PROBABILITY", "SEQUENCE_RECURRENCE", "DIFFERENTIATE", "TAKE_LIMIT", "INCLUSION_EXCLUSION"}:
        return {"cause": "OPERATION_VS_DOMAIN_COLLISION", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The named mathematical procedure belongs on a domain/theorem warrant over a reusable core effect."}
    if existing == "OPTIMIZE" and independent == "BOUND":
        return {"cause": "OPERATION_VS_GOAL_EFFECT_COLLISION", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "Optimization is a goal-directed use of the generic BOUND operation."}
    if existing == "CONTRADICTION" and independent == "CASE_SPLIT":
        return {"cause": "GRANULARITY_DISAGREEMENT", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The source span contains both branch analysis and contradiction-based rejection."}
    if existing == "OTHER":
        return {"cause": "AMBIGUOUS_SOURCE", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The source has a possible operation cue, but the existing annotation correctly preserved uncertainty rather than fabricating a precise label."}
    if existing == "APPLY_THEOREM" and independent == "CASE_SPLIT" and "cents" in low:
        return {"cause": "ANNOTATION_ERROR", "genuine_semantic_disagreement": True, "resolved_by_ontology_axes": False, "explanation": "The source says to change representation into cents; it does not invoke a theorem. This is a genuine old-label error requiring review."}
    return {"cause": "GRANULARITY_DISAGREEMENT", "genuine_semantic_disagreement": False, "resolved_by_ontology_axes": True, "explanation": "The labels describe different parts of a compound source span; both are retained in provenance and axes."}


def build_disagreements(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(r["trajectory_id"], r["step_id"]): r for r in records}
    matrix = []
    for audit in read_json(HARD_AUDIT):
        for mismatch in audit["operation_mismatches"]:
            key = (audit["problem_id"], f"s{mismatch['index']}")
            record = by_key[key]
            adj = classify_disagreement(record, mismatch["independent"], mismatch["source_span"])
            core, layer = core_for(record)
            matrix.append({
                "trajectory": audit["problem_id"], "step": f"s{mismatch['index']}",
                "category": record["category"], "source_span": mismatch["source_span"],
                "existing_label": record["observed_operation"], "independent_label": mismatch["independent"],
                "existing_reasoning_mode": record["original_reasoning_mode"],
                "existing_warrant": record["original_warrant"],
                "current_candidate_core": record["original_candidate_core"],
                "current_layer": record["original_layer"], **adj,
                "proposed_axis_view": {
                    "core_operation": core, "reasoning_mode": mode_for(record),
                    "warrant": warrant_for(record)[0], "knowledge_layer": layer,
                    "goal_effect": goal_effect(record, core), "scope_effect": scope_effect(record),
                    "epistemic_effect": epistemic_effect(record, core),
                },
            })
    return matrix


def build_view(records: list[dict[str, Any]], disagreements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(d["trajectory"], d["step"]): d for d in disagreements}
    view = []
    for record in records:
        core, layer = core_for(record)
        d = by_key.get((record["trajectory_id"], record["step_id"]))
        uncertainty = "UNRESOLVED" if core == "UNRESOLVED" else "CERTAIN"
        if d and d["genuine_semantic_disagreement"]:
            uncertainty = "ANNOTATION_REVIEW"
        elif d and d["cause"] == "AMBIGUOUS_SOURCE":
            uncertainty = "SOURCE_AMBIGUOUS"
        view.append({
            "schema_version": "reasoning-ontology-v1",
            "trajectory_id": record["trajectory_id"], "step_id": record["step_id"],
            "category": record["category"], "level": record["level"],
            "source_span": record["source_span"], "reasoning_mode": mode_for(record),
            "core_operation": core, "warrant": {"type": warrant_for(record)[0], "basis": warrant_for(record)[1], "original": record["original_warrant"]},
            "knowledge_layer": layer, "goal_effect": goal_effect(record, core),
            "scope_effect": scope_effect(record), "epistemic_effect": epistemic_effect(record, core),
            "preconditions": record["preconditions"], "obligations_created": record["obligations_created"],
            "obligations_discharged": record["obligations_discharged"], "dependencies": record["dependencies"],
            "state_delta": record["state_delta"], "atomicity": record["atomicity"],
            "meta_operations": meta_ops(record["source_span"]), "uncertainty": uncertainty,
            "provenance": {
                "observed_operation": record["observed_operation"],
                "original_reasoning_mode": record["original_reasoning_mode"],
                "original_candidate_core": record["original_candidate_core"],
                "original_layer": record["original_layer"], "disagreement": d,
            },
        })
    return view


def saturation(view: list[dict[str, Any]], accepted_core: set[str]) -> list[dict[str, Any]]:
    rows = []
    previous = {"core": set(), "library": set(), "meta": set(), "warrant": set()}
    for total in [25, 50, 75, 100, 125]:
        subset = [item for item in view if int(item["trajectory_id"].split("-")[-1]) <= total]
        candidate_core = {item["core_operation"] for item in subset if item["core_operation"] != "UNRESOLVED"}
        core = candidate_core & accepted_core
        library = {item["knowledge_layer"] for item in subset if item["knowledge_layer"] in {"THEOREM_LIBRARY", "DOMAIN_LIBRARY"}}
        meta = {op for item in subset for op in item["meta_operations"]}
        warrants = {item["warrant"]["type"] for item in subset if item["warrant"]["type"] != "UNKNOWN"}
        rows.append({
            "trajectories": total, "transitions": len(subset),
            "observed_labels": len({item["provenance"]["observed_operation"] for item in subset}),
            "ontology_core_operations": len(core),
            "new_core_operations": sorted(core - previous["core"]) if total > 25 else sorted(core),
            "candidate_ontology_core_operations": len(candidate_core),
            "candidate_new_core_operations": sorted(candidate_core - previous.get("candidate_core", set())) if total > 25 else sorted(candidate_core),
            "library_operations": len(library),
            "new_library_operations": sorted(library - previous["library"]) if total > 25 else sorted(library),
            "meta_operations": len(meta),
            "new_meta_operations": sorted(meta - previous["meta"]) if total > 25 else sorted(meta),
            "warrant_types": len(warrants),
            "new_warrant_types": sorted(warrants - previous["warrant"]) if total > 25 else sorted(warrants),
        })
        previous = {"core": core, "candidate_core": candidate_core, "library": library, "meta": meta, "warrant": warrants}
    return rows


def topk(view: list[dict[str, Any]], accepted_core: set[str]) -> list[dict[str, Any]]:
    units = [item["core_operation"] for item in view if item["core_operation"] in accepted_core]
    counts = Counter(units)
    rows = []
    for k in [5, 10, 15, 20, len(counts)]:
        top = {op for op, _ in counts.most_common(k)}
        rows.append({
            "k": "all" if k == len(counts) else k, "k_numeric": k,
            "coverage": sum(op in top for op in units) / max(len(units), 1),
            "units": len(units), "distinct_core_operations": len(counts),
            "candidate_distinct_core_operations": len({item["core_operation"] for item in view if item["core_operation"] != "UNRESOLVED"}),
        })
    return rows


def core_adjudication(view: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(item["core_operation"] for item in view)
    domains = defaultdict(set)
    layers = defaultdict(Counter)
    keep = KEEP_AS_CORE
    rows = []
    for op in counts:
        for item in view:
            if item["core_operation"] == op:
                domains[op].add(item["category"])
                layers[op][item["knowledge_layer"]] += 1
        if op == "UNRESOLVED":
            decision, evidence = "UNRESOLVED", "Insufficient source evidence or explicitly ambiguous OTHER/search text."
        elif op in keep:
            decision, evidence = "KEEP_AS_CORE", "Generic state/proof/control effect recurs; named mathematical knowledge is factored onto warrant/layer axes."
        else:
            decision, evidence = "MERGE_INTO_OTHER_CORE", "No independent evidence supports a distinct primitive."
        rows.append({
            "core_operation": op, "frequency": counts[op], "domain_spread": sorted(domains[op]),
            "knowledge_layer_evidence": dict(layers[op]), "decision": decision, "evidence": evidence,
        })
    return sorted(rows, key=lambda row: (-row["frequency"], row["core_operation"]))


def write_matrix(matrix: list[dict[str, Any]]) -> str:
    lines = [
        "# Gold-125 label disagreement matrix", "",
        "All 43 hard-audit disagreements are preserved here. The matrix is an adjudication of axes, not an overwrite of frozen annotations.", "",
        "| # | Trajectory | Step | Existing | Independent | Cause | Genuine? |",
        "|---:|---|---|---|---|---|---|",
    ]
    for i, item in enumerate(matrix, 1):
        lines.append(f"| {i} | {item['trajectory']} | {item['step']} | {item['existing_label']} | {item['independent_label']} | {item['cause']} | {'YES' if item['genuine_semantic_disagreement'] else 'no'} |")
    genuine = sum(item["genuine_semantic_disagreement"] for item in matrix)
    lines += ["", "## Totals", "", f"- Before disagreement count: {len(matrix)}", f"- Explained by axes or preserved uncertainty: {len(matrix) - genuine}", f"- Genuine semantic disagreements remaining: {genuine}", f"- Annotation errors: {sum(item['cause'] == 'ANNOTATION_ERROR' for item in matrix)}", "", "| Cause | Count |", "|---|---:|"]
    lines += [f"| {cause} | {count} |" for cause, count in Counter(item["cause"] for item in matrix).most_common()]
    lines += ["", "## Detailed adjudication", ""]
    for i, item in enumerate(matrix, 1):
        lines += [
            f"### {i}. {item['trajectory']} {item['step']}", "",
            f"- Existing label: {item['existing_label']}; independent label: {item['independent_label']}",
            f"- Cause: {item['cause']}; genuine: {item['genuine_semantic_disagreement']}",
            f"- Existing mode: {item['existing_reasoning_mode']}; candidate/layer: {item['current_candidate_core']} / {item['current_layer']}",
            f"- Explanation: {item['explanation']}",
            f"- Proposed axes: {json.dumps(item['proposed_axis_view'], ensure_ascii=False)}",
            f"- Source span: {item['source_span']}", "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def write_design(view: list[dict[str, Any]], matrix: list[dict[str, Any]]) -> str:
    counts = Counter(item["core_operation"] for item in view)
    unresolved = counts["UNRESOLVED"]
    lines = [
        "# Reasoning ontology v1 design", "",
        "Ontology-v1 is a derived multi-axis view over frozen Gold-125 annotations. It does not change HML syntax, HML semantics, or canonical trajectories.", "",
        "## Design decision", "",
        "A transition may have one generic operation plus independent reasoning mode, warrant, knowledge layer, goal effect, scope effect, epistemic effect, preconditions, obligations, and state delta. The flat-label disagreement is therefore not a single categorical contest.", "",
        "Examples:", "",
        "- DISCHARGE versus EVALUATE becomes core_operation=EVALUATE plus goal_effect=DISCHARGE.",
        "- TRIG_IDENTITY versus TRANSFORM becomes core_operation=TRANSFORM plus a trigonometry warrant in DOMAIN_LIBRARY.",
        "- SEARCH_META versus CONSTRUCT becomes reasoning_mode=SEARCH_META plus core_operation=CONSTRUCT.",
        "",
        "## Axis contract", "",
        "| Axis | Question |", "|---|---|",
        "| reasoning_mode | Why is this action selected now? |",
        "| core_operation | What reusable state/proof/control effect occurs? |",
        "| warrant | What justifies the effect? |",
        "| knowledge_layer | Where does theorem/domain/backend knowledge live? |",
        "| goal_effect | Does the step create, advance, or discharge a goal? |",
        "| scope_effect | Does it open, close, or join a branch/assumption? |",
        "| epistemic_effect | Does it assert, derive, propose, verify, or reject? |",
        "| preconditions/obligations/state_delta | What must hold and what changes? |",
        "",
        "## Quality snapshot", "",
        f"- Derived transitions: {len(view)}",
        f"- Candidate core operation values: {len([op for op in counts if op != 'UNRESOLVED'])}",
        f"- Adjudicated KEEP_AS_CORE operations: {len(KEEP_AS_CORE)}",
        f"- UNRESOLVED transitions: {unresolved} ({unresolved / len(view):.1%})",
        f"- OTHER source labels retained: {sum(item['provenance']['observed_operation'] == 'OTHER' for item in view)}",
        f"- Genuine disagreement remainder: {sum(item['genuine_semantic_disagreement'] for item in matrix)}",
        "",
        "The ontology is not declared fully stabilized while UNRESOLVED remains material or the annotation-error review remains open.", "",
        "## Core boundary", "",
        "The proposed generic interface contains DECLARE, RECORD, MODEL, CONSTRUCT, TRANSFORM, SUBSTITUTE, APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, COUNT, EVALUATE, BOUND, SELECT, VERIFY, CONTRADICTION, and DISCHARGE. Named trigonometric, modular, probability, sequence, calculus, and counting rules are warrants/libraries rather than bespoke core instructions.", "",
    ]
    return "\n".join(lines)


def write_core_report(adjudication: list[dict[str, Any]]) -> str:
    lines = [
        "# Core operation adjudication v1", "",
        "These are derived-view decisions. Frozen observed labels are unchanged.", "",
        "| Operation | Frequency | Domains | Layer evidence | Decision | Evidence |",
        "|---|---:|---|---|---|---|",
    ]
    for item in adjudication:
        lines.append(f"| {item['core_operation']} | {item['frequency']} | {', '.join(item['domain_spread'])} | {item['knowledge_layer_evidence']} | {item['decision']} | {item['evidence']} |")
    lines += ["", "## Specific cleanup decisions", "",
        "- TRIG_IDENTITY -> TRANSFORM plus TRIGONOMETRY_IDENTITY warrant and DOMAIN_LIBRARY.",
        "- MODULAR_REASONING -> TRANSFORM plus MODULAR_ARITHMETIC warrant and DOMAIN_LIBRARY.",
        "- PROBABILITY/EVALUATE_PROBABILITY -> EVALUATE plus PROBABILITY_LAW warrant and DOMAIN_LIBRARY.",
        "- SEQUENCE_RECURRENCE -> TRANSFORM plus SEQUENCE_RULE warrant and DOMAIN_LIBRARY.",
        "- DIFFERENTIATE/INTEGRATE -> TRANSFORM plus CALCULUS_RULE warrant and DOMAIN_LIBRARY.",
        "- TAKE_LIMIT -> EVALUATE plus CALCULUS_RULE warrant and DOMAIN_LIBRARY.",
        "- INCLUSION_EXCLUSION/PIGEONHOLE -> COUNT plus theorem/counting warrant.",
        "- OPTIMIZE -> BOUND with goal_effect=ADVANCE.",
        "- DISCHARGE -> goal effect, with an underlying operation retained when evidenced.",
        "- OTHER and unsupported search/meta choices remain UNRESOLVED.",
        ""]
    return "\n".join(lines)


def write_saturation(rows: list[dict[str, Any]], top: list[dict[str, Any]]) -> str:
    lines = [
        "# Gold-125 ontology-v1 saturation report", "",
        "Exploratory evidence only; no asymptotic saturation claim is made.", "",
        "| Trajectories | Transitions | Observed | Accepted core | New accepted core | Candidate core | Library | Meta | Warrants |",
        "|---:|---:|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['trajectories']} | {row['transitions']} | {row['observed_labels']} | {row['ontology_core_operations']} | {', '.join(row['new_core_operations']) or 'none'} | {row['candidate_ontology_core_operations']} | {row['library_operations']} | {row['meta_operations']} | {row['warrant_types']} |")
    lines += ["", "## Core top-k coverage", "", "| k | Coverage | Units |", "|---:|---:|---:|"]
    for row in top:
        lines.append(f"| {row['k']} | {row['coverage']:.1%} | {row['units']} |")
    lines += ["", "Ontology-v1 does not carry the pre-cleanup count of 27 as sacred. It factors named warrants and orthogonal effects before counting reusable operations. Candidate operations excluded by adjudication remain visible in the derived view.", ""]
    return "\n".join(lines)


def draw_plot(path: Path, title: str, x: list[int], y: list[float], ylabel: str) -> None:
    width, height = 1100, 700
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    left, right, top, bottom = 105, 50, 90, 90
    x0, x1, y0, y1 = left, width - right, height - bottom, top
    ymax = max(1, math.ceil(max(y) * 1.2))
    draw.text((40, 25), title, fill="black")
    draw.text((20, height // 2), ylabel, fill="black")
    draw.line((x0, y0, x1, y0), fill="black", width=2)
    draw.line((x0, y0, x0, y1), fill="black", width=2)
    points = []
    for i, (xx, yy) in enumerate(zip(x, y)):
        px = x0 + (x1 - x0) * i / max(len(x) - 1, 1)
        py = y0 - (y0 - y1) * yy / ymax
        points.append((px, py))
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill="#2166ac")
        draw.text((px - 18, y0 + 10), str(xx), fill="black")
        draw.text((px - 18, py - 28), str(round(yy, 2)), fill="black")
    if len(points) > 1:
        draw.line(points, fill="#2166ac", width=4)
    for tick in range(0, ymax + 1, max(1, ymax // 5)):
        py = y0 - (y0 - y1) * tick / ymax
        draw.line((x0 - 8, py, x0, py), fill="black")
        draw.text((x0 - 45, py - 8), str(tick), fill="black")
    image.save(path)


def audit_amps(path: Path) -> dict[str, Any]:
    import pyarrow.parquet as pq
    table = pq.read_table(path)
    rows = table.to_pylist()
    columns = table.column_names
    values = {column: [row.get(column) for row in rows] for column in columns}
    topic = [text(v) for v in values.get("topic_name", [])]
    problem = [text(v) for v in values.get("problem", [])]
    solution = [text(v) for v in values.get("hints/solutions", [])]
    combined = [problem[i] + "\n" + solution[i] for i in range(len(rows))]
    patterns = {
        "visual_dependent": r"\[asy\]|begin\{asy\}|includegraphics|<img|\.png|\.jpg|\bdiagram\b|\bfigure\b|shown below|shown above",
        "multiple_choice": r"(?im)^\s*(?:\(?[A-E]\)|[A-E][\.:])\s+|\bchoices?\b|multiple[- ]choice|select the correct",
        "latex_heavy": r"\\[A-Za-z]+|\$[^$]+\$|\\\(|\\\[",
        "planning_cues": r"(?i)\b(first|notice|we need to|let'?s|it suffices|consider|instead|by symmetry|this means|we can rewrite)\b",
    }
    lengths = [len(s) for s in solution]
    return {
        "source_path": str(path), "rows": len(rows), "columns": columns,
        "byte_size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "null_counts": {column: sum(value is None for value in values[column]) for column in columns},
        "empty_counts": {column: sum(not text(value).strip() for value in values[column]) for column in columns},
        "topic_count": len(set(topic)),
        "numeric_topic_id_count": sum(bool(re.fullmatch(r"\s*\d+\s*", value)) for value in topic),
        "opaque_topic_id_count": sum(not bool(re.fullmatch(r"\s*\d+\s*", value)) for value in topic),
        "visual_dependent_count": sum(bool(re.search(patterns["visual_dependent"], value)) for value in combined),
        "multiple_choice_count": sum(bool(re.search(patterns["multiple_choice"], value)) for value in combined),
        "latex_heavy_count": sum(bool(re.search(patterns["latex_heavy"], value)) for value in combined),
        "planning_cue_count": sum(bool(re.search(patterns["planning_cues"], value)) for value in combined),
        "duplicate_problem_count": len(rows) - len(set(problem)),
        "duplicate_problem_solution_pair_count": len(rows) - len(set(zip(problem, solution))),
        "malformed_or_incomplete_proxy_count": sum(not problem[i].strip() or not solution[i].strip() for i in range(len(rows))),
        "solution_length": {
            "min": min(lengths), "p25": statistics.quantiles(lengths, n=100)[24],
            "median": statistics.median(lengths), "p75": statistics.quantiles(lengths, n=100)[74],
            "p90": statistics.quantiles(lengths, n=100)[89], "p95": statistics.quantiles(lengths, n=100)[94],
            "p99": statistics.quantiles(lengths, n=100)[98], "max": max(lengths),
        },
    }


def select_amps_plan(path: Path, limit: int = 100) -> list[dict[str, Any]]:
    import pyarrow.parquet as pq
    rows = pq.read_table(path).to_pylist()
    visual = re.compile(r"\[asy\]|begin\{asy\}|includegraphics|<img|\.png|\.jpg|\bdiagram\b|\bfigure\b|shown below|shown above", re.I)
    multiple = re.compile(r"(?im)^\s*(?:\(?[A-E]\)|[A-E][\.:])\s+|\bchoices?\b|multiple[- ]choice|select the correct")
    cue = re.compile(r"(?i)\b(first|notice|we need to|let'?s|it suffices|consider|instead|by symmetry|this means|we can rewrite)\b")
    candidates = []
    seen_pairs = set()
    for index, row in enumerate(rows):
        topic, problem, solution = text(row.get("topic_name")), text(row.get("problem")), text(row.get("hints/solutions"))
        pair = (problem, solution)
        if not problem.strip() or not solution.strip() or pair in seen_pairs:
            continue
        combined = problem + "\n" + solution
        if visual.search(combined) or multiple.search(combined) or not 120 <= len(solution) <= 3500:
            continue
        score = (20 if topic else 0) + (10 if cue.search(solution) else 0) + min(len(solution) / 500, 5)
        candidates.append((score, index, topic, problem, solution))
        seen_pairs.add(pair)
    candidates.sort(key=lambda item: (-item[0], item[1]))
    chosen, topics = [], set()
    for score, index, topic, problem, solution in candidates:
        if topic in topics:
            continue
        chosen.append({
            "candidate_id": f"AMPS-CANDIDATE-{len(chosen)+1:03d}",
            "source_row_index": index, "topic_name": topic, "problem": problem,
            "solution": solution,
            "source_hash": hashlib.sha256((problem + "\n" + solution).encode()).hexdigest(),
            "selection_score": score, "status": "PROSPECTIVE_ONLY_NOT_ANNOTATED",
        })
        topics.add(topic)
        if len(chosen) == limit:
            break
    return chosen


def amps_markdown(audit: dict[str, Any]) -> str:
    length = audit["solution_length"]
    lines = [
        "# AMPS-Khan dataset audit", "",
        "AMPS-Khan is a second distribution for cross-source falsification of the small-core thesis, not permission to create training data. The Desktop original was not modified.", "",
        "## Provenance", "",
        f"- Original parquet path: {audit['source_path']}",
        f"- Repository copy: {AMPS_RAW}",
        "- Original companion CSV: /Users/moheet/Desktop/0000.csv; not used as source of truth",
        f"- Byte size: {audit['byte_size']}",
        f"- SHA-256: {audit['sha256']}",
        f"- Rows: {audit['rows']}",
        f"- Columns: {', '.join(audit['columns'])}",
        "",
        "## Distribution audit", "",
        f"- Distinct topics: {audit['topic_count']}",
        f"- Numeric topic IDs: {audit['numeric_topic_id_count']}",
        f"- Opaque/non-numeric topic IDs: {audit['opaque_topic_id_count']}",
        f"- Null counts: {json.dumps(audit['null_counts'])}",
        f"- Empty counts: {json.dumps(audit['empty_counts'])}",
        f"- Empty/malformed proxy rows: {audit['malformed_or_incomplete_proxy_count']}",
        f"- Exact duplicate problem texts: {audit['duplicate_problem_count']}",
        f"- Exact duplicate problem+solution pairs: {audit['duplicate_problem_solution_pair_count']}",
        f"- Visual-dependent marker rows: {audit['visual_dependent_count']}",
        f"- Multiple-choice marker rows: {audit['multiple_choice_count']}",
        f"- LaTeX-heavy marker rows: {audit['latex_heavy_count']}",
        f"- Planning-cue rows: {audit['planning_cue_count']}",
        "",
        "## Solution length distribution", "",
        "| Statistic | Characters |", "|---|---:|",
    ]
    lines += [f"| {name} | {value} |" for name, value in length.items()]
    lines += [
        "",
        "## Interpretation", "",
        "The topics mix numeric identifiers with opaque human-readable families. The distribution contains clean textual/LaTeX mathematics, visual-dependent rows, multiple-choice rows, and duplicate/incomplete material. Any cross-source semantic study must filter and stratify before annotation.",
        "",
        "No AMPS trajectory was created in this mission. The future test is new core, meta, library, backend, warrant, and state-field demand relative to ontology-v1.",
        "",
    ]
    return "\n".join(lines)


def amps_plan_markdown(selected: list[dict[str, Any]], stable: bool) -> str:
    lines = [
        "# AMPS-Khan cross-source replication preparation", "",
        "This is a bounded candidate-selection plan, not an annotation run. No 100k-row processing and no training were performed.", "",
        f"- Ontology gate passed: {stable}",
        f"- Prospective topic-diverse candidates: {len(selected)}",
        "- Candidate status: PROSPECTIVE_ONLY_NOT_ANNOTATED",
        "- Approval condition: resolve ontology-v1 unresolved and annotation-review cases before creating trajectories.",
        "",
        "## Cross-source test", "",
        "Given ontology-v1 learned/discovered from MATH, count separately: new core operation, new meta operation, new library operation, new backend operation, new warrant, and new state field. New mathematics is not automatically a new reasoning primitive.",
        "",
        "## Filters", "",
        "- Original parquet is the source of truth.",
        "- One candidate per topic family where possible.",
        "- Exclude null/empty, visual-dependent, and multiple-choice rows.",
        "- Prefer source planning cues and clean machine-readable mathematics.",
        "- Preserve row index, topic, source text, and stable hash.",
        "",
        "## Candidate preview", "",
        "| Candidate | Row | Topic | Planning cue | Solution chars | Status |",
        "|---|---:|---|---|---:|---|",
    ]
    cue = re.compile(r"(?i)\b(first|notice|we need to|let'?s|it suffices|consider|instead|by symmetry|this means|we can rewrite)\b")
    for item in selected:
        lines.append(f"| {item['candidate_id']} | {item['source_row_index']} | {item['topic_name']} | {'yes' if cue.search(item['solution']) else 'no'} | {len(item['solution'])} | {item['status']} |")
    lines += ["", "This is not a Gold-100 trajectory corpus and must not be annotated automatically.", ""]
    return "\n".join(lines)


def main() -> None:
    records = load_steps()
    disagreements = build_disagreements(records)
    view = build_view(records, disagreements)
    adjudication = core_adjudication(view)
    accepted_core = {item["core_operation"] for item in adjudication if item["decision"] == "KEEP_AS_CORE"}
    sat = saturation(view, accepted_core)
    top = topk(view, accepted_core)
    counts = Counter(item["core_operation"] for item in view)
    genuine = sum(item["genuine_semantic_disagreement"] for item in disagreements)
    unresolved = counts["UNRESOLVED"]
    unresolved_fraction = unresolved / len(view)
    stable = unresolved_fraction < 0.10 and genuine == 0

    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    for item in view:
        write_json(OUT / item["trajectory_id"] / f"{item['step_id']}.json", item)
    write_json(OUT / "gold125_ontology_v1_all_transitions.json", view)
    write_json(REPORTS / "gold125_label_disagreement_matrix.json", disagreements)
    write_json(REPORTS / "gold125_ontology_v1_saturation.json", sat)
    write_json(REPORTS / "gold125_ontology_v1_core_topk.json", top)
    write_json(REPORTS / "core_operation_adjudication_v1.json", adjudication)
    (REPORTS / "gold125_label_disagreement_matrix.md").write_text(write_matrix(disagreements), encoding="utf-8")
    (REPORTS / "reasoning_ontology_v1_design.md").write_text(write_design(view, disagreements), encoding="utf-8")
    (REPORTS / "core_operation_adjudication_v1.md").write_text(write_core_report(adjudication), encoding="utf-8")
    (REPORTS / "gold125_ontology_v1_saturation.md").write_text(write_saturation(sat, top), encoding="utf-8")
    write_json(REPORTS / "gold125_ontology_quality_gate.json", {
        "before_disagreement_count": len(disagreements),
        "explained_by_axes_or_uncertainty": len(disagreements) - genuine,
        "genuine_semantic_disagreement_count": genuine,
        "annotation_error_count": sum(item["cause"] == "ANNOTATION_ERROR" for item in disagreements),
        "ontology_core_operation_count": len(accepted_core),
        "ontology_core_candidate_operation_count": len([op for op in counts if op != "UNRESOLVED"]),
        "merged_candidate_operations": sorted(op for op in counts if op not in accepted_core and op != "UNRESOLVED"),
        "unresolved_transition_count": unresolved,
        "unresolved_fraction": unresolved_fraction,
        "other_source_label_count": sum(item["provenance"]["observed_operation"] == "OTHER" for item in view),
        "other_source_label_fraction": sum(item["provenance"]["observed_operation"] == "OTHER" for item in view) / len(view),
        "ontology_stabilization_status": "PASS" if stable else "UNSTABLE_REVIEW_REQUIRED",
        "reason": "UNRESOLVED remains material and the annotation-error review remains open." if not stable else "No material unresolved or genuine disagreement remains.",
    })
    x = [row["trajectories"] for row in sat]
    draw_plot(FIGURES / "core_operation_saturation_gold125.png", "Gold-125 exploratory: accepted ontology-v1 core saturation", x, [row["ontology_core_operations"] for row in sat], "distinct accepted core operations")
    draw_plot(FIGURES / "new_core_operations_per_tranche_gold125.png", "Gold-125 exploratory: new ontology-v1 core operations", x, [len(row["new_core_operations"]) for row in sat], "new core operations")
    draw_plot(FIGURES / "core_topk_coverage_gold125.png", "Gold-125 exploratory: ontology-v1 core top-k coverage", [row["k_numeric"] for row in top], [row["coverage"] * 100 for row in top], "coverage percent")

    if not AMPS_DESKTOP.exists():
        raise FileNotFoundError(f"AMPS source not found: {AMPS_DESKTOP}")
    AMPS_RAW.parent.mkdir(parents=True, exist_ok=True)
    if not AMPS_RAW.exists() or hashlib.sha256(AMPS_RAW.read_bytes()).hexdigest() != hashlib.sha256(AMPS_DESKTOP.read_bytes()).hexdigest():
        shutil.copy2(AMPS_DESKTOP, AMPS_RAW)
    audit = audit_amps(AMPS_DESKTOP)
    write_json(REPORTS / "amps_khan_dataset_audit.json", audit)
    (REPORTS / "amps_khan_dataset_audit.md").write_text(amps_markdown(audit), encoding="utf-8")
    selected = select_amps_plan(AMPS_DESKTOP)
    write_json(REPORTS / "amps_khan_candidate_selection_plan.json", {"status": "PROSPECTIVE_ONLY_NOT_ANNOTATED", "candidates": selected})
    (REPORTS / "amps_khan_candidate_selection_plan.md").write_text(amps_plan_markdown(selected, stable), encoding="utf-8")
    print(json.dumps({
        "gold125_transitions": len(view), "before_disagreements": len(disagreements),
        "genuine_disagreements": genuine, "annotation_errors": sum(item["cause"] == "ANNOTATION_ERROR" for item in disagreements),
        "ontology_core_operations": len(accepted_core),
        "ontology_core_candidate_operations": len([op for op in counts if op != "UNRESOLVED"]),
        "unresolved_transitions": unresolved, "unresolved_fraction": unresolved_fraction,
        "ontology_status": "PASS" if stable else "UNSTABLE_REVIEW_REQUIRED",
        "amps_rows": audit["rows"], "amps_candidate_preview_count": len(selected),
        "hml_core_modified": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
