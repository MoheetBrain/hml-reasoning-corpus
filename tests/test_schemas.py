"""Independent JSON Schema validation for the corpus's declared schemas.

A generator validating its own output is not independent evidence. Before this
file existed, nothing in the corpus ever ran a JSON Schema validator: the only
appearance of `experiments/semantic_firewall/schemas/semantic_case.schema.json`
in code was as a file being hashed into a freeze manifest. That blind spot let
`$defs/action` sit in an unsatisfiable state -- `additionalProperties: false`
with fifteen `required` names and no `properties` block, which is *valid* JSON
Schema and therefore passes `check_schema`, yet rejects every instance it was
written to describe.

These tests use a real, third-party validator (`jsonschema`) so the evidence is
independent of the code that produced the artifacts.
"""

import copy
import hashlib
import json
import re
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - environment guard
    raise ImportError(
        "tests/test_schemas.py requires the `jsonschema` package. It is deliberately a "
        "hard requirement rather than a skip: skipping would restore the exact blind spot "
        "this file exists to close (no independent validator ever runs)."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
FIREWALL = ROOT / "experiments" / "semantic_firewall"
SEMANTIC_CASE_SCHEMA = FIREWALL / "schemas" / "semantic_case.schema.json"
FIXTURES = FIREWALL / "acceptance" / "fixtures.json"

# Schemas this repository owns. `hml_core/` is a pinned, read-only submodule and
# is deliberately excluded: this suite must not fail on a file it may not fix.
OWNED_SCHEMA_DIRS = (ROOT / "schemas", ROOT / "experiments")

# JSON Schema keywords whose values are subschemas, by shape.
SCHEMA_VALUED = (
    "additionalItems",
    "additionalProperties",
    "contains",
    "contentSchema",
    "else",
    "if",
    "items",
    "not",
    "propertyNames",
    "then",
    "unevaluatedItems",
    "unevaluatedProperties",
)
SCHEMA_MAP_VALUED = ("$defs", "definitions", "dependentSchemas", "patternProperties", "properties")
SCHEMA_LIST_VALUED = ("allOf", "anyOf", "oneOf", "prefixItems")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fixture_cases():
    return [entry["case"] for entry in load(FIXTURES)["fixtures"]]


def walk_subschemas(node, path="#"):
    """Yield (json_pointer, subschema) for every subschema in a schema document.

    Descends only through JSON Schema keywords, so a user-defined property that
    happens to be named `required` or `additionalProperties` is never mistaken
    for a keyword.
    """
    if not isinstance(node, dict):
        return
    yield path, node
    for keyword in SCHEMA_VALUED:
        if keyword in node:
            yield from walk_subschemas(node[keyword], f"{path}/{keyword}")
    for keyword in SCHEMA_MAP_VALUED:
        block = node.get(keyword)
        if isinstance(block, dict):
            for name, sub in block.items():
                yield from walk_subschemas(sub, f"{path}/{keyword}/{name}")
    for keyword in SCHEMA_LIST_VALUED:
        block = node.get(keyword)
        if isinstance(block, list):
            for index, sub in enumerate(block):
                yield from walk_subschemas(sub, f"{path}/{keyword}/{index}")


def unsatisfiable_closed_objects(document):
    """Return [(pointer, unreachable_required_names)] for closed-yet-required subschemas.

    `additionalProperties: false` forbids every member name that is not matched
    by `properties` or `patternProperties`. Any name in `required` that is not so
    matched can therefore never be supplied, and the subschema rejects every
    object -- the defect this guard exists to catch, wherever it recurs.
    """
    findings = []
    for pointer, sub in walk_subschemas(document):
        if sub.get("additionalProperties") is not False:
            continue
        required = sub.get("required")
        if not isinstance(required, list) or not required:
            continue
        declared = set(sub.get("properties") or {})
        patterns = list(sub.get("patternProperties") or {})
        unreachable = [
            name
            for name in required
            if name not in declared and not any(re.search(pattern, name) for pattern in patterns)
        ]
        if unreachable:
            findings.append((pointer, unreachable))
    return findings


def owned_schema_documents():
    """Every corpus-owned JSON file that declares itself a JSON Schema."""
    found = []
    for base in OWNED_SCHEMA_DIRS:
        for path in sorted(base.rglob("*.json")):
            try:
                document = load(path)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(document, dict) and "$schema" in document:
                found.append((path, document))
    return found


def test_semantic_case_schema_is_a_valid_schema_for_its_declared_draft():
    schema = load(SEMANTIC_CASE_SCHEMA)
    # `default=None` means: resolve strictly from the declared `$schema`, never guess.
    validator_class = jsonschema.validators.validator_for(schema, default=None)
    assert validator_class is not None, f"unrecognised $schema: {schema.get('$schema')!r}"
    assert validator_class.META_SCHEMA["$id"].rstrip("#") == schema["$schema"].rstrip("#")
    validator_class.check_schema(schema)


def test_every_acceptance_fixture_validates_against_the_semantic_case_schema():
    schema = load(SEMANTIC_CASE_SCHEMA)
    validator = jsonschema.validators.validator_for(schema)(schema)
    cases = fixture_cases()
    assert len(cases) == 30
    failures = {}
    for entry, case in zip(load(FIXTURES)["fixtures"], cases):
        errors = sorted(validator.iter_errors(case), key=lambda error: list(error.absolute_path))
        if errors:
            failures[entry["fixture_id"]] = [
                f"{error.validator} at /{'/'.join(map(str, error.absolute_path))}" for error in errors
            ]
    assert failures == {}, f"{len(failures)}/30 acceptance fixtures rejected: {failures}"


def test_every_frozen_benchmark_case_validates_against_the_semantic_case_schema():
    """The 200 DEV/FINAL cases are instances of the same schema; hold them to it too."""
    schema = load(SEMANTIC_CASE_SCHEMA)
    validator = jsonschema.validators.validator_for(schema)(schema)
    dev = sorted((FIREWALL / "data" / "dev" / "cases").glob("*.json"))
    final = sorted((FIREWALL / "data" / "final" / "cases").glob("*.json"))
    assert (len(dev), len(final)) == (40, 160)
    failures = {path.name: [error.validator for error in validator.iter_errors(load(path))] for path in dev + final}
    assert {name: errs for name, errs in failures.items() if errs} == {}


def test_no_owned_schema_declares_an_unsatisfiable_closed_object():
    """The general guard: closed object + a `required` name it can never accept."""
    documents = owned_schema_documents()
    assert documents, "no corpus-owned JSON Schema documents were discovered; the guard would be vacuous"
    findings = {
        str(path.relative_to(ROOT)): unsatisfiable_closed_objects(document)
        for path, document in documents
        if unsatisfiable_closed_objects(document)
    }
    assert findings == {}, f"unsatisfiable subschemas: {findings}"


def test_the_unsatisfiability_guard_actually_fires():
    """Non-vacuity: the guard must detect the defect, at any depth, and stay quiet otherwise."""
    defect = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "$defs": {"buried": {"type": "object", "additionalProperties": False, "required": ["a", "b"]}},
    }
    assert unsatisfiable_closed_objects(defect) == [("#/$defs/buried", ["a", "b"])]

    partial = copy.deepcopy(defect)
    partial["$defs"]["buried"]["properties"] = {"a": {}}
    assert unsatisfiable_closed_objects(partial) == [("#/$defs/buried", ["b"])]

    repaired = copy.deepcopy(defect)
    repaired["$defs"]["buried"]["properties"] = {"a": {}, "b": {}}
    assert unsatisfiable_closed_objects(repaired) == []

    by_pattern = copy.deepcopy(defect)
    by_pattern["$defs"]["buried"]["patternProperties"] = {"^[ab]$": {}}
    assert unsatisfiable_closed_objects(by_pattern) == []

    # A property literally named like a keyword must not be read as one.
    decoy = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"required": {"type": "array"}, "additionalProperties": {"type": "boolean"}},
    }
    assert unsatisfiable_closed_objects(decoy) == []

    # And the guard must be live against the real document, not just synthetic input.
    live = load(SEMANTIC_CASE_SCHEMA)
    closed = [pointer for pointer, sub in walk_subschemas(live) if sub.get("additionalProperties") is False]
    assert sorted(closed) == ["#", "#/$defs/action", "#/$defs/claim", "#/$defs/state"]


