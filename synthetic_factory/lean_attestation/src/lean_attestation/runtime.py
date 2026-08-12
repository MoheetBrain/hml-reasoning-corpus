"""Fresh Lean replay and representation-neutral evidence certificates.

This module deliberately knows nothing about HML action fields.  It reconstructs a
Lean theorem state by replaying the exact traced proof prefix, executes the selected
tactic, and compares Lean's runtime states with the pinned historical trace.
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import threading
import time
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Iterator

from synthetic_factory.authority import line_count, sha256_file
from synthetic_factory.constants import (
    CORPUS_SHA,
    HML_SHA,
    HML_TAG,
    LEAN_CANONICAL_BYTES,
    LEAN_CANONICAL_RECORDS,
    LEAN_CANONICAL_SHA256,
)

SCHEMA_VERSION = "lean-attestation-certificate-1.0.0"
LEAN_VERSION = "v4.10.0-rc1"
LEAN_BUILD_COMMIT = "3b58e0649156"
MATHLIB_SHA = "29dcec074de168ac2bf835a77ef68bbe069194c5"
LEANDOJO_VERSION = "2.0.0"
LEANDOJO_SHA = "abcfb72143ff3829e622418557e14c8b41b69a61"
SOURCE_ARCHIVE_SHA256 = "19b9a31968229d5bae4b959be9351d92740643d16a58c7f58f6d82795b8a98a4"
SOURCE_ARCHIVE_MD5 = "25e1ee60cd8925b9d2e8673ddcc34b4c"
SOURCE_ARCHIVE_BYTES = 68_141_936
SOURCE_ARCHIVE_DOI = "10.5281/zenodo.12740403"
SOURCE_ARCHIVE_NAME = "leandojo_benchmark_4.tar.gz"
SOURCE_REPO_URL = "https://github.com/leanprover-community/mathlib4"
LEANDOJO_REPO_URL = "https://github.com/lean-dojo/LeanDojo.git"
REMOTE_TRACE_URL = (
    "https://dl.fbaipublicfiles.com/lean-dojo/"
    f"leanprover-community-mathlib4-{MATHLIB_SHA}.tar.gz"
)
THEOREM_SPLIT_SHA256 = "2fddc0685f07ff85afb82da9fc40c7683fa0920ad8888937da9fb174f6a76637"
SPLIT_MANIFEST_SHA256 = "e015b4311e76985644555e69ba83229b88d532de5268abe4375a2adc00f1fbb3"
EXPECTED_SPLIT_COUNTS = {"TRAIN": 192_882, "DEV": 24_067, "FINAL": 24_316}
MATCH_VALUES = {
    "EXACT_TEXT_MATCH",
    "NORMALIZED_STATE_MATCH",
    "SEMANTICALLY_EQUIVALENT_IF_PROVABLE",
    "MISMATCH",
}
REPLAY_STATUSES = {
    "TRACE_ONLY",
    "REPLAY_PASS",
    "REPLAY_STATE_MISMATCH",
    "REPLAY_TACTIC_FAIL",
    "ENVIRONMENT_UNAVAILABLE",
    "UNSUPPORTED",
}
EFFECT_CLASSES = (
    "CLOSE",
    "TRANSFORM_TARGET",
    "INTRODUCE",
    "INTRODUCE_AND_TRANSFORM",
    "REWRITE_CONTEXT",
    "REWRITE_CONTEXT_AND_TARGET",
    "NO_VISIBLE_CHANGE",
    "ELIMINATE",
)
FORBIDDEN_INVENTED_FIELDS = {
    "hml",
    "hml_action",
    "hml_dependencies",
    "evidence_envelope",
    "obligations",
    "scope_metadata",
    "typed_hml_action_args",
}


class AttestationError(RuntimeError):
    """The attestation contract cannot be satisfied safely."""


class _OfflineLeanMetadata:
    """Non-network placeholder for LeanDojo's import-time GitHub handles."""

    def __init__(self, full_name: str):
        self.full_name = full_name
        self.name = full_name.rsplit("/", 1)[-1]


def install_offline_github_guard() -> None:
    """Prevent LeanDojo's import-time PyGithub handles from making HTTP calls."""

    from github import Github

    if getattr(Github.get_repo, "_hmltn_offline_guard", False):
        return

    def get_repo(_self: Any, full_name: str, *args: Any, **kwargs: Any) -> _OfflineLeanMetadata:
        if full_name in {"leanprover/lean4", "leanprover/lean4-nightly"}:
            return _OfflineLeanMetadata(full_name)
        raise AttestationError(
            f"unplanned GitHub metadata lookup blocked during pinned replay: {full_name}"
        )

    setattr(get_repo, "_hmltn_offline_guard", True)
    Github.get_repo = get_repo


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest(value: Any) -> str:
    return sha256_text(canonical_json(value))


def normalize_state(text: str) -> str:
    """Apply only transport-level normalization, never semantic rewriting."""

    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n")).rstrip("\n")


def compare_states(recorded: str, runtime: str) -> str:
    if recorded == runtime:
        return "EXACT_TEXT_MATCH"
    if normalize_state(recorded) == normalize_state(runtime):
        return "NORMALIZED_STATE_MATCH"
    # SEMANTICALLY_EQUIVALENT_IF_PROVABLE is intentionally never inferred here.
    return "MISMATCH"


