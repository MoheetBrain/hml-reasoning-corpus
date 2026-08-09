#!/usr/bin/env python3
"""Print the exact declared Gold-10 payload size."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hml_corpus.size import measure_gold10  # noqa: E402


if __name__ == "__main__":
    for key, value in measure_gold10(Path(__file__).resolve().parents[1]).items():
        print(f"{key}: {value}")