def test_malformed_actions_are_rejected():
    """Negative control: the fixtures must not pass merely because nothing is checked."""
    schema = load(SEMANTIC_CASE_SCHEMA)
    validator = jsonschema.validators.validator_for(schema)(schema)
    good = fixture_cases()[0]
    assert validator.is_valid(good), "control case must validate for the negatives to mean anything"

    extra_key = copy.deepcopy(good)
    extra_key["action"]["undeclared_field"] = "surprise"
    assert not validator.is_valid(extra_key)

    missing_required = copy.deepcopy(good)
    del missing_required["action"]["warrant"]
    assert not validator.is_valid(missing_required)

    # Pins the typed value schemas: these are the only constraints beyond membership.
    for field, wrong_value in (
        ("id", 12345),
        ("summary", ["not", "a", "string"]),
        ("dependencies", "p0"),
        ("typing", "Proposition"),
        ("scope_effect", []),
    ):
        wrong_type = copy.deepcopy(good)
        wrong_type["action"][field] = wrong_value
        assert not validator.is_valid(wrong_type), f"action.{field} accepted a wrongly typed value"

    outside_action = copy.deepcopy(good)
    outside_action["semantic_focus"] = "NOT_A_DECLARED_FOCUS"
    assert not validator.is_valid(outside_action)


