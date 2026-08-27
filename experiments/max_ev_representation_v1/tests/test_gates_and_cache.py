"""Tests for the pre-GPU gates, the coarse controls and the feature cache.

Each of these guards a way the experiment could produce a number that means something other
than what it appears to mean.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from experiments.max_ev_representation_v1.audit.counterfactual_splits import (
    audit_splits,
    canonical_fingerprint,
)
from experiments.max_ev_representation_v1.harness.cache import (
    CacheKey,
    FeatureCache,
    verify_precision,
)
from experiments.max_ev_representation_v1.harness.shortcut_controls import (
    LENGTH_FEATURE_NAMES,
    STRUCTURE_FEATURE_NAMES,
    length_only_features,
    minimal_pair_report,
    structure_count_features,
)

DATASET = Path(__file__).resolve().parents[1] / "dataset/v1"
needs_dataset = pytest.mark.skipif(
    not (DATASET / "MANIFEST.json").exists(), reason="dataset not built"
)


# ----------------------------------------------------------------- split isolation


@needs_dataset
def test_counterfactual_families_never_straddle_a_split():
    audit = audit_splits(DATASET)
    d = audit.to_dict()
    assert d["cross_split_family_leaks"] == 0, d["leak_examples"][:3]
    assert d["cross_split_source_family_leaks"] == 0, d["leak_examples"][:3]
    assert d["exact_duplicate_leaks"] == 0
    assert d["near_duplicate_leaks"] == 0
    assert audit.passed


@needs_dataset
def test_every_family_has_its_full_sibling_set():
    audit = audit_splits(DATASET)
    assert audit.to_dict()["siblings_per_family"] == {3: audit.families_total}


def test_fingerprint_ignores_formatting_but_not_content():
    a = {"renders": {"R_HML": "claim x\n  proposition \"p\"\n"}}
    b = {"renders": {"R_HML": "claim x\n\n   proposition \"p\"\n"}}
    c = {"renders": {"R_HML": "claim x\n  proposition \"q\"\n"}}
    assert canonical_fingerprint(a) == canonical_fingerprint(b)
    assert canonical_fingerprint(a) != canonical_fingerprint(c)


# ----------------------------------------------------------------- coarse controls


def test_length_features_carry_no_token_identity():
    """Two texts with identical shape but disjoint vocabulary must be indistinguishable."""
    a = length_only_features(["aaa bbb\nccc ddd"])
    b = length_only_features(["xxx yyy\nzzz www"])
    assert a.shape == (1, len(LENGTH_FEATURE_NAMES))
    assert np.allclose(a, b)


def test_structure_counts_read_records_not_mathematics():
    ast = (
        '(transition\n (state before\n  (scopes global)\n'
        '  (claim a (id "a") (proposition "P") (status "GIVEN") (scope "global")'
        ' (domain "D") (dependencies ()))\n'
        '  (goal g0 (id "g0") (proposition "Q") (status "OPEN") (scope "global"))\n )\n'
        ' (state after\n  (scopes global)\n'
        '  (claim a (id "a") (proposition "P") (status "GIVEN") (scope "global")'
        ' (domain "D") (dependencies ()))\n'
        '  (claim c1 (id "c1") (proposition "R") (status "DERIVED") (scope "global")'
        ' (domain "D") (dependencies (a)))\n'
        '  (goal g0 (id "g0") (proposition "Q") (status "OPEN") (scope "global"))\n )\n'
        ' (evidence e1 (id "e1") (kind "K") (status "VALID") (trusted true)'
        ' (supports_rule "R") (premise_ids (a)) (payload {}))\n)'
    )
    feats = structure_count_features([ast])[0]
    names = dict(zip(STRUCTURE_FEATURE_NAMES, feats))
    assert names["n_claims_before"] == 1
    assert names["n_claims_after"] == 2
    assert names["claims_delta"] == 1
    assert names["n_goals_before"] == 1
    assert names["n_evidence"] == 1


def test_structure_counts_are_blind_to_proposition_text():
    def ast(prop):
        return (
            '(transition\n (state before\n  (scopes global)\n'
            f'  (claim a (id "a") (proposition "{prop}") (status "GIVEN") (scope "global")'
            ' (domain "D") (dependencies ()))\n )\n (state after\n  (scopes global)\n'
            f'  (claim a (id "a") (proposition "{prop}") (status "GIVEN") (scope "global")'
            ' (domain "D") (dependencies ()))\n )\n)'
        )
    assert np.allclose(
        structure_count_features([ast("x = 0")]),
        structure_count_features([ast("forall n, n > 1")]),
    )


# ----------------------------------------------------------------- minimal pairs


def test_minimal_pair_report_scores_direction_not_class():
    rows = [
        {"semantic_id": "S1", "label": "VALID", "audit": {"mutation_type": None}},
        {"semantic_id": "S1", "label": "INVALID",
         "audit": {"mutation_type": "REMOVE_REQUIRED_PREMISE"}},
        {"semantic_id": "S2", "label": "VALID", "audit": {"mutation_type": None}},
        {"semantic_id": "S2", "label": "INVALID",
         "audit": {"mutation_type": "REMOVE_REQUIRED_PREMISE"}},
    ]
    # index 0 == VALID. S1 is ordered correctly, S2 is inverted.
    probs = np.array([[0.8, 0.1, 0.1], [0.3, 0.6, 0.1],
                      [0.2, 0.7, 0.1], [0.9, 0.05, 0.05]])
    rep = minimal_pair_report(probs, rows, {"VALID": 0, "INVALID": 1, "UNRESOLVED": 2})
    assert rep["overall"]["n"] == 2
    assert rep["overall"]["pairwise_accuracy"] == 0.5
    fam = rep["by_mutation_family"]["REMOVE_REQUIRED_PREMISE"]
    assert fam["n"] == 2


def test_minimal_pair_margin_is_signed():
    """A family the model reads backwards must show a negative margin, not chance accuracy."""
    rows = [
        {"semantic_id": "S", "label": "VALID", "audit": {"mutation_type": None}},
        {"semantic_id": "S", "label": "INVALID", "audit": {"mutation_type": "F"}},
    ]
    probs = np.array([[0.1, 0.8, 0.1], [0.9, 0.05, 0.05]])
    rep = minimal_pair_report(probs, rows, {"VALID": 0, "INVALID": 1, "UNRESOLVED": 2})
    assert rep["overall"]["mean_probability_margin"] < 0
    assert rep["overall"]["pairwise_accuracy"] == 0.0


# ----------------------------------------------------------------- feature cache


def _key(**over) -> CacheKey:
    base = dict(
        model_sha="m" * 40, tokenizer_sha="m" * 40, dataset_sha="d" * 64,
        renderer_commit="b011511", code_sha="c" * 64, max_length=8192,
        dtype="bfloat16", poolings=("mean_last", "mean_mid"),
    )
    base.update(over)
    return CacheKey(**base)


def test_cache_round_trips_and_restores_float32(tmp_path: Path):
    cache = FeatureCache(tmp_path, _key())
    feats = {
        "mean_last": np.random.randn(7, 16).astype(np.float32),
        "__token_lengths__": np.arange(7, dtype=np.int32),
    }
    assert cache.load("R_HML", "dev") is None
    cache.store("R_HML", "dev", feats, {"items": 7})
    got = cache.load("R_HML", "dev")
    assert got is not None
    assert got["mean_last"].dtype == np.float32
    assert got["mean_last"].shape == (7, 16)
    assert np.array_equal(got["__token_lengths__"], feats["__token_lengths__"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_sha", "z" * 40), ("tokenizer_sha", "z" * 40), ("dataset_sha", "z" * 64),
        ("renderer_commit", "deadbeef"), ("code_sha", "z" * 64), ("max_length", 4096),
        ("dtype", "float16"), ("poolings", ("mean_last",)),
    ],
)
def test_any_provenance_change_is_a_miss(tmp_path: Path, field: str, value):
    """A cache that returns stale features is worse than no cache."""
    cache = FeatureCache(tmp_path, _key())
    cache.store("R_HML", "dev", {"mean_last": np.zeros((3, 4), np.float32)}, {})
    other = FeatureCache(tmp_path, _key(**{field: value}))
    assert other.load("R_HML", "dev") is None


def test_float16_round_trip_cost_is_small_enough_to_ignore():
    """§6 permits float16 storage only if it does not move probe-relevant statistics."""
    rng = np.random.default_rng(0)
    arr = rng.normal(scale=3.0, size=(512, 256)).astype(np.float32)
    stats = verify_precision(arr)
    assert stats["mean_relative_error"] < 1e-3
    assert stats["max_std_shift"] < 1e-2


def test_cache_metadata_records_full_provenance(tmp_path: Path):
    cache = FeatureCache(tmp_path, _key())
    cache.store("R_HML", "dev", {"mean_last": np.zeros((2, 3), np.float32)}, {"items": 2})
    meta = json.loads((cache.root / "R_HML" / "dev.meta.json").read_text())
    for required in ("model_sha", "tokenizer_sha", "dataset_sha", "renderer_commit",
                     "code_sha", "max_length", "dtype", "poolings", "digest"):
        assert required in meta["key"], required
    assert meta["hidden_size"] == 3
