import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "MASTER_SYNTHETIC_MATH_HML.md"


def _text() -> str:
    return MASTER.read_text(encoding="utf-8")


def test_exactly_six_complete_hundred_problem_corpora():
    text = _text()
    found = re.findall(r"(?m)^## (ALG|GEN|CALC|PROB|LINALG|MIXED)-(\d{3}) —", text)
    assert len(found) == 600
    for corpus in ("ALG", "GEN", "CALC", "PROB", "LINALG", "MIXED"):
        numbers = sorted(int(number) for key, number in found if key == corpus)
        assert numbers == list(range(1, 101))


def test_transition_count_reconciles_and_every_transition_is_classified():
    text = _text()
    declared = int(re.search(r"\| Atomic reasoning transitions \| (\d+) \|", text).group(1))
    headings = re.findall(r"(?m)^#### (?:ALG|GEN|CALC|PROB|LINALG|MIXED)-\d{3}-T\d{3}$", text)
    classifications = re.findall(r"(?m)^- \*\*Classification:\*\* `[^`]+`", text)
    assert len(headings) == declared
    assert len(classifications) == declared


def test_hml_validation_counts_reconcile_and_no_invalid_is_accepted():
    text = _text()
    rendered = int(re.search(r"\| Frozen-HML renderings emitted \| (\d+) \|", text).group(1))
    schema_pass = int(re.search(r"\| Neutral-schema validations passed \| (\d+) \|", text).group(1))
    roundtrips = int(re.search(r"\| Frozen-HML exact round trips \| (\d+) \|", text).group(1))
    assert text.count("~~~~hml\n") == rendered
    assert text.count("schema `PASS`; HML round trip `PASS`") == schema_pass == roundtrips
    assert "runtime verdict `INVALID`" not in text
    assert "| Frozen-HML `INVALID` verdicts accepted | 0 |" in text


def test_every_problem_preserves_full_source_and_final_result():
    text = _text()
    assert text.count("<details><summary>Open complete source problem and worked solution</summary>") == 600
    assert text.count("### Final mathematical result") == 600
    assert text.count("### Candidate / branch / obligation ledger") == 600


def test_frozen_authority_is_explicit():
    text = _text()
    assert "hml-semantic-pre-gemma-v1" in text
    assert "84bf9897689b0ed78a2caaefc1db850d49b81260" in text
    assert "semantic-firewall-case-0.1.0" in text
