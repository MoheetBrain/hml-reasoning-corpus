#!/usr/bin/env python3
"""Build the evidence-first reasoning-layer discovery deliverables.

This program never trains or scores a language model.  It mines the already
scored 3,000-row holdout (now discovery data), the frozen HML50K corpus, and the
larger LeanDojo canonical trace.  Fresh holdouts are selected by metadata-only
hashing and excluded from every discovery statistic.
"""

from __future__ import annotations

import collections
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from semantic_extractor import (  # noqa: E402
    HISTORY_WINDOW,
    SCHEMA_VERSION,
    canonical,
    dependency_edges,
    digest_text,
    extract_reasoning_state,
    parse_lean_state,
    raw_history_payload,
    state_delta,
    tactic_family,
)


SIGNAL_REPO = Path("/Users/moheet/Documents/ChatGPT/hamiltonian-lang-final-signal")
SOURCE = Path("/Users/moheet/hml_research_artifacts/lean_domino_v2/lean_canonical_records.jsonl")
HML50K = REPO / "data/hml_50k_final"
VNEXT = REPO / "data/vnext_10k/full_audit_records.jsonl.gz"
COMMON = SIGNAL_REPO / "experiments/common_envelope_10k"
PREVIOUS = SIGNAL_REPO / "experiments/final_hml_signal"
OUT = REPO / "experiments/reasoning_layer_discovery"
SEALED = OUT / "sealed"

SELECTION_SEED = "REASONING_LAYER_FRESH_HOLDOUTS_20260824_V1"
TARGET_HOLDOUT_ROWS = 3000
PROTOCOL_COMMIT = "ce5614947da1bf184d2e04c0107211cdddf4ee20"
RESULT_COMMIT = "4bbd71c86c6650265679c565e12a48630ef4b58f"
CORPUS_COMMIT = "627194144abd9396dadbebf0b7834e76b937d908"

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_']*|[∀∃↔→¬=≤<∈⊆∧∨+*/^-]")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
META_RE = re.compile(r"\?(?:m|u)\.\d+")


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical(row) + "\n")


def write_deterministic_gzip_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            for row in rows:
                zipped.write((canonical(row) + "\n").encode("utf-8"))


def load_gzip_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def parent_id(row: dict[str, Any]) -> str:
    return f"{row['source_file']}::{row['theorem_id']}"


def transition_hash(row: dict[str, Any]) -> str:
    return digest_text(canonical({
        "example_id": row["example_id"],
        "state_before": row["lean"]["raw_state_before"],
        "action": row["lean"]["raw_tactic"],
        "state_after": row["lean"]["raw_state_after"],
    }))


def normalize_text(text: str) -> str:
    text = META_RE.sub("?META", text)
    text = NUMBER_RE.sub("#", text)
    return " ".join(text.split())


def structural_signature(raw_state: str) -> str:
    parsed = parse_lean_state(raw_state)
    payload = []
    for goal in parsed["goals"]:
        hyp_shapes = []
        names = {hyp["name"] for hyp in goal["hypotheses"]}
        for hyp in goal["hypotheses"]:
            value = normalize_text(hyp["type"])
            for name in sorted(names, key=len, reverse=True):
                value = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", "@", value)
            hyp_shapes.append(value)
        target = normalize_text(goal["target"])
        for name in sorted(names, key=len, reverse=True):
            target = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", "@", target)
        payload.append({
            "case": bool(goal["case_label"]),
            "hypothesis_type_shapes": hyp_shapes,
            "target": target,
            "target_shape": goal["target_shape"],
        })
    return digest_text(canonical(payload))


def compact_source_row(row: dict[str, Any]) -> dict[str, Any]:
    raw = row["lean"]["raw_state_before"]
    parsed = parse_lean_state(raw)
    active = parsed["goals"][0] if parsed["goals"] else None
    return {
        "example_id": row["example_id"],
        "parent_id": parent_id(row),
        "step_index": row["transition_index"],
        "depth": row["proof_depth"],
        "official_split": row["lean_official_split"],
        "state_hash": digest_text(raw),
        "structural_signature": structural_signature(raw),
        "action_family": tactic_family(row["lean"]["raw_tactic"]),
        "n_goals": parsed["open_goal_count"],
        "hypothesis_count": sum(len(g["hypotheses"]) for g in parsed["goals"]),
        "target_shape": "NO_GOAL" if active is None else active["target_shape"],
        "case_label": None if active is None else active["case_label"],
    }


def load_hml_records() -> tuple[dict[str, dict[str, Any]], set[str], set[str], set[str]]:
    records: dict[str, dict[str, Any]] = {}
    parents: set[str] = set()
    states: set[str] = set()
    final_ids: set[str] = set()
    for row in load_gzip_jsonl(HML50K / "canonical/records.jsonl.gz"):
        records[row["canonical_source_example_id"]] = row
        parents.add(row["parent_id"])
        raw = row["neutral_transition"]["state_before"]["claims"]["p0"]["proposition"]
        states.add(digest_text(raw))
        if row["split"] == "final":
            final_ids.add(row["canonical_source_example_id"])
    return records, parents, states, final_ids


def load_vnext_parents() -> set[str]:
    return {row["parent_id"] for row in load_gzip_jsonl(VNEXT)}


def choose_exact_parent_groups(
    groups: dict[str, list[dict[str, Any]]], salt: str, target: int,
) -> tuple[list[dict[str, Any]], set[str]]:
    ordered = sorted(groups, key=lambda p: digest_text(f"{SELECTION_SEED}|{salt}|{p}"))
    chosen: list[dict[str, Any]] = []
    chosen_parents: set[str] = set()
    total = 0
    for parent in ordered:
        size = len(groups[parent])
        if total + size <= target:
            chosen.extend(groups[parent])
            chosen_parents.add(parent)
            total += size
        if total == target:
            break
    if total != target:
        raise AssertionError(f"could not select exactly {target} rows for {salt}: {total}")
    chosen.sort(key=lambda x: (x["parent_id"], x["step_index"], x["example_id"]))
    return chosen, chosen_parents


