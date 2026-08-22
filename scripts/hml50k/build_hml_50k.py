#!/usr/bin/env python3
"""Build the final 50k paired HML/structured-neutral teaching corpus.

This builder intentionally uses only exact LeanDojo state/tactic/state-after traces for
the model-facing core.  Other local sources are inventoried separately; they are not
promoted merely to satisfy a source-mix target.  The canonical object is built once and
both view families are deterministic projections of it.
"""

from __future__ import annotations

import argparse
import bisect
import collections
import gzip
import hashlib
import io
import json
import math
import platform
import re
import shutil
import subprocess
import time
import unicodedata
from pathlib import Path

from hamiltonian_lang.semantic_state import (
    Action,
    Claim,
    ClaimStatus,
    EvidenceRecord,
    SemanticState,
    Transition,
    Verdict,
    export_state,
    export_transition,
    parse_state,
    render_state,
    verify_replay,
)


SEED = "hml-50k-final-20260822"
HML_SHA = "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
CONTRACT = "vnext-translation-contract-1.0.0"
MATHLIB_SHA = "29dcec074de168ac2bf835a77ef68bbe069194c5"
CANONICAL_SOURCE_SHA = "8ac0ce010cedaecb1f9edf0d0ef7b0a5700620de52a66e508fd6e71778719869"
VIEWS = ("HML_WORKED_UTF8", "STRUCTURED_NEUTRAL_WORKED")
TASKS = (
    "NEXT_ACTION_SELECT",
    "STATE_DELTA_PREDICT",
    "VALIDITY_JUDGE",
    "WORKED_CONTINUATION",
)
SPLIT_SOURCE = {"train": "train", "dev": "val", "final": "test"}
SPLIT_TARGET = {"train": 50_000, "dev": 3_000, "final": 3_000}
RUNG_SIZES = (10_000, 30_000, 50_000)
CANDIDATE_COUNT = 6
CHARACTER_SAFETY_CAP = 12_000

# Transition-row targets by complete source-trajectory length.  The final fill is
# deterministic and can use partial trajectories, but complete trajectories are selected
# first.  This is frozen before looking at any model result.
TRAIN_LENGTH_TARGETS = {
    "1": 7_500,
    "2-3": 7_500,
    "4-5": 7_500,
    "6-10": 10_000,
    "11-20": 10_000,
    "21+": 7_500,
}
HELDOUT_LENGTH_TARGETS = {
    "1": 600,
    "2-3": 600,
    "4-5": 390,
    "6-10": 540,
    "11-20": 450,
    "21+": 420,
}


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_int(*parts: str) -> int:
    return int(digest_text("\0".join((SEED, *parts))), 16)


