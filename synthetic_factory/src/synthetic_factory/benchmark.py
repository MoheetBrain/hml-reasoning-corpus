"""Process-isolated frozen-verifier throughput benchmark."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import resource
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from .authority import assert_authority
from .records import canonical_json
from .verifier_runner import primary_result


def factory_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _init_worker(scratch_root: str) -> None:
    worker = Path(scratch_root) / f"worker_{os.getpid()}"
    worker.mkdir(parents=True, exist_ok=False)
    os.environ["TMPDIR"] = str(worker)
    tempfile.tempdir = str(worker)


def _verify_task(task: tuple[int, dict[str, Any], dict[str, Any]]) -> tuple[int, str, str]:
    index, source, counterfactual = task
    before = primary_result(source)
    after = primary_result(counterfactual)
    return index, before["verdict"], after["verdict"]


def load_pairs() -> list[dict[str, Any]]:
    path = factory_root() / "data" / "stage100" / "canonical_pairs.jsonl"
    if not path.exists():
        raise RuntimeError("generate Stage100 before benchmarking")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def run_once(*, workers: int, tasks: int, pairs: list[dict[str, Any]]) -> dict[str, Any]:
    run_id = f"{uuid.uuid4().hex}-w{workers}"
    scratch = factory_root() / "scratch" / run_id
    scratch.mkdir(parents=True, exist_ok=False)
    work = [
        (
            index,
            pairs[index % len(pairs)]["source_transition"],
            pairs[index % len(pairs)]["counterfactual_transition"],
        )
        for index in range(tasks)
    ]
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    try:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_init_worker,
            initargs=(str(scratch),),
        ) as pool:
            results = list(pool.map(_verify_task, work, chunksize=max(1, tasks // (workers * 8))))
    finally:
        elapsed = time.perf_counter() - started
        usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        shutil.rmtree(scratch)

    results.sort()
    failures = sum(before != "VALID" or after != "INVALID" for _, before, after in results)
    result_hash = hashlib.sha256(
        "\n".join(canonical_json(row) for row in results).encode("utf-8")
    ).hexdigest()
    child_cpu_seconds = (
        usage_after.ru_utime
        + usage_after.ru_stime
        - usage_before.ru_utime
        - usage_before.ru_stime
    )
    return {
        "workers": workers,
        "tasks": tasks,
        "transition_verifications": tasks * 2,
        "wall_seconds": elapsed,
        "tasks_per_second": tasks / elapsed,
        "verifications_per_second": tasks * 2 / elapsed,
        "aggregate_cpu_utilization_percent": 100 * child_cpu_seconds / elapsed,
        "allocated_cpu_utilization_percent": 100 * child_cpu_seconds / (elapsed * workers),
        "peak_child_rss_kib": usage_after.ru_maxrss,
        "failures": failures,
        "deterministic_result_sha256": result_hash,
        "scratch_isolated": True,
        "scratch_removed": not scratch.exists(),
    }


def benchmark(*, worker_counts: list[int], tasks: int) -> dict[str, Any]:
    authority = assert_authority()
    pairs = load_pairs()
    runs = [run_once(workers=workers, tasks=tasks, pairs=pairs) for workers in worker_counts]
    stable = all(run["failures"] == 0 for run in runs) and len(
        {run["deterministic_result_sha256"] for run in runs}
    ) == 1
    eligible = [run for run in runs if run["failures"] == 0]
    selected = max(eligible, key=lambda run: run["tasks_per_second"]) if stable else None
    result = {
        "benchmark": "stage100_frozen_verifier_process_scaling",
        "authority": {
            "hml_sha": authority["hml"]["sha"],
            "corpus_sha": authority["corpus"]["authority_sha"],
        },
        "runs": runs,
        "deterministic_across_worker_counts": stable,
        "selected_workers": selected["workers"] if selected else None,
        "selection_rule": "fastest zero-failure run, only if all result hashes agree",
    }
    root = factory_root()
    output = root / "manifests" / "benchmark.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        "| {workers} | {wall_seconds:.3f} | {tasks_per_second:.1f} | "
        "{verifications_per_second:.1f} | {aggregate_cpu_utilization_percent:.1f}% | "
        "{allocated_cpu_utilization_percent:.1f}% | {peak_child_rss_kib} | {failures} |".format(**run)
        for run in runs
    )
    report = f"""# Performance benchmark

The same {tasks:,} ordered pair-verification tasks were executed for every worker
count. Each task imports and checks both the original and counterfactual transition in
a process-isolated scratch directory. All scratch directories were removed afterward.

| Workers | Wall s | Pairs/s | Verifications/s | Aggregate CPU | Allocated CPU | Peak child RSS KiB | Failures |
|---:|---:|---:|---:|---:|---:|---:|---:|
{rows}

- Deterministic result across worker counts: **{str(stable).lower()}**
- Selected stable worker count: **{result['selected_workers']}**
- Result SHA-256: `{runs[0]['deterministic_result_sha256']}`

`ru_maxrss` is the operating system's peak-child statistic, not a sum across workers.
The chosen setting is empirical for this VM and is not encoded as a semantic default.
"""
    (root / "reports" / "PERFORMANCE.md").write_text(report, encoding="utf-8")
    assert_authority()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=int, default=1000)
    parser.add_argument("--workers", type=int, nargs="+", default=[4, 8, 16, 20])
    args = parser.parse_args()
    print(json.dumps(benchmark(worker_counts=args.workers, tasks=args.tasks), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