# ---------------------------------------------------------------------------
# The second amendment: per-object hardening, and the holes it deliberately left
#
# The first amendment made the schema satisfiable. It did not make it
# discriminating: `source`, `claim` and `evidence` had `required` and nothing
# else, and `obligations`, `candidates`, `branches`, `goals` and all fifteen
# action sub-objects were bare `{"type": "object"}`. Everything below is a
# negative control for what the second amendment closed, or a POSITIVE control
# pinning what it deliberately left open -- because an undocumented hole and a
# documented one look identical from outside, and only one of them is a decision.
# ---------------------------------------------------------------------------

#: Region values well-formed under the amended value schemas, used to show the
#: negatives fail for the stated reason and not because the shape was wrong.
WELL_FORMED_REGION_VALUE = {
    "obligations": {"id": "o9", "proposition": "debt", "status": "OPEN", "mandatory": True, "dependencies": ["p0"]},
    "candidates": {"id": "k9", "proposition": "x = 1", "status": "PROPOSED", "scope": "global", "constraint_ids": ["p0"]},
    "branches": {"id": "b9", "predicate": "case", "status": "OPEN", "conclusion": None, "partition_id": None},
    "goals": {"id": "g9", "proposition": "target", "status": "OPEN", "scope": "global"},
}

#: `$defs` left open on purpose, with the evidence that forbade closing them.
DELIBERATELY_OPEN_DEFS = {
    "source": "SEMANTIC_STATE_CONTRACT.md names `source` an open dictionary",
    "evidence": "the canonical EvidenceRecord keeps unmodelled keys in an extensible payload",
    "obligation": "the canonical Obligation declares seven fields; the corpus shows five",
    "candidate": "the canonical Candidate declares nine; FX2 shows six; the corpus shows five",
    "branch": "the canonical Branch declares six; the corpus shows four",
    "goal": "no second, independently built sample exists to corroborate the corpus",
}


def semantic_case_validator():
    schema = load(SEMANTIC_CASE_SCHEMA)
    return jsonschema.validators.validator_for(schema)(schema), schema


def fixture_by_id(fixture_id):
    for entry in load(FIXTURES)["fixtures"]:
        if entry["fixture_id"] == fixture_id:
            return entry
    raise AssertionError(f"no such fixture: {fixture_id}")


def test_the_closed_claim_object_rejects_an_undeclared_key():
    """`$defs/claim` is the one object this amendment closed. Prove it is shut.

    Four independent sources agree on exactly six fields -- `required`, the union
    and the intersection of all 736 frozen claim instances, the union over the 76
    FX2 claim instances, and `semantic_state.model.Claim`. A seventh key is a typo.
    """
    validator, _ = semantic_case_validator()
    good = fixture_cases()[0]
    assert validator.is_valid(good), "the control must validate first, or the negatives prove nothing"

    def first_claim(case):
        return next(iter(case["state_before"]["claims"].values()))

    typo = copy.deepcopy(good)
    first_claim(typo)["staus"] = "GIVEN"  # the misspelling that motivated closing it
    assert not validator.is_valid(typo), "a misspelled claim key was accepted"

    missing = copy.deepcopy(good)
    del first_claim(missing)["status"]
    assert not validator.is_valid(missing)

    for field, wrong_value in (
        ("id", 1),
        ("proposition", None),
        ("status", ["GIVEN"]),
        ("scope", ["global"]),  # unhashable: `set` membership in _scope raises TypeError
        ("domain", ["Integer"]),  # unhashable: the domain-lattice walk in _is_subtype raises
        ("dependencies", "p0"),
        ("dependencies", [["p0"]]),  # unhashable: used as a dict key in _dependency
    ):
        wrong = copy.deepcopy(good)
        first_claim(wrong)[field] = wrong_value
        assert not validator.is_valid(wrong), f"claim.{field} accepted {wrong_value!r}"

    # `domain: null` IS accepted: the canonical Claim types it `str | None`.
    nullable = copy.deepcopy(good)
    first_claim(nullable)["domain"] = None
    assert validator.is_valid(nullable), "claim.domain must admit null, per the canonical dataclass"


