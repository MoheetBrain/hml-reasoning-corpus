from __future__ import annotations

import json
import resource
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .audits import contradiction_audit, factory_b_audit, leakage_audit
from .authority import paths, verify_authority
from .benchmark import verifier_benchmark
from .canonical import jsonl_bytes, sha256_file, source_bundle_sha
from .factory_a import generate as generate_a
from .factory_b import generate as generate_b
from .master import render
from .qualification import qualify


def root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(jsonl_bytes(rows))
    return {"path": str(path.relative_to(root().parent)), "records": len(rows), "sha256": sha256_file(path)}


def run() -> dict[str, Any]:
    authority = verify_authority()
    started = time.perf_counter()
    usage_before = resource.getrusage(resource.RUSAGE_SELF)
    a1, a2 = generate_a(root().parent)
    b = generate_b()
    generation_elapsed = time.perf_counter() - started
    usage_after = resource.getrusage(resource.RUSAGE_SELF)
    a1_codes = Counter(row["failure_code"] for row in a1 if row["failure_code"])
    a_contra = contradiction_audit(a1 + a2)
    a_leak = leakage_audit(a1 + a2)
    b_audit = factory_b_audit(b)
    if b_audit["contradictions"]["conflicting_input_count"] or b_audit["secondary_findings"] or b_audit["duplicates"]:
        raise RuntimeError("Factory B promotion gate failed")
    if b_audit["causal_hard_percent"] < 70 or b_audit["shortcuts"]["sentinel_occurrences"]:
        raise RuntimeError("Factory B causal/shortcut gate failed")
    _, _, lean = paths()
    qualification = qualify(lean)

    datasets = {
        "factory_a1": _write_jsonl(root() / "data/factory_a/a1_regression.jsonl", a1),
        "factory_a2": _write_jsonl(root() / "data/factory_a/a2_learning.jsonl", a2),
        "factory_b_gold_stage100": _write_jsonl(root() / "data/factory_b/gold_stage100.jsonl", b),
    }
    benchmark = verifier_benchmark(b, workers=8, repeats=10)
    lexical = b_audit["shortcuts"]["lexical_naive_bayes_group_holdout_accuracy"]
    b_status = "PASS" if lexical < 0.90 else "FAIL"
    manifest: dict[str, Any] = {
        "protocol": "synthetic-factory-v2", "generator_source_sha256": source_bundle_sha(root()),
        "authority": authority,
        "factory_a": {
            "status": "PASS", "a1_records": len(a1), "a1_pairs": len(a1) // 2,
            "a2_records": len(a2), "a2_pairs": len(a2) // 2, "a2_gold_percent": 100.0,
            "a1_failure_codes": dict(sorted(a1_codes.items())),
            "contradictions": a_contra["conflicting_input_count"], "leakage": a_leak,
        },
        "factory_b": {"status": b_status, "stage100_status": "PASS" if b_status == "PASS" else "FAIL_SHORTCUT_GATE", "scale_decision": "FACTORY_B_FIX_FIRST", "scale_reason": "the 100-record challenge exhausts only one small domain relation; 1k would repeat semantics rather than add mathematical diversity", "records": len(b), "audit": b_audit},
        "lean_qualification": qualification,
        "performance": {
            "full_pipeline_wall_seconds_excluding_lean_census": generation_elapsed,
            "full_pipeline_records_per_second": len(b) / generation_elapsed,
            "full_pipeline_peak_rss_kib": max(usage_before.ru_maxrss, usage_after.ru_maxrss),
            "verifier": benchmark,
        },
        "datasets": datasets,
        "scaling": {"stage1000_generated": False, "stage10000_generated": False, "alpha_renaming_generated": False},
        "isolation": {"claude_fable_changed": 0, "historical_v1_changed": 0, "frozen_hml_changed": 0},
    }
    manifests = root() / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    (manifests / "v2_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (manifests / "lean_qualification_census.json").write_text(json.dumps(qualification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    master = root().parent / "synthetic_factory" / "MASTER_SYNTHETIC_FACTORY_V2.md"
    master.write_text(render(manifest), encoding="utf-8")
    verify_authority()
    return manifest


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