def seal_holdouts(
    candidates: dict[str, list[dict[str, Any]]], hml50k_parents: set[str], vnext_parents: set[str],
    previous_states: set[str],
) -> tuple[dict[str, Any], set[str]]:
    previous_parents = hml50k_parents | vnext_parents
    eligible = {
        parent: rows for parent, rows in candidates.items()
        if parent not in previous_parents and all(row["state_hash"] not in previous_states for row in rows)
    }
    a, a_parents = choose_exact_parent_groups(eligible, "FRESH_FINAL_A", TARGET_HOLDOUT_ROWS)
    remaining = {p: rows for p, rows in eligible.items() if p not in a_parents}
    a_states = {row["state_hash"] for row in a}
    remaining = {p: rows for p, rows in remaining.items() if not any(r["state_hash"] in a_states for r in rows)}
    b, b_parents = choose_exact_parent_groups(remaining, "FRESH_FINAL_B", TARGET_HOLDOUT_ROWS)
    if a_parents & b_parents:
        raise AssertionError("fresh holdout parent overlap")
    if {x["state_hash"] for x in a} & {x["state_hash"] for x in b}:
        raise AssertionError("fresh holdout state overlap")

    assignments = []
    for holdout, rows in (("FRESH_FINAL_A", a), ("FRESH_FINAL_B", b)):
        for row in rows:
            assignments.append({
                "holdout": holdout,
                "example_id": row["example_id"],
                "parent_id": row["parent_id"],
                "step_index": row["step_index"],
                "official_split": row["official_split"],
                "current_state_sha256": row["state_hash"],
                "transition_commitment_sha256": row["transition_hash"],
                "gold_action_commitment_sha256": row["action_hash"],
            })
    assignment_path = SEALED / "fresh_holdout_assignments.jsonl.gz"
    write_deterministic_gzip_jsonl(assignment_path, assignments)

    def arm_summary(name: str, rows: list[dict[str, Any]], parents: set[str]) -> dict[str, Any]:
        ids = sorted(row["example_id"] for row in rows)
        state_hashes = sorted(row["state_hash"] for row in rows)
        transition_hashes = sorted(row["transition_hash"] for row in rows)
        return {
            "status": "SEALED_LABELS_UNINSPECTED",
            "records": len(rows),
            "parents": len(parents),
            "official_split_counts": dict(sorted(collections.Counter(x["official_split"] for x in rows).items())),
            "record_id_set_sha256": digest_text("\n".join(ids) + "\n"),
            "parent_id_set_sha256": digest_text("\n".join(sorted(parents)) + "\n"),
            "current_state_hash_set_sha256": digest_text("\n".join(state_hashes) + "\n"),
            "transition_commitment_set_sha256": digest_text("\n".join(transition_hashes) + "\n"),
        }

    manifest = {
        "artifact": "FRESH_HOLDOUT_MANIFEST",
        "version": "1.0.0",
        "created_utc": "2026-08-24",
        "selection_seed": SELECTION_SEED,
        "selection_policy": "metadata-only deterministic hash order over unused parents from all LeanDojo official splits; complete theorem parents greedily admitted without exceeding 3,000 rows",
        "source": {
            "path": str(SOURCE),
            "sha256": file_sha(SOURCE),
            "mathlib_commit": "29dcec074de168ac2bf835a77ef68bbe069194c5",
        },
        "exclusions": {
            "hml50k_parent_count": len(hml50k_parents),
            "vnext_parent_count": len(vnext_parents),
            "excluded_previous_parent_union_count": len(previous_parents),
            "hml50k_state_hash_count": len(previous_states),
            "zero_parent_overlap_with_all_previous_hml50k_and_vnext": True,
            "zero_exact_state_overlap_with_previous_hml50k": True,
            "zero_parent_overlap_a_vs_b": True,
            "zero_exact_state_overlap_a_vs_b": True,
        },
        "label_firewall": {
            "labels_or_predictions_inspected_during_semantic_design": False,
            "action_text_present_in_manifest": False,
            "assignments_contain_only_action_hash_commitments": True,
            "unlock_rule_a": "only after V1 ontology and extractor are committed",
            "unlock_rule_b": "only after one evidence-cited V2 revision following FINAL_A",
        },
        "holdouts": {
            "FRESH_FINAL_A": arm_summary("FRESH_FINAL_A", a, a_parents),
            "FRESH_FINAL_B": arm_summary("FRESH_FINAL_B", b, b_parents),
        },
        "sealed_assignment_file": {
            "path": str(assignment_path.relative_to(OUT)),
            "sha256": file_sha(assignment_path),
            "rows": len(assignments),
        },
        "integrity": "PASS",
    }
    write_json(OUT / "FRESH_HOLDOUT_MANIFEST.json", manifest)
    return manifest, a_parents | b_parents


def entropy(counter: collections.Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counter.values())


def conditional_entropy(groups: dict[Any, collections.Counter[str]]) -> float:
    total = sum(sum(counter.values()) for counter in groups.values())
    if not total:
        return 0.0
    return sum((sum(counter.values()) / total) * entropy(counter) for counter in groups.values())


def bin_count(value: int) -> str:
    if value == 0:
        return "0"
    if value == 1:
        return "1"
    if value <= 3:
        return "2-3"
    if value <= 7:
        return "4-7"
    if value <= 15:
        return "8-15"
    return "16+"


def module_features(raw_state: str, prior: list[dict[str, str]]) -> dict[str, list[str]]:
    semantic = extract_reasoning_state(raw_state, prior)
    active = semantic["active_goal"]
    goal = [
        f"G:count={bin_count(len(semantic['open_goals']))}",
        f"G:active_shape={None if active is None else active['target_shape']}",
        f"G:hypotheses={bin_count(0 if active is None else active['hypothesis_count'])}",
    ] + [f"G:open_shape={item['target_shape']}" for item in semantic["open_goals"]]
    deps = semantic["local_dependencies"]
    dependency = [
        f"D:edges={bin_count(len(deps))}",
        f"D:goal_refs={bin_count(sum(item['to'] == '@goal' for item in deps))}",
    ]
    scope = semantic["active_scope"]
    branch_scope = [
        f"SB:case_present={scope['source_explicit']}",
        f"SB:case={scope['case_label'] or 'NONE'}",
    ]
    history = [f"H:steps={bin_count(semantic['trajectory_position']['steps_completed'])}"]
    for item in semantic["recent_actions"]:
        history.append(f"H:action:{item['offset']}={item['family']}")
    for item in semantic["recent_deltas"]:
        history.extend([
            f"H:goal_delta:{item['offset']}={item['open_goal_delta']}",
            f"H:target_changed:{item['offset']}={item['target_changed']}",
            f"H:hyp_add:{item['offset']}={bin_count(len(item['hypotheses_added']))}",
            f"H:hyp_remove:{item['offset']}={bin_count(len(item['hypotheses_removed']))}",
        ])
    return {"G": goal, "D": dependency, "SB": branch_scope, "H": history}


def base_features(raw_state: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(raw_state)]
    counts = collections.Counter(tokens)
    # Binary lexical features prevent very long contexts from dominating the cheap probe.
    return [f"T:{token}" for token, _ in counts.most_common(192)]


class MultinomialNB:
    def __init__(self) -> None:
        self.class_rows: collections.Counter[str] = collections.Counter()
        self.feature_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
        self.class_feature_totals: collections.Counter[str] = collections.Counter()
        self.vocabulary: set[str] = set()
        self.total = 0

    def fit_one(self, label: str, features: Iterable[str]) -> None:
        self.class_rows[label] += 1
        self.total += 1
        for feature in features:
            self.feature_counts[label][feature] += 1
            self.class_feature_totals[label] += 1
            self.vocabulary.add(feature)

    def predict(self, features: Iterable[str]) -> str:
        values = list(features)
        best_label = ""
        best_score = -math.inf
        class_count = len(self.class_rows)
        vocabulary_size = max(1, len(self.vocabulary))
        for label, count in self.class_rows.items():
            score = math.log((count + 1) / (self.total + class_count))
            denom = self.class_feature_totals[label] + vocabulary_size
            feature_counts = self.feature_counts[label]
            for feature in values:
                score += math.log((feature_counts.get(feature, 0) + 1) / denom)
            if score > best_score or (score == best_score and label < best_label):
                best_label, best_score = label, score
        return best_label