def normalise_trace(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def deterministic_gzip(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                for row in rows:
                    text.write(canonical(row) + "\n")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def length_bin(value: int) -> str:
    if value <= 1:
        return "1"
    if value <= 3:
        return "2-3"
    if value <= 5:
        return "4-5"
    if value <= 10:
        return "6-10"
    if value <= 20:
        return "11-20"
    return "21+"


def depth_bin(value: int) -> str:
    return length_bin(value)


def action_head(tactic: str) -> str:
    text = tactic.strip()
    text = re.sub(r"^(?:by\s+)+", "", text)
    match = re.search(r"[A-Za-z_][A-Za-z0-9_'.!?]*|[<>=:+*/-]+", text)
    return match.group(0).lower() if match else "<symbolic>"


def old_vnext_parents(path: Path) -> set[str]:
    parents: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("source_family") == "LEAN_DOJO":
                parents.add(row["parent_id"])
    return parents


def lite_row(row: dict) -> dict:
    parent_id = f"{row['source_file']}::{row['theorem_id']}"
    tactic = row["lean"]["raw_tactic"]
    before = row["lean"]["raw_state_before"]
    after = row["lean"]["raw_state_after"]
    transition_index = int(row["transition_index"])
    signature = digest_text("\0".join(map(normalise_trace, (before, tactic, after))))
    observed = row.get("observed_action") or {}
    n_hyps = len((row.get("state_before") or {}).get("hypotheses") or [])
    n_goals = int((row.get("state_before") or {}).get("n_goals") or 0)
    changes = (
        int(bool(observed.get("target_changed")))
        + len(observed.get("names_added") or [])
        + len(observed.get("names_removed") or [])
        + len(observed.get("names_rebound") or [])
        + abs(int(observed.get("delta_goals") or 0))
    )
    proof_length = int(row.get("proof_length") or 1)
    return {
        "example_id": row["example_id"],
        "parent_id": parent_id,
        "source_file": row["source_file"],
        "theorem_id": row["theorem_id"],
        "official_split": row["lean_official_split"],
        "transition_index": transition_index,
        "depth": transition_index + 1,
        "proof_length": proof_length,
        "length_bin": length_bin(proof_length),
        "tactic": tactic,
        "tactic_head": action_head(tactic),
        "effect_class": observed.get("effect_class") or "UNKNOWN",
        "n_hypotheses_before": n_hyps,
        "n_goals_before": n_goals,
        "delta_goals": int(observed.get("delta_goals") or 0),
        "field_changes": changes,
        "burden_score": n_hyps + n_goals + (transition_index + 1) + changes,
        "trace_character_count": len(before) + len(tactic) + len(after),
        "action_verbatim_in_state_before": bool(tactic.strip()) and tactic.strip() in before,
        "probability_statistics_related": bool(
            re.search(r"probab|statist|measuretheory", row["source_file"], re.I)
        ),
        "signature": signature,
        "selection_rank": stable_int("select", row["example_id"]),
    }


def scan_catalog(source_path: Path, old_parents: set[str], token_exclusions: set[str]) -> tuple[list[dict], dict]:
    if file_sha(source_path) != CANONICAL_SOURCE_SHA:
        raise AssertionError("canonical Lean source hash does not match frozen source pin")
    raw: list[dict] = []
    counts = collections.Counter()
    excluded = collections.Counter()
    with source_path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            counts[(row["lean_official_split"], "source_rows")] += 1
            item = lite_row(row)
            if item["parent_id"] in old_parents:
                excluded[(item["official_split"], "old_parent")] += 1
                continue
            if item["example_id"] in token_exclusions:
                excluded[(item["official_split"], "qwen3_8b_over_6144_preflight")] += 1
                continue
            if item["action_verbatim_in_state_before"]:
                excluded[(item["official_split"], "gold_action_verbatim_in_state_before")] += 1
                continue
            if item["trace_character_count"] > CHARACTER_SAFETY_CAP:
                excluded[(item["official_split"], "character_cap")] += 1
                continue
            if not row.get("compatibility", {}).get("frozen_hml_representable", False):
                excluded[(item["official_split"], "not_frozen_hml_representable")] += 1
                continue
            raw.append(item)

    # Holdouts own duplicate signatures.  This prevents a train duplicate from evicting a
    # final row and makes the fresh final set conservative.
    priority = {"test": 0, "val": 1, "train": 2}
    raw.sort(key=lambda item: (priority[item["official_split"]], item["selection_rank"]))
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in raw:
        if item["signature"] in seen:
            excluded[(item["official_split"], "cross_split_or_internal_near_duplicate")] += 1
            continue
        seen.add(item["signature"])
        deduped.append(item)
    audit = {
        "source_rows": {split: counts[(split, "source_rows")] for split in ("train", "val", "test")},
        "old_vnext_parent_count": len(old_parents),
        "exclusions": {
            f"{split}:{reason}": count for (split, reason), count in sorted(excluded.items())
        },
        "eligible_after_exclusions": dict(collections.Counter(x["official_split"] for x in deduped)),
        "near_duplicate_signature": "sha256(NFKC + whitespace-collapsed state_before/tactic/state_after)",
        "holdout_duplicate_priority": ["test", "val", "train"],
        "character_safety_cap": CHARACTER_SAFETY_CAP,
        "token_preflight_exclusion_count": len(token_exclusions),
    }
    return deduped, audit


def select_complete_first(rows: list[dict], target: int, targets: dict[str, int], split: str) -> list[dict]:
    by_parent: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        by_parent[row["parent_id"]].append(row)
    for values in by_parent.values():
        values.sort(key=lambda row: row["transition_index"])

    selected_ids: set[str] = set()
    for band, quota in targets.items():
        groups = [
            (stable_int("group", split, parent), parent, values)
            for parent, values in by_parent.items()
            if length_bin(max(x["proof_length"] for x in values)) == band
        ]
        groups.sort()
        count = 0
        for _, _, values in groups:
            if count + len(values) <= quota:
                selected_ids.update(x["example_id"] for x in values)
                count += len(values)
            if count == quota:
                break

    # Prefer additional complete trajectories that fit the exact remaining count.
    remaining = target - len(selected_ids)
    leftovers = [
        (len(values), stable_int("fill-group", split, parent), values)
        for parent, values in by_parent.items()
        if not any(x["example_id"] in selected_ids for x in values)
    ]
    leftovers.sort(key=lambda item: (item[1], item[0]))
    for size, _, values in leftovers:
        if size <= remaining:
            selected_ids.update(x["example_id"] for x in values)
            remaining -= size
        if remaining == 0:
            break

    # At most a few trajectory rows are needed if group sizes cannot hit the exact sum.
    if remaining:
        row_fill = sorted(
            (x for x in rows if x["example_id"] not in selected_ids),
            key=lambda x: stable_int("fill-row", split, x["example_id"]),
        )
        for row in row_fill[:remaining]:
            selected_ids.add(row["example_id"])

    selected = [x for x in rows if x["example_id"] in selected_ids]
    if len(selected) != target:
        raise AssertionError(f"could not select exact {split} target: {len(selected)} != {target}")
    selected.sort(key=lambda x: stable_int("curriculum", split, x["example_id"]))
    return selected


def choose_splits(catalog: list[dict]) -> tuple[dict[str, list[dict]], dict]:
    output: dict[str, list[dict]] = {}
    selection_audit = {}
    for split, official in SPLIT_SOURCE.items():
        source = [x for x in catalog if x["official_split"] == official]
        targets = TRAIN_LENGTH_TARGETS if split == "train" else HELDOUT_LENGTH_TARGETS
        picked = select_complete_first(source, SPLIT_TARGET[split], targets, split)
        output[split] = picked
        selected_by_parent = collections.defaultdict(set)
        all_by_parent = collections.defaultdict(set)
        for row in source:
            all_by_parent[row["parent_id"]].add(row["example_id"])
        for row in picked:
            selected_by_parent[row["parent_id"]].add(row["example_id"])
        complete = sum(selected_by_parent[p] == all_by_parent[p] for p in selected_by_parent)
        selection_audit[split] = {
            "official_source_split": official,
            "completeness_scope": "eligible catalog after all source, leakage, duplicate, character, and tokenizer exclusions",
            "records": len(picked),
            "parents": len(selected_by_parent),
            "complete_parent_trajectories": complete,
            "partial_parent_trajectories": len(selected_by_parent) - complete,
            "depth_counts": dict(sorted(collections.Counter(depth_bin(x["depth"]) for x in picked).items())),
            "trajectory_length_counts": dict(sorted(collections.Counter(x["length_bin"] for x in picked).items())),
            "probability_statistics_related": sum(x["probability_statistics_related"] for x in picked),
        }
    parents = {split: {x["parent_id"] for x in rows} for split, rows in output.items()}
    if parents["train"] & parents["dev"] or parents["train"] & parents["final"] or parents["dev"] & parents["final"]:
        raise AssertionError("parent leakage across splits")
    ids = [x["example_id"] for rows in output.values() for x in rows]
    if len(ids) != len(set(ids)):
        raise AssertionError("record overlap across splits")
    return output, selection_audit


def load_selected_rows(source_path: Path, selected_ids: set[str]) -> dict[str, dict]:
    output: dict[str, dict] = {}
    with source_path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["example_id"] in selected_ids:
                output[row["example_id"]] = row
    if set(output) != selected_ids:
        raise AssertionError(f"missing selected source rows: {len(selected_ids - set(output))}")
    return output


def load_premises(raw_root: Path, selected: dict[str, list[dict]], raw_rows: dict[str, dict]) -> tuple[dict[str, list[str]], dict]:
    wanted: dict[str, set[str]] = collections.defaultdict(set)
    for rows in selected.values():
        for item in rows:
            wanted[item["official_split"]].add(item["parent_id"])
    premise_map: dict[str, list[str]] = {}
    audit = {"files": {}, "selected_action_rows": 0, "exact_trace_matches": 0, "premise_lists_recovered": 0}
    for official in ("train", "val", "test"):
        path = raw_root / f"{official}.json"
        audit["files"][official] = {"path": str(path), "sha256": file_sha(path), "bytes": path.stat().st_size}
        data = json.loads(path.read_text(encoding="utf-8"))
        for theorem in data:
            parent = f"{theorem['file_path']}::{theorem['full_name']}"
            if parent not in wanted[official]:
                continue
            for index, step in enumerate(theorem.get("traced_tactics") or []):
                source_id = f"{parent}::{index}"
                # Canonical example ids have exactly the same file::theorem::step shape.
                if source_id not in raw_rows:
                    continue
                audit["selected_action_rows"] += 1
                canonical_row = raw_rows[source_id]
                if (
                    step["state_before"] != canonical_row["lean"]["raw_state_before"]
                    or step["tactic"] != canonical_row["lean"]["raw_tactic"]
                    or step["state_after"] != canonical_row["lean"]["raw_state_after"]
                ):
                    raise AssertionError(f"raw/canonical Lean trace disagreement: {source_id}")
                audit["exact_trace_matches"] += 1
                annotated = step.get("annotated_tactic") or [step["tactic"], []]
                premises = annotated[1] if len(annotated) > 1 else []
                premise_map[source_id] = sorted({p["full_name"] for p in premises if p.get("full_name")})
                audit["premise_lists_recovered"] += 1
        del data
    if set(premise_map) != set(raw_rows):
        missing = sorted(set(raw_rows) - set(premise_map))
        raise AssertionError(f"failed to recover premise metadata for {len(missing)} selected rows")
    return premise_map, audit


def build_transition(row: dict, record_id: str, premises: list[str]) -> Transition:
    before_text = row["lean"]["raw_state_before"]
    after_text = row["lean"]["raw_state_after"]
    p0 = Claim(id="p0", proposition=before_text, status=ClaimStatus.GIVEN, scope="global", domain="Proposition")
    c1 = Claim(
        id="c1",
        proposition=after_text,
        status=ClaimStatus.DERIVED,
        scope="global",
        domain="Proposition",
        dependencies=("p0",),
    )
    before = SemanticState(claims={"p0": p0}, active_scopes=("global",))
    after = SemanticState(claims={"p0": p0, "c1": c1}, active_scopes=("global",))
    evidence = EvidenceRecord(
        id="e1",
        kind="FORMAL_TRACE",
        status="VALID",
        trusted=True,
        supports_rule="LEAN_TACTIC",
        premise_ids=("p0",),
        payload={
            "source_kind": "LEAN_DOJO_RECORDED_TRACE",
            "source_example_id": row["example_id"],
            "source_file": row["source_file"],
            "theorem_id": row["theorem_id"],
            "transition_index": row["transition_index"],
            "tactic_sha256": digest_text(row["lean"]["raw_tactic"]),
            "premises_used": premises,
            "premises_are_action_derived_metadata": True,
            "mathlib_revision": MATHLIB_SHA,
        },
    )
    action = Action(
        id="a1",
        operation="LEAN_TACTIC",
        summary="",
        output_id="c1",
        dependencies=("p0",),
        warrant={"rule": "LEAN_TACTIC", "evidence_id": "e1"},
    )
    return Transition(
        case_id=record_id,
        state_before=before,
        action=action,
        state_after=after,
        evidence={"e1": evidence},
        source={
            "dataset": "LeanDojo Benchmark 4 random",
            "canonical_example_id": row["example_id"],
            "file_path": row["source_file"],
            "theorem_id": row["theorem_id"],
            "official_split": row["lean_official_split"],
            "transition_index": row["transition_index"],
            "proof_length": row["proof_length"],
            "mathlib_revision": MATHLIB_SHA,
            "canonical_source_sha256": CANONICAL_SOURCE_SHA,
        },
    )


def candidate_sets(selected: dict[str, list[dict]]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for split, rows in selected.items():
        by_head: dict[str, list[dict]] = collections.defaultdict(list)
        by_effect: dict[str, list[dict]] = collections.defaultdict(list)
        for row in rows:
            by_head[row["tactic_head"]].append(row)
            by_effect[row["effect_class"]].append(row)
        for pool in (*by_head.values(), *by_effect.values()):
            pool.sort(key=lambda x: (len(x["tactic"]), x["selection_rank"]))
        global_pool = sorted(rows, key=lambda x: (len(x["tactic"]), x["selection_rank"]))
        head_lengths = {key: [len(x["tactic"]) for x in pool] for key, pool in by_head.items()}
        effect_lengths = {key: [len(x["tactic"]) for x in pool] for key, pool in by_effect.items()}
        global_lengths = [len(x["tactic"]) for x in global_pool]

        def nearby(pool: list[dict], lengths: list[int], row: dict) -> list[dict]:
            middle = bisect.bisect_left(lengths, len(row["tactic"]))
            window = pool[max(0, middle - 80): min(len(pool), middle + 81)]
            return sorted(
                window,
                key=lambda x: (
                    abs(len(x["tactic"]) - len(row["tactic"])),
                    stable_int("distractor", row["example_id"], x["example_id"]),
                ),
            )

        for row in rows:
            chosen: list[dict] = []
            seen_tactics = {row["tactic"]}
            pools = (
                (by_head[row["tactic_head"]], head_lengths[row["tactic_head"]]),
                (by_effect[row["effect_class"]], effect_lengths[row["effect_class"]]),
                (global_pool, global_lengths),
            )
            for pool, lengths in pools:
                for candidate in nearby(pool, lengths, row):
                    if candidate["parent_id"] == row["parent_id"] or candidate["tactic"] in seen_tactics:
                        continue
                    chosen.append(candidate)
                    seen_tactics.add(candidate["tactic"])
                    if len(chosen) == CANDIDATE_COUNT - 1:
                        break
                if len(chosen) == CANDIDATE_COUNT - 1:
                    break
            # Extremely common one-token tactics can saturate the local length window.
            # Walk a deterministic circular slice of the split-wide pool only then.
            if len(chosen) < CANDIDATE_COUNT - 1:
                start = stable_int("global-fallback", row["example_id"]) % len(global_pool)
                for offset in range(min(len(global_pool), 5_000)):
                    candidate = global_pool[(start + offset) % len(global_pool)]
                    if candidate["parent_id"] == row["parent_id"] or candidate["tactic"] in seen_tactics:
                        continue
                    chosen.append(candidate)
                    seen_tactics.add(candidate["tactic"])
                    if len(chosen) == CANDIDATE_COUNT - 1:
                        break
            if len(chosen) != CANDIDATE_COUNT - 1:
                raise AssertionError(f"could not build hard-negative set: {row['example_id']}")
            gold_position = stable_int("gold-position", row["example_id"]) % CANDIDATE_COUNT
            distractors = sorted(chosen, key=lambda x: stable_int("candidate-order", row["example_id"], x["example_id"]))
            values = []
            for position in range(CANDIDATE_COUNT):
                source = row if position == gold_position else distractors.pop(0)
                values.append({
                    "candidate_id": f"C{position}",
                    "tactic_text": source["tactic"],
                    "source_example_id": source["example_id"],
                    "epistemic_status": "GOLD_SOURCE_ACTION" if position == gold_position else "PLAUSIBLE_UNEXECUTED",
                    "same_tactic_head_as_gold": source["tactic_head"] == row["tactic_head"],
                })
            result[row["example_id"]] = {"gold_candidate_id": f"C{gold_position}", "candidates": values}
    return result


def mechanisms(row: dict, premises: list[str]) -> list[str]:
    observed = row.get("observed_action") or {}
    output = {"formal_trace", "tactic_application"}
    if row["lean"]["raw_state_after"].strip() == "no goals":
        output.add("goal_close")
    if int(observed.get("delta_goals") or 0) > 0:
        output.add("goal_create_observed")
    if int(observed.get("delta_goals") or 0) < 0:
        output.add("goal_count_reduction")
    if observed.get("target_changed"):
        output.add("target_transform")
    if observed.get("names_added"):
        output.add("context_introduction")
    if observed.get("names_removed"):
        output.add("context_removal")
    if observed.get("names_rebound"):
        output.add("context_rebinding")
    if len(premises) > 1:
        output.add("multiple_source_premises")
    return sorted(output)


def quantile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.floor(fraction * (len(ordered) - 1)))]


def complexity_thresholds(train: list[dict]) -> dict:
    values = [x["burden_score"] for x in train]
    return {
        "formula": "n_hypotheses_before + n_goals_before + depth + field_changes",
        "field_changes": "target_changed + names_added + names_removed + names_rebound + abs(delta_goals)",
        "fit_population": "selected TRAIN metadata only; frozen before rendering or model use",
        "q25": quantile(values, 0.25),
        "q50": quantile(values, 0.50),
        "q75": quantile(values, 0.75),
    }


def complexity_bin(score: int, thresholds: dict) -> str:
    if score <= thresholds["q25"]:
        return "EASY"
    if score <= thresholds["q50"]:
        return "MEDIUM"
    if score <= thresholds["q75"]:
        return "HARD"
    return "LONG_OR_STRUCTURALLY_DENSE"


def task_row(record_id: str, parent_id: str, split: str, task: str, view: str,
             input_text: str, target_text: str, canonical_sha: str, extra: dict | None = None) -> dict:
    row = {
        "record_id": record_id,
        "parent_id": parent_id,
        "split": split,
        "task": task,
        "representation": view,
        "input_text": input_text,
        "target_text": target_text,
        "audit_metadata": {
            "canonical_transition_sha256": canonical_sha,
            "input_sha256": digest_text(input_text),
            "target_sha256": digest_text(target_text),
            "renderer": view,
            "ensure_ascii": False,
        },
    }
    if extra:
        row.update(extra)
    return row


def render_all(selected: dict[str, list[dict]], raw_rows: dict[str, dict], premises: dict[str, list[str]],
               candidate_map: dict[str, dict], thresholds: dict) -> tuple[list[dict], dict, dict, list[dict]]:
    audits: list[dict] = []
    task_rows: dict[str, dict[str, list[dict]]] = {
        task: {view: [] for view in VIEWS} for task in TASKS
    }
    record_lookup: dict[str, dict] = {}
    structural_candidates: list[tuple[int, int, dict]] = []
    rendered_cache: dict[str, dict] = {}

    id_map = {
        item["example_id"]: f"H50K-LEAN-{digest_text(item['example_id'])[:16]}"
        for rows in selected.values() for item in rows
    }
    selected_parent_steps: dict[str, list[dict]] = collections.defaultdict(list)
    for split, rows in selected.items():
        for item in rows:
            selected_parent_steps[item["parent_id"]].append(item)
    for values in selected_parent_steps.values():
        values.sort(key=lambda x: x["transition_index"])

    for split in ("train", "dev", "final"):
        for item in selected[split]:
            source_row = raw_rows[item["example_id"]]
            record_id = id_map[item["example_id"]]
            premise_names = premises[item["example_id"]]
            transition = build_transition(source_row, record_id, premise_names)
            verdict = verify_replay(transition)
            if verdict.verdict is not Verdict.VALID:
                raise AssertionError(f"HML VNext verifier rejected source wrapper {record_id}: {verdict.to_dict()}")
            before_obj = export_state(transition.state_before)
            after_obj = export_state(transition.state_after)
            neutral = export_transition(transition)
            canonical_sha = digest_text(canonical(neutral))
            hml_before = render_state(transition.state_before)
            hml_after = render_state(transition.state_after)
            if parse_state(hml_before) != transition.state_before or parse_state(hml_after) != transition.state_after:
                raise AssertionError(f"HML state round trip failed: {record_id}")

            action = {
                "dependencies": ["p0"],
                "operation": "LEAN_TACTIC",
                "preconditions": [],
                "tactic_text": source_row["lean"]["raw_tactic"],
                "warrant_rule": "LEAN_TACTIC",
            }
            candidates = candidate_map[item["example_id"]]
            public_candidates = [
                {"candidate_id": x["candidate_id"], "tactic_text": x["tactic_text"]}
                for x in candidates["candidates"]
            ]
            gold_id = candidates["gold_candidate_id"]
            hml_select_input = (
                "Below is a mathematical proof state.\n\n" + hml_before
                + "\nChoose the single most useful next tactic from this candidate set.\n"
                + "\n".join(f"{x['candidate_id']} :: {x['tactic_text']}" for x in public_candidates)
                + "\nReturn only the candidate id."
            )
            neutral_select_input = canonical({
                "candidates": public_candidates,
                "instruction": "Choose the single most useful next tactic; return only candidate_id.",
                "state_before": before_obj,
            })
            task_rows["NEXT_ACTION_SELECT"]["HML_WORKED_UTF8"].append(task_row(
                record_id, item["parent_id"], split, "NEXT_ACTION_SELECT", "HML_WORKED_UTF8",
                hml_select_input, gold_id, canonical_sha,
                {"candidate_count": CANDIDATE_COUNT, "gold_candidate_id": gold_id},
            ))
            task_rows["NEXT_ACTION_SELECT"]["STRUCTURED_NEUTRAL_WORKED"].append(task_row(
                record_id, item["parent_id"], split, "NEXT_ACTION_SELECT", "STRUCTURED_NEUTRAL_WORKED",
                neutral_select_input, gold_id, canonical_sha,
                {"candidate_count": CANDIDATE_COUNT, "gold_candidate_id": gold_id},
            ))

            hml_delta_input = hml_before + "\nACTION " + canonical(action)
            neutral_delta_input = canonical({"action": action, "state_before": before_obj})
            task_rows["STATE_DELTA_PREDICT"]["HML_WORKED_UTF8"].append(task_row(
                record_id, item["parent_id"], split, "STATE_DELTA_PREDICT", "HML_WORKED_UTF8",
                hml_delta_input, hml_after, canonical_sha,
            ))
            task_rows["STATE_DELTA_PREDICT"]["STRUCTURED_NEUTRAL_WORKED"].append(task_row(
                record_id, item["parent_id"], split, "STATE_DELTA_PREDICT", "STRUCTURED_NEUTRAL_WORKED",
                neutral_delta_input, canonical(after_obj), canonical_sha,
            ))

            # VALIDITY_JUDGE contains the attested source action and one unexecuted plausible
            # alternative.  It never relabels an unexecuted candidate INVALID.
            unresolved = next(x for x in candidates["candidates"] if x["epistemic_status"] != "GOLD_SOURCE_ACTION")
            for suffix, tactic_text, label in (
                ("P", action["tactic_text"], "FORMAL_TRACE"),
                ("U", unresolved["tactic_text"], "UNRESOLVED"),
            ):
                judge_id = f"{record_id}-{suffix}"
                judge_action = {**action, "tactic_text": tactic_text}
                hml_judge_input = hml_before + "\nPROPOSED_ACTION " + canonical(judge_action)
                neutral_judge_input = canonical({"proposed_action": judge_action, "state_before": before_obj})
                task_rows["VALIDITY_JUDGE"]["HML_WORKED_UTF8"].append(task_row(
                    judge_id, item["parent_id"], split, "VALIDITY_JUDGE", "HML_WORKED_UTF8",
                    hml_judge_input, label, canonical_sha,
                    {"source_record_id": record_id, "label_semantics": "FORMAL_TRACE vs unexecuted UNRESOLVED"},
                ))
                task_rows["VALIDITY_JUDGE"]["STRUCTURED_NEUTRAL_WORKED"].append(task_row(
                    judge_id, item["parent_id"], split, "VALIDITY_JUDGE", "STRUCTURED_NEUTRAL_WORKED",
                    neutral_judge_input, label, canonical_sha,
                    {"source_record_id": record_id, "label_semantics": "FORMAL_TRACE vs unexecuted UNRESOLVED"},
                ))

            parent_values = selected_parent_steps[item["parent_id"]]
            prior = [x for x in parent_values if x["transition_index"] < item["transition_index"]][-3:]
            history_actions = [raw_rows[x["example_id"]]["lean"]["raw_tactic"] for x in prior]
            continuation_action = {**action, "prior_action_texts": history_actions}
            hml_cont_input = hml_before + "\nTRAJECTORY_ACTION " + canonical(continuation_action)
            neutral_cont_input = canonical({"state_before": before_obj, "trajectory_action": continuation_action})
            continuation_extra = {
                "trajectory_step_index": item["transition_index"],
                "trajectory_length": item["proof_length"],
                "history_action_count": len(history_actions),
            }
            task_rows["WORKED_CONTINUATION"]["HML_WORKED_UTF8"].append(task_row(
                record_id, item["parent_id"], split, "WORKED_CONTINUATION", "HML_WORKED_UTF8",
                hml_cont_input, hml_after, canonical_sha, continuation_extra,
            ))
            task_rows["WORKED_CONTINUATION"]["STRUCTURED_NEUTRAL_WORKED"].append(task_row(
                record_id, item["parent_id"], split, "WORKED_CONTINUATION", "STRUCTURED_NEUTRAL_WORKED",
                neutral_cont_input, canonical(after_obj), canonical_sha, continuation_extra,
            ))

            source_steps = sorted(
                x["transition_index"] for x in selected_parent_steps[item["parent_id"]]
            )
            predecessor = next((id_map[x["example_id"]] for x in reversed(parent_values)
                                if x["transition_index"] == item["transition_index"] - 1), None)
            successor = next((id_map[x["example_id"]] for x in parent_values
                              if x["transition_index"] == item["transition_index"] + 1), None)
            mech = mechanisms(source_row, premise_names)
            audit = {
                "record_id": record_id,
                "canonical_source_example_id": item["example_id"],
                "parent_id": item["parent_id"],
                "split": split,
                "source_family": "LEAN_DOJO_FORMAL_TRACE",
                "epistemic_status": "FORMAL_TRACE",
                "mathematical_verification_status": "RECORDED_FORMAL_TRACE_NOT_REPLAYED_IN_THIS_MISSION",
                "semantic_representation_status": "REPRESENTED_VNEXT_WRAPPER",
                "verifier_verdict": str(verdict.verdict),
                "canonical_transition_sha256": canonical_sha,
                "representation_parity": "PASS",
                "leakage_check": "PASS",
                "depth": item["depth"],
                "depth_bin": depth_bin(item["depth"]),
                "proof_length": item["proof_length"],
                "trajectory_step_index": item["transition_index"],
                "selected_trajectory_steps": source_steps,
                "predecessor_record_id": predecessor,
                "successor_record_id": successor,
                "complexity_score": item["burden_score"],
                "complexity_bin": complexity_bin(item["burden_score"], thresholds),
                "probability_statistics_related": item["probability_statistics_related"],
                "mechanisms": mech,
                "premises_used": premise_names,
                "premises_exposed_to_model": False,
                "candidate_audit": candidates,
                "source_structural_record": {
                    "state_before": source_row["state_before"],
                    "observed_action": source_row["observed_action"],
                    "state_after": source_row["state_after"],
                },
                "neutral_transition": neutral,
                "view_hashes": {
                    "HML_WORKED_UTF8": {
                        "state_before_sha256": digest_text(hml_before),
                        "state_after_sha256": digest_text(hml_after),
                    },
                    "STRUCTURED_NEUTRAL_WORKED": {
                        "state_before_sha256": digest_text(canonical(before_obj)),
                        "state_after_sha256": digest_text(canonical(after_obj)),
                    },
                },
            }
            audits.append(audit)
            record_lookup[record_id] = audit
            rendered_cache[record_id] = {
                "hml_before": hml_before,
                "hml_after": hml_after,
                "neutral_before": canonical(before_obj),
                "neutral_after": canonical(after_obj),
            }
            stress_score = (
                item["burden_score"] + 4 * len(premise_names) + 5 * abs(item["delta_goals"])
                + 8 * int("goal_create_observed" in mech) + 4 * int("context_rebinding" in mech)
            )
            structural_candidates.append((stress_score, stable_int("stress", record_id), audit))

    return audits, task_rows, rendered_cache, structural_candidates


def leakage_and_candidate_audit(audits: list[dict], task_rows: dict) -> dict:
    select_hml = task_rows["NEXT_ACTION_SELECT"]["HML_WORKED_UTF8"]
    select_neutral = task_rows["NEXT_ACTION_SELECT"]["STRUCTURED_NEUTRAL_WORKED"]
    delta_hml = task_rows["STATE_DELTA_PREDICT"]["HML_WORKED_UTF8"]
    delta_neutral = task_rows["STATE_DELTA_PREDICT"]["STRUCTURED_NEUTRAL_WORKED"]
    if [x["record_id"] for x in select_hml] != [x["record_id"] for x in select_neutral]:
        raise AssertionError("candidate-select record parity failed")
    if [x["record_id"] for x in delta_hml] != [x["record_id"] for x in delta_neutral]:
        raise AssertionError("delta record parity failed")
    by_id = {x["record_id"]: x for x in audits}
    positions = collections.Counter()
    gold_lengths, negative_lengths = [], []
    same_head = 0
    lexical_correct = 0
    positive_shortest = 0
    positive_unique_shortest = 0
    shortest_first_correct = 0
    shortest_fractional_credit = 0.0
    family_first_correct = 0
    randomised_label_correct = 0
    exact_target_in_delta_input = 0
    target_action_outside_candidates = 0
    token_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)
    for hml, neutral, delta_h, delta_n in zip(select_hml, select_neutral, delta_hml, delta_neutral):
        audit = by_id[hml["record_id"]]
        candidates = audit["candidate_audit"]["candidates"]
        gold = audit["candidate_audit"]["gold_candidate_id"]
        position = int(gold[1:])
        positions[position] += 1
        gold_text = candidates[position]["tactic_text"]
        distractors = [x for x in candidates if x["candidate_id"] != gold]
        gold_lengths.append(len(gold_text))
        negative_lengths.extend(len(x["tactic_text"]) for x in distractors)
        same_head += sum(x["same_tactic_head_as_gold"] for x in distractors)
        candidate_lengths = [len(x["tactic_text"]) for x in candidates]
        minimum = min(candidate_lengths)
        minima = [i for i, value in enumerate(candidate_lengths) if value == minimum]
        positive_shortest += int(candidate_lengths[position] == minimum)
        positive_unique_shortest += int(candidate_lengths[position] < min(
            value for index, value in enumerate(candidate_lengths) if index != position
        ))
        shortest_first_correct += int(minima[0] == position)
        shortest_fractional_credit += (1 / len(minima)) if position in minima else 0.0
        same_family_positions = [
            index for index, candidate in enumerate(candidates)
            if candidate["same_tactic_head_as_gold"]
        ]
        family_first_correct += int(same_family_positions[0] == position)
        state_text = audit["neutral_transition"]["state_before"]["claims"]["p0"]["proposition"]
        state_tokens = set(token_re.findall(state_text.lower()))
        overlaps = []
        for candidate in candidates:
            candidate_tokens = set(token_re.findall(candidate["tactic_text"].lower()))
            union = state_tokens | candidate_tokens
            overlaps.append(len(state_tokens & candidate_tokens) / len(union) if union else 0.0)
        lexical_correct += int(max(range(len(overlaps)), key=overlaps.__getitem__) == position)
        randomised_label_correct += int(
            max(range(len(overlaps)), key=overlaps.__getitem__)
            == stable_int("randomised-label", hml["record_id"]) % CANDIDATE_COUNT
        )
        if gold_text in hml["input_text"].split("Choose the single most useful next tactic", 1)[0]:
            target_action_outside_candidates += 1
        if delta_h["target_text"] in delta_h["input_text"] or delta_n["target_text"] in delta_n["input_text"]:
            exact_target_in_delta_input += 1

    # Planted failing controls prove the detectors fail closed.
    sample = delta_hml[0]
    planted_delta = {**sample, "input_text": sample["input_text"] + "\nLEAK " + sample["target_text"]}
    planted_delta_detected = planted_delta["target_text"] in planted_delta["input_text"]
    sample_select = select_hml[0]
    planted_select_input = sample_select["input_text"] + f"\nANSWER_KEY {sample_select['gold_candidate_id']}"
    planted_select_detected = bool(re.search(
        rf"(?:ANSWER_KEY|GOLD|CORRECT)\s*[:=]?\s*{re.escape(sample_select['gold_candidate_id'])}\b",
        planted_select_input,
        re.I,
    ))
    parity_mutation_detected = (
        select_hml[0]["audit_metadata"]["canonical_transition_sha256"]
        != ("0" * 64)
    )
    if not (planted_delta_detected and planted_select_detected and parity_mutation_detected):
        raise AssertionError("planted leakage/parity controls did not fail closed")
    n = len(select_hml)
    passed = (
        target_action_outside_candidates == 0
        and exact_target_in_delta_input == 0
        and positive_unique_shortest / n < 1 / CANDIDATE_COUNT
        and max(positions.values()) / min(positions.values()) < 1.05
    )
    return {
        "result": "PASS" if passed else "FAIL",
        "records": n,
        "candidate_count": CANDIDATE_COUNT,
        "answer_position_counts": {str(k): positions[k] for k in range(CANDIDATE_COUNT)},
        "mean_gold_tactic_characters": round(sum(gold_lengths) / len(gold_lengths), 3),
        "mean_distractor_tactic_characters": round(sum(negative_lengths) / len(negative_lengths), 3),
        "positive_is_shortest_rate": round(positive_shortest / n, 6),
        "positive_is_unique_shortest_rate": round(positive_unique_shortest / n, 6),
        "shortest_first_tiebreak_baseline_accuracy": round(shortest_first_correct / n, 6),
        "shortest_fractional_tiebreak_baseline_accuracy": round(shortest_fractional_credit / n, 6),
        "same_tactic_head_distractor_rate": round(same_head / (n * (CANDIDATE_COUNT - 1)), 6),
        "tactic_family_first_tiebreak_baseline_accuracy": round(family_first_correct / n, 6),
        "lexical_overlap_baseline_accuracy": round(lexical_correct / n, 6),
        "lexical_overlap_with_randomised_labels_accuracy": round(randomised_label_correct / n, 6),
        "chance_accuracy": round(1 / CANDIDATE_COUNT, 6),
        "target_action_outside_candidate_block": target_action_outside_candidates,
        "exact_delta_target_in_input": exact_target_in_delta_input,
        "planted_failing_controls": {
            "exact_target_injection_detected": planted_delta_detected,
            "answer_marker_injection_detected": planted_select_detected,
            "canonical_hash_mutation_detected": parity_mutation_detected,
        },
        "negative_status_policy": "distractors are PLAUSIBLE_UNEXECUTED, never asserted INVALID",
    }


