#!/usr/bin/env python3
"""Build the first gated 10k VNext curriculum from qualified local sources."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import heapq
import io
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

from hamiltonian_lang.semantic_state import (
    Action, Candidate, CandidateStatus, Claim, ClaimStatus, EvidenceRecord,
    SemanticState, Transition, Verdict, export_state, export_transition,
    import_transition, parse_state, parse_transition, render_state,
    render_transition, verify_replay, verify_runtime,
)
from hamiltonian_lang.semantic_state.tree_view import (
    parse_tree_state, parse_tree_transition, render_tree_state, render_tree_transition,
)

from experiments.prm800k_audit.audit_prm800k import candidate_records, load_math_metadata
from scripts.build_prm800k_gap_pilot import EXPECTED_FILES
from scripts.vnext.corpus_rederive import _decode_json_ast, _json_ast


SEED = "hmltn-vnext-10k-20260813"
HML_SHA = "68178f07784d2a17a9aed9c4dedbea9c740c97a0"
CONTRACT = "vnext-translation-contract-1.0.0"
PRM_SHA = "7ecc794703b2877f63226f2477a49b34f9b25163"
MATHLIB_SHA = "29dcec074de168ac2bf835a77ef68bbe069194c5"
SOURCE_TARGETS = {
    "LEAN_DOJO": 4000,
    "PRM800K": 2000,
    "MATH": 2000,
    "AMPS": 1000,
    "SYNTHETIC_HARD_TAIL": 1000,
}


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalized_problem(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = re.sub(r"\\boxed\s*\{([^{}]*)\}", r"\1", value)
    return value


def deterministic_gzip(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8") as text:
                for row in rows:
                    text.write(canonical(row) + "\n")


def unknown_evidence(eid: str, rule: str, deps: tuple[str, ...], payload: dict) -> EvidenceRecord:
    return EvidenceRecord(
        id=eid, kind="SOURCE_DERIVATION", status="UNKNOWN", trusted=False,
        supports_rule=rule, premise_ids=deps, payload=payload,
    )


def plain_transition(case_id: str, before_text: str, after_text: str, operation: str,
                     source: dict, *, replay_valid: bool = False) -> Transition:
    p0 = Claim(id="p0", proposition=before_text, status=ClaimStatus.GIVEN,
               scope="global", domain="Proposition")
    c1 = Claim(id="c1", proposition=after_text, status=ClaimStatus.DERIVED,
               scope="global", domain="Proposition", dependencies=("p0",))
    before = SemanticState(claims={"p0": p0}, active_scopes=("global",))
    after = SemanticState(claims={"p0": p0, "c1": c1}, active_scopes=("global",))
    eid = "e1"
    evidence = (
        EvidenceRecord(id=eid, kind="FORMAL_TRACE_REPLAY", status="VALID", trusted=True,
                       supports_rule=operation, premise_ids=("p0",), payload=source)
        if replay_valid
        else unknown_evidence(eid, operation, ("p0",), source)
    )
    action = Action(
        id="a1", operation=operation, summary="", output_id="c1",
        dependencies=("p0",), warrant={"rule": operation, "evidence_id": eid},
    )
    return Transition(case_id=case_id, state_before=before, action=action,
                      state_after=after, evidence={eid: evidence}, source=source)


def prm_transition(row: dict) -> Transition:
    claims = {
        "p0": Claim(id="p0", proposition=row["problem"], status=ClaimStatus.GIVEN,
                    scope="global", domain="Proposition")
    }
    for index, prefix in enumerate(row["preceding_state_proxy"], 1):
        cid = f"p{index:03d}"
        claims[cid] = Claim(id=cid, proposition=prefix["text"], status=ClaimStatus.GIVEN,
                            scope="global", domain="Proposition")
    before = SemanticState(claims=claims, active_scopes=("global",))
    dep = (next(reversed(claims)),)
    source = {
        "repository": "https://github.com/openai/prm800k.git", "commit": PRM_SHA,
        "file": row["provenance"]["source_split_file"], "line": row["source_line"],
        "candidate_id": row["candidate_id"], "source_process_label": row["rating"],
        "label_is_mathematical_certificate": False,
    }
    eid = "e1"
    if not row["is_chosen_completion"]:
        candidate = Candidate(
            id="candidate_action", proposition=row["candidate_text"],
            status=CandidateStatus.PROPOSED, scope="global", constraint_ids=dep,
            origin="PRM800K alternative reasoning action", dependencies=dep,
        )
        after = SemanticState(claims=claims, candidates={candidate.id: candidate},
                              active_scopes=("global",))
        operation = "PROPOSE_REASONING_ACTION"
        action = Action(
            id="a1", operation=operation, summary="", dependencies=dep,
            candidate_effect={"kind": "CREATE", "candidate_id": candidate.id},
            warrant={"rule": operation, "evidence_id": eid},
        )
    else:
        claim = Claim(id="c_out", proposition=row["candidate_text"],
                      status=ClaimStatus.DERIVED, scope="global", domain="Proposition",
                      dependencies=dep)
        after = SemanticState(claims={**claims, claim.id: claim}, active_scopes=("global",))
        operation = "GENERIC_REASONING_ACTION"
        action = Action(
            id="a1", operation=operation, summary="", output_id=claim.id,
            dependencies=dep, warrant={"rule": operation, "evidence_id": eid},
        )
    evidence = unknown_evidence(eid, operation, dep, source)
    return Transition(case_id=f"VN10K-PRM-{row['candidate_id']}", state_before=before,
                      action=action, state_after=after, evidence={eid: evidence}, source=source)


def math_spans(text: str) -> list[str]:
    spans = []
    for match in re.finditer(r"\$\$(.*?)\$\$|(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", text, re.S):
        value = (match.group(1) or match.group(2) or "").strip()
        if value and value not in spans:
            spans.append(value)
    return spans


def select_prm(source_root: Path, excluded: set[str]) -> list[dict]:
    targets = {-1: 800, 0: 500, 1: 700}
    heaps: dict[int, list[tuple[int, str, dict]]] = {rating: [] for rating in targets}
    meta = load_math_metadata(source_root)
    files = ("phase1_train.jsonl", "phase2_train.jsonl")
    for filename in files:
        path = source_root / "prm800k" / "data" / filename
        if file_sha(path) != EXPECTED_FILES[filename]:
            raise AssertionError(f"PRM source hash mismatch: {filename}")
        phase, split = filename.removesuffix(".jsonl").split("_", 1)
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                source_row = json.loads(line)
                for row in candidate_records(phase, split, line_number, source_row, meta):
                    rating = row["rating"]
                    if rating not in targets or row["candidate_id"] in excluded:
                        continue
                    rank = int(digest(SEED + row["candidate_id"]), 16)
                    item = (-rank, row["candidate_id"], row)
                    heap = heaps[rating]
                    if len(heap) < targets[rating]:
                        heapq.heappush(heap, item)
                    elif item > heap[0]:
                        heapq.heapreplace(heap, item)
                if filename == "phase2_train.jsonl" and line_number >= 40000 and all(
                    len(heaps[rating]) == target for rating, target in targets.items()
                ):
                    break
    selected = [item[2] for heap in heaps.values() for item in heap]
    if collections.Counter(row["rating"] for row in selected) != targets:
        raise AssertionError("PRM label quotas were not met")
    return sorted(selected, key=lambda row: row["candidate_id"])


def complexity(neutral: dict) -> tuple[int, list[str]]:
    action = neutral["action"]
    before, after = neutral["state_before"], neutral["state_after"]
    mechanisms = []
    if (action.get("candidate_effect") or {}).get("kind") == "CREATE": mechanisms.append("candidate_create")
    branch_kind = (action.get("branch_effect") or {}).get("kind")
    if branch_kind == "OPEN": mechanisms.append("branch_open")
    if branch_kind == "CLOSE": mechanisms.append("branch_close")
    if branch_kind == "JOIN": mechanisms.append("branch_join")
    if action.get("operation") == "WEAKEN": mechanisms.append("implicit_logical_weakening")
    if action.get("exactness_effect"): mechanisms.append("approximate")
    if action.get("obligations_created") or action.get("obligations_discharged"): mechanisms.append("obligations")
    if before.get("active_scopes") != after.get("active_scopes"): mechanisms.append("scope_change")
    if len(action.get("dependencies") or []) > 1: mechanisms.append("multiple_dependencies")
    if any(claim.get("status") == "ASSUMED" for claim in after.get("claims", {}).values()): mechanisms.append("assumption")
    if any(branch.get("scope") != "global" for branch in after.get("branches", {}).values()): mechanisms.append("nested_branch")
    text = canonical(after)
    if re.search(r"\\forall|\\exists|\bforall\b|\bexists\b", text): mechanisms.append("quantifier")
    if not mechanisms: mechanisms.append("ordinary_claim_derivation")
    score = 10 * len(mechanisms) + len(action.get("dependencies") or [])
    return score, sorted(set(mechanisms))


def metadata_record(record_id: str, source_family: str, parent_id: str, problem: str,
                    domain: str, difficulty: str, epistemic: str, transition: Transition,
                    mechanisms: list[str], process_label=None) -> dict:
    group = digest(normalized_problem(problem))
    execute = epistemic in {"FORMALLY_VERIFIED_TRANSITION", "BACKEND_VERIFIED_TRANSITION"}
    return {
        "record_id": record_id, "source_family": source_family, "parent_id": parent_id,
        "parent_group_sha256": group, "problem_normalized_sha256": group,
        "domain": domain, "difficulty": difficulty, "epistemic_status": epistemic,
        "source_process_label": process_label,
        "mathematical_verification_status": (
            "FORMAL_REPLAY_VERIFIED" if epistemic == "FORMALLY_VERIFIED_TRANSITION"
            else "DETERMINISTIC_LOGICAL_REPLAY" if epistemic == "BACKEND_VERIFIED_TRANSITION"
            else "UNATTESTED"
        ),
        "semantic_representation_status": "REPRESENTED_VNEXT",
        "mechanisms": mechanisms,
        "task_eligibility": {
            "EXECUTE": execute,
            "APPLICABILITY": False,
            "JUDGE": source_family in {"LEAN_DOJO", "PRM800K"},
            "REPAIR": False,
            "COMPREHENSION": True,
        },
        "transition": transition,
    }


def parity_and_views(item: dict) -> tuple[dict, dict[str, dict]]:
    transition = item.pop("transition")
    replay = any(e.status == "VALID" for e in transition.evidence.values())
    result = verify_replay(transition) if replay else verify_runtime(transition)
    if result.verdict is Verdict.INVALID:
        raise AssertionError(f"{item['record_id']}: {result.to_dict()}")
    linear = render_transition(transition)
    tree = render_tree_transition(transition)
    if parse_transition(linear) != transition or parse_tree_transition(tree) != transition:
        raise AssertionError(f"{item['record_id']}: transition representation mismatch")
    neutral = export_transition(transition)
    ast = _json_ast(neutral)
    if _decode_json_ast(ast) != neutral:
        raise AssertionError(f"{item['record_id']}: AST mismatch")
    safe_action = {
        "operation": neutral["action"].get("operation"),
        "dependencies": neutral["action"].get("dependencies", []),
        "preconditions": neutral["action"].get("preconditions", []),
        "warrant_rule": (neutral["action"].get("warrant") or {}).get("rule"),
    }
    safe_neutral = {"state_before": neutral["state_before"], "action": safe_action}
    forbidden = {"state_after", "summary", "output_id", "source", "target_delta"}
    if forbidden & set(safe_action) or "state_after" in safe_neutral:
        raise AssertionError(f"{item['record_id']}: unsafe input projection")
    after_state = transition.state_after
    linear_before, linear_after = render_state(transition.state_before), render_state(after_state)
    tree_before, tree_after = render_tree_state(transition.state_before), render_tree_state(after_state)
    if parse_state(linear_before) != transition.state_before or parse_state(linear_after) != after_state:
        raise AssertionError(f"{item['record_id']}: HML state mismatch")
    if parse_tree_state(tree_before) != transition.state_before or parse_tree_state(tree_after) != after_state:
        raise AssertionError(f"{item['record_id']}: tree state mismatch")
    item["neutral"] = neutral
    item["canonical_sha256"] = digest(canonical(neutral))
    item["verifier_verdict"] = str(result.verdict)
    item["representation_parity"] = "PASS"
    item["leakage_check"] = "PASS"
    audit = {**item, "views": {"HML_LINEAR": linear, "HML_TREE": tree, "AST": ast}}
    views = {
        "HML_LINEAR": {"record_id": item["record_id"], "input": linear_before + "\nACTION " + canonical(safe_action), "target": linear_after},
        "HML_TREE": {"record_id": item["record_id"], "input": tree_before + "\nACTION " + canonical(safe_action), "target": tree_after},
        "AST": {"record_id": item["record_id"], "input": _json_ast(safe_neutral), "target": _json_ast(export_state(after_state))},
        "STRUCTURED_NEUTRAL": {"record_id": item["record_id"], "input": safe_neutral, "target": export_state(after_state)},
    }
    return audit, views


def split_for(group: str) -> str:
    bucket = int(digest(SEED + ":split:" + group)[:8], 16) % 100
    return "train" if bucket < 80 else "dev" if bucket < 90 else "test"


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=root / "data/vnext_10k")
    parser.add_argument("--lean", type=Path, default=Path("/Users/moheet/hml_research_artifacts/leandojo/sample.jsonl"))
    parser.add_argument("--prm-root", type=Path, default=Path("/Users/moheet/Documents/ChatGPT/prm800k"))
    parser.add_argument("--math", type=Path, default=root / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet")
    parser.add_argument("--amps", type=Path, default=root / "data/raw/amps_khan/0000.parquet")
    parser.add_argument("--hard-tail", type=Path, default=root / "data/vnext_600/full_audit_records.jsonl.gz")
    parser.add_argument("--prm-pilot", type=Path, default=root / "experiments/prm800k_audit/results/cross_source_gap_pilot_v1.jsonl")
    args = parser.parse_args()

    raw: list[dict] = []
    seen_signatures: set[str] = set()

    lean_rows = [json.loads(line) for line in args.lean.read_text(encoding="utf-8").splitlines() if line]
    lean_rows.sort(key=lambda row: digest(SEED + row["proof_id"] + str(row["step_index"])))
    for row in lean_rows:
        signature = digest(row["state_before"] + "\0" + row["tactic_surface"] + "\0" + row["state_after"])
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        rid = f"VN10K-LEAN-{len([x for x in raw if x['source_family']=='LEAN_DOJO']) + 1:04d}"
        transition = plain_transition(
            rid, row["state_before"], row["state_after"], "LEAN_TACTIC",
            {**row["provenance"], "proof_id": row["proof_id"], "step_index": row["step_index"],
             "tactic": row["tactic_surface"], "premises_used": row["premises_used"]},
            replay_valid=True,
        )
        mechanisms = ["ordinary_claim_derivation"]
        if row["derived"].get("closed"): mechanisms.append("goal_close")
        if row["derived"].get("delta_goals", 0) > 0: mechanisms.append("goal_create")
        raw.append(metadata_record(rid, "LEAN_DOJO", row["proof_id"], row["theorem_id"],
                                   "formal_lean", "not_applicable", "FORMALLY_VERIFIED_TRANSITION",
                                   transition, mechanisms))
        if sum(x["source_family"] == "LEAN_DOJO" for x in raw) == 4000:
            break

    pilot_ids = {json.loads(line)["source"]["candidate_id"] for line in args.prm_pilot.read_text().splitlines() if line}
    prm_rows = select_prm(args.prm_root, pilot_ids)
    used_problem_hashes = set()
    for row in prm_rows:
        transition = prm_transition(row)
        mechanisms = ["candidate_create"] if not row["is_chosen_completion"] else ["ordinary_claim_derivation"]
        if row["rating"] == -1: mechanisms.append("error_process_negative")
        raw.append(metadata_record(
            transition.case_id, "PRM800K", row["trajectory_id"], row["problem"],
            str(row["subject"]), str(row["level"]), "HUMAN_PROCESS_LABEL", transition,
            mechanisms, process_label=row["rating"],
        ))
        used_problem_hashes.add(digest(normalized_problem(row["problem"])))

    math_source_sha = file_sha(args.math)
    math_table = pq.read_table(args.math, columns=["problem", "level", "type", "solution"]).to_pylist()
    math_table.sort(key=lambda row: digest(SEED + row["problem"]))
    math_count = 0
    for row in math_table:
        ph = digest(normalized_problem(row["problem"]))
        if ph in used_problem_hashes:
            continue
        spans = math_spans(row["solution"])
        before = spans[0] if spans else row["problem"]
        after = spans[1] if len(spans) > 1 else row["solution"]
        rid = f"VN10K-MATH-{math_count + 1:04d}"
        source = {"dataset": "Hendrycks MATH train", "row_problem_sha256": ph,
                  "source_file_sha256": math_source_sha, "solution_sha256": digest(row["solution"])}
        transition = plain_transition(rid, before, after, "SOURCE_DERIVATION", source)
        raw.append(metadata_record(rid, "MATH", ph, row["problem"], row["type"], row["level"],
                                   "REPRESENTABLE_UNVERIFIED", transition,
                                   ["ordinary_claim_derivation"]))
        used_problem_hashes.add(ph)
        math_count += 1
        if math_count == 2000: break

    amps_source_sha = file_sha(args.amps)
    amps_table = pq.read_table(args.amps, columns=["topic_name", "problem", "hints/solutions"]).to_pylist()
    amps_table = [row for row in amps_table if row.get("problem")]
    amps_table.sort(key=lambda row: digest(SEED + row["problem"]))
    amps_count = 0
    for row in amps_table:
        ph = digest(normalized_problem(row["problem"]))
        if ph in used_problem_hashes:
            continue
        solution = row["hints/solutions"] or ""
        spans = math_spans(solution)
        before = spans[0] if spans else row["problem"]
        after = spans[1] if len(spans) > 1 else solution
        if not after.strip():
            continue
        rid = f"VN10K-AMPS-{amps_count + 1:04d}"
        source = {"dataset": "AMPS/Khan", "row_problem_sha256": ph,
                  "source_file_sha256": amps_source_sha, "solution_sha256": digest(solution)}
        transition = plain_transition(rid, before, after, "PROCEDURAL_TRANSFORM", source)
        raw.append(metadata_record(rid, "AMPS", ph, row["problem"], str(row["topic_name"]),
                                   "not_provided", "REPRESENTABLE_UNVERIFIED", transition,
                                   ["ordinary_claim_derivation", "procedural_operator"]))
        used_problem_hashes.add(ph)
        amps_count += 1
        if amps_count == 1000: break

    hard_candidates = []
    with gzip.open(args.hard_tail, "rt", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            score, mechanisms = complexity(item["structured_neutral"])
            hard_candidates.append((score, digest(SEED + item["record_id"]), item, mechanisms))
    hard_candidates.sort(key=lambda item: (-item[0], item[1]))
    for index, (_, _, item, mechanisms) in enumerate(hard_candidates[:1000], 1):
        transition = import_transition(item["structured_neutral"])
        epistemic = (
            "BACKEND_VERIFIED_TRANSITION"
            if any(e.status == "VALID" for e in transition.evidence.values())
            else "REPRESENTABLE_UNVERIFIED"
        )
        rid = f"VN10K-HARD-{index:04d}"
        transition = Transition(
            case_id=rid, state_before=transition.state_before, action=transition.action,
            state_after=transition.state_after, evidence=transition.evidence,
            source={**transition.source, "upstream_record_id": item["record_id"]},
        )
        parent = str(item["record_id"]).split("-T", 1)[0].split("::", 1)[0]
        raw.append(metadata_record(rid, "SYNTHETIC_HARD_TAIL", parent, parent,
                                   "synthetic_math", "mixed", epistemic, transition, mechanisms))

    counts = collections.Counter(item["source_family"] for item in raw)
    if counts != collections.Counter(SOURCE_TARGETS) or len(raw) != 10000:
        raise AssertionError(f"source composition mismatch: {counts}")

    audits, arm_rows = [], collections.defaultdict(list)
    for item in raw:
        audit, views = parity_and_views(item)
        audit["split"] = split_for(audit["parent_group_sha256"])
        audits.append(audit)
        for arm, view in views.items():
            view["split"] = audit["split"]
            arm_rows[arm].append(view)

    # Weighted deterministic curriculum ordering: every 10-row block is 4/2/2/1/1 while
    # source queues have data, making all nested snapshots diverse and exact subsets.
    queues = {
        family: collections.deque(sorted(
            (item for item in audits if item["source_family"] == family),
            key=lambda item: digest(SEED + ":order:" + item["record_id"]),
        )) for family in SOURCE_TARGETS
    }
    pattern = ["LEAN_DOJO"] * 4 + ["PRM800K"] * 2 + ["MATH"] * 2 + ["AMPS", "SYNTHETIC_HARD_TAIL"]
    ordered = []
    while any(queues.values()):
        progressed = False
        for family in pattern:
            if queues[family]:
                ordered.append(queues[family].popleft())
                progressed = True
        if not progressed: break
    order_index = {item["record_id"]: index for index, item in enumerate(ordered)}
    audits.sort(key=lambda item: order_index[item["record_id"]])
    for rows in arm_rows.values(): rows.sort(key=lambda item: order_index[item["record_id"]])

    out = args.output_root
    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        deterministic_gzip(out / f"{split}.jsonl.gz", (
            {key: value for key, value in item.items() if key != "views"}
            for item in audits if item["split"] == split
        ))
        for arm, rows in arm_rows.items():
            deterministic_gzip(out / "views" / arm / f"{split}.jsonl.gz",
                               (item for item in rows if item["split"] == split))
    deterministic_gzip(out / "full_audit_records.jsonl.gz", audits)

    snapshots = {}
    for size in (100, 250, 1000, 5000, 10000):
        selected = audits[:size]
        snapshots[str(size)] = {
            "record_ids": [item["record_id"] for item in selected],
            "source_counts": dict(sorted(collections.Counter(item["source_family"] for item in selected).items())),
            "task_counts": {
                task: sum(item["task_eligibility"][task] for item in selected)
                for task in ("EXECUTE", "APPLICABILITY", "JUDGE", "REPAIR", "COMPREHENSION")
            },
        }
    (out / "snapshots.json").write_text(json.dumps(snapshots, indent=2, sort_keys=True) + "\n")

    paths = sorted(path for path in out.rglob("*") if path.is_file() and path.name != "manifest.json")
    split_counts = collections.Counter(item["split"] for item in audits)
    epistemic_counts = collections.Counter(item["epistemic_status"] for item in audits)
    mechanism_counts = collections.Counter(m for item in audits for m in item["mechanisms"])
    # Keep absent curriculum mechanisms explicit.  A missing key must not be
    # mistaken for unmeasured coverage by downstream consumers.
    for mechanism in (
        "candidate_derive", "candidate_reject", "candidate_verify_or_promote",
        "exact_explicit", "quantifier_operation", "repair_transition",
        "theorem_or_library_backed",
    ):
        mechanism_counts.setdefault(mechanism, 0)
    domain_counts = collections.Counter(item["domain"] for item in audits)
    difficulty_counts = collections.Counter(item["difficulty"] for item in audits)
    task_counts = {
        task: sum(item["task_eligibility"][task] for item in audits)
        for task in ("EXECUTE", "APPLICABILITY", "JUDGE", "REPAIR", "COMPREHENSION")
    }
    manifest = {
        "schema_version": "hmltn-vnext-curriculum-1.0.0",
        "record_count": len(audits), "hml_semantic_commit": HML_SHA,
        "contract_version": CONTRACT, "corpus_build_base_commit": "3bbb4256fe424e126ad1058c7bb8223c58b3afeb",
        "split_seed": SEED, "split_policy": "parent theorem/problem/trajectory group before atomic rows; 80/10/10 hash buckets",
        "source_revisions": {
            "LEAN_DOJO": {"mathlib4": MATHLIB_SHA, "lean": "v4.10.0-rc1", "derived_sample_sha256": file_sha(args.lean)},
            "PRM800K": {"commit": PRM_SHA},
            "MATH": {"file_sha256": math_source_sha},
            "AMPS": {"file_sha256": amps_source_sha},
            "SYNTHETIC_HARD_TAIL": {"vnext_600_sha256": file_sha(args.hard_tail)},
        },
        "source_counts": dict(sorted(counts.items())),
        "epistemic_counts": dict(sorted(epistemic_counts.items())),
        "split_counts": dict(sorted(split_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "difficulty_counts": dict(sorted(difficulty_counts.items())),
        "mechanism_counts": dict(sorted(mechanism_counts.items())),
        "numeric_status_counts": {
            "APPROXIMATE_EXPLICIT": mechanism_counts["approximate"],
            "EXACT_EXPLICIT": mechanism_counts["exact_explicit"],
            "UNANNOTATED": len(audits) - mechanism_counts["approximate"] - mechanism_counts["exact_explicit"],
        },
        "task_eligibility_counts": task_counts,
        "representation_counts": {arm: len(rows) for arm, rows in sorted(arm_rows.items())},
        "representation_parity": "10000/10000 PASS",
        "leakage_audit": "10000/10000 PASS",
        "deduplication": {
            "exact_transition_signatures": "deduplicated",
            "normalized_problem_hash": "cross-source PRM/MATH/AMPS exclusion and shared split grouping",
            "parent_group_split_leakage": "PASS",
            "miniF2F_ProofNet_bulk_training": False,
        },
        "known_deficits": {
            "candidate_reject": 0, "candidate_verify_or_promote": 0,
            "repair_eligible": 0,
            "reason": "No trustworthy certified negative/correction pairs were available; complexity was not synthesized."
        },
        "snapshots": {size: {key: value for key, value in entry.items() if key != "record_ids"} for size, entry in snapshots.items()},
        "files": {str(path.relative_to(out)): {"bytes": path.stat().st_size, "sha256": file_sha(path)} for path in paths},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "records": len(audits), "source_counts": manifest["source_counts"],
        "split_counts": manifest["split_counts"], "epistemic_counts": manifest["epistemic_counts"],
        "task_counts": task_counts, "manifest": str(out / "manifest.json"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
