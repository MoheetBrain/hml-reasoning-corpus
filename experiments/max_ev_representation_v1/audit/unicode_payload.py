"""Decoded-payload Unicode audit (mission §3A).

Why the previous audit passed corrupted data
--------------------------------------------
``HML50K_UNICODE_AUDIT.md`` reported ``PASS`` on the 50K corpus by counting JSON ``\\uXXXX``
escape sequences **in the serialized file** and finding zero. That measurement was correct
and irrelevant. Every row was written with ``ensure_ascii=False``, so the JSON layer really
did contain no escapes -- while the *string the model reads* contained six-character
sequences ``\\``, ``u``, ``2``, ``7``, ``1``, ``d`` where a glyph belonged, because an inner
serialization step had already escaped the mathematics before the outer writer ever saw it.

Escaping at the JSON layer and escaping inside the payload are different defects, and only
the second one reaches the model. This audit therefore parses the JSON, takes the decoded
``str``, and looks for the literal escape *text* in it.

What counts as contamination
----------------------------
A decoded payload string containing the six characters ``\\uXXXX`` -- backslash, ``u``, and
four hex digits -- where ``XXXX`` names a codepoint the surrounding text otherwise carries
literally. Genuine Unicode (``⊢``, ``∀``, ``ℝ``) is not contamination; it is the intended
content. A backslash that is not followed by ``u`` and four hex digits is not contamination
either: ``\\n`` inside a Lean proposition and LaTeX such as ``\\frac`` are ordinary text.

The ``\\u`` form is the only one checked because it is the only one Python's
``json.dumps(ensure_ascii=True)`` emits. Surrogate pairs appear as two adjacent ``\\uXXXX``
runs and are counted as two hits, which is the honest count of escape characters injected.

Legitimate exceptions
---------------------
Mission §3D allows contamination only where "the source mathematically contains that
literal string intentionally" -- a document *about* escaping. Such rows must be listed
explicitly by id in ``allowed_ids``; there is no pattern-based amnesty, because a rule broad
enough to excuse a real defect is worse than no rule.
"""

from __future__ import annotations

import gzip
import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "LITERAL_ESCAPE",
    "PayloadFinding",
    "AuditResult",
    "scan_text",
    "scan_object",
    "audit_jsonl",
]

#: The literal escape *text*: a backslash, ``u``, four hex digits. Matched against a decoded
#: ``str``, never against file bytes -- that distinction is the whole point of this module.
LITERAL_ESCAPE = re.compile(r"\\u[0-9a-fA-F]{4}")

#: Fields whose contents reach the model. Contamination anywhere is a defect, but
#: contamination here is the one that invalidates an experiment.
MODEL_FACING_DEFAULT = ("input_text", "target_text", "prompt", "completion", "render")


@dataclass(frozen=True)
class PayloadFinding:
    """One contaminated string, located precisely enough to fix."""

    record_id: str
    path: str
    escapes: int
    chars: int
    sample: str
    model_facing: bool

    @property
    def fraction(self) -> float:
        """Share of the string that is escape text -- the §24 "15.2% of every prompt" figure."""
        return (self.escapes * 6 / self.chars) if self.chars else 0.0


@dataclass
class AuditResult:
    rows: int = 0
    contaminated_rows: int = 0
    total_escapes: int = 0
    total_chars: int = 0
    model_facing_chars: int = 0
    model_facing_escapes: int = 0
    findings: list[PayloadFinding] = field(default_factory=list)
    allowed_hits: int = 0
    genuine_non_ascii: int = 0

    @property
    def passed(self) -> bool:
        return self.contaminated_rows == 0

    @property
    def contaminated_fraction(self) -> float:
        return (
            self.model_facing_escapes * 6 / self.model_facing_chars
            if self.model_facing_chars
            else 0.0
        )

    def to_dict(self, max_findings: int = 50) -> dict[str, Any]:
        return {
            "result": "PASS" if self.passed else "FAIL",
            "rows": self.rows,
            "contaminated_rows": self.contaminated_rows,
            "total_literal_escapes": self.total_escapes,
            "genuine_non_ascii_codepoints": self.genuine_non_ascii,
            "model_facing_chars": self.model_facing_chars,
            "model_facing_escape_chars": self.model_facing_escapes * 6,
            "model_facing_contaminated_fraction": round(self.contaminated_fraction, 6),
            "allowed_exception_hits": self.allowed_hits,
            "findings": [
                {
                    "record_id": f.record_id,
                    "path": f.path,
                    "escapes": f.escapes,
                    "chars": f.chars,
                    "fraction": round(f.fraction, 6),
                    "model_facing": f.model_facing,
                    "sample": f.sample,
                }
                for f in self.findings[:max_findings]
            ],
            "findings_truncated": max(0, len(self.findings) - max_findings),
        }


def scan_text(text: str) -> list[str]:
    """Literal ``\\uXXXX`` sequences in one decoded string. Empty list means clean."""
    return LITERAL_ESCAPE.findall(text)


def scan_object(
    obj: Any, path: str = "", model_facing: Iterable[str] = MODEL_FACING_DEFAULT
) -> Iterator[tuple[str, str, list[str], bool]]:
    """Walk a decoded JSON object, yielding ``(path, text, escapes, model_facing)``.

    Keys are walked as well as values: a contaminated key is just as broken, and a walker
    that skipped them would report clean on a record whose identifiers carry the defect.
    """
    facing = tuple(model_facing)
    if isinstance(obj, str):
        yield path, obj, scan_text(obj), any(
            path == f".{k}" or path.endswith(f".{k}") for k in facing
        )
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, str) and scan_text(key):
                yield f"{path}<key>", key, scan_text(key), False
            yield from scan_object(value, f"{path}.{key}", facing)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from scan_object(value, f"{path}[{i}]", facing)


def _open(path: Path):
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open(
        encoding="utf-8"
    )


def audit_jsonl(
    path: str | Path,
    *,
    id_field: str = "record_id",
    allowed_ids: Iterable[str] = (),
    model_facing: Iterable[str] = MODEL_FACING_DEFAULT,
    limit: int | None = None,
) -> AuditResult:
    """Audit one JSONL(.gz) file at the decoded-payload level."""
    path = Path(path)
    allowed = set(allowed_ids)
    res = AuditResult()
    with _open(path) as handle:
        for i, line in enumerate(handle):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            rid = str(record.get(id_field, f"row{i}"))
            res.rows += 1
            row_dirty = False
            for field_path, text, escapes, facing in scan_object(record, "", model_facing):
                res.total_chars += len(text)
                res.genuine_non_ascii += sum(1 for c in text if ord(c) > 127)
                if facing:
                    res.model_facing_chars += len(text)
                    res.model_facing_escapes += len(escapes)
                if not escapes:
                    continue
                res.total_escapes += len(escapes)
                if rid in allowed:
                    res.allowed_hits += len(escapes)
                    continue
                row_dirty = True
                hit = LITERAL_ESCAPE.search(text)
                start = max(0, hit.start() - 40) if hit else 0
                res.findings.append(
                    PayloadFinding(
                        record_id=rid,
                        path=field_path or ".",
                        escapes=len(escapes),
                        chars=len(text),
                        sample=text[start : start + 100],
                        model_facing=facing,
                    )
                )
            if row_dirty:
                res.contaminated_rows += 1
    return res