def test_state_region_values_are_validated_rather_than_merely_accepted():
    """`obligations`, `candidates`, `branches`, `goals` were `{"type": "object"}`.

    A region whose values are unchecked passes everything, including values that
    are not objects at all -- and a non-object obligation made the reference
    checker raise AttributeError instead of returning a verdict.
    """
    validator, schema = semantic_case_validator()
    good = fixture_cases()[0]
    assert validator.is_valid(good)

    for region, ref in (
        ("obligations", "#/$defs/obligation"),
        ("candidates", "#/$defs/candidate"),
        ("branches", "#/$defs/branch"),
        ("goals", "#/$defs/goal"),
    ):
        wiring = schema["$defs"]["state"]["properties"][region]
        assert wiring.get("additionalProperties", {}).get("$ref") == ref, f"{region} is not wired to a value schema"

        # Positive control first: the well-formed value must be accepted.
        populated = copy.deepcopy(good)
        populated["state_before"][region]["probe"] = copy.deepcopy(WELL_FORMED_REGION_VALUE[region])
        assert validator.is_valid(populated), f"a well-formed {region} value was rejected"

        for bad in (5, "x", [], None):
            broken = copy.deepcopy(good)
            broken["state_before"][region]["probe"] = bad
            assert not validator.is_valid(broken), f"{region} accepted a non-object value {bad!r}"

    # And the specific type confusions the reference checker cannot survive.
    for region, field, wrong_value in (
        ("obligations", "dependencies", "xc1y"),  # `output_id in "xc1y"` is a substring test
        ("obligations", "mandatory", 0),  # falsy: silently downgrades mandatory debt
        ("obligations", "status", ["OPEN"]),
        ("candidates", "constraint_ids", "p0"),  # `set("p0")` is a set of characters
        ("candidates", "status", 1),
        ("branches", "status", []),
        ("goals", "proposition", {}),
    ):
        broken = copy.deepcopy(good)
        value = copy.deepcopy(WELL_FORMED_REGION_VALUE[region])
        value[field] = wrong_value
        broken["state_before"][region]["probe"] = value
        assert not validator.is_valid(broken), f"{region} value accepted {field}={wrong_value!r}"


def test_action_sub_object_and_evidence_types_are_pinned():
    """The fifteen action sub-objects stay open, but their value types do not.

    Each shape below made `reference_checker.check_case` raise rather than return
    a verdict, on the pre-amendment schema. `semantic_case_v2.schema.json` $refs
    `#/$defs/action`, so these constraints bind FX2 too and were checked against
    all 268 action instances before being added.
    """
    validator, _ = semantic_case_validator()
    good = fixture_cases()[0]
    assert validator.is_valid(good)

    for path, wrong_value in (
        (("action", "output_id"), ["c1"]),
        (("action", "output_id"), 7),
        (("action", "dependencies"), [["p0"]]),
        (("action", "dependencies"), [1]),
        (("action", "preconditions"), ["pre0"]),
        (("action", "obligations_discharged"), ["o1"]),
        (("action", "warrant", "evidence_id"), ["e_source"]),
        (("action", "warrant", "rule"), 3),
        (("action", "candidate_effect", "candidate_id"), ["cand1"]),
        (("action", "goal_effect", "goal_id"), {}),
        (("action", "branch_effect", "branch_ids"), "b1"),  # a string iterates character by character
        (("action", "branch_effect", "coverage_evidence_id"), []),
        (("action", "epistemic_effect", "evidence_id"), {}),
        (("action", "scope_effect", "discharge_evidence_id"), 0),
        (("action", "typing", "input_domains"), ["p0"]),
    ):
        broken = copy.deepcopy(good)
        target = broken
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = wrong_value
        assert not validator.is_valid(broken), f"{'.'.join(path)} accepted {wrong_value!r}"

    # `output_id: null` is legitimate -- 11 FX2 actions use it, and the canonical
    # Action dataclass types it `str | None`. Guards against over-tightening.
    nullable = copy.deepcopy(good)
    nullable["action"]["output_id"] = None
    assert validator.is_valid(nullable), "action.output_id must admit null"

    for field, wrong_value in (
        ("trusted", "false"),
        ("trusted", 1),
        ("premise_ids", "p0"),
        ("checked_constraints", "p0"),
        ("branch_ids", "b1"),
        ("id", None),
    ):
        broken = copy.deepcopy(good)
        next(iter(broken["evidence"].values()))[field] = wrong_value
        assert not validator.is_valid(broken), f"evidence.{field} accepted {wrong_value!r}"

    missing = copy.deepcopy(good)
    del next(iter(missing["evidence"].values()))["kind"]
    assert not validator.is_valid(missing)

    for field, wrong_value in (("gold125_overlap", "false"), ("level", 4), ("problem", None)):
        broken = copy.deepcopy(good)
        broken["source"][field] = wrong_value
        assert not validator.is_valid(broken), f"source.{field} accepted {wrong_value!r}"

    missing_source_key = copy.deepcopy(good)
    del missing_source_key["source"]["solution_span_hash"]
    assert not validator.is_valid(missing_source_key)