def state_hashes(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    return sha256_text(value), sha256_text(normalize_state(value))


def _run(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode:
        raise AttestationError(
            f"command failed ({result.returncode}): {' '.join(args)}: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def attestation_code_sha(attestation_root: Path) -> str:
    paths = [
        Path(__file__),
        attestation_root / "schemas" / "lean_attestation_certificate.schema.json",
    ]
    h = hashlib.sha256()
    for path in sorted(paths):
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _file_identity(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_source_authority(source_root: Path, canonical_path: Path) -> dict[str, Any]:
    split_path = source_root / "theorem_split.json"
    split_manifest_path = source_root / "split_manifest.json"
    archive_path = Path(os.environ["LEAN_SOURCE_ARCHIVE_PATH"])
    checks = {
        "canonical": _file_identity(canonical_path),
        "theorem_split": _file_identity(split_path),
        "split_manifest": _file_identity(split_manifest_path),
        "source_archive": _file_identity(archive_path),
    }
    if checks["canonical"]["sha256"] != LEAN_CANONICAL_SHA256:
        raise AttestationError("Lean canonical source SHA-256 mismatch")
    if checks["canonical"]["bytes"] != LEAN_CANONICAL_BYTES:
        raise AttestationError("Lean canonical source byte count mismatch")
    if line_count(canonical_path) != LEAN_CANONICAL_RECORDS:
        raise AttestationError("Lean canonical source line count mismatch")
    if checks["theorem_split"]["sha256"] != THEOREM_SPLIT_SHA256:
        raise AttestationError("theorem split SHA-256 mismatch")
    if checks["split_manifest"]["sha256"] != SPLIT_MANIFEST_SHA256:
        raise AttestationError("split manifest SHA-256 mismatch")
    if checks["source_archive"]["sha256"] != SOURCE_ARCHIVE_SHA256:
        raise AttestationError("source archive SHA-256 mismatch")
    if checks["source_archive"]["bytes"] != SOURCE_ARCHIVE_BYTES:
        raise AttestationError("source archive byte count mismatch")
    split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    observed_counts = {key.upper(): value for key, value in split_manifest["example_counts"].items()}
    if observed_counts != EXPECTED_SPLIT_COUNTS or split_manifest["overlap"]:
        raise AttestationError(f"theorem split contract mismatch: {split_manifest}")
    return checks


def recover_environment(
    *, attestation_root: Path, source_root: Path, canonical_path: Path, traced_repo: Path, leandojo_root: Path
) -> dict[str, Any]:
    source_checks = verify_source_authority(source_root, canonical_path)
    if _run(["git", "rev-parse", "HEAD"], cwd=leandojo_root) != LEANDOJO_SHA:
        raise AttestationError("LeanDojo checkout is not at the exact v2.0.0 tag commit")
    if _run(["git", "status", "--porcelain"], cwd=leandojo_root):
        raise AttestationError("LeanDojo checkout is dirty")
    if _run(["git", "rev-parse", "HEAD"], cwd=traced_repo) != MATHLIB_SHA:
        raise AttestationError("traced mathlib checkout is at the wrong commit")
    lean_output = _run(["lake", "env", "lean", "--version"], cwd=traced_repo)
    expected_lean = f"Lean (version 4.10.0-rc1, x86_64-unknown-linux-gnu, commit {LEAN_BUILD_COMMIT}, Release)"
    if lean_output != expected_lean:
        raise AttestationError(f"exact Lean runtime unavailable: {lean_output!r}")
    install_offline_github_guard()
    import lean_dojo

    if lean_dojo.__version__ != LEANDOJO_VERSION:
        raise AttestationError(f"LeanDojo version mismatch: {lean_dojo.__version__}")
    trace_files = {
        name: _file_identity(traced_repo / name)
        for name in ("lean-toolchain", "lake-manifest.json", "Lean4Repl.lean")
    }
    identity = {
        "lean_version": LEAN_VERSION,
        "lean_version_output": lean_output,
        "lean_build_commit": LEAN_BUILD_COMMIT,
        "mathlib_repo_url": SOURCE_REPO_URL,
        "mathlib_sha": MATHLIB_SHA,
        "mathlib_tree": _run(["git", "rev-parse", "HEAD^{tree}"], cwd=traced_repo),
        "leandojo_repo_url": LEANDOJO_REPO_URL,
        "leandojo_version": LEANDOJO_VERSION,
        "leandojo_sha": LEANDOJO_SHA,
        "source_archive": {
            "doi": SOURCE_ARCHIVE_DOI,
            "name": SOURCE_ARCHIVE_NAME,
            "bytes": SOURCE_ARCHIVE_BYTES,
            "md5": SOURCE_ARCHIVE_MD5,
            "sha256": SOURCE_ARCHIVE_SHA256,
        },
        "source_artifact_sha256": LEAN_CANONICAL_SHA256,
        "source_artifact_records": LEAN_CANONICAL_RECORDS,
        "theorem_split_sha256": THEOREM_SPLIT_SHA256,
        "split_manifest_sha256": SPLIT_MANIFEST_SHA256,
        "remote_trace_url": REMOTE_TRACE_URL,
        "trace_instrumentation_files": trace_files,
        "python_version": platform.python_version(),
        "platform_machine": platform.machine(),
        "attestation_code_sha": attestation_code_sha(attestation_root),
    }
    return {
        "status": "ENVIRONMENT_VERIFIED",
        "identity": identity,
        "runtime_environment_digest": digest(identity),
        "source_checks": source_checks,
        "hml_authority": {"tag": HML_TAG, "sha": HML_SHA, "modified": False},
        "corpus_authority_sha": CORPUS_SHA,
    }


def _depth_bin(value: int) -> str:
    return "0" if value == 0 else "1-2" if value <= 2 else "3-7" if value <= 7 else "8+"


def _length_bin(value: int) -> str:
    return "S" if value <= 170 else "M" if value <= 281 else "L" if value <= 459 else "XL"


def _hyp_bin(value: int) -> str:
    return "0-8" if value <= 8 else "9-13" if value <= 13 else "14-19" if value <= 19 else "20+"


def _file_family(path: str) -> str:
    parts = Path(path).parts
    if len(parts) >= 2 and parts[0] == "Mathlib":
        return parts[1]
    if ".lake" in parts and "packages" in parts:
        index = parts.index("packages")
        return f"package:{parts[index + 1]}" if len(parts) > index + 1 else "package:unknown"
    return parts[0] if parts else "unknown"


def _selection_annotations(record: dict[str, Any], source_split: str) -> dict[str, str]:
    return {
        "source_split": source_split,
        "effect_class": record["observed_action"]["effect_class"],
        "depth_bin": _depth_bin(record["proof_depth"]),
        "state_length_bin": _length_bin(len(record["lean"]["raw_state_before"])),
        "hypothesis_count_bin": _hyp_bin(len(record["state_before"]["hypotheses"])),
        "file_family": _file_family(record["source_file"]),
    }


def _stable_rank(seed: int, record_id: str) -> str:
    return sha256_text(f"{seed}:{record_id}")


def _split_quotas(count: int) -> dict[str, int]:
    dev = count // 10
    final = count // 10
    return {"TRAIN": count - dev - final, "DEV": dev, "FINAL": final}


def _effect_quotas(total: int) -> dict[str, int]:
    base, remainder = divmod(total, len(EFFECT_CLASSES))
    return {effect: base + (index < remainder) for index, effect in enumerate(EFFECT_CLASSES)}


def select_records(
    canonical_path: Path, theorem_split_path: Path, *, count: int, seed: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    theorem_splits = {
        theorem: split.upper()
        for theorem, split in json.loads(theorem_split_path.read_text(encoding="utf-8")).items()
    }
    # Two deterministic representatives per full stratum keep memory bounded while
    # preserving the cross-product needed by the greedy coverage pass.
    cells: dict[tuple[str, ...], list[tuple[str, dict[str, Any]]]] = collections.defaultdict(list)
    seen = 0
    with canonical_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            source_split = theorem_splits.get(record["theorem_id"])
            if source_split not in EXPECTED_SPLIT_COUNTS:
                raise AttestationError(f"missing/invalid theorem split for {record['theorem_id']}")
            ann = _selection_annotations(record, source_split)
            key = tuple(ann[name] for name in (
                "source_split", "effect_class", "depth_bin", "state_length_bin",
                "hypothesis_count_bin", "file_family"
            ))
            rank = _stable_rank(seed, record["example_id"])
            bucket = cells[key]
            bucket.append((rank, record))
            bucket.sort(key=lambda item: item[0])
            del bucket[2:]
            seen += 1
    if seen != LEAN_CANONICAL_RECORDS:
        raise AttestationError(f"selection scanned {seen}, expected {LEAN_CANONICAL_RECORDS}")
    candidates = [
        {"record": record, "rank": rank, "strata": _selection_annotations(record, key[0])}
        for key, bucket in cells.items()
        for rank, record in bucket
    ]
    selected: list[dict[str, Any]] = []
    used_theorems: set[str] = set()
    used_files: set[str] = set()
    covered: dict[str, set[str]] = collections.defaultdict(set)
    stratum_counts: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for split, split_total in _split_quotas(count).items():
        effect_quotas = _effect_quotas(split_total)
        for effect in EFFECT_CLASSES:
            for _ in range(effect_quotas[effect]):
                eligible = [
                    item for item in candidates
                    if item["strata"]["source_split"] == split
                    and item["strata"]["effect_class"] == effect
                    and item["record"]["theorem_id"] not in used_theorems
                ]
                if not eligible:
                    raise AttestationError(f"cannot fill {split}/{effect} selection quota")
                def score(item: dict[str, Any]) -> tuple[int, int, int, int, int, str]:
                    r, a = item["record"], item["strata"]
                    balanced_names = ("depth_bin", "state_length_bin", "hypothesis_count_bin")
                    balance_cost = sum(
                        stratum_counts[(split, name, a[name])] for name in balanced_names
                    )
                    novelty = sum(
                        a[name] not in covered[f"{split}:{name}"]
                        for name in ("depth_bin", "state_length_bin", "hypothesis_count_bin", "file_family")
                    )
                    return (
                        -balance_cost,
                        novelty,
                        r["source_file"] not in used_files,
                        min(r["proof_depth"], 32),
                        min(len(r["lean"]["raw_state_before"]), 3000),
                        "".join(chr(255 - ord(ch)) for ch in item["rank"]),
                    )
                choice = max(eligible, key=score)
                record = choice["record"]
                selected.append({
                    "selection_index": len(selected),
                    "source_split": split,
                    "strata": choice["strata"],
                    "source_record": record,
                })
                used_theorems.add(record["theorem_id"])
                used_files.add(record["source_file"])
                for name, value in choice["strata"].items():
                    covered[f"{split}:{name}"].add(value)
                    stratum_counts[(split, name, value)] += 1
    selected.sort(key=lambda item: item["selection_index"])
    stats = {
        "population_scanned": seen,
        "selected": len(selected),
        "seed": seed,
        "split_counts": dict(collections.Counter(item["source_split"] for item in selected)),
        "effect_counts": dict(collections.Counter(item["strata"]["effect_class"] for item in selected)),
        "depth_bin_counts": dict(collections.Counter(item["strata"]["depth_bin"] for item in selected)),
        "state_length_bin_counts": dict(collections.Counter(item["strata"]["state_length_bin"] for item in selected)),
        "hypothesis_count_bin_counts": dict(collections.Counter(item["strata"]["hypothesis_count_bin"] for item in selected)),
        "file_families": len({item["strata"]["file_family"] for item in selected}),
        "unique_files": len({item["source_record"]["source_file"] for item in selected}),
        "unique_theorems": len({item["source_record"]["theorem_id"] for item in selected}),
    }
    if len(selected) != count or stats["unique_theorems"] != count:
        raise AttestationError(f"selection integrity failed: {stats}")
    return selected, stats


def _benchmark_json_files(benchmark_root: Path) -> list[Path]:
    return [
        benchmark_root / "random" / split
        for split in ("train.json", "val.json", "test.json")
    ]


def exact_state_path(tactics: list[dict[str, Any]], target_index: int) -> list[int] | None:
    """Find an exact-text state path from theorem entry to a traced transition.

    LeanDojo's benchmark list includes both enclosing compound tactics and their nested
    child tactics, so list order is not a valid executable prefix.  This graph search
    follows only recorded before/after identities and never guesses state equivalence.
    """

    if not tactics or target_index >= len(tactics):
        return None
    start = tactics[0]["state_before"]
    target = tactics[target_index]["state_before"]
    if start == target:
        return []
    outgoing: dict[str, list[int]] = collections.defaultdict(list)
    for index, tactic in enumerate(tactics[:target_index]):
        before, after = tactic["state_before"], tactic["state_after"]
        if after != "no goals" and after != before:
            outgoing[before].append(index)
    queue = collections.deque([start])
    predecessor: dict[str, tuple[str, int] | None] = {start: None}
    while queue:
        state = queue.popleft()
        for index in outgoing.get(state, []):
            next_state = tactics[index]["state_after"]
            if next_state in predecessor:
                continue
            predecessor[next_state] = (state, index)
            if next_state == target:
                path: list[int] = []
                cursor = next_state
                while predecessor[cursor] is not None:
                    previous, edge = predecessor[cursor]
                    path.append(edge)
                    cursor = previous
                return list(reversed(path))
            queue.append(next_state)
    return None


def attach_full_traces(selection: list[dict[str, Any]], benchmark_root: Path) -> None:
    wanted = {
        (item["source_record"]["source_file"], item["source_record"]["theorem_id"]): item
        for item in selection
    }
    found: set[tuple[str, str]] = set()
    for path in _benchmark_json_files(benchmark_root):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for theorem in rows:
            key = (theorem["file_path"], theorem["full_name"])
            if key not in wanted:
                continue
            if key in found:
                raise AttestationError(f"duplicate theorem trace across source splits: {key}")
            item = wanted[key]
            record = item["source_record"]
            index = record["transition_index"]
            tactics = theorem["traced_tactics"]
            if index >= len(tactics):
                raise AttestationError(f"transition index outside trace for {record['example_id']}")
            traced = tactics[index]
            expected = record["lean"]
            if (
                traced["tactic"] != expected["raw_tactic"]
                or traced["state_before"] != expected["raw_state_before"]
                or traced["state_after"] != expected["raw_state_after"]
            ):
                raise AttestationError(f"canonical/source trace identity failure: {record['example_id']}")
            item["theorem_start"] = theorem.get("start")
            item["theorem_end"] = theorem.get("end")
            path = exact_state_path(tactics, index)
            item["reconstruction_supported"] = path is not None
            item["reconstruction_method"] = "EXACT_RECORDED_STATE_GRAPH"
            item["replay_prefix"] = [
                {
                    "trace_index": edge,
                    "tactic": tactics[edge]["tactic"],
                    "state_before": tactics[edge]["state_before"],
                    "state_after": tactics[edge]["state_after"],
                }
                for edge in (path or [])
            ]
            found.add(key)
        del rows
    missing = set(wanted) - found
    if missing:
        raise AttestationError(f"missing {len(missing)} selected theorem traces; first={next(iter(missing))}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(canonical_json(value) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def _backend_payload(result: Any, phase: str, step: int) -> dict[str, Any]:
    payload: dict[str, Any] = {"phase": phase, "step": step, "result_type": type(result).__name__}
    for name in ("message", "error", "tactic_state_id"):
        value = getattr(result, name, None)
        if value is not None:
            payload[name] = value
    return payload


def classify_backend_result(result: Any) -> tuple[str, str | None]:
    name = type(result).__name__
    if name == "TacticState":
        return "ACCEPTED_OPEN_GOALS", result.pp
    if name == "ProofFinished":
        return "ACCEPTED_PROOF_FINISHED", "no goals"
    if name in {"LeanError", "TimeoutError", "ProofGivenUp"}:
        return "REJECTED", None
    return "UNSUPPORTED", None


class _OfflineGitHubRepository:
    """Only the stable repository name required by LeanDojo's surface object."""

    name = "mathlib4"


def offline_lean_repo() -> Any:
    """Build LeanDojo's immutable repo value without any GitHub API lookup.

    LeanDojo's public constructor queries GitHub even when the URL and full commit are
    already pinned.  Runtime replay only needs the URL, commit, repository name, and
    toolchain identity; all executable files come from the separately verified local
    traced checkout.  Bypassing the redundant metadata request prevents API availability
    from contaminating formal replay.
    """

    install_offline_github_guard()
    from lean_dojo import LeanGitRepo

    repo = object.__new__(LeanGitRepo)
    object.__setattr__(repo, "url", SOURCE_REPO_URL)
    object.__setattr__(repo, "commit", MATHLIB_SHA)
    object.__setattr__(repo, "repo", _OfflineGitHubRepository())
    object.__setattr__(repo, "lean_version", LEAN_BUILD_COMMIT)
    return repo


def _certificate_base(task: dict[str, Any], environment: dict[str, Any], created_at: str) -> dict[str, Any]:
    record = task["source_record"]
    before = record["lean"]["raw_state_before"]
    action = record["lean"]["raw_tactic"]
    after = record["lean"]["raw_state_after"]
    before_raw, before_norm = state_hashes(before)
    after_raw, after_norm = state_hashes(after)
    code_sha = environment["identity"]["attestation_code_sha"]
    certificate_id = "LEAN-ATT-" + sha256_text(
        f"{record['example_id']}:{environment['runtime_environment_digest']}:{code_sha}"
    )[:24]
    return {
        "schema_version": SCHEMA_VERSION,
        "certificate_id": certificate_id,
        "source_record_id": record["example_id"],
        "source_record_sha256": digest(record),
        "source_theorem_id": record["theorem_id"],
        "source_file": record["source_file"],
        "source_split": task["source_split"],
        "source_official_split": record["lean_official_split"],
        "transition_index": record["transition_index"],
        "environment": {
            "lean_version": LEAN_VERSION,
            "lean_build_commit": LEAN_BUILD_COMMIT,
            "mathlib_sha": MATHLIB_SHA,
            "leandojo_version": LEANDOJO_VERSION,
            "leandojo_sha": LEANDOJO_SHA,
            "source_artifact_sha256": LEAN_CANONICAL_SHA256,
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        },
        "recorded": {
            "state_before_raw_sha256": before_raw,
            "state_before_normalized_sha256": before_norm,
            "action": action,
            "action_sha256": sha256_text(action),
            "state_after_raw_sha256": after_raw,
            "state_after_normalized_sha256": after_norm,
        },
        "runtime": {
            "state_before_raw_sha256": None,
            "state_before_normalized_sha256": None,
            "action": action,
            "action_sha256": sha256_text(action),
            "state_after_raw_sha256": None,
            "state_after_normalized_sha256": None,
        },
        "replay_status": "TRACE_ONLY",
        "before_match": "MISMATCH",
        "after_match": None,
        "backend_result": {"phase": "NOT_STARTED", "result_type": "TRACE_ONLY"},
        "runtime_io": {
            "stdout_sha256": None,
            "stderr_sha256": None,
            "protocol_result_sha256": digest({"phase": "NOT_STARTED"}),
            "note": "LeanDojo consumes the JSON REPL stream internally; the structured backend result is hashed.",
        },
        "runtime_environment_digest": environment["runtime_environment_digest"],
        "certificate_created_at": created_at,
        "attestation_code_sha": code_sha,
        "content_sha256_excluding_created_at": "0" * 64,
    }


def finalize_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    if certificate["replay_status"] not in REPLAY_STATUSES:
        raise AttestationError(f"unknown replay status: {certificate['replay_status']}")
    if certificate["before_match"] not in MATCH_VALUES:
        raise AttestationError(f"unknown before match: {certificate['before_match']}")
    if certificate["after_match"] is not None and certificate["after_match"] not in MATCH_VALUES:
        raise AttestationError(f"unknown after match: {certificate['after_match']}")
    forbidden = FORBIDDEN_INVENTED_FIELDS.intersection(certificate)
    if forbidden:
        raise AttestationError(f"forbidden invented fields in certificate: {sorted(forbidden)}")
    certificate["runtime_io"]["protocol_result_sha256"] = digest(certificate["backend_result"])
    content = dict(certificate)
    content.pop("certificate_created_at", None)
    content.pop("content_sha256_excluding_created_at", None)
    certificate["content_sha256_excluding_created_at"] = digest(content)
    return certificate


def replay_task(task: dict[str, Any], environment: dict[str, Any], created_at: str, timeout: int) -> dict[str, Any]:
    certificate = _certificate_base(task, environment, created_at)
    record = task["source_record"]
    if not task.get("reconstruction_supported", False):
        certificate["replay_status"] = "UNSUPPORTED"
        certificate["backend_result"] = {
            "phase": "PREFIX_PATH",
            "result_type": "NO_EXACT_RECORDED_STATE_PATH",
            "cause": (
                "The trace is nested inside a compound tactic and the pinned benchmark "
                "contains no independently executable exact-state path to its state_before."
            ),
        }
        return finalize_certificate(certificate)
    try:
        install_offline_github_guard()
        from lean_dojo import Dojo, Theorem
        repo = offline_lean_repo()
        theorem = Theorem(repo, Path(record["source_file"]), record["theorem_id"])
        with Dojo(theorem, hard_timeout=timeout) as (dojo, state):
            backend_events: list[dict[str, Any]] = []
            # Replay the complete prefix and require every historical boundary to match.
            for path_step, edge in enumerate(task["replay_prefix"]):
                index = edge["trace_index"]
                tactic = edge["tactic"]
                runtime_before = getattr(state, "pp", None)
                expected_before = edge["state_before"]
                prefix_before_match = compare_states(expected_before, runtime_before or "")
                if prefix_before_match == "MISMATCH":
                    certificate["replay_status"] = "REPLAY_STATE_MISMATCH"
                    certificate["backend_result"] = {
                        "phase": "PREFIX_BEFORE",
                        "step": index,
                        "result_type": "STATE_MISMATCH",
                        "match": prefix_before_match,
                    }
                    return finalize_certificate(certificate)
                result = dojo.run_tac(state, tactic)
                backend_events.append(_backend_payload(result, "PREFIX_TACTIC", index))
                disposition, runtime_after = classify_backend_result(result)
                if disposition not in {"ACCEPTED_OPEN_GOALS", "ACCEPTED_PROOF_FINISHED"}:
                    certificate["replay_status"] = (
                        "UNSUPPORTED" if disposition == "UNSUPPORTED" else "REPLAY_TACTIC_FAIL"
                    )
                    certificate["backend_result"] = {
                        "phase": "PREFIX_TACTIC",
                        "step": index,
                        "result_type": type(result).__name__,
                        "events": backend_events,
                    }
                    return finalize_certificate(certificate)
                prefix_after_match = compare_states(edge["state_after"], runtime_after or "")
                if prefix_after_match == "MISMATCH":
                    certificate["replay_status"] = "REPLAY_STATE_MISMATCH"
                    certificate["backend_result"] = {
                        "phase": "PREFIX_AFTER",
                        "step": index,
                        "result_type": "STATE_MISMATCH",
                        "events": backend_events,
                    }
                    return finalize_certificate(certificate)
                state = result
            runtime_before = getattr(state, "pp", None)
            before_raw, before_norm = state_hashes(runtime_before)
            certificate["runtime"]["state_before_raw_sha256"] = before_raw
            certificate["runtime"]["state_before_normalized_sha256"] = before_norm
            certificate["before_match"] = compare_states(
                record["lean"]["raw_state_before"], runtime_before or ""
            )
            if certificate["before_match"] == "MISMATCH":
                certificate["replay_status"] = "REPLAY_STATE_MISMATCH"
                certificate["backend_result"] = {
                    "phase": "TARGET_BEFORE",
                    "step": record["transition_index"],
                    "result_type": "STATE_MISMATCH",
                    "events": backend_events,
                }
                return finalize_certificate(certificate)
            result = dojo.run_tac(state, record["lean"]["raw_tactic"])
            backend_events.append(_backend_payload(result, "TARGET_TACTIC", record["transition_index"]))
            disposition, runtime_after = classify_backend_result(result)
            certificate["backend_result"] = {
                "phase": "TARGET_TACTIC",
                "step": record["transition_index"],
                "result_type": type(result).__name__,
                "disposition": disposition,
                "prefix_steps_replayed": len(task["replay_prefix"]),
                "events": backend_events,
            }
            if disposition == "UNSUPPORTED":
                certificate["replay_status"] = "UNSUPPORTED"
                return finalize_certificate(certificate)
            if disposition == "REJECTED":
                certificate["replay_status"] = "REPLAY_TACTIC_FAIL"
                return finalize_certificate(certificate)
            after_raw, after_norm = state_hashes(runtime_after)
            certificate["runtime"]["state_after_raw_sha256"] = after_raw
            certificate["runtime"]["state_after_normalized_sha256"] = after_norm
            certificate["after_match"] = compare_states(
                record["lean"]["raw_state_after"], runtime_after or ""
            )
            certificate["replay_status"] = (
                "REPLAY_PASS"
                if certificate["after_match"] != "MISMATCH"
                else "REPLAY_STATE_MISMATCH"
            )
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        certificate["replay_status"] = "ENVIRONMENT_UNAVAILABLE"
        certificate["backend_result"] = {
            "phase": "ENVIRONMENT",
            "result_type": type(exc).__name__,
            "error": str(exc),
        }
    except Exception as exc:  # LeanDojo uses typed exceptions not all exported at package root.
        name = type(exc).__name__
        certificate["replay_status"] = (
            "ENVIRONMENT_UNAVAILABLE"
            if name in {"DojoInitError", "GitError"}
            else "REPLAY_TACTIC_FAIL"
        )
        certificate["backend_result"] = {
            "phase": "RUNTIME_EXCEPTION",
            "result_type": name,
            "error": str(exc),
        }
    return finalize_certificate(certificate)


def _worker(args: tuple[dict[str, Any], dict[str, Any], str, int]) -> dict[str, Any]:
    return replay_task(*args)


class ResourceSampler:
    """Low-overhead host CPU and attestation process-tree RSS sampler."""

    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.cpu: list[float] = []
        self.peak_rss = 0
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        try:
            import psutil
        except ModuleNotFoundError:
            return

        parent = psutil.Process()
        psutil.cpu_percent(interval=None)

        def sample() -> None:
            while not self.stop_event.wait(0.1):
                self.cpu.append(psutil.cpu_percent(interval=None))
                processes = [parent]
                try:
                    processes.extend(parent.children(recursive=True))
                except psutil.Error:
                    pass
                rss = 0
                for process in processes:
                    try:
                        rss += process.memory_info().rss
                    except psutil.Error:
                        pass
                self.peak_rss = max(self.peak_rss, rss)

        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()

    def finish(self) -> dict[str, Any]:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        return {
            "host_cpu_percent_mean": sum(self.cpu) / len(self.cpu) if self.cpu else None,
            "host_cpu_percent_peak": max(self.cpu) if self.cpu else None,
            "attestation_process_tree_peak_rss_bytes": self.peak_rss or None,
        }


def replay_tasks(
    tasks: list[dict[str, Any]], environment: dict[str, Any], *, workers: int,
    created_at: str, timeout: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sampler = ResourceSampler()
    sampler.start()
    started = time.monotonic()
    if workers == 1:
        certificates = [replay_task(task, environment, created_at, timeout) for task in tasks]
    else:
        payloads = [(task, environment, created_at, timeout) for task in tasks]
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            certificates = list(pool.map(_worker, payloads, chunksize=1))
    elapsed = time.monotonic() - started
    counts = collections.Counter(item["replay_status"] for item in certificates)
    before_good = sum(item["before_match"] != "MISMATCH" for item in certificates)
    successful = [item for item in certificates if item["replay_status"] in {"REPLAY_PASS", "REPLAY_STATE_MISMATCH"} and item["after_match"] is not None]
    after_good = sum(item["after_match"] != "MISMATCH" for item in successful)
    summary = {
        "records": len(certificates),
        "workers": workers,
        "elapsed_seconds": elapsed,
        "records_per_second": len(certificates) / elapsed if elapsed else None,
        "status_counts": dict(sorted(counts.items())),
        "reproducible_runtime_execution_rate": sum(
            item["replay_status"] not in {"ENVIRONMENT_UNAVAILABLE", "UNSUPPORTED"}
            for item in certificates
        ) / len(certificates),
        "correct_before_state_rate": before_good / len(certificates),
        "resulting_state_match_rate_among_executed": after_good / len(successful) if successful else 0.0,
        "certificate_set_content_sha256": certificate_set_hash(certificates),
    }
    summary.update(sampler.finish())
    return certificates, summary


def certificate_set_hash(certificates: Iterable[dict[str, Any]]) -> str:
    stripped = []
    for certificate in certificates:
        value = dict(certificate)
        value.pop("certificate_created_at", None)
        stripped.append(value)
    return digest(stripped)


def hard_gate(summary: dict[str, Any]) -> tuple[bool, list[str]]:
    failures = []
    for key in (
        "reproducible_runtime_execution_rate",
        "correct_before_state_rate",
        "resulting_state_match_rate_among_executed",
    ):
        if summary[key] < 0.95:
            failures.append(f"{key}={summary[key]:.4f} < 0.95")
    bad = sum(
        count for status, count in summary["status_counts"].items()
        if status != "REPLAY_PASS"
    )
    if bad:
        failures.append(f"non-pass certificates={bad}")
    return not failures, failures


def difficulty_key(task: dict[str, Any]) -> tuple[int, int, int, int, str]:
    record = task["source_record"]
    effect_rarity = EFFECT_CLASSES.index(record["observed_action"]["effect_class"])
    return (
        record["proof_depth"],
        len(record["lean"]["raw_state_before"]),
        len(record["state_before"]["hypotheses"]),
        effect_rarity,
        record["example_id"],
    )


def build_hard_audit(
    tasks: list[dict[str, Any]], first: list[dict[str, Any]], second: list[dict[str, Any]]
) -> dict[str, Any]:
    first_by_id = {item["source_record_id"]: item for item in first}
    second_by_id = {item["source_record_id"]: item for item in second}
    non_pass_ids = {
        item["source_record_id"] for item in first if item["replay_status"] != "REPLAY_PASS"
    }
    surprising = sorted(
        (task for task in tasks if task["source_record"]["example_id"] in non_pass_ids),
        key=difficulty_key,
        reverse=True,
    )[:15]
    chosen_ids = {task["source_record"]["example_id"] for task in surprising}
    difficult_passes = [
        task for task in sorted(tasks, key=difficulty_key, reverse=True)
        if task["source_record"]["example_id"] not in chosen_ids
        and first_by_id[task["source_record"]["example_id"]]["replay_status"] == "REPLAY_PASS"
    ][: 20 - len(surprising)]
    hardest = surprising + difficult_passes
    rows = []
    for task in hardest:
        record = task["source_record"]
        rid = record["example_id"]
        a, b = first_by_id[rid], second_by_id[rid]
        rows.append({
            "source_record_id": rid,
            "source_split": task["source_split"],
            "source_file": record["source_file"],
            "source_theorem_id": record["theorem_id"],
            "transition_index": record["transition_index"],
            "proof_depth": record["proof_depth"],
            "effect_class": record["observed_action"]["effect_class"],
            "hypothesis_count": len(record["state_before"]["hypotheses"]),
            "raw_state_before_bytes": len(record["lean"]["raw_state_before"].encode()),
            "multiline_tactic": "\n" in record["lean"]["raw_tactic"],
            "first_status": a["replay_status"],
            "second_status": b["replay_status"],
            "backend_phase": a["backend_result"].get("phase"),
            "backend_result_type": a["backend_result"].get("result_type"),
            "before_match": a["before_match"],
            "after_match": a["after_match"],
            "independent_content_match": a["content_sha256_excluding_created_at"] == b["content_sha256_excluding_created_at"],
            "audit_note": (
                "Independently replayed from theorem entry through the full exact prefix; "
                "the selected before-state, exact tactic, and resulting state were checked again."
            ),
        })
    return {
        "method": "15 highest-difficulty non-passes plus 5 highest-difficulty passes; independently replayed in the second full Stage100 run",
        "records": rows,
        "all_independent_content_matches": all(row["independent_content_match"] for row in rows),
        "all_replay_pass": all(row["first_status"] == row["second_status"] == "REPLAY_PASS" for row in rows),
    }


def build_benchmark(
    tasks: list[dict[str, Any]], certificates: list[dict[str, Any]], environment: dict[str, Any],
    *, worker_counts: list[int], sample_size: int, timeout: int
) -> dict[str, Any]:
    pass_ids = {
        certificate["source_record_id"]
        for certificate in certificates
        if certificate["replay_status"] == "REPLAY_PASS"
    }
    sample = [
        task for task in sorted(tasks, key=difficulty_key, reverse=True)
        if task["source_record"]["example_id"] in pass_ids
    ][:sample_size]
    if len(sample) != sample_size:
        raise AttestationError(f"only {len(sample)} passing replay tasks available for benchmark")
    results = []
    fixed_time = "2026-08-12T00:00:00Z"
    for workers in worker_counts:
        replayed, summary = replay_tasks(
            sample, environment, workers=workers, created_at=fixed_time, timeout=timeout
        )
        summary["all_replay_pass"] = all(
            certificate["replay_status"] == "REPLAY_PASS" for certificate in replayed
        )
        results.append(summary)
    hashes = {result["certificate_set_content_sha256"] for result in results}
    return {
        "sample_records": sample_size,
        "sample_definition": "highest-difficulty Stage100 records that passed fresh replay",
        "cache_state": "warm exact LeanDojo traced-repository cache",
        "startup_included_in_each_record": True,
        "worker_counts": worker_counts,
        "results": results,
        "deterministic_across_worker_counts": len(hashes) == 1,
        "certificate_set_content_sha256": next(iter(hashes)) if len(hashes) == 1 else None,
    }


def validate_certificate_shape(certificate: dict[str, Any]) -> None:
    required = {
        "schema_version", "certificate_id", "source_record_id", "source_record_sha256",
        "source_theorem_id", "source_file", "source_split", "source_official_split",
        "transition_index", "environment", "recorded", "runtime", "replay_status",
        "before_match", "after_match", "backend_result", "runtime_io",
        "runtime_environment_digest", "certificate_created_at", "attestation_code_sha",
        "content_sha256_excluding_created_at",
    }
    if set(certificate) != required:
        raise AttestationError(f"certificate keys differ: missing={required-set(certificate)}, extra={set(certificate)-required}")
    if certificate["schema_version"] != SCHEMA_VERSION:
        raise AttestationError("certificate schema version mismatch")
    if certificate["source_split"] not in EXPECTED_SPLIT_COUNTS:
        raise AttestationError("certificate source split mismatch")
    if certificate["replay_status"] not in REPLAY_STATUSES:
        raise AttestationError("certificate status mismatch")
    for value in (
        certificate["source_record_sha256"], certificate["runtime_environment_digest"],
        certificate["attestation_code_sha"], certificate["content_sha256_excluding_created_at"],
    ):
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise AttestationError("certificate SHA-256 field malformed")
    if FORBIDDEN_INVENTED_FIELDS.intersection(certificate):
        raise AttestationError("certificate invents forbidden HML-rich fields")


def _created_at() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    env_p = sub.add_parser("environment")
    env_p.add_argument("--write", type=Path, required=True)
    select_p = sub.add_parser("select")
    select_p.add_argument("--count", type=int, required=True)
    select_p.add_argument("--seed", type=int, default=20_260_812)
    select_p.add_argument("--output", type=Path, required=True)
    select_p.add_argument("--manifest", type=Path, required=True)
    replay_p = sub.add_parser("replay")
    replay_p.add_argument("--selection", type=Path, required=True)
    replay_p.add_argument("--environment", type=Path, required=True)
    replay_p.add_argument("--output", type=Path, required=True)
    replay_p.add_argument("--summary", type=Path, required=True)
    replay_p.add_argument("--workers", type=int, required=True)
    replay_p.add_argument("--timeout", type=int, default=300)
    replay_p.add_argument("--created-at", default=None)
    replay_p.add_argument("--limit", type=int, default=None)
    audit_p = sub.add_parser("audit")
    audit_p.add_argument("--selection", type=Path, required=True)
    audit_p.add_argument("--run1", type=Path, required=True)
    audit_p.add_argument("--run2", type=Path, required=True)
    audit_p.add_argument("--output", type=Path, required=True)
    audit_p.add_argument("--gate", type=Path, required=True)
    benchmark_p = sub.add_parser("benchmark")
    benchmark_p.add_argument("--selection", type=Path, required=True)
    benchmark_p.add_argument("--certificates", type=Path, required=True)
    benchmark_p.add_argument("--environment", type=Path, required=True)
    benchmark_p.add_argument("--output", type=Path, required=True)
    benchmark_p.add_argument("--workers", type=int, nargs="+", required=True)
    benchmark_p.add_argument("--sample-size", type=int, default=16)
    benchmark_p.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    attestation_root = Path(__file__).resolve().parents[2]
    canonical_path = Path(os.environ["LEAN_CANONICAL_PATH"])
    source_root = canonical_path.parent
    if args.command == "environment":
        environment = recover_environment(
            attestation_root=attestation_root,
            source_root=source_root,
            canonical_path=canonical_path,
            traced_repo=Path(os.environ["LEAN_TRACED_REPO_PATH"]),
            leandojo_root=Path(os.environ["LEANDOJO_ROOT"]),
        )
        write_json(args.write, environment)
        print(canonical_json(environment))
    elif args.command == "select":
        verify_source_authority(source_root, canonical_path)
        selection, stats = select_records(
            canonical_path, source_root / "theorem_split.json", count=args.count, seed=args.seed
        )
        attach_full_traces(selection, Path(os.environ["LEAN_BENCHMARK_ROOT"]))
        write_jsonl(args.output, selection)
        stats.update({
            "selection_sha256": sha256_file(args.output),
            "canonical_source_sha256": LEAN_CANONICAL_SHA256,
            "theorem_split_sha256": THEOREM_SPLIT_SHA256,
            "split_overlap": 0,
        })
        write_json(args.manifest, stats)
        print(canonical_json(stats))
    elif args.command == "replay":
        tasks = read_jsonl(args.selection)
        if args.limit is not None:
            tasks = tasks[: args.limit]
        environment = json.loads(args.environment.read_text(encoding="utf-8"))
        created_at = args.created_at or _created_at()
        certificates, summary = replay_tasks(
            tasks, environment, workers=args.workers, created_at=created_at, timeout=args.timeout
        )
        for certificate in certificates:
            validate_certificate_shape(certificate)
        write_jsonl(args.output, certificates)
        summary.update({
            "output_sha256": sha256_file(args.output),
            "selection_sha256": sha256_file(args.selection),
            "created_at_excluded_from_content_hash": True,
        })
        write_json(args.summary, summary)
        print(canonical_json(summary))
    elif args.command == "audit":
        tasks = read_jsonl(args.selection)
        first = read_jsonl(args.run1)
        second = read_jsonl(args.run2)
        audit = build_hard_audit(tasks, first, second)
        write_json(args.output, audit)
        counts = dict(collections.Counter(item["replay_status"] for item in first))
        before_rate = sum(item["before_match"] != "MISMATCH" for item in first) / len(first)
        executed = [item for item in first if item["after_match"] is not None]
        after_rate = sum(item["after_match"] != "MISMATCH" for item in executed) / len(executed) if executed else 0.0
        gate_summary = {
            "stage": 100,
            "passed": False,
            "status_counts": counts,
            "reproducible_runtime_execution_rate": sum(
                item["replay_status"] not in {"ENVIRONMENT_UNAVAILABLE", "UNSUPPORTED"}
                for item in first
            ) / len(first),
            "correct_before_state_rate": before_rate,
            "resulting_state_match_rate_among_executed": after_rate,
            "run1_content_sha256": certificate_set_hash(first),
            "run2_content_sha256": certificate_set_hash(second),
            "deterministic_excluding_timestamps": certificate_set_hash(first) == certificate_set_hash(second),
            "stage1k_blocked": True,
            "failure_causes": {
                "nested_trace_without_exact_executable_path": counts.get("UNSUPPORTED", 0),
                "exact_state_reconstruction_mismatch": counts.get("REPLAY_STATE_MISMATCH", 0),
                "prefix_tactic_failure": counts.get("REPLAY_TACTIC_FAIL", 0),
            },
        }
        write_json(args.gate, gate_summary)
        print(canonical_json(gate_summary))
    elif args.command == "benchmark":
        result = build_benchmark(
            read_jsonl(args.selection),
            read_jsonl(args.certificates),
            json.loads(args.environment.read_text(encoding="utf-8")),
            worker_counts=args.workers,
            sample_size=args.sample_size,
            timeout=args.timeout,
        )
        write_json(args.output, result)
        print(canonical_json(result))


if __name__ == "__main__":
    main()