def run_probe(
    selected: dict[str, dict[str, Any]], source_rows: dict[str, dict[str, Any]], histories: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    variants = {
        "BASE_LEXICAL": [],
        "BASE_PLUS_GOALS": ["G"],
        "BASE_PLUS_DEPENDENCIES": ["D"],
        "BASE_PLUS_BRANCH_SCOPE": ["SB"],
        "BASE_PLUS_HISTORY": ["H"],
        "FULL_SEMANTICS": ["G", "D", "SB", "H"],
    }
    models = {name: MultinomialNB() for name in variants}
    train_ids = [example for example, row in selected.items() if row["split"] == "train" and example in source_rows]
    dev_ids = [example for example, row in selected.items() if row["split"] == "final" and example in source_rows]

    for example in train_ids:
        source = source_rows[example]
        raw = source["lean"]["raw_state_before"]
        label = tactic_family(source["lean"]["raw_tactic"])
        modules = module_features(raw, histories.get(example, []))
        base = base_features(raw)
        for name, used in variants.items():
            models[name].fit_one(label, base + [f for module in used for f in modules[module]])

    results = {}
    for name, used in variants.items():
        correct = 0
        by_depth: dict[str, list[int]] = collections.defaultdict(list)
        for example in dev_ids:
            source = source_rows[example]
            raw = source["lean"]["raw_state_before"]
            gold = tactic_family(source["lean"]["raw_tactic"])
            modules = module_features(raw, histories.get(example, []))
            pred = models[name].predict(base_features(raw) + [f for module in used for f in modules[module]])
            hit = int(pred == gold)
            correct += hit
            depth = source["proof_depth"] + 1
            bucket = "1" if depth == 1 else "2-3" if depth <= 3 else "4-5" if depth <= 5 else "6-10" if depth <= 10 else "11-20" if depth <= 20 else "21+"
            by_depth[bucket].append(hit)
        accuracy = correct / len(dev_ids)
        results[name] = {
            "target": "next recorded tactic family (cheap proxy, not six-way action selection)",
            "train_rows": len(train_ids),
            "discovery_dev_rows": len(dev_ids),
            "accuracy": accuracy,
            "by_depth_accuracy": {k: sum(v) / len(v) for k, v in sorted(by_depth.items())},
        }
    baseline = results["BASE_LEXICAL"]["accuracy"]
    for result in results.values():
        result["delta_vs_base_pp"] = 100 * (result["accuracy"] - baseline)
    return results


def build_histories(parent_rows: dict[str, list[dict[str, Any]]], selected_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    histories: dict[str, list[dict[str, str]]] = {}
    for rows in parent_rows.values():
        rows.sort(key=lambda x: (x["transition_index"], x["example_id"]))
        prior: list[dict[str, str]] = []
        for row in rows:
            if row["example_id"] in selected_ids:
                histories[row["example_id"]] = list(prior)
            prior.append({
                "state_before": row["lean"]["raw_state_before"],
                "action": row["lean"]["raw_tactic"],
                "state_after": row["lean"]["raw_state_after"],
            })
    return histories


def load_prediction_maps() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    common_rows = {}
    with (COMMON / "diagnostics/paired_final_diagnostics.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            common_rows[row["record_id"]] = row
    old_hml = json.loads((PREVIOUS / "raw_predictions/10k_hml_s1.json").read_text(encoding="utf-8"))
    old_neutral = json.loads((PREVIOUS / "raw_predictions/10k_neutral_s1.json").read_text(encoding="utf-8"))
    return common_rows, {x["record_id"]: x for x in old_hml["rows"]}, {x["record_id"]: x for x in old_neutral["rows"]}


def taxonomy_for(row: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    if row["disagreement_category"] == "BOTH_CORRECT":
        return [], "NONE", []
    categories: list[str] = []
    evidence: list[str] = []
    if row["disagreement_category"] in {"NEUTRAL_ONLY", "HML_ONLY"}:
        categories.append("REPRESENTATION_COMPLEXITY")
        evidence.append("semantically matched common-envelope arms disagree on this row")
    if row["n_goals"] > 1:
        categories.append("GOAL_SELECTION")
        evidence.append("wrong prediction occurs with multiple source-explicit open goals")
    if row["gold_references_local_hypothesis"]:
        categories.append("PREMISE_DEPENDENCY")
        evidence.append("recorded correct tactic explicitly references a local declaration")
    if row["case_marker_present"]:
        categories.append("BRANCH_STATE")
        evidence.append("current Lean state contains a source-explicit case identity")
    if row["same_family_candidate_count"] == 6:
        categories.append("ACTION_APPLICABILITY")
        evidence.append("all six plausible candidates share the recorded tactic family; alternatives were not replayed")
    categories = list(dict.fromkeys(categories))
    priority = ["REPRESENTATION_COMPLEXITY", "GOAL_SELECTION", "PREMISE_DEPENDENCY", "BRANCH_STATE", "ACTION_APPLICABILITY"]
    primary = next((x for x in priority if x in categories), "UNKNOWN")
    if primary == "UNKNOWN":
        evidence.append("available passive trace does not identify a more specific causal failure")
    return categories or ["UNKNOWN"], primary, evidence


def build_failure_rows(
    selected: dict[str, dict[str, Any]], source_rows: dict[str, dict[str, Any]], histories: dict[str, list[dict[str, str]]],
    common_rows: dict[str, dict[str, Any]], old_hml: dict[str, Any], old_neutral: dict[str, Any],
) -> list[dict[str, Any]]:
    by_record = {row["record_id"]: (example, row) for example, row in selected.items() if row["split"] == "final"}
    output = []
    for record_id, diagnostic in sorted(common_rows.items()):
        example, corpus = by_record[record_id]
        source = source_rows[example]
        raw = source["lean"]["raw_state_before"]
        parsed = parse_lean_state(raw)
        active = parsed["goals"][0] if parsed["goals"] else {"hypotheses": [], "target": "", "target_shape": "NO_GOAL", "case_label": None}
        local_names = [hyp["name"] for goal in parsed["goals"] for hyp in goal["hypotheses"]]
        gold_tactic = source["lean"]["raw_tactic"]
        gold_tokens = set(TOKEN_RE.findall(gold_tactic))
        candidates = corpus["candidate_audit"]["candidates"]
        families = [tactic_family(x["tactic_text"]) for x in candidates]
        gold_family = tactic_family(gold_tactic)
        prior = histories.get(example, [])
        semantic = extract_reasoning_state(raw, prior)
        disagreement = "BOTH_CORRECT" if diagnostic["hml_correct"] and diagnostic["neutral_correct"] else "HML_ONLY" if diagnostic["hml_correct"] else "NEUTRAL_ONLY" if diagnostic["neutral_correct"] else "BOTH_WRONG"
        row = {
            "record_id": record_id,
            "canonical_source_example_id": example,
            "theorem_parent": diagnostic["parent_id"],
            "discovery_split": "DISCOVERY_DEV_FROM_OLD_FINAL",
            "disagreement_category": disagreement,
            "proof_depth": diagnostic["depth"],
            "trajectory_step_index": source["transition_index"],
            "steps_completed": len(prior),
            "number_hypotheses": sum(len(goal["hypotheses"]) for goal in parsed["goals"]),
            "n_goals": parsed["open_goal_count"],
            "multiple_goals": parsed["open_goal_count"] > 1,
            "goal_form": active["target_shape"],
            "case_marker_present": bool(active["case_label"]),
            "case_label_hash": None if not active["case_label"] else digest_text(active["case_label"]),
            "local_dependency_edge_count": len(dependency_edges(parsed)),
            "gold_references_local_hypothesis": any(name in gold_tokens for name in local_names),
            "candidate_families": families,
            "same_family_candidate_count": sum(family == gold_family for family in families),
            "recorded_tactic_family": gold_family,
            "recent_action_families": [tactic_family(event["action"]) for event in prior[-HISTORY_WINDOW:]],
            "repeated_recent_action": len(prior) >= 2 and tactic_family(prior[-1]["action"]) == tactic_family(prior[-2]["action"]),
            "recent_state_deltas": [state_delta(event["state_before"], event["state_after"]) for event in prior[-HISTORY_WINDOW:]],
            "actual_failed_or_invalid_actions_available": False,
            "hml_prompt_tokens": diagnostic["hml_prompt_tokens"],
            "neutral_prompt_tokens": diagnostic["neutral_prompt_tokens"],
            "lexical_baseline_correct": diagnostic["lexical_heuristic_correct"],
            "complexity": diagnostic["complexity"],
            "current_state_sha256": digest_text(raw),
            "raw_history_sha256": digest_text(canonical(raw_history_payload(prior))),
            "semantic_state_sha256": digest_text(canonical(semantic)),
            "gold_label": f"C{diagnostic['gold_index']}",
            "common_envelope": {
                "hml_prediction": f"C{diagnostic['hml_prediction']}",
                "neutral_prediction": f"C{diagnostic['neutral_prediction']}",
                "hml_correct": diagnostic["hml_correct"],
                "neutral_correct": diagnostic["neutral_correct"],
            },
            "previous_envelope": {
                "hml_prediction": f"C{old_hml[record_id]['pred_index']}",
                "neutral_prediction": f"C{old_neutral[record_id]['pred_index']}",
                "hml_correct": old_hml[record_id]["correct"],
                "neutral_correct": old_neutral[record_id]["correct"],
            },
            "prediction_changed_previous_to_common": {
                "hml": old_hml[record_id]["pred_index"] != diagnostic["hml_prediction"],
                "neutral": old_neutral[record_id]["pred_index"] != diagnostic["neutral_prediction"],
            },
        }
        categories, primary, evidence = taxonomy_for(row)
        row["error_taxonomy"] = categories
        row["primary_error_category"] = primary
        row["taxonomy_evidence"] = evidence
        output.append(row)
    if len(output) != 3000:
        raise AssertionError(f"expected 3000 discovery rows, got {len(output)}")
    return output


def state_sufficiency_analysis(
    compact_rows: dict[str, list[dict[str, Any]]], sealed_parents: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    exact: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    structural: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    structural_history: dict[tuple[str, tuple[str, ...]], collections.Counter[str]] = collections.defaultdict(collections.Counter)
    examples: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    rows_used = 0
    parents_used = 0
    for parent, rows in compact_rows.items():
        if parent in sealed_parents:
            continue
        parents_used += 1
        rows.sort(key=lambda x: (x["step_index"], x["example_id"]))
        previous: list[str] = []
        for row in rows:
            family = row["action_family"]
            exact[row["state_hash"]][family] += 1
            structural[row["structural_signature"]][family] += 1
            hkey = tuple(previous[-HISTORY_WINDOW:])
            structural_history[(row["structural_signature"], hkey)][family] += 1
            if len(examples[row["structural_signature"]]) < 12:
                examples[row["structural_signature"]].append({
                    "example_id": row["example_id"], "parent_id": parent,
                    "step_index": row["step_index"], "state_hash": row["state_hash"],
                    "recorded_action_family": family, "previous_action_families": list(hkey),
                    "n_goals": row["n_goals"], "hypothesis_count": row["hypothesis_count"],
                    "target_shape": row["target_shape"], "case_marker_present": bool(row["case_label"]),
                })
            previous.append(family)
            rows_used += 1

    exact_amb = {key: value for key, value in exact.items() if len(value) > 1}
    structural_amb = {key: value for key, value in structural.items() if len(value) > 1}
    candidates = []
    for signature, counts in structural_amb.items():
        sample = examples[signature]
        if len({x["recorded_action_family"] for x in sample}) < 2:
            continue
        history_groups: dict[tuple[str, ...], collections.Counter[str]] = collections.defaultdict(collections.Counter)
        for (sig, history), counter in structural_history.items():
            if sig == signature:
                history_groups[history].update(counter)
        h_state = entropy(counts)
        h_history = conditional_entropy(history_groups)
        candidates.append({
            "structural_signature_sha256": signature,
            "rows": sum(counts.values()),
            "action_family_count": len(counts),
            "action_family_distribution": dict(counts.most_common()),
            "action_entropy_bits": h_state,
            "action_entropy_with_recent_history_bits": h_history,
            "history_explained_bits": h_state - h_history,
            "representative_rows": sample,
        })
    candidates.sort(key=lambda x: (x["history_explained_bits"], x["rows"]), reverse=True)
    candidates = candidates[:200]
    summary = {
        "source_rows_used": rows_used,
        "source_parents_used": parents_used,
        "fresh_holdout_rows_used": 0,
        "exact_state_signatures": len(exact),
        "exact_state_alias_clusters_with_multiple_recorded_action_families": len(exact_amb),
        "exact_state_rows_in_ambiguous_clusters": sum(sum(x.values()) for x in exact_amb.values()),
        "structural_state_signatures": len(structural),
        "structural_alias_clusters_with_multiple_recorded_action_families": len(structural_amb),
        "structural_rows_in_ambiguous_clusters": sum(sum(x.values()) for x in structural_amb.values()),
        "conditional_entropy_action_family_given_structural_state_bits": conditional_entropy(structural),
        "conditional_entropy_action_family_given_structural_state_and_recent_action_families_bits": conditional_entropy(structural_history),
    }
    summary["recent_history_entropy_reduction_bits"] = (
        summary["conditional_entropy_action_family_given_structural_state_bits"]
        - summary["conditional_entropy_action_family_given_structural_state_and_recent_action_families_bits"]
    )
    summary["interpretation"] = (
        "observational evidence that recent successful trajectory history reduces ambiguity beyond a deterministic structural current-state signature"
        if summary["recent_history_entropy_reduction_bits"] > 0 else
        "no observational entropy reduction from the tested recent-history signature"
    )
    return summary, candidates


def mutual_information(rows: list[tuple[str, str]]) -> float:
    joint = collections.Counter(rows)
    xs = collections.Counter(x for x, _ in rows)
    ys = collections.Counter(y for _, y in rows)
    total = len(rows)
    value = 0.0
    for (x, y), count in joint.items():
        pxy = count / total
        value += pxy * math.log2(pxy / ((xs[x] / total) * (ys[y] / total)))
    return value


def module_screen(
    failure_rows: list[dict[str, Any]], probe: dict[str, Any], state_summary: dict[str, Any],
    selected: dict[str, dict[str, Any]], source_rows: dict[str, dict[str, Any]], histories: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    error_rows = [row for row in failure_rows if row["primary_error_category"] != "NONE"]
    dev_examples = [example for example, row in selected.items() if row["split"] == "final"]
    module_payload_chars: dict[str, list[int]] = collections.defaultdict(list)
    module_presence: dict[str, int] = collections.Counter()
    mi_rows: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for example in dev_examples:
        source = source_rows[example]
        raw = source["lean"]["raw_state_before"]
        semantic = extract_reasoning_state(raw, histories.get(example, []))
        label = tactic_family(source["lean"]["raw_tactic"])
        payloads = {
            "GOALS": {"active_goal": semantic["active_goal"], "open_goals": semantic["open_goals"]},
            "DEPENDENCIES": semantic["local_dependencies"],
            "BRANCH_SCOPE": semantic["active_scope"],
            "HISTORY": {k: semantic[k] for k in ("trajectory_position", "recent_actions", "recent_deltas", "progress_summary")},
        }
        presence = {
            "GOALS": bool(semantic["open_goals"]),
            "DEPENDENCIES": bool(semantic["local_dependencies"]),
            "BRANCH_SCOPE": semantic["active_scope"]["source_explicit"],
            "HISTORY": bool(semantic["recent_actions"]),
        }
        active = semantic["active_goal"]
        coarse_values = {
            "GOALS": canonical({
                "count": bin_count(len(semantic["open_goals"])),
                "active_shape": None if active is None else active["target_shape"],
                "hypotheses": bin_count(0 if active is None else active["hypothesis_count"]),
            }),
            "DEPENDENCIES": canonical({
                "edges": bin_count(len(semantic["local_dependencies"])),
                "goal_refs": bin_count(sum(x["to"] == "@goal" for x in semantic["local_dependencies"])),
            }),
            "BRANCH_SCOPE": canonical({"case_present": semantic["active_scope"]["source_explicit"]}),
            "HISTORY": canonical({
                "steps": bin_count(semantic["trajectory_position"]["steps_completed"]),
                "previous_family": None if not semantic["recent_actions"] else semantic["recent_actions"][-1]["family"],
                "previous_goal_delta": None if not semantic["recent_deltas"] else semantic["recent_deltas"][-1]["open_goal_delta"],
            }),
        }
        for module, payload in payloads.items():
            module_payload_chars[module].append(len(canonical(payload)))
            module_presence[module] += int(presence[module])
            mi_rows[module].append((coarse_values[module], label))

    mapping = {
        "GOALS": "BASE_PLUS_GOALS", "DEPENDENCIES": "BASE_PLUS_DEPENDENCIES",
        "BRANCH_SCOPE": "BASE_PLUS_BRANCH_SCOPE", "HISTORY": "BASE_PLUS_HISTORY",
    }
    modules = {}
    failure_map = {
        "GOALS": ["GOAL_SELECTION"], "DEPENDENCIES": ["PREMISE_DEPENDENCY"],
        "BRANCH_SCOPE": ["BRANCH_STATE", "SCOPE_CONFUSION"],
        "HISTORY": ["TRAJECTORY_MEMORY", "STRATEGY_STATE", "SEARCH_LOOP"],
    }
    for module in mapping:
        screen = probe[mapping[module]]
        addressed = failure_map[module]
        evidence_errors = sum(any(category in row["error_taxonomy"] for category in addressed) for row in error_rows)
        prevalence = module_presence[module] / len(dev_examples)
        keep = (
            module == "GOALS"
            or evidence_errors >= 25
            or (module == "HISTORY" and state_summary["recent_history_entropy_reduction_bits"] > 0)
            or screen["delta_vs_base_pp"] > 0
        )
        modules[module] = {
            "provenance": ["A_SOURCE_EXPLICIT", "B_FORMALLY_DERIVABLE"],
            "prevalence": prevalence,
            "mean_approx_token_cost": sum(module_payload_chars[module]) / len(module_payload_chars[module]) / 4,
            "failure_classes_addressed": addressed,
            "evidence_tagged_error_rows": evidence_errors,
            "coarse_plug_in_mutual_information_with_tactic_family_bits": mutual_information(mi_rows[module]),
            "cheap_probe_accuracy": screen["accuracy"],
            "cheap_probe_delta_vs_base_pp": screen["delta_vs_base_pp"],
            "model_screen": "NOT_RUN",
            "decision": "KEEP_V1" if keep else "DROP_V1",
            "decision_basis": "source-supported prevalence/failure evidence and discovery-only cheap probe; not confirmatory",
        }
    modules["OBLIGATIONS"] = {
        "decision": "DROP_V1", "reason": "passive Lean source has no obligation object distinct from ordinary open goals",
        "provenance": [], "model_screen": "NOT_RUN",
    }
    modules["VERIFIED_SEARCH_MEMORY"] = {
        "decision": "DROP_V1", "reason": "passive successful traces contain no failed attempts; no candidate replay was authorized in this stage",
        "provenance": [], "model_screen": "NOT_RUN",
    }
    modules["LEMMA_INVARIANT_ROLE"] = {
        "decision": "DROP_V1", "reason": "strategy/role labels are not source-explicit or deterministically certified in the acquired trace",
        "provenance": [], "model_screen": "NOT_RUN",
    }
    return {
        "screening_status": "DISCOVERY_ONLY_NOT_CONFIRMATORY",
        "base_probe": probe["BASE_LEXICAL"],
        "full_probe": probe["FULL_SEMANTICS"],
        "modules": modules,
        "admitted_modules": [name for name, result in modules.items() if result.get("decision") == "KEEP_V1"],
    }


def make_schema(admitted: list[str]) -> dict[str, Any]:
    required = ["schema_version"]
    properties: dict[str, Any] = {"schema_version": {"const": SCHEMA_VERSION}}
    module_fields = {
        "GOALS": ["active_goal", "open_goals"],
        "DEPENDENCIES": ["local_dependencies"],
        "BRANCH_SCOPE": ["active_scope"],
        "HISTORY": ["trajectory_position", "recent_actions", "recent_deltas", "progress_summary"],
    }
    hash_field = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    active_goal_object = {
        "type": "object", "additionalProperties": False,
        "required": ["position", "goal_hash", "target", "target_shape", "hypothesis_count"],
        "properties": {
            "position": {"const": 0}, "goal_hash": hash_field, "target": {"type": "string"},
            "target_shape": {"enum": ["EMPTY", "FORALL", "EXISTS", "IFF", "IMPLIES", "NOT", "EQUALITY", "ORDER", "MEMBERSHIP", "SUBSET", "AND", "OR", "APPLICATION"]},
            "hypothesis_count": {"type": "integer", "minimum": 0},
        },
    }
    open_goal_item = {
        "type": "object", "additionalProperties": False,
        "required": ["position", "goal_hash", "case_label", "target_shape", "hypothesis_count"],
        "properties": {
            "position": {"type": "integer", "minimum": 0}, "goal_hash": hash_field,
            "case_label": {"type": ["string", "null"]},
            "target_shape": active_goal_object["properties"]["target_shape"],
            "hypothesis_count": {"type": "integer", "minimum": 0},
        },
    }
    delta_item = {
        "type": "object", "additionalProperties": False,
        "required": ["offset", "open_goal_delta", "target_changed", "hypotheses_added", "hypotheses_removed", "hypotheses_rebound"],
        "properties": {
            "offset": {"type": "integer", "minimum": -HISTORY_WINDOW, "maximum": -1},
            "open_goal_delta": {"type": "integer"}, "target_changed": {"type": "boolean"},
            "hypotheses_added": {"type": "array", "items": {"type": "string"}},
            "hypotheses_removed": {"type": "array", "items": {"type": "string"}},
            "hypotheses_rebound": {"type": "array", "items": {"type": "string"}},
        },
    }
    all_definitions = {
        "active_goal": {"oneOf": [{"type": "null"}, active_goal_object]},
        "open_goals": {"type": "array", "items": open_goal_item},
        "local_dependencies": {
            "type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["goal_index", "from", "to"],
                "properties": {
                    "goal_index": {"type": "integer", "minimum": 0},
                    "from": {"type": "string", "minLength": 1}, "to": {"type": "string", "minLength": 1},
                },
            },
        },
        "active_scope": {
            "type": "object", "additionalProperties": False,
            "required": ["case_label", "source_explicit"],
            "properties": {"case_label": {"type": ["string", "null"]}, "source_explicit": {"type": "boolean"}},
        },
        "trajectory_position": {
            "type": "object", "additionalProperties": False, "required": ["steps_completed"],
            "properties": {"steps_completed": {"type": "integer", "minimum": 0}},
        },
        "recent_actions": {
            "type": "array", "maxItems": HISTORY_WINDOW,
            "items": {
                "type": "object", "additionalProperties": False, "required": ["offset", "family"],
                "properties": {
                    "offset": {"type": "integer", "minimum": -HISTORY_WINDOW, "maximum": -1},
                    "family": {"type": "string", "minLength": 1},
                },
            },
        },
        "recent_deltas": {"type": "array", "maxItems": HISTORY_WINDOW, "items": delta_item},
        "progress_summary": {
            "type": "object", "additionalProperties": False,
            "required": ["open_goal_count", "recent_net_goal_delta", "repeated_recent_action_family"],
            "properties": {
                "open_goal_count": {"type": "integer", "minimum": 0},
                "recent_net_goal_delta": {"type": "integer"},
                "repeated_recent_action_family": {"type": ["string", "null"]},
            },
        },
    }
    for module in admitted:
        for field in module_fields[module]:
            required.append(field)
            properties[field] = all_definitions[field]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://hml.reasoning.local/schemas/reasoning-state-v1.json",
        "title": "Representation-neutral reasoning state V1",
        "description": "Small evidence-selected pre-action state; canonical JSON is the primary rendering.",
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
        "x-scientific-constraints": {
            "uses_gold_or_future_action": False,
            "allowed_provenance_classes": ["A_SOURCE_EXPLICIT", "B_FORMALLY_DERIVABLE", "C_REPLAY_VERIFIED"],
            "actual_v1_provenance_classes": ["A_SOURCE_EXPLICIT", "B_FORMALLY_DERIVABLE"],
            "serialization": "canonical JSON",
            "history_window": HISTORY_WINDOW,
            "not_hml_v2": True,
        },
    }


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def render_reports(
    failure_rows: list[dict[str, Any]], state_summary: dict[str, Any], alias_cases: list[dict[str, Any]],
    screen: dict[str, Any], manifest: dict[str, Any], probe: dict[str, Any], source_counts: dict[str, Any],
) -> None:
    groups = collections.Counter(row["disagreement_category"] for row in failure_rows)
    primary = collections.Counter(row["primary_error_category"] for row in failure_rows if row["primary_error_category"] != "NONE")
    neutral_changed = sum(row["prediction_changed_previous_to_common"]["neutral"] for row in failure_rows)
    hml_changed = sum(row["prediction_changed_previous_to_common"]["hml"] for row in failure_rows)
    both_wrong = [row for row in failure_rows if row["disagreement_category"] == "BOTH_WRONG"]
    representative = {}
    for category in primary:
        representative[category] = [row["record_id"] for row in failure_rows if row["primary_error_category"] == category][:8]
    depth_categories: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for row in failure_rows:
        if row["primary_error_category"] != "NONE":
            depth = row["proof_depth"]
            bucket = "1" if depth == 1 else "2-5" if depth <= 5 else "6-10" if depth <= 10 else "11-20" if depth <= 20 else "21+"
            depth_categories[bucket][row["primary_error_category"]] += 1

    lessons = f"""# Current experiment lessons

## Immutable evidence

- Unequal-envelope experiment: HML 85.75%, Neutral 50.20%, delta +35.55pp.
- Frozen common-envelope experiment (`{PROTOCOL_COMMIT}` protocol; `{RESULT_COMMIT}` result data): HML 85.33%, Neutral 88.10%, delta -2.77pp, clustered 95% CI [-3.72, -1.81]pp.
- Verdict: `COMMON_ENVELOPE_EFFECT_FAILED`; seed 2 remains stopped.
- The old 3,000-row FINAL is relabelled only conceptually as `DISCOVERY_DEV`; historical files are unchanged.

## What the pair of experiments establishes

The 37.90pp Neutral recovery under a common envelope, versus a 0.42pp HML decline, identifies interface accessibility as the source of the earlier headline gap. Existing HML serialization does not beat canonical Neutral JSON. The new program therefore tests retained reasoning information and semantic organization, not syntax.

Across the same rows, {neutral_changed:,} Neutral predictions and {hml_changed:,} HML predictions changed from the unequal to the common envelope. The common-envelope partition is: BOTH_CORRECT {groups['BOTH_CORRECT']:,}, NEUTRAL_ONLY {groups['NEUTRAL_ONLY']:,}, HML_ONLY {groups['HML_ONLY']:,}, BOTH_WRONG {groups['BOTH_WRONG']:,}.

## Scientific boundary

This evidence is specific to Qwen3-8B BF16, the frozen 10K LoRA recipe, six-way one-step next-action selection, and the old HML50K FINAL parents. It does not establish universal JSON superiority, current-state sufficiency, or multi-step theorem-solving value. No old result was rewritten and no new model training occurred in this discovery stage.
"""
    (OUT / "CURRENT_EXPERIMENT_LESSONS.md").write_text(lessons, encoding="utf-8")

    atlas_lines = [
        "# Reasoning failure atlas", "", "## Population", "",
        f"All 3,000 old-FINAL rows are retained as discovery data. Counts: BOTH_CORRECT {groups['BOTH_CORRECT']:,}; NEUTRAL_ONLY {groups['NEUTRAL_ONLY']:,}; HML_ONLY {groups['HML_ONLY']:,}; BOTH_WRONG {groups['BOTH_WRONG']:,}.", "",
        "The primary category is a deterministic evidence tag, not a claim that the model's hidden causal mechanism was observed. Candidate alternatives are `PLAUSIBLE_UNEXECUTED`; consequently `ACTION_APPLICABILITY` means within-family discrimination pressure, not verified invalidity of the rejected candidates.", "", "## Evidence-backed primary categories", "",
        "| category | rows | representative record IDs |", "|---|---:|---|",
    ]
    for category, count in primary.most_common():
        atlas_lines.append(f"| {category} | {count:,} | {', '.join(representative[category])} |")
    atlas_lines += ["", "## Primary-category counts by proof depth", "", "| depth | " + " | ".join(primary) + " |", "|---|" + "---:|" * len(primary)]
    for depth in ("1", "2-5", "6-10", "11-20", "21+"):
        atlas_lines.append("| " + depth + " | " + " | ".join(str(depth_categories[depth][category]) for category in primary) + " |")
    atlas_lines += [
        "", "## Objective feature coverage", "",
        f"- BOTH_WRONG rows mined first: {len(both_wrong):,}.",
        f"- Rows with source-explicit multiple goals: {sum(r['multiple_goals'] for r in failure_rows):,}.",
        f"- Rows whose recorded tactic names a local declaration: {sum(r['gold_references_local_hypothesis'] for r in failure_rows):,}.",
        f"- Rows with source-explicit `case` identity: {sum(r['case_marker_present'] for r in failure_rows):,}.",
        f"- Rows with actual failed/invalid actions in passive history: 0.",
        "", "Each machine row also records depth, parent, hypotheses, goal form, candidate/tactic families, trajectory position, recent actions and deltas, repeated actions, prompt lengths, lexical baseline, complexity, old/common predictions, hashes, taxonomy evidence and provenance limits.",
        "", "## Unavailable categories", "",
        "`SEARCH_LOOP` and failed-route memory cannot be diagnosed from these successful traces. `SCOPE_CONFUSION`, strategy state, and lemma/invariant roles are not assigned without stronger observable evidence. Such rows remain `UNKNOWN` or receive only a coarser source-supported tag.",
    ]
    (OUT / "REASONING_FAILURE_ATLAS.md").write_text("\n".join(atlas_lines) + "\n", encoding="utf-8")

    state_report = f"""# State sufficiency report

## Method

The audit used {state_summary['source_rows_used']:,} transitions from {state_summary['source_parents_used']:,} Lean theorem parents after excluding both sealed fresh holdouts. No `FRESH_FINAL_A/B` row entered discovery statistics. Deterministic signatures were computed from the exact current state and from an identifier/number-normalized structural state. The target is the recorded next tactic family; this is an observational sufficiency diagnostic, not a uniqueness claim about valid Lean actions.

## Aliasing

- Exact current-state hashes: {state_summary['exact_state_signatures']:,}; ambiguous exact clusters: {state_summary['exact_state_alias_clusters_with_multiple_recorded_action_families']:,}, covering {state_summary['exact_state_rows_in_ambiguous_clusters']:,} rows.
- Structural current-state signatures: {state_summary['structural_state_signatures']:,}; ambiguous clusters: {state_summary['structural_alias_clusters_with_multiple_recorded_action_families']:,}, covering {state_summary['structural_rows_in_ambiguous_clusters']:,} rows.
- H(next tactic family | structural current state): {state_summary['conditional_entropy_action_family_given_structural_state_bits']:.4f} bits.
- H(next tactic family | structural state, last {HISTORY_WINDOW} successful tactic families): {state_summary['conditional_entropy_action_family_given_structural_state_and_recent_action_families_bits']:.4f} bits.
- Observed reduction: {state_summary['recent_history_entropy_reduction_bits']:.4f} bits.

## Interpretation

{state_summary['interpretation'].capitalize()}. This supports testing bounded successful history, but it does not prove that identical Lean states require a unique action or that history is causally necessary: formal proofs permit multiple valid tactics and the corpus contains one successful trace per example. The 200 highest-evidence deterministic clusters are saved separately with hashes, action-family distributions and representative IDs; no holdout examples are included.

## Candidate missing variables

Recent successful actions and their state deltas reduce recorded-action ambiguity beyond the tested structural signature and are available online before the next action. Explicit goal queues, local declaration dependencies and case identity are already present or derivable from the current Lean state; they test semantic accessibility/organization rather than missing raw information. Failed-route memory, branch parent/coverage, goal genealogy and strategy/lemma roles are absent from passive source and are not admitted.
"""
    (OUT / "STATE_SUFFICIENCY_REPORT.md").write_text(state_report, encoding="utf-8")

    requirements = f"""# Semantic requirements audit

## Admission rule

A field is admitted only when it is prevalent enough to matter, addresses observed failure or ambiguity, is available strictly before the next action, avoids gold/future data, is computable online, and has a precise update rule. Headline data permits provenance A/B/C only; V1 uses A and B.

| module | source status | online | provenance | decision |
|---|---|---:|---|---|
| Goal structure | Lean pretty state exposes ordered open goals, active first goal, hypotheses and targets; no goal genealogy | yes | A/B | {screen['modules']['GOALS']['decision']} |
| Local dependencies | declaration-name references in later local types and targets are deterministic | yes | B | {screen['modules']['DEPENDENCIES']['decision']} |
| Branch/scope | `case` identity is explicit; branch parent, coverage and general nested scope are absent | yes, limited | A | {screen['modules']['BRANCH_SCOPE']['decision']} |
| Successful history | prior exact states/actions and derived deltas exist in complete trace prefixes | yes | A/B | {screen['modules']['HISTORY']['decision']} |
| Distinct obligations | not distinct from ordinary Lean goals | no supported object | — | DROP_V1 |
| Search memory | no failed attempts in passive successful traces | no | — | DROP_V1 |
| Lemma/invariant/strategy role | would require interpretation not formal evidence | not certified | D only | DROP_V1 |

## Leakage firewall

The extractor accepts only `(current_raw_state, prior_events)`. It does not accept the current tactic, state-after, proof length, future steps, candidate ordering or gold label. `trajectory_position.steps_completed` is the prefix length, not total proof length. The history window is {HISTORY_WINDOW}; RAW_HISTORY must contain exactly the same bounded pre-action events used by SEMANTIC_STATE.

## Acquisition decision

No Erdős/research-proof acquisition is justified before the formal test. The local source supports a narrow V1 test of successful-history compression plus organization of goals, dependencies and explicit case identity. Genuine discovery traces would be required for rejected conjectures, failed routes, invariant discovery, strategy shifts, uncertainty and branch coverage.
"""
    (OUT / "SEMANTIC_REQUIREMENTS_AUDIT.md").write_text(requirements, encoding="utf-8")

    screen_lines = [
        "# Semantic module screen", "", "Discovery-only screening predicts the next recorded tactic family, not the six-way confirmatory label. It is a cheap attribution proxy and cannot support a headline claim.", "",
        f"BASE lexical probe: {pct(probe['BASE_LEXICAL']['accuracy'])}. FULL semantics: {pct(probe['FULL_SEMANTICS']['accuracy'])} ({probe['FULL_SEMANTICS']['delta_vs_base_pp']:+.2f}pp).", "",
        "| module | prevalence | approx tokens | tagged error rows | MI bits | probe delta | decision |", "|---|---:|---:|---:|---:|---:|---|",
    ]
    for name, result in screen["modules"].items():
        if "prevalence" not in result:
            continue
        screen_lines.append(
            f"| {name} | {pct(result['prevalence'])} | {result['mean_approx_token_cost']:.1f} | {result['evidence_tagged_error_rows']:,} | {result['coarse_plug_in_mutual_information_with_tactic_family_bits']:.4f} | {result['cheap_probe_delta_vs_base_pp']:+.2f}pp | {result['decision']} |"
        )
    screen_lines += [
        "", "## Keep/drop boundary", "",
        f"Admitted: {', '.join(screen['admitted_modules']) or 'none'}. Obligations, verified search memory and lemma/invariant roles are dropped because the source cannot support them. No 2K/5K model screen or new training was run.",
        "", "The final data renderer remains decomposable into GOALS, DEPENDENCIES, BRANCH_SCOPE and HISTORY so `FULL minus module` ablations remain possible without changing the ontology.",
    ]
    (OUT / "SEMANTIC_MODULE_SCREEN.md").write_text("\n".join(screen_lines) + "\n", encoding="utf-8")

    semantics = f"""# Reasoning state semantics V1

V1 is a representation-neutral, canonical-JSON state. It is not HML-V2. Its history horizon is the last {HISTORY_WINDOW} successful pre-action transitions.

## Fields

| field | type | meaning and update | provenance | online availability | discovery frequency | expected failure class |
|---|---|---|---|---|---:|---|
| `active_goal` | object/null | First source-ordered open goal; recompute from current Lean state. Includes target, coarse target shape, hypothesis count and content hash. | A/B | current state | {pct(screen['modules']['GOALS']['prevalence'])} | GOAL_SELECTION |
| `open_goals` | array | Source order of all open goals with case label, shape, hypothesis count and hash; replace on each state. No parent/child claim. | A/B | current state | {pct(screen['modules']['GOALS']['prevalence'])} | GOAL_SELECTION |
| `local_dependencies` | edge array | A declaration points to a later declaration or `@goal` when its exact local name occurs in the dependent type/target; recompute. This is lexical-formal reference, not theorem dependency. | B | current state | {pct(screen['modules']['DEPENDENCIES']['prevalence'])} non-empty | PREMISE_DEPENDENCY |
| `active_scope` | object | The active goal's explicit Lean `case` label, if present. No inferred branch parent, membership or coverage. | A | current state | {pct(screen['modules']['BRANCH_SCOPE']['prevalence'])} explicit | BRANCH_STATE/SCOPE_CONFUSION |
| `trajectory_position` | object | Count of successful prior events. Never includes total proof length. | A/B | prefix | {pct(screen['modules']['HISTORY']['prevalence'])} non-zero | TRAJECTORY_MEMORY |
| `recent_actions` | array | Tactic-family heads of the last {HISTORY_WINDOW} successful actions, oldest to newest; append after verified/recorded success and truncate left. | A/B | prefix | {pct(screen['modules']['HISTORY']['prevalence'])} non-empty | TRAJECTORY_MEMORY/STRATEGY_STATE |
| `recent_deltas` | array | Deterministic goal/target/local-declaration changes for the same events; append and truncate with actions. | B | prefix | {pct(screen['modules']['HISTORY']['prevalence'])} non-empty | TRAJECTORY_MEMORY |
| `progress_summary` | object | Open-goal count, net recent goal delta and immediate repeated-family flag, recomputed from current state/history. | B | current+prefix | 100.00% | TRAJECTORY_MEMORY/STRATEGY_STATE |

## Three-arm information contract

- BASE_STATE: canonical JSON containing the exact current mathematical state only.
- RAW_HISTORY: BASE_STATE plus a neutral chronological array of the exact last {HISTORY_WINDOW} pre-action `(state_before, action, state_after)` events.
- SEMANTIC_STATE: BASE_STATE plus exactly the admitted V1 fields derived from that same current state/history.

Instructions, candidates, labels, model, recipe and envelope must otherwise be byte-identical. The semantic renderer must support module removal without recomputation. FINAL_A remains locked until this schema/extractor commit is recorded; FINAL_B remains locked for one evidence-cited V2 revision only.

## Explicit non-semantics

V1 does not represent failed routes, candidate validity, obligations distinct from goals, goal genealogy, branch coverage, theorem-premise use by the next action, inferred strategy, invariant/lemma role, proof length or future success. These omissions are deliberate evidence boundaries.
"""
    (OUT / "REASONING_STATE_SEMANTICS_V1.md").write_text(semantics, encoding="utf-8")

    lessons_hashes = {
        "source_inventory": source_counts,
        "holdout_integrity": manifest["integrity"],
        "failure_rows": len(failure_rows),
        "fresh_holdout_rows_used_in_discovery": 0,
    }
    write_json(OUT / "discovery_summary.json", lessons_hashes)


def validate_extractor(selected: dict[str, dict[str, Any]], source_rows: dict[str, dict[str, Any]], histories: dict[str, list[dict[str, str]]], admitted: list[str]) -> dict[str, Any]:
    module_fields = {
        "GOALS": ["active_goal", "open_goals"], "DEPENDENCIES": ["local_dependencies"],
        "BRANCH_SCOPE": ["active_scope"],
        "HISTORY": ["trajectory_position", "recent_actions", "recent_deltas", "progress_summary"],
    }
    expected = {"schema_version"} | {field for module in admitted for field in module_fields[module]}
    deterministic = True
    failures = []
    checked = 0
    for example, corpus in selected.items():
        if corpus["split"] not in {"dev", "final"} or example not in source_rows:
            continue
        source = source_rows[example]
        raw = source["lean"]["raw_state_before"]
        history = histories.get(example, [])
        first = extract_reasoning_state(raw, history)
        second = extract_reasoning_state(raw, history)
        projected = {key: value for key, value in first.items() if key in expected}
        if canonical(first) != canonical(second):
            deterministic = False
            failures.append(f"{example}: nondeterministic")
        if not expected <= set(projected):
            failures.append(f"{example}: missing fields")
        if len(first["recent_actions"]) > HISTORY_WINDOW or len(first["recent_deltas"]) > HISTORY_WINDOW:
            failures.append(f"{example}: history overflow")
        checked += 1
    return {
        "result": "PASS" if deterministic and not failures else "FAIL",
        "rows_checked": checked,
        "deterministic": deterministic,
        "history_window": HISTORY_WINDOW,
        "gold_or_future_arguments_in_api": False,
        "provenance_classes": ["A_SOURCE_EXPLICIT", "B_FORMALLY_DERIVABLE"],
        "failures": failures[:100],
    }


def write_stage_manifest() -> None:
    files = {}
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "DISCOVERY_STAGE_MANIFEST.json":
            files[str(path.relative_to(OUT))] = {"bytes": path.stat().st_size, "sha256": file_sha(path)}
    for path in (
        HERE / "semantic_extractor.py",
        HERE / "build_discovery_stage.py",
        REPO / "tests/test_reasoning_layer_discovery.py",
    ):
        files[str(path.relative_to(REPO))] = {"bytes": path.stat().st_size, "sha256": file_sha(path)}
    write_json(OUT / "DISCOVERY_STAGE_MANIFEST.json", {
        "artifact": "REASONING_LAYER_DISCOVERY_STAGE_V1",
        "result": "PASS",
        "authorities": {
            "corpus_commit": CORPUS_COMMIT,
            "common_envelope_protocol_commit": PROTOCOL_COMMIT,
            "common_envelope_result_data_commit": RESULT_COMMIT,
            "common_envelope_frozen_tag": "common-envelope-10k-final-20260824",
        },
        "manifest_self_hash": "excluded_by_design; freeze with the git commit/tree",
        "files": files,
    })


def main() -> None:
    started = time.time()
    for path in (SOURCE, HML50K / "canonical/records.jsonl.gz", VNEXT, COMMON, PREVIOUS):
        if not path.exists():
            raise FileNotFoundError(path)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    selected, hml_parents, previous_states, final_examples = load_hml_records()
    vnext_parents = load_vnext_parents()
    previous_parents = hml_parents | vnext_parents
    selected_ids = set(selected)

    source_rows: dict[str, dict[str, Any]] = {}
    parent_full_rows: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    compact_by_parent: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    holdout_candidates: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    source_split_counts: collections.Counter[str] = collections.Counter()
    source_row_count = 0
    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            source_row_count += 1
            source_split_counts[row["lean_official_split"]] += 1
            parent = parent_id(row)
            compact = compact_source_row(row)
            compact_by_parent[parent].append(compact)
            if row["example_id"] in selected_ids or parent in hml_parents:
                parent_full_rows[parent].append(row)
            if row["example_id"] in selected_ids:
                source_rows[row["example_id"]] = row
            # LeanDojo's unused official-test remainder is too small for two new
            # 3K parent-disjoint sets.  Freshness is enforced against every prior
            # parent/state, so all official splits are eligible and recorded.
            if parent not in previous_parents:
                holdout_candidates[parent].append({
                    "example_id": row["example_id"], "parent_id": parent,
                    "step_index": row["transition_index"], "official_split": row["lean_official_split"],
                    "state_hash": digest_text(row["lean"]["raw_state_before"]),
                    "transition_hash": transition_hash(row),
                    "action_hash": digest_text(row["lean"]["raw_tactic"]),
                })
    if set(source_rows) != selected_ids:
        missing = sorted(selected_ids - set(source_rows))[:10]
        raise AssertionError(f"selected source rows missing: {missing}")

    manifest, sealed_parents = seal_holdouts(holdout_candidates, hml_parents, vnext_parents, previous_states)
    histories = build_histories(parent_full_rows, selected_ids)
    common_rows, old_hml, old_neutral = load_prediction_maps()
    failure_rows = build_failure_rows(selected, source_rows, histories, common_rows, old_hml, old_neutral)
    write_jsonl(OUT / "reasoning_failure_rows.jsonl", failure_rows)

    state_summary, alias_cases = state_sufficiency_analysis(compact_by_parent, sealed_parents)
    write_json(OUT / "state_sufficiency_metrics.json", state_summary)
    write_jsonl(OUT / "state_aliasing_candidates.jsonl", alias_cases)

    probe = run_probe(selected, source_rows, histories)
    write_json(OUT / "semantic_probe_results.json", probe)
    screen = module_screen(failure_rows, probe, state_summary, selected, source_rows, histories)
    write_json(OUT / "semantic_module_screen.json", screen)
    admitted = screen["admitted_modules"]
    schema = make_schema(admitted)
    write_json(OUT / "REASONING_STATE_SCHEMA_V1.json", schema)

    validation = validate_extractor(selected, source_rows, histories, admitted)
    write_json(OUT / "extractor_validation.json", validation)
    source_counts = {
        "canonical_source_rows": source_row_count,
        "canonical_source_parents": len(compact_by_parent),
        "canonical_official_splits": dict(sorted(source_split_counts.items())),
        "hml50k_records": len(selected),
        "hml50k_parents": len(hml_parents),
        "vnext_previous_parents": len(vnext_parents),
    }
    render_reports(failure_rows, state_summary, alias_cases, screen, manifest, probe, source_counts)

    integrity = {
        "result": "PASS" if validation["result"] == "PASS" and manifest["integrity"] == "PASS" and len(failure_rows) == 3000 else "FAIL",
        "historical_files_modified": False,
        "hml_core_modified": False,
        "new_model_training_or_scoring_run": False,
        "fresh_holdout_rows_in_discovery_statistics": 0,
        "fresh_holdouts": manifest["exclusions"],
        "extractor": validation,
        "admitted_modules": admitted,
        "schema_fields": schema["required"],
        "wall_seconds": round(time.time() - started, 3),
    }
    write_json(OUT / "DISCOVERY_STAGE_INTEGRITY.json", integrity)
    status = "SEMANTIC_TEST_READY" if integrity["result"] == "PASS" and "HISTORY" in admitted else "INSUFFICIENT_EVIDENCE_FOR_SEMANTIC_SCHEMA"
    write_json(OUT / "STAGE_STATUS.json", {"status": status, "integrity": integrity["result"], "training_authorized_in_this_stage": False})
    write_stage_manifest()
    print(canonical({
        "status": status, "output": str(OUT), "failure_rows": len(failure_rows),
        "admitted_modules": admitted, "holdout_a": manifest["holdouts"]["FRESH_FINAL_A"],
        "holdout_b": manifest["holdouts"]["FRESH_FINAL_B"], "wall_seconds": round(time.time() - started, 3),
    }))


if __name__ == "__main__":
    main()
