from __future__ import annotations

import concurrent.futures
import os
import resource
import tempfile
import time
from pathlib import Path
from typing import Any


def _worker(transition: dict[str, Any]) -> str:
    from .verifier import verify
    return verify(transition)["verdict"]


def verifier_benchmark(rows: list[dict[str, Any]], workers: int = 8, repeats: int = 10) -> dict[str, Any]:
    transitions = [row["oracle"]["transition"] for row in rows] * repeats
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="hmltn-v2-bench-") as scratch:
        os.environ["TMPDIR"] = scratch
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            verdicts = list(pool.map(_worker, transitions, chunksize=max(1, len(transitions) // (workers * 8))))
    elapsed = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    failures = sum(verdict not in {"VALID", "INVALID", "UNRESOLVED"} for verdict in verdicts)
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    return {
        "workers": workers, "tasks": len(transitions), "wall_seconds": elapsed,
        "verifications_per_second": len(transitions) / elapsed,
        "aggregate_cpu_percent": 100 * cpu / elapsed,
        "allocated_cpu_percent": 100 * cpu / (elapsed * workers),
        "peak_child_rss_kib": after.ru_maxrss, "failures": failures,
        "scratch_isolated_and_removed": True,
    }
