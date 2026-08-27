"""Regression tests for the decoded-payload Unicode audit (mission §3A).

The mission requires cases for real mathematical Unicode, intentionally double-encoded
Unicode, ordinary ASCII and mixtures -- and, above all, that the audit **fails the old
corrupted artifact** that the previous audit passed.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from experiments.max_ev_representation_v1.audit.unicode_payload import (
    audit_jsonl,
    scan_text,
)

CORPUS = Path(__file__).resolve().parents[3]
OLD_HML_VIEW = CORPUS / "data/hml_50k_final/tasks/VALIDITY_JUDGE/HML_WORKED_UTF8/dev.jsonl.gz"
OLD_NEUTRAL_VIEW = (
    CORPUS / "data/hml_50k_final/tasks/VALIDITY_JUDGE/STRUCTURED_NEUTRAL_WORKED/dev.jsonl.gz"
)


# --------------------------------------------------------------------------- scan_text


def test_genuine_mathematical_unicode_is_clean():
    """Literal glyphs are the intended content, not a defect."""
    assert scan_text("⊢ ∀ (n : ℕ), n ≤ n") == []
    assert scan_text("α : Type u_1\nr : α → α → Prop") == []
    assert scan_text("inst✝⁵ : Monoid M") == []


def test_double_encoded_unicode_is_contamination():
    text = "inst\\u271d\\u2075 : Monoid M"
    assert scan_text(text) == ["\\u271d", "\\u2075"]


def test_plain_ascii_is_clean():
    assert scan_text("state\n  claim p0\n    status GIVEN") == []
    assert scan_text("") == []


def test_backslash_that_is_not_an_escape_is_clean():
    """``\\n`` in a proposition and LaTeX ``\\frac`` are ordinary text, not escapes."""
    assert scan_text("case neg\\nM : Type u") == []
    assert scan_text(r"$f(x)=\frac{ax+b}{cx+d}$") == []
    assert scan_text(r"\upsilon and \u12 and \uZZZZ") == []  # needs exactly 4 hex digits


def test_mixed_case_counts_only_the_escapes():
    text = "⊢ ∀ x, inst\\u271d : Monoid M and \\frac{1}{2}"
    assert scan_text(text) == ["\\u271d"]


def test_uppercase_hex_is_detected():
    assert scan_text("\\u22A2") == ["\\u22A2"]


# --------------------------------------------------------------------------- audit_jsonl


def _write(tmp_path: Path, rows: list[dict], name: str = "rows.jsonl") -> Path:
    p = tmp_path / name
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


def test_clean_file_passes(tmp_path: Path):
    p = _write(tmp_path, [{"record_id": "a", "input_text": "⊢ ∀ (n : ℕ), n ≤ n"}])
    res = audit_jsonl(p)
    assert res.passed
    assert res.contaminated_rows == 0
    assert res.genuine_non_ascii > 0


def test_contaminated_file_fails_and_locates_the_field(tmp_path: Path):
    p = _write(tmp_path, [{"record_id": "a", "input_text": "inst\\u271d : Monoid M"}])
    res = audit_jsonl(p)
    assert not res.passed
    assert res.contaminated_rows == 1
    assert res.findings[0].path == ".input_text"
    assert res.findings[0].model_facing is True
    assert res.findings[0].escapes == 1


def test_ensure_ascii_true_serialization_is_caught(tmp_path: Path):
    """The exact defect: an inner ``json.dumps`` escapes before the outer writer runs."""
    inner = json.dumps("⊢ ∀ x", ensure_ascii=True)  # -> '"\\u22a2 \\u2200 x"'
    p = _write(tmp_path, [{"record_id": "a", "input_text": inner}])
    res = audit_jsonl(p)
    assert not res.passed
    assert res.total_escapes == 2


def test_nested_and_list_payloads_are_walked(tmp_path: Path):
    p = _write(
        tmp_path,
        [{"record_id": "a", "meta": {"notes": ["fine", "bad \\u2200"]}}],
    )
    res = audit_jsonl(p)
    assert not res.passed
    assert res.findings[0].path == ".meta.notes[1]"
    assert res.findings[0].model_facing is False


def test_allowed_ids_exempts_only_that_row(tmp_path: Path):
    rows = [
        # A document *about* escaping: the escape text is the subject matter (§3D).
        {"record_id": "doc-about-escaping", "input_text": "the sequence \\u271d denotes ✝"},
        {"record_id": "real-defect", "input_text": "inst\\u271d : M"},
    ]
    p = _write(tmp_path, rows)
    res = audit_jsonl(p, allowed_ids={"doc-about-escaping"})
    assert not res.passed
    assert res.contaminated_rows == 1
    assert res.allowed_hits == 1
    assert res.findings[0].record_id == "real-defect"


def test_contaminated_fraction_is_reported(tmp_path: Path):
    p = _write(tmp_path, [{"record_id": "a", "input_text": "\\u2200" * 10}])
    res = audit_jsonl(p)
    assert res.contaminated_fraction == pytest.approx(1.0)


# ------------------------------------------------- the artifact the old audit passed


@pytest.mark.skipif(not OLD_HML_VIEW.exists(), reason="historical 50K artifact absent")
def test_audit_fails_the_old_corrupted_hml_view():
    """Mission §3A: the new audit MUST fail the artifact the old one passed."""
    res = audit_jsonl(OLD_HML_VIEW, limit=500)
    assert not res.passed, "the historical HML view is known-contaminated"
    assert res.contaminated_rows > 0
    assert res.contaminated_fraction > 0.05


@pytest.mark.skipif(not OLD_NEUTRAL_VIEW.exists(), reason="historical 50K artifact absent")
def test_the_matched_neutral_view_is_clean():
    """The confound was asymmetric: only the HML arm carried escape text."""
    res = audit_jsonl(OLD_NEUTRAL_VIEW, limit=500)
    assert res.passed, "the neutral arm was clean, which is what made the comparison unfair"


@pytest.mark.skipif(not OLD_HML_VIEW.exists(), reason="historical 50K artifact absent")
def test_raw_file_shows_no_json_level_escapes():
    """Pins *why* the old audit passed, so the defect cannot be reintroduced silently."""
    with gzip.open(OLD_HML_VIEW, "rb") as f:
        raw = f.read(2_000_000)
    # The file-level measurement the old audit made: the bytes really do contain no
    # JSON escape at the serialization layer...
    decoded_line = raw.split(b"\n")[0].decode("utf-8")
    record = json.loads(decoded_line)
    # ...and yet the decoded payload is contaminated.
    assert scan_text(record["input_text"]), "payload must be contaminated"
