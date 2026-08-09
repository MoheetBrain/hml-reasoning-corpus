"""Deterministic Gold-10 payload size measurement."""

from __future__ import annotations

import re
from pathlib import Path


TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def gold10_payload_files(root: Path) -> list[Path]:
    paths = sorted((root / "data" / "gold_10").glob("G[0-9][0-9].json"))
    paths.extend(sorted((root / "examples" / "gold_10").rglob("*")))
    return [path for path in paths if path.is_file()]


def measure_gold10(root: Path) -> dict[str, int | str]:
    paths = gold10_payload_files(root)
    texts = [path.read_text(encoding="utf-8") for path in paths]
    return {
        "tokenizer": r"Unicode lexical tokens matching \w+|[^\w\s]",
        "file_count": len(paths),
        "utf8_bytes": sum(len(text.encode("utf-8")) for text in texts),
        "lexical_tokens": sum(len(TOKEN_RE.findall(text)) for text in texts),
        "canonical_trajectory_files": len([p for p in paths if p.parent.name == "gold_10" and p.suffix == ".json"]),
        "rendering_and_source_files": len([p for p in paths if p.parent.name != "gold_10"]),
    }