def test_the_string_false_evidence_flag_is_the_reason_trusted_is_typed():
    """The one constraint here that changes a verdict rather than preventing a crash.

    `_epistemic` reads the flag as `not record.get("trusted")`. The boolean
    `false` correctly refuses the promotion; the STRING "false" is truthy, so it
    licensed VERIFIED. The schema is the only boundary that can tell them apart --
    `neutral.py` coerces with `bool(...)` and would agree with the mistake.
    """
    from experiments.semantic_firewall.reference_checker import check_case

    validator, _ = semantic_case_validator()
    legal = fixture_by_id("FX-EPI-LEGAL")["case"]
    assert validator.is_valid(legal)
    assert check_case(legal)["verdict"] == "VALID"

    evidence_id = legal["action"]["epistemic_effect"]["evidence_id"]

    honest = copy.deepcopy(legal)
    honest["evidence"][evidence_id]["trusted"] = False
    assert check_case(honest)["verdict"] == "INVALID"
    assert validator.is_valid(honest), "an honest boolean must remain schema-valid"

    disguised = copy.deepcopy(legal)
    disguised["evidence"][evidence_id]["trusted"] = "false"
    assert check_case(disguised)["verdict"] == "VALID", (
        "if the checker ever refuses this itself, this schema constraint stops being load-bearing"
    )
    assert not validator.is_valid(disguised), "the schema must refuse what the checker cannot see"


def test_the_objects_left_open_are_open_on_purpose_and_say_why():
    """Pin the holes. An undocumented hole and a decision look the same from outside.

    Each of these accepts an undeclared key today. That is the recorded outcome of
    the audit, not an oversight, and every one carries its reason in the schema's
    own `description`. If a later change closes one of them, this test fails and
    forces the reason to be revisited rather than silently discarded.
    """
    validator, schema = semantic_case_validator()
    good = fixture_cases()[0]
    assert validator.is_valid(good)

    for name, reason in DELIBERATELY_OPEN_DEFS.items():
        block = schema["$defs"][name]
        assert block.get("additionalProperties") is not False, f"$defs/{name} was closed; revisit: {reason}"
        assert len(block.get("description", "")) > 200, f"$defs/{name} is open without a recorded reason"

    typo_in_source = copy.deepcopy(good)
    typo_in_source["source"]["levl"] = "Level 4"
    assert validator.is_valid(typo_in_source), "source is open by decision; see $defs/source description"

    typo_in_evidence = copy.deepcopy(good)
    next(iter(typo_in_evidence["evidence"].values()))["trustd"] = True
    assert validator.is_valid(typo_in_evidence), "evidence is open by decision; a payload key is indistinguishable"

    extra_in_effect = copy.deepcopy(good)
    extra_in_effect["action"]["branch_effect"]["partition_note"] = "x"
    assert validator.is_valid(extra_in_effect), "the *_effect maps are named open in the canonical contract"

    # The one array left unconstrained, and the frozen fixture that forces it.
    created = schema["$defs"]["action"]["properties"]["obligations_created"]
    assert "items" not in created, "constraining this flips FX2-MAL-UNHASHABLE-REFUSE's declared schema_valid"
    assert "FX2-MAL-UNHASHABLE-REFUSE" in created["description"]
    unhashable = copy.deepcopy(good)
    unhashable["action"]["obligations_created"] = [[1], [2]]
    assert validator.is_valid(unhashable)