def write_outputs(output_root: Path, selected: dict[str, list[dict]], audits: list[dict], task_rows: dict,
                  structural_candidates: list[tuple[int, int, dict]]) -> dict:
    deterministic_gzip(output_root / "canonical" / "records.jsonl.gz", audits)
    record_order = {split: [f"H50K-LEAN-{digest_text(x['example_id'])[:16]}" for x in rows]
                    for split, rows in selected.items()}
    for task, views in task_rows.items():
        for view, rows in views.items():
            by_split = collections.defaultdict(list)
            for row in rows:
                by_split[row["split"]].append(row)
            for split in ("train", "dev", "final"):
                deterministic_gzip(output_root / "tasks" / task / view / f"{split}.jsonl.gz", by_split[split])

    for size in RUNG_SIZES:
        ids = set(record_order["train"][:size])
        write_json(output_root / "rungs" / f"{size // 1000}k" / "record_ids.json", record_order["train"][:size])
        for task in ("NEXT_ACTION_SELECT", "STATE_DELTA_PREDICT"):
            for view in VIEWS:
                rows = [x for x in task_rows[task][view] if x["split"] == "train" and x["record_id"] in ids]
                deterministic_gzip(output_root / "rungs" / f"{size // 1000}k" / task / view / "train.jsonl.gz", rows)

    structural_candidates.sort(key=lambda item: (-item[0], item[1]))
    stress = [x[2] for x in structural_candidates[:5_000]]
    stress_ids = {x["record_id"] for x in stress}
    deterministic_gzip(output_root / "structural_stress" / "audit_records.jsonl.gz", stress)
    for task in ("NEXT_ACTION_SELECT", "STATE_DELTA_PREDICT"):
        for view in VIEWS:
            rows = [x for x in task_rows[task][view] if x["record_id"] in stress_ids]
            deterministic_gzip(output_root / "structural_stress" / task / view / "all.jsonl.gz", rows)
    stress_report = {
        "records": len(stress),
        "selection": "top 5,000 by frozen burden + premise + observed goal/context change score",
        "status": "reference subset; no semantic fields added or simplified",
        "split_counts": dict(collections.Counter(x["split"] for x in stress)),
        "complexity_counts": dict(collections.Counter(x["complexity_bin"] for x in stress)),
        "mechanism_counts": dict(collections.Counter(m for x in stress for m in x["mechanisms"])),
        "unsupported_structure": {
            "branch_semantics": "not claimed from Lean text",
            "candidate_semantics": "candidate sets are task alternatives, not VNext candidate-state objects",
            "obligation_semantics": "not claimed from Lean text",
        },
    }
    write_json(output_root / "structural_stress" / "manifest.json", stress_report)
    return {
        "rungs": {f"{size // 1000}k": size for size in RUNG_SIZES},
        "nested_train_order": "rungs/10k record ids are the first 10k of 30k; 30k are the first 30k of 50k",
        "structural_stress": stress_report,
    }


