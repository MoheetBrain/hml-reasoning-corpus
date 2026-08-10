#!/usr/bin/env python3
"""Reproduce the compact quantitative MiniLang artifact audit.

The script reads the selectively extracted translation corpus and SqliteDict
database without importing the artifact's Python environment. SqliteDict values
are ordinary pickle blobs, so the standard library is sufficient.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import os
import pickle
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


PUBLIC_COMMANDS = (
    "HAVE",
    "CONSIDER",
    "RULE",
    "CHOOSE",
    "SIMP",
    "CASE_SPLIT",
    "INDUCT",
    "END",
    "NEXT",
    "INTRO",
)

IMPLEMENTED_COMMANDS = (
    "END", "NEXT", "CONSIDER", "HAVE", "CASE_SPLIT", "INDUCT", "SIMP",
    "CRUSH", "INTRO", "ALL_INTRO", "HAMMER", "PRINT", "RULE", "LET",
    "APPLY", "UNFOLD", "CHOOSE", "NOTATION", "OPEN_MODULE", "DEFINE",
    "CONFIG", "STEP",
)

COMMAND_RE = re.compile(
    r"^\s*(" + "|".join(sorted(IMPLEMENTED_COMMANDS, key=len, reverse=True)) + r")\b"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            h.update(block)
    return h.hexdigest()


def md5_file(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            h.update(block)
    return h.hexdigest()


def dump_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def quantiles(values: list[int]) -> dict[str, float]:
    if not values:
        return {}
    vals = sorted(values)

    def q(p: float) -> float:
        pos = (len(vals) - 1) * p
        lo, hi = math.floor(pos), math.ceil(pos)
        if lo == hi:
            return float(vals[lo])
        return vals[lo] * (hi - pos) + vals[hi] * (pos - lo)

    return {
        "min": float(vals[0]),
        "p25": q(0.25),
        "median": q(0.5),
        "p75": q(0.75),
        "p90": q(0.9),
        "p95": q(0.95),
        "p99": q(0.99),
        "max": float(vals[-1]),
        "mean": sum(vals) / len(vals),
    }


def command_sequence(script: str) -> list[str]:
    sequence: list[str] = []
    for line in script.splitlines():
        if line.lstrip().startswith("(*"):
            continue
        match = COMMAND_RE.match(line)
        if match:
            sequence.append(match.group(1))
    return sequence


def session_of(file_name: str) -> str:
    match = re.search(r"/thys/([^/]+)", file_name)
    if match:
        return "AFP/" + match.group(1)
    match = re.search(r"/src/([^/]+)", file_name)
    if match:
        return "Isabelle/" + match.group(1)
    return "other"


def premise_hint_count(command_line: str) -> int:
    """Lexical lower-bound proxy, not a theorem-dependency count."""
    if " WITH " not in command_line:
        return 0
    tail = command_line.split(" WITH ", 1)[1].split(" WITHOUT ", 1)[0]
    return len([token for token in tail.split() if token])


def depth_proxy(script: str) -> int:
    """Lower-bound lexical block depth from HAVE/CONSIDER indentation.

    The JSONL is a printer rendering, not the proof tree. Leading indentation is
    nevertheless produced from the nested ``mast`` AST, so it gives a reproducible
    lower-bound proxy. Exact state-tree depth requires interpreter replay.
    """
    depths = []
    for line in script.splitlines():
        if line.lstrip().startswith("(*") or not COMMAND_RE.match(line):
            continue
        depths.append((len(line) - len(line.lstrip(" "))) // 2)
    return max(depths, default=0)


def ngram_rows(counter: collections.Counter[tuple[str, ...]], limit: int = 30) -> list[dict[str, Any]]:
    return [
        {"sequence": list(sequence), "count": count}
        for sequence, count in counter.most_common(limit)
    ]


def analyse_operations(jsonl_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    op_counts: collections.Counter[str] = collections.Counter()
    bigrams: collections.Counter[tuple[str, ...]] = collections.Counter()
    trigrams: collections.Counter[tuple[str, ...]] = collections.Counter()
    sessions: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    lengths: list[int] = []
    character_lengths: list[int] = []
    depths: list[int] = []
    premise_fanins: list[int] = []
    structural = collections.Counter()
    consider_modes = collections.Counter()
    records: list[dict[str, Any]] = []

    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            script = row["translation"]
            sequence = command_sequence(script)
            lengths.append(len(sequence))
            character_lengths.append(len(script))
            depths.append(depth_proxy(script))
            op_counts.update(sequence)
            session = session_of(row["file"])
            sessions[session].update(sequence)
            bigrams.update(zip(sequence, sequence[1:]))
            trigrams.update(zip(sequence, sequence[1:], sequence[2:]))
            structural["proofs_with_NEXT"] += "NEXT" in sequence
            structural["proofs_with_INDUCT"] += "INDUCT" in sequence
            structural["proofs_with_CASE_SPLIT"] += "CASE_SPLIT" in sequence
            structural["proofs_with_CONSIDER"] += "CONSIDER" in sequence
            structural["proofs_with_HAVE"] += "HAVE" in sequence
            structural["NEXT_commands"] += sequence.count("NEXT")
            structural["proofs_exactly_END"] += sequence == ["END"]
            structural["proofs_exactly_NEXT"] += sequence == ["NEXT"]
            structural["proofs_with_escape_hatch"] += any(
                command not in PUBLIC_COMMANDS for command in sequence
            )
            structural["subgoal_refinement_commands"] += sum(
                sequence.count(name)
                for name in ("HAVE", "CONSIDER", "RULE", "CASE_SPLIT", "INDUCT")
            )
            for cmd_line in script.splitlines():
                command_match = COMMAND_RE.match(cmd_line)
                if command_match:
                    premise_fanins.append(premise_hint_count(cmd_line))
                    if command_match.group(1) == "CONSIDER":
                        if " | " in cmd_line:
                            consider_modes["CONSIDER_disjunctive_or_mixed"] += 1
                        elif " where " in cmd_line:
                            consider_modes["CONSIDER_single_existential"] += 1
                        else:
                            consider_modes["CONSIDER_single_clause_ambiguous"] += 1
            records.append({
                "file": row["file"],
                "decl_line": row["decl_line"],
                "proof_line": row["proof_line"],
                "translation": script,
                "operations": sequence,
                "operation_count": len(sequence),
                "depth_proxy": depths[-1],
            })

    total_ops = sum(op_counts.values())
    entropy = -sum(
        (count / total_ops) * math.log2(count / total_ops)
        for count in op_counts.values()
    )
    ranked = op_counts.most_common()
    public_counts = collections.Counter({name: op_counts[name] for name in PUBLIC_COMMANDS})
    escape_counts = op_counts - public_counts
    semantic_family_counts = public_counts.copy()
    semantic_family_counts["END_OR_NEXT"] = semantic_family_counts.pop("END") + semantic_family_counts.pop("NEXT")
    semantic_family_counts.pop("CONSIDER")
    semantic_family_counts.update(consider_modes)

    def ranked_coverage(counter: collections.Counter[str], k: int) -> float:
        denominator = sum(counter.values())
        return sum(value for _, value in counter.most_common(k)) / denominator

    def coverage(k: int) -> float:
        return sum(count for _, count in ranked[:k]) / total_ops

    session_rows = []
    for session, counts in sorted(sessions.items(), key=lambda item: sum(item[1].values()), reverse=True):
        session_rows.append({
            "session": session,
            "operation_count": sum(counts.values()),
            "operation_frequencies": dict(counts.most_common()),
        })

    result = {
        "source_file": str(jsonl_path),
        "translated_proof_count": len(records),
        "total_serialized_commands": total_ops,
        "unique_implemented_command_labels_observed": len(op_counts),
        "operation_frequencies": dict(ranked),
        "paper_surface_command_frequencies": dict(public_counts.most_common()),
        "pragmatic_escape_hatch_frequencies": dict(escape_counts.most_common()),
        "paper_semantic_family_frequency_proxy": dict(semantic_family_counts.most_common()),
        "paper_semantic_family_coverage_proxy": {
            f"top_{k}": ranked_coverage(semantic_family_counts, k)
            for k in (1, 3, 5, 10)
        },
        "coverage": {f"top_{k}": coverage(k) for k in (1, 3, 5, 10)},
        "shannon_entropy_bits_per_command": entropy,
        "effective_operation_perplexity": 2 ** entropy,
        "operations_per_proof": quantiles(lengths),
        "translation_characters_per_proof": quantiles(character_lengths),
        "premise_hint_lexical_fanin": quantiles(premise_fanins),
        "nesting_depth_proxy": {
            **quantiles(depths),
            "interpretation": (
                "Printer indentation from the nested translator mast AST; a reproducible lower-bound proxy. "
                "Exact interpreter proof-tree depth requires replay and is not claimed."
            ),
        },
        "structural_event_counts": dict(structural),
        "top_bigrams": ngram_rows(bigrams),
        "top_trigrams": ngram_rows(trigrams),
        "rare_operation_tail": [
            {"operation": name, "count": count, "share": count / total_ops}
            for name, count in reversed(ranked)
            if count / total_ops < 0.001
        ],
        "top_sessions": session_rows[:30],
        "measurement_caveats": [
            "The corpus command labels include pragmatic escape hatches beyond the paper's ten semantic operations.",
            "Command counts are not mathematical-transition counts and are not directly comparable to Gold-125 annotation units.",
            "WITH-token counts are lexical premise-hint proxies, not certified dependency fan-in.",
            "Subgoal and branch effects are only structurally characterized without replaying 290,185 proofs.",
        ],
    }
    return result, records


FAILURE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("unsupported Isar syntax", ("unsupported bracket", "unsupported \"text_raw\"", "outer syntax", "bad source")),
    ("unsupported semantic operation", ("unsupported \"nitpick\"", "unsupported \"refute\"", "unsupported \"quickcheck\"", "unsupported \"@proof\"", "unsupported \"applys\"")),
    ("nested scope/context", ("assume: variables", "duplicate fixed variable", "no such variable", "obtained context", "illegal application of proof command")),
    ("branch/case machinery", ("subgoal is not paired", "bug case", "undefined case", "case qualifier", "cases'", "too many parameters for case", "goal_cases", "incorrect number of vars")),
    ("theorem/premise machinery", ("undefined fact", "cannot parse the `that` fact", "bad fact selection", "no current facts", "calculation", "no unifiers", "failed to retrieve literal fact")),
    ("locale/context machinery", ("undefined locale", "open_module", "locale")),
    ("induction", ("nominal_induct", "induct rule", "induction")),
    ("automation/tactic interaction", ("proof obligation fails", "prf_fail", "fail to apply the tactic", "fail to apply the rules", "failed to refine", "found ?")),
    ("timeout/resource failure", ("timeout", "timed out", "exceeds window", "resource")),
    ("malformed source", ("inner lexical error", "inner syntax error", "ill-typed", "type unification failed", "ambiguous input")),
    ("implementation bug", ("bug", "subscript", "option raised", "match raised", "unequallengths", "oneshot_already_set", "cterm raised", "term raised", "thm 0 raised", "thm 1 raised")),
    ("parser/translator limitation", ("parse_fail", "scan.ml", "bad_source", "print_prop", "fail to print type", "unsupported")),
)


def classify_failure(error: Any) -> str:
    text = " | ".join(str(item) for item in error) if isinstance(error, (list, tuple)) else str(error)
    lowered = text.lower()
    for label, needles in FAILURE_RULES:
        if any(needle in lowered for needle in needles):
            return label
    return "unresolved"


def semantic_assessment(category: str) -> tuple[str, str]:
    if category == "unsupported semantic operation":
        return (
            "ambiguous_not_demonstrated",
            "The rejected source command may be non-proof testing/search or may be replaceable by an escape hatch/backend; failure alone does not establish missing Minilang denotation.",
        )
    if category in {"branch/case machinery", "nested scope/context", "induction"}:
        return (
            "possible_model_or_implementation_boundary",
            "These cases touch genuine proof-state structure, but observed diagnostics arise in the translator/interpreter implementation and require source-level adjudication before calling them semantic gaps.",
        )
    return (
        "translator_or_backend_limitation",
        "The diagnostic concerns translation, replay, surface terms, fact lookup, automation, resources, or an implementation exception rather than an absent semantic transition schema.",
    )


def database_key(file_name: str, line: str, category: str) -> str:
    return f"{file_name}:{line}:{category}"


def analyse_failures(db_path: Path, sample_per_class: int = 12) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, tuple[Any, ...]]]:
    connection = sqlite3.connect(db_path)
    category_totals: collections.Counter[str] = collections.Counter()
    category_successes: collections.Counter[str] = collections.Counter()
    category_failures: collections.Counter[str] = collections.Counter()
    failure_taxonomy: collections.Counter[str] = collections.Counter()
    samples: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)

    for key, blob in connection.execute("SELECT key, value FROM unnamed"):
        category = key.rsplit(":", 1)[-1]
        value = pickle.loads(blob)
        category_totals[category] += 1
        error = value[1]
        if error:
            category_failures[category] += 1
        else:
            category_successes[category] += 1
        if category == "refined" and error:
            taxon = classify_failure(error)
            failure_taxonomy[taxon] += 1
            if len(samples[taxon]) < sample_per_class:
                identifier = key[: -len(":refined")]
                assessment, reason = semantic_assessment(taxon)
                sample = {
                    "identifier": identifier,
                    "category": taxon,
                    "error": error,
                    "semantic_model_assessment": assessment,
                    "assessment_reason": reason,
                    "original_isar": None,
                }
                samples[taxon].append(sample)

    for group in samples.values():
        for sample in group:
            found = connection.execute(
                "SELECT value FROM unnamed WHERE key=?",
                (sample["identifier"] + ":origin",),
            ).fetchone()
            sample["original_isar"] = pickle.loads(found[0])[0] if found else None
            sample["provenance_sha256"] = sha256_bytes(
                json.dumps(sample, sort_keys=True, default=str).encode("utf-8")
            )

    origin_count = category_totals["origin"]
    refined_success = category_successes["refined"]
    refined_failures = category_failures["refined"]
    missing_refined = origin_count - category_totals["refined"]
    missing_samples = []
    if missing_refined:
        query = """
            SELECT o.key, o.value
            FROM unnamed AS o
            LEFT JOIN unnamed AS r
              ON r.key = substr(o.key, 1, length(o.key)-length(':origin')) || ':refined'
            WHERE o.key LIKE '%:origin' AND r.key IS NULL
            LIMIT ?
        """
        for key, blob in connection.execute(query, (sample_per_class,)):
            value = pickle.loads(blob)
            sample = {
                "identifier": key[: -len(":origin")],
                "category": "unresolved_no_refined_record",
                "error": None,
                "semantic_model_assessment": "unresolved",
                "assessment_reason": "No refined row exists, so the artifact supplies no goal-level failure diagnostic.",
                "original_isar": value[0],
            }
            sample["provenance_sha256"] = sha256_bytes(json.dumps(sample, sort_keys=True).encode())
            missing_samples.append(sample)

    all_samples = [item for group in samples.values() for item in group] + missing_samples
    result = {
        "database": str(db_path),
        "database_sha256": sha256_file(db_path),
        "row_count": sum(category_totals.values()),
        "rows_by_category": dict(category_totals.most_common()),
        "successes_by_category": dict(category_successes.most_common()),
        "failures_by_category": dict(category_failures.most_common()),
        "source_goal_count": origin_count,
        "verified_refined_translation_count": refined_success,
        "recorded_refined_failure_count": refined_failures,
        "missing_refined_record_count": missing_refined,
        "overall_translation_success_rate": refined_success / origin_count,
        "overall_translation_failure_or_missing_rate": 1 - refined_success / origin_count,
        "recorded_failure_taxonomy": dict(failure_taxonomy.most_common()),
        "sample_design": {
            "method": "First N stable database-order records per diagnostic class plus missing-record stratum.",
            "records_per_class_target": sample_per_class,
            "sample_count": len(all_samples),
            "limitation": "Diagnostic stratification is reproducible but is not a random prevalence estimator within classes.",
        },
        "forensic_conclusion": (
            "The artifact does not establish that any material fraction of the 14.72% tail is caused by an absent ten-operation semantic schema. "
            "Most recorded diagnostics are translator, replay, surface, fact-context, tactic/automation, resource, or implementation failures; branch/scope/induction cases remain the strongest candidates for deeper semantic adjudication."
        ),
    }
    connection.close()
    return result, all_samples, {}


def choose_representatives(records: list[dict[str, Any]], db_path: Path, per_operation: int = 10) -> list[dict[str, Any]]:
    by_operation: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        for operation in sorted(set(record["operations"])):
            if operation in PUBLIC_COMMANDS and len(by_operation[operation]) < per_operation:
                by_operation[operation].append(record)

    selected: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for operation, group in by_operation.items():
        for record in group:
            selected[(record["file"], record["decl_line"])].add(operation)
    for tag, record in (
        ("short_proof", min(records, key=lambda item: item["operation_count"])),
        ("long_proof", max(records, key=lambda item: item["operation_count"])),
        ("deep_nesting_proxy", max(records, key=lambda item: item["depth_proxy"])),
    ):
        selected[(record["file"], record["decl_line"])].add(tag)

    record_map = {(row["file"], row["decl_line"]): row for row in records}
    connection = sqlite3.connect(db_path)
    output = []
    for identity, reasons in sorted(selected.items()):
        row = record_map[identity]
        key = database_key(row["file"], row["decl_line"], "origin")
        found = connection.execute("SELECT value FROM unnamed WHERE key=?", (key,)).fetchone()
        origin = pickle.loads(found[0])[0] if found else None
        item = {
            "kind": "verified_translation",
            "selection_reasons": sorted(reasons),
            "artifact_translation_path": "./OOPSLA26 Artifact/results/translation/minilang.jsonl",
            "source_theorem_identity": row["proof_line"],
            "source_file": row["file"],
            "declaration_line": row["decl_line"],
            "exact_original_isar": origin,
            "translated_minilang": row["translation"],
            "operation_sequence": row["operations"],
            "operation_count": row["operation_count"],
            "depth_proxy": row["depth_proxy"],
        }
        item["provenance_sha256"] = sha256_bytes(json.dumps(item, sort_keys=True).encode())
        output.append(item)
    connection.close()
    return output


def analyse_result_csvs(results_dir: Path) -> list[dict[str, Any]]:
    csv.field_size_limit(100_000_000)
    rows = []
    for path in sorted(results_dir.glob("*.csv")):
        cases: dict[str, bool] = {}
        attempts = 0
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            for row in csv.DictReader(handle):
                attempts += 1
                index = row["index"]
                cases.setdefault(index, False)
                cases[index] = cases[index] or row.get("status") == "Status.SUCCESS"
        rows.append({
            "file": path.name,
            "sha256": sha256_file(path),
            "case_count": len(cases),
            "successful_cases": sum(cases.values()),
            "artifact_csv_success_rate": sum(cases.values()) / len(cases),
            "csv_rows": attempts,
        })
    return rows


def source_manifest(archive: Path, tree_path: Path, verbose_path: Path | None, selected_root: Path) -> dict[str, Any]:
    paths = [line.rstrip("\n") for line in tree_path.open(encoding="utf-8", errors="replace")]
    extension_counts: collections.Counter[str] = collections.Counter()
    top_counts: collections.Counter[str] = collections.Counter()
    for name in paths:
        pure = name.rstrip("/")
        if name.endswith("/"):
            extension_counts["<directory>"] += 1
        else:
            suffix = Path(pure).suffix.lower() or "<no_extension>"
            extension_counts[suffix] += 1
        parts = pure.split("/")
        if len(parts) > 2:
            top_counts[parts[2]] += 1

    total_member_bytes = None
    if verbose_path:
        total_member_bytes = 0
        pattern = re.compile(r"^[dl-][rwx-]{9}\s+\d+\s+\S+\s+\S+\s+(\d+)\s+")
        for line in verbose_path.open(encoding="utf-8", errors="replace"):
            match = pattern.match(line)
            if match:
                total_member_bytes += int(match.group(1))

    stat = archive.stat()
    semantic_sources = []
    for relative in (
        "docs/Reference_Manual.pdf",
        "MLML/contrib/Isa-Mini/library/proof.ML",
        "MLML/contrib/Isa-Mini/translator/library/translator.ML",
        "MLML/contrib/auto_sledgehammer/Auto_Sledgehammer.thy",
        "MLML/contrib/auto_sledgehammer/library/sledgehammer_solver.ML",
        "README.md",
        "LICENSE",
        "COPYING",
    ):
        path = selected_root / relative
        if path.exists():
            semantic_sources.append({
                "artifact_relative_path": "./OOPSLA26 Artifact/" + relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    return {
        "identity": {
            "title": "Artifact: A Minimal Proof Language for Neural Theorem Proving over Isabelle/HOL",
            "zenodo_record": 18454706,
            "published_artifact_version": "v2",
            "official_record_url": "https://zenodo.org/records/18454706",
            "related_paper": "arXiv:2507.18885v4",
        },
        "archive": {
            "absolute_path_at_audit": str(archive),
            "filename": archive.name,
            "bytes": stat.st_size,
            "mtime_unix": stat.st_mtime,
            "sha256": sha256_file(archive),
            "md5": md5_file(archive),
            "official_md5_match": md5_file(archive) == "6f5a1fe82aa182945f6520f7682fa05f",
        },
        "tree": {
            "entry_count": len(paths),
            "full_tree_sha256": sha256_file(tree_path),
            "full_tree_repository_copy": "experiments/minilang_audit/source_tree.txt.gz",
            "total_member_file_bytes": total_member_bytes,
            "counts_by_extension": dict(extension_counts.most_common()),
            "counts_by_top_level_area": dict(top_counts.most_common()),
            "embedded_git_metadata": "No .git directory/HEAD/config found in the archive tree; no source repository commit SHA is recoverable from the package.",
        },
        "license": {
            "artifact": "GNU Affero General Public License v3 or later",
            "files": ["./OOPSLA26 Artifact/COPYING", "./OOPSLA26 Artifact/LICENSE"],
            "copyright": "2026 Qiyuan Xu",
        },
        "selected_extraction": {
            "absolute_path_at_audit": str(selected_root),
            "policy": "Selective extraction only; the 33.99 GB tar payload was never fully materialized.",
        },
        "semantic_source_hashes": semantic_sources,
        "content_classification": {
            "semantic_source": [
                "docs/Reference_Manual.pdf",
                "MLML/contrib/Isa-Mini/library/proof.ML",
                "MLML/contrib/Isa-Mini/translator/library/translator.ML",
                "MLML/contrib/auto_sledgehammer",
            ],
            "source_corpora": ["Bundled Isabelle2024 sources", "AFP 2025-02-12 sources"],
            "generated_data": ["translation JSONL", "translation SqliteDict databases", "fine-tuning JSONL archives", "model outputs", "evaluation databases/CSVs"],
            "runtime_dependencies": ["Isabelle heaps", "AFP heaps", "Poly/ML", "solver binaries", "Python environment artifacts"],
            "model_checkpoints": "No model weights/checkpoints are packaged; README links eight Hugging Face models.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--verbose-tree", type=Path)
    parser.add_argument("--selected-root", type=Path, required=True)
    parser.add_argument("--large-root", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    translation = args.large_root / "results/translation/minilang.jsonl"
    db_path = args.large_root / "MLML/data/translation/results.db"
    operation_stats, records = analyse_operations(translation)
    failure_stats, failure_samples, _ = analyse_failures(db_path)
    representatives = choose_representatives(records, db_path)
    evaluation = analyse_result_csvs(args.results_dir)
    operation_stats["evaluation_csv_reconstruction"] = evaluation

    dump_json(args.output / "source_manifest.json", source_manifest(
        args.archive, args.tree, args.verbose_tree, args.selected_root
    ))
    dump_json(args.output / "operation_statistics.json", operation_stats)
    dump_json(args.output / "translation_failures.json", {
        "summary": failure_stats,
        "stratified_samples": failure_samples,
    })
    with (args.output / "representative_examples.jsonl").open("w", encoding="utf-8") as handle:
        for item in representatives:
            handle.write(json.dumps(item, sort_keys=True) + "\n")

    print(json.dumps({
        "operation_statistics": str(args.output / "operation_statistics.json"),
        "translation_failures": str(args.output / "translation_failures.json"),
        "representative_examples": len(representatives),
    }, indent=2))


if __name__ == "__main__":
    main()
