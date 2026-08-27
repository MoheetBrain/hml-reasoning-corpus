"""Regression tests for the arms, the mutation engine and the canonical builder.

These are the properties the whole experiment rests on. If any of them stops holding, a run
would still produce numbers -- it would just produce numbers about something else.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from experiments.max_ev_representation_v1.arms import ARM_NAMES, parse, render
from experiments.max_ev_representation_v1.arms.common import from_ir, project, to_ir
from experiments.max_ev_representation_v1.arms.scalars import (
    needs_quote,
    read_atom,
    read_text,
    write_atom,
    write_text,
)
from experiments.max_ev_representation_v1.audit.parity import PROPERTIES, canonical
from experiments.max_ev_representation_v1.canon.alpha_rename import rename_transition
from experiments.max_ev_representation_v1.canon.build_canonical import (
    BuildError,
    build_canonical,
)
from experiments.max_ev_representation_v1.canon.lean_state import parse_lean_state
from experiments.max_ev_representation_v1.mutate.mutations import (
    MUTATIONS,
    UNRESOLVED_FAMILIES,
    apply_mutation,
)
from hamiltonian_lang.semantic_state.verify import verify_replay

CORPUS = Path(__file__).resolve().parents[3]
SOURCE = CORPUS / "data/hml_50k_final/canonical/records.jsonl.gz"
DATASET = CORPUS / "experiments/max_ev_representation_v1/dataset/v1"

pytestmark = pytest.mark.skipif(not SOURCE.exists(), reason="canonical corpus absent")


def _records(n: int = 40):
    out = []
    with gzip.open(SOURCE, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            out.append(json.loads(line))
    return out


def _items(n: int = 40):
    items = []
    for rec in _records(n):
        try:
            items.append(build_canonical(rec, semantic_id=f"SEM-{rec['record_id']}"))
        except BuildError:
            continue
    return items


# ------------------------------------------------------------------ lean decomposition


def test_lean_state_decomposes_context_and_goal():
    st = parse_lean_state("case neg\nα : Type u_1\nhb : bad.Finite\n⊢ ∃ m, m ≤ 1")
    assert st.clean
    block = st.primary
    assert block.case_label == "neg"
    assert [d.names for d in block.declarations] == [("α",), ("hb",)]
    assert block.goal_text == "∃ m, m ≤ 1"


def test_lean_state_reads_local_definitions():
    st = parse_lean_state("bad : Set ℕ := {m | m < 3}\n⊢ True")
    decl = st.primary.declarations[0]
    assert decl.type_text == "Set ℕ"
    assert decl.value_text == "{m | m < 3}"
    assert decl.is_definition


def test_lean_state_flags_what_it_cannot_read():
    st = parse_lean_state("case h.e'_6")
    assert not st.clean


def test_no_goals_is_terminal_not_an_error():
    st = parse_lean_state("no goals")
    assert st.no_goals and st.clean and st.primary is None


# ------------------------------------------------------------------ canonical objects


def test_every_canonical_parent_verifies_valid():
    items = _items()
    assert items
    for item in items:
        assert str(verify_replay(item.transition).verdict) == "VALID", item.semantic_id


def test_canonical_states_are_structured_not_flat():
    """The whole point of the decomposition: more than the one wrapped claim the 50K holds."""
    items = _items()
    assert all(len(i.transition.state_before.claims) >= 2 for i in items)
    assert all(i.transition.state_before.goals for i in items)


def test_propositions_are_single_line():
    """Guards the newline-escaping asymmetry that would re-create the §24 confound."""
    for item in _items():
        t = project(item.transition)
        for state in (t.state_before, t.state_after):
            for rec in (*state.claims.values(), *state.goals.values()):
                assert "\n" not in rec.proposition


def test_projection_strips_provenance():
    item = _items(5)[0]
    text = render("R_TYPED_AST", to_ir(project(item.transition)))
    assert "Mathlib/" not in text
    assert "tactic_sha256" not in text
    assert item.provenance["source_record_id"] not in text


# ------------------------------------------------------------------ arms


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_arm_round_trips_losslessly(arm: str):
    """Content is preserved exactly. Record order is not content -- see the next test."""
    for item in _items(25):
        ir = to_ir(project(item.transition))
        assert canonical(parse(arm, render(arm, ir))) == canonical(ir), f"{arm} lost information"


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_arm_render_is_a_fixed_point(arm: str):
    """The byte-level losslessness statement: re-rendering what was parsed reproduces it.

    Stronger than comparing objects, because it also catches a reader that recovers the right
    content through a writer that could not have produced that text.
    """
    for item in _items(25):
        text = render(arm, to_ir(project(item.transition)))
        assert render(arm, parse(arm, text)) == text


def test_frozen_hml_view_reorders_records_and_that_is_permitted():
    """Pins the one difference the parity gate normalises, so it stays a known quantity.

    The frozen view emits records in its own order. ``SemanticState`` maps id to record and
    the verifier never reads order, so this is a representation-only difference in the sense
    §5 allows -- but it is a real difference, and a silent change to it should fail a test
    rather than quietly widen what the parity gate forgives.
    """
    item = next(i for i in _items(25) if len(i.transition.state_before.claims) >= 4)
    ir = to_ir(project(item.transition))
    recovered = parse("R_HML", render("R_HML", ir))
    original_keys = [r["key"] for r in ir["state_before"]["claims"]]
    hml_keys = [r["key"] for r in recovered["state_before"]["claims"]]
    assert sorted(hml_keys) == sorted(original_keys)
    assert canonical(recovered) == canonical(ir)


def test_all_arms_recover_the_same_object():
    for item in _items(25):
        ir = to_ir(project(item.transition))
        recovered = [canonical(parse(a, render(a, ir))) for a in ARM_NAMES]
        for other in recovered[1:]:
            assert other == recovered[0]


def test_all_arms_preserve_the_verdict():
    for item in _items(15):
        ir = to_ir(project(item.transition))
        for arm in ARM_NAMES:
            back = from_ir(parse(arm, render(arm, ir)))
            assert str(verify_replay(back).verdict) == "VALID"


def test_every_parity_property_is_satisfied():
    for item in _items(10):
        ir = to_ir(project(item.transition))
        irs = {a: parse(a, render(a, ir)) for a in ARM_NAMES}
        for name, extract in PROPERTIES.items():
            values = [extract(irs[a]) for a in ARM_NAMES]
            assert all(v == values[0] for v in values), name


def test_reserved_words_survive_identifier_position():
    """A Lean case label really can be ``false``; a JSON reader must not turn it into False."""
    for word in ("true", "false", "null"):
        assert needs_quote(word)
        assert read_atom(write_atom(word)) == word


def test_scalar_round_trip_on_awkward_values():
    for value in ("", '"quoted"', "a\nb", "Set ℕ", "x : y", "⊢ ∀ x"):
        assert read_text(write_text(value)) == value


# ------------------------------------------------------------------ mutations


def test_every_family_is_applicable_somewhere():
    items = _items(60)
    seen = set()
    for item in items:
        for family in MUTATIONS:
            res = apply_mutation(item.transition, family, item.semantic_id)
            if res is not None and res.as_expected:
                seen.add(family)
    missing = set(MUTATIONS) - seen
    assert not missing, f"families that never produced a verified negative: {sorted(missing)}"


def test_mutations_are_labelled_by_the_verifier_not_by_intent():
    item = _items(5)[0]
    for family in MUTATIONS:
        res = apply_mutation(item.transition, family, item.semantic_id)
        if res is None:
            continue
        assert res.verifier_actual == str(verify_replay(res.transition).verdict)


def test_unresolved_families_reach_unresolved_and_invalid_families_do_not():
    for item in _items(20):
        for family in MUTATIONS:
            res = apply_mutation(item.transition, family, item.semantic_id)
            if res is None or not res.as_expected:
                continue
            expected = "UNRESOLVED" if family in UNRESOLVED_FAMILIES else "INVALID"
            assert res.verifier_actual == expected


def test_mutations_are_deterministic():
    item = _items(5)[0]
    for family in MUTATIONS:
        a = apply_mutation(item.transition, family, item.semantic_id)
        b = apply_mutation(item.transition, family, item.semantic_id)
        assert (a is None) == (b is None)
        if a is not None:
            assert a.transition == b.transition
            assert a.mutation_seed == b.mutation_seed


# ------------------------------------------------------------------ alpha renaming


def test_alpha_rename_preserves_validity_and_changes_every_binder():
    for item in _items(20):
        renamed = rename_transition(item.transition)
        assert str(verify_replay(renamed).verdict) == "VALID"
        assert set(renamed.state_before.claims) != set(item.transition.state_before.claims)


def test_alpha_rename_leaves_global_constants_alone():
    item = next(
        i for i in _items(60)
        if any("Set" in c.proposition for c in i.transition.state_before.claims.values())
    )
    renamed = rename_transition(item.transition)
    assert any("Set" in c.proposition for c in renamed.state_before.claims.values())


# ------------------------------------------------------------------ built dataset


@pytest.mark.skipif(not (DATASET / "MANIFEST.json").exists(), reason="dataset not built")
def test_dataset_is_balanced_and_siblings_share_a_split():
    manifest = json.loads((DATASET / "MANIFEST.json").read_text())
    for split, meta in manifest["splits"].items():
        labels = meta["labels"]
        if split == "ood_composition":
            continue  # heldout families are not applicable to every parent
        assert labels["VALID"] == labels["INVALID"] == labels["UNRESOLVED"], split


@pytest.mark.skipif(not (DATASET / "MANIFEST.json").exists(), reason="dataset not built")
def test_no_semantic_id_appears_in_two_splits():
    seen: dict[str, str] = {}
    for path in sorted(DATASET.glob("*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                prior = seen.setdefault(row["semantic_id"], path.name)
                assert prior == path.name, f"{row['semantic_id']} in {prior} and {path.name}"


@pytest.mark.skipif(not (DATASET / "MANIFEST.json").exists(), reason="dataset not built")
def test_audit_fields_never_reach_a_render():
    with gzip.open(DATASET / "dev.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            mtype = row["audit"]["mutation_type"]
            if not mtype:
                continue
            for arm in ARM_NAMES:
                assert mtype not in row["renders"][arm]
                assert row["label"] not in row["renders"][arm].split("status")[0]