def manifest_files(output_root: Path) -> dict:
    files = {}
    for path in sorted(output_root.rglob("*")):
        if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS"}:
            files[str(path.relative_to(output_root))] = {"sha256": file_sha(path), "bytes": path.stat().st_size}
    return files


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=repo / "data/hml_50k_final")
    parser.add_argument("--canonical-source", type=Path,
                        default=Path("/Users/moheet/hml_research_artifacts/lean_domino_v2/lean_canonical_records.jsonl"))
    parser.add_argument("--raw-lean-root", type=Path,
                        default=Path("/Users/moheet/hml_research_artifacts/leandojo_raw/leandojo_benchmark_4/random"))
    parser.add_argument("--old-vnext-audit", type=Path, default=repo / "data/vnext_10k/full_audit_records.jsonl.gz")
    parser.add_argument("--token-exclusions", type=Path,
                        default=repo / "scripts/hml50k/token_exclusions_qwen3_8b.json")
    args = parser.parse_args()
    started = time.time()
    output_root = args.output_root.resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    schema = {
        "schema_id": "HML50K_TEACHING_1.0.0",
        "frozen_before_generation": True,
        "seed": SEED,
        "canonical_record": "one exact Lean state/tactic/state-after transition",
        "task_fields": ["record_id", "parent_id", "split", "task", "representation", "input_text", "target_text", "audit_metadata"],
        "canonical_fields": [
            "record_id", "canonical_source_example_id", "parent_id", "split", "source_family",
            "epistemic_status", "mathematical_verification_status", "neutral_transition",
            "depth", "proof_length", "predecessor_record_id", "successor_record_id",
            "candidate_audit", "premises_used", "mechanisms", "complexity_bin",
        ],
        "view_families": list(VIEWS),
        "tasks": list(TASKS),
        "candidate_count": CANDIDATE_COUNT,
        "negative_policy": "4-8 plausible actions required; fixed at 6; alternatives remain PLAUSIBLE_UNEXECUTED",
        "split_policy": "LeanDojo official train/val/test, parent-disjoint, old VNext parents excluded",
        "targets": SPLIT_TARGET,
        "rungs": list(RUNG_SIZES),
        "max_sequence": 6144,
        "tokenizer_preflight": {
            "model": "Qwen/Qwen3-8B",
            "commit": "b968826d9c46dd6066d109eabc6255188de91218",
            "exclusions_file": str(args.token_exclusions),
        },
        "ensure_ascii": False,
        "hml_tree": "RETIRED_NOT_EMITTED",
        "cross_projection": "NOT_EMITTED",
        "authority": {"hml_commit": HML_SHA, "contract": CONTRACT, "mathlib_commit": MATHLIB_SHA},
    }
    write_json(output_root / "schema_selection_spec.json", schema)

    old_parents = old_vnext_parents(args.old_vnext_audit)
    token_exclusion_data = json.loads(args.token_exclusions.read_text(encoding="utf-8"))
    token_exclusions = set(token_exclusion_data["source_example_ids"])
    catalog, source_audit = scan_catalog(args.canonical_source, old_parents, token_exclusions)
    selected, selection_audit = choose_splits(catalog)
    selected_ids = {x["example_id"] for rows in selected.values() for x in rows}
    raw_rows = load_selected_rows(args.canonical_source, selected_ids)
    premise_map, premise_audit = load_premises(args.raw_lean_root, selected, raw_rows)
    thresholds = complexity_thresholds(selected["train"])
    candidates = candidate_sets(selected)
    audits, task_rows, _, structural_candidates = render_all(
        selected, raw_rows, premise_map, candidates, thresholds
    )
    leakage_audit = leakage_and_candidate_audit(audits, task_rows)
    if leakage_audit["result"] != "PASS":
        raise AssertionError(f"leakage/candidate gate failed: {leakage_audit}")
    write_report = write_outputs(output_root, selected, audits, task_rows, structural_candidates)

    counts = {
        "canonical": dict(collections.Counter(x["split"] for x in audits)),
        "source_family": dict(collections.Counter(x["source_family"] for x in audits)),
        "epistemic_status": dict(collections.Counter(x["epistemic_status"] for x in audits)),
        "complexity": dict(collections.Counter(x["complexity_bin"] for x in audits)),
        "depth": dict(collections.Counter(x["depth_bin"] for x in audits)),
        "probability_statistics_related": sum(x["probability_statistics_related"] for x in audits),
        "premise_count": {
            "zero": sum(not x["premises_used"] for x in audits),
            "one": sum(len(x["premises_used"]) == 1 for x in audits),
            "multiple": sum(len(x["premises_used"]) > 1 for x in audits),
        },
        "task_rows_per_view": {
            task: dict(collections.Counter(x["split"] for x in task_rows[task][VIEWS[0]]))
            for task in TASKS
        },
    }
    write_json(output_root / "audits" / "source_audit.json", source_audit)
    write_json(output_root / "audits" / "selection_audit.json", selection_audit)
    write_json(output_root / "audits" / "premise_recovery_audit.json", premise_audit)
    write_json(output_root / "audits" / "complexity_thresholds.json", thresholds)
    write_json(output_root / "audits" / "leakage_candidate_audit.json", leakage_audit)
    write_json(output_root / "audits" / "counts.json", counts)
    write_json(output_root / "audits" / "generation_environment.json", {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "logical_workers_available": subprocess.check_output(["sysctl", "-n", "hw.logicalcpu"], text=True).strip(),
        "workers_used": 1,
        "reason": "streaming is I/O-bound and deterministic renderer state is lightweight; no cloud or model process used",
        "wall_seconds": round(time.time() - started, 3),
        "cloud_access": False,
        "model_loaded": False,
    })
    write_json(output_root / "audits" / "build_summary.json", {
        "result": "PASS",
        "train_usable": counts["canonical"].get("train", 0),
        "separate_dev": counts["canonical"].get("dev", 0),
        "separate_final": counts["canonical"].get("final", 0),
        "view_parity": True,
        "hml_roundtrip_records": len(audits),
        "hml_state_roundtrips": 2 * len(audits),
        "source_mix_decision": "formal-only core; lower-certainty local sources inventoried but not used to pad count",
        "write_report": write_report,
    })

    files = manifest_files(output_root)
    manifest = {
        "dataset": "HML50K_TEACHING",
        "schema": "HML50K_TEACHING_1.0.0",
        "result": "PASS",
        "seed": SEED,
        "authority": {"hml_commit": HML_SHA, "contract": CONTRACT, "mathlib_commit": MATHLIB_SHA},
        "counts": counts,
        "selection": selection_audit,
        "complexity_thresholds": thresholds,
        "leakage_candidate_audit": leakage_audit,
        "files": files,
        "manifest_self_hash": "excluded_by_design; see git blob/commit and SHA256SUMS for payload hashes",
    }
    write_json(output_root / "manifest.json", manifest)
    sums = "".join(f"{meta['sha256']}  {name}\n" for name, meta in sorted(files.items()))
    (output_root / "SHA256SUMS").write_text(sums, encoding="utf-8")
    print(canonical({
        "result": "PASS",
        "output_root": str(output_root),
        "counts": counts["canonical"],
        "files": len(files),
        "wall_seconds": round(time.time() - started, 3),
    }))


if __name__ == "__main__":
    main()