# ---------------------------------------------------------------------------
# FX2 — the second-generation suite
# ---------------------------------------------------------------------------

FX2_DIR = ROOT / "experiments" / "semantic_firewall_v2"


def _fx2_validator():
    """A validator for the v2 schema, with the frozen base registered so $refs resolve."""
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    base = json.loads(
        (ROOT / "experiments/semantic_firewall/schemas/semantic_case.schema.json").read_text()
    )
    v2 = json.loads((FX2_DIR / "schemas/semantic_case_v2.schema.json").read_text())
    Draft202012Validator.check_schema(v2)
    registry = Registry().with_resource(base["$id"], Resource.from_contents(base))
    return Draft202012Validator(v2, registry=registry), v2


def test_the_fx2_artifact_is_strict_rfc8259_json():
    """No NaN, no Infinity. An earlier build embedded a NaN literal and an independent
    parser rejected the entire file — the artifact must be readable by any conforming
    implementation, not only by the one that wrote it."""
    text = (FX2_DIR / "fixtures_v2.json").read_text()

    def refuse(literal):
        raise AssertionError(f"non-standard JSON literal in the artifact: {literal}")

    json.loads(text, parse_constant=refuse)


def test_every_fx2_case_validates_except_the_deliberately_malformed_ones():
    validator, _ = _fx2_validator()
    suite = json.loads((FX2_DIR / "fixtures_v2.json").read_text())
    for fixture in suite["fixtures"]:
        errors = sorted(validator.iter_errors(fixture["case"]), key=lambda e: list(e.path))
        if fixture["schema_valid"]:
            assert not errors, (
                f"{fixture['fixture_id']}: {errors[0].validator} at "
                f"{list(errors[0].absolute_path)}: {errors[0].message}"
            )
        else:
            assert errors, (
                f"{fixture['fixture_id']} is declared schema-invalid but validates; a MAL "
                f"fixture that passes a schema of well-formed cases is not testing anything"
            )


def test_the_fx2_schema_rejects_what_it_should():
    """Negative controls, so the FX2 validation cannot pass vacuously."""
    validator, _ = _fx2_validator()
    suite = json.loads((FX2_DIR / "fixtures_v2.json").read_text())
    control = next(f["case"] for f in suite["fixtures"] if f["schema_valid"])
    assert not list(validator.iter_errors(control)), "the control must validate first"

    for name, mutate in (
        ("extra action key", lambda c: c["action"].update(nonsense="x")),
        ("split claims to be ACCEPTANCE", lambda c: c.update(split="ACCEPTANCE")),
        ("unknown semantic_focus", lambda c: c.update(semantic_focus="NONSENSE")),
        ("fabricated MATH provenance", lambda c: c["source"].update(dataset="MATH")),
        ("id outside the FX2 namespace", lambda c: c.update(case_id="FX-DEP-LEGAL")),
    ):
        case = copy.deepcopy(control)
        mutate(case)
        assert list(validator.iter_errors(case)), f"{name} should have been rejected"


def test_the_fx2_manifest_hashes_match_the_files_it_names():
    manifest = json.loads((FX2_DIR / "manifest.json").read_text())
    for name, record in manifest["files"].items():
        path = FX2_DIR / name
        assert path.exists(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], name
        assert path.stat().st_size == record["bytes"], name


def test_fx2_does_not_touch_the_frozen_thirty():
    """The additive guarantee, checked rather than promised."""
    manifest = json.loads((FX2_DIR / "manifest.json").read_text())
    frozen = ROOT / "experiments/semantic_firewall/acceptance/fixtures.json"
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == manifest["extends"]["sha256"]
    original = {f["fixture_id"] for f in json.loads(frozen.read_text())["fixtures"]}
    fx2 = {f["fixture_id"] for f in json.loads((FX2_DIR / "fixtures_v2.json").read_text())["fixtures"]}
    assert not (original & fx2), "an FX2 id collides with a frozen fixture id"
    assert len(original) == 30
