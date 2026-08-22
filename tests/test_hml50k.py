from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "data/hml_50k_final"
VIEWS = ("HML_WORKED_UTF8", "STRUCTURED_NEUTRAL_WORKED")


def _rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def test_declared_counts_and_audits_pass() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["counts"]["canonical"] == {"train": 50_000, "dev": 3_000, "final": 3_000}
    for name in (
        "build_summary.json",
        "candidate_audit.json",
        "dedup_audit.json",
        "final_split_contamination_audit.json",
        "leakage_audit.json",
        "mutation_tests.json",
        "parity_audit.json",
        "token_length_audit.json",
        "trajectory_depth_audit.json",
        "unicode_audit.json",
    ):
        assert json.loads((ROOT / "audits" / name).read_text())["result"] == "PASS"


def test_manifest_payload_hashes() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for relative, metadata in manifest["files"].items():
        path = ROOT / relative
        assert path.stat().st_size == metadata["bytes"]
        assert _sha(path) == metadata["sha256"]


def test_primary_view_identity_and_label_parity() -> None:
    for split, expected in (("train", 50_000), ("dev", 3_000), ("final", 3_000)):
        paths = [ROOT / "tasks/NEXT_ACTION_SELECT" / view / f"{split}.jsonl.gz" for view in VIEWS]
        count = 0
        for hml, neutral in zip(_rows(paths[0]), _rows(paths[1]), strict=True):
            count += 1
            assert (hml["record_id"], hml["parent_id"], hml["split"], hml["target_text"]) == (
                neutral["record_id"], neutral["parent_id"], neutral["split"], neutral["target_text"]
            )
            assert hml["audit_metadata"]["canonical_transition_sha256"] == neutral["audit_metadata"]["canonical_transition_sha256"]
        assert count == expected


def test_nested_rungs() -> None:
    ids10 = json.loads((ROOT / "rungs/10k/record_ids.json").read_text())
    ids30 = json.loads((ROOT / "rungs/30k/record_ids.json").read_text())
    ids50 = json.loads((ROOT / "rungs/50k/record_ids.json").read_text())
    assert len(ids10) == 10_000 and len(ids30) == 30_000 and len(ids50) == 50_000
    assert ids10 == ids30[:10_000]
    assert ids30 == ids50[:30_000]


def test_literal_utf8_and_no_hml_tree() -> None:
    unicode_audit = json.loads((ROOT / "audits/unicode_audit.json").read_text())
    assert sum(x["json_unicode_escape_sequences"] for x in unicode_audit["files"].values()) == 0
    assert sum(x["literal_non_ascii_codepoints"] for x in unicode_audit["files"].values()) > 0
    assert not list(ROOT.rglob("*HML_TREE*"))
