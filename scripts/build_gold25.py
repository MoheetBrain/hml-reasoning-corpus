#!/usr/bin/env python3
"""Build the audited MATH Gold-25 semantic-discovery artifacts.

The raw parquet is read but never rewritten. This script contains the human-audited
selection and trajectory annotations; it intentionally emits neutral trajectories and
does not generate HML programs.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/math/train-00000-of-00001-7320a6f3aba8ebd2.parquet"
OUT = ROOT / "data/gold25"
TRAJ = OUT / "trajectories"
PROBLEM_REPORTS = ROOT / "reports/gold25"
GAP_REPORTS = ROOT / "reports/semantic_gaps/math_gold25"


SELECTED: list[dict[str, Any]] = [
    {"problem_id": "MATH-GOLD-001", "row": 0, "category": "Algebra", "selection_reason": "Piecewise continuity exposes equation construction at boundaries, coupled substitutions, and a hidden continuity precondition."},
    {"problem_id": "MATH-GOLD-002", "row": 380, "category": "Algebra", "selection_reason": "Combines variable introduction, an algebraic identity, exact evaluation, and a sign condition before square-root extraction."},
    {"problem_id": "MATH-GOLD-003", "row": 8680, "category": "Algebra", "selection_reason": "Compact equation solving with cross-multiplication, expansion, cancellation, and a denominator restriction."},
    {"problem_id": "MATH-GOLD-004", "row": 8508, "category": "Algebra", "selection_reason": "Explicit case split plus two candidate solutions and direct candidate verification."},
    {"problem_id": "MATH-GOLD-005", "row": 273, "category": "Algebra", "selection_reason": "Natural-language relations become a typed system of equations and then a substitution/elimination chain."},
    {"problem_id": "MATH-GOLD-006", "row": 4012, "category": "Intermediate Algebra", "selection_reason": "Logarithm change-of-base, domain precondition, coefficient normalization, and exponentiation."},
    {"problem_id": "MATH-GOLD-007", "row": 3469, "category": "Intermediate Algebra", "selection_reason": "Shows substitution, polynomial expansion/factoring, alternative derivation, and a result invariant across candidates."},
    {"problem_id": "MATH-GOLD-008", "row": 9744, "category": "Intermediate Algebra", "selection_reason": "A definition-driven parity proof requiring function composition and an implicit universal argument."},
    {"problem_id": "MATH-GOLD-009", "row": 3391, "category": "Intermediate Algebra", "selection_reason": "Theorem application with hypotheses, inequality lower bound, equality conditions, and witness construction."},
    {"problem_id": "MATH-GOLD-010", "row": 1745, "category": "Counting & Probability", "selection_reason": "Distinguishes identical from distinguishable objects through explicit combinatorial casework."},
    {"problem_id": "MATH-GOLD-011", "row": 1747, "category": "Counting & Probability", "selection_reason": "Complementary probability with sampling without replacement and exact fraction cancellation."},
    {"problem_id": "MATH-GOLD-012", "row": 1825, "category": "Counting & Probability", "selection_reason": "Finite-case decomposition, impossibility bound, permutation multiplicity, and probability aggregation."},
    {"problem_id": "MATH-GOLD-013", "row": 9107, "category": "Counting & Probability", "selection_reason": "Palindromic symmetry becomes independent digit choices with a leading-zero precondition."},
    {"problem_id": "MATH-GOLD-014", "row": 10603, "category": "Number Theory", "selection_reason": "Prime factorization and divisibility rules reduce a digit problem to constrained candidate selection."},
    {"problem_id": "MATH-GOLD-015", "row": 4963, "category": "Number Theory", "selection_reason": "Congruence construction, parameter substitution, lower-bound reasoning, and minimality verification."},
    {"problem_id": "MATH-GOLD-016", "row": 5222, "category": "Number Theory", "selection_reason": "Index translation across omitted squares exposes sequence-state reasoning and counting exclusions."},
    {"problem_id": "MATH-GOLD-017", "row": 4886, "category": "Number Theory", "selection_reason": "Prime-exponent representation and predicate intersection count admissible factors."},
    {"problem_id": "MATH-GOLD-018", "row": 7140, "category": "Precalculus", "selection_reason": "Named trigonometric theorem, exact radical algebra, rationalization, and normalization."},
    {"problem_id": "MATH-GOLD-019", "row": 7300, "category": "Precalculus", "selection_reason": "Complex-domain ambiguity, quadratic transformation, identity multiplication, and power propagation."},
    {"problem_id": "MATH-GOLD-020", "row": 7014, "category": "Precalculus", "selection_reason": "Vector bilinearity and symmetry cancel cross terms before norm substitution."},
    {"problem_id": "MATH-GOLD-021", "row": 2583, "category": "Geometry", "selection_reason": "Geometric theorem becomes an algebraic constraint followed by factorization and constructive witness selection."},
    {"problem_id": "MATH-GOLD-022", "row": 3384, "category": "Geometry", "selection_reason": "Geometric definitions generate an equation; radius positivity and factor-pair reasoning complete it."},
    {"problem_id": "MATH-GOLD-023", "row": 2646, "category": "Geometry", "selection_reason": "Triangle inequality creates a bounded integer domain and an exhaustive finite sum."},
    {"problem_id": "MATH-GOLD-024", "row": 5591, "category": "Prealgebra", "selection_reason": "A pure evaluation trajectory exposes precedence, left-to-right normalization, and arithmetic verification."},
    {"problem_id": "MATH-GOLD-025", "row": 5609, "category": "Prealgebra", "selection_reason": "Word-problem modeling, inequality transformation, integer rounding, and threshold verification."},
]


def pre(condition: str, status: str = "satisfied", evidence: str = "", source_omission: bool = False) -> dict[str, Any]:
    return {"condition": condition, "status": status, "evidence": evidence or ("Given or established in the current state." if status == "satisfied" else "The worked solution does not state this condition explicitly."), "source_omission": source_omission}


def obligation(oid: str, statement: str, status: str = "discharged", evidence: str = "", source_omission: bool = False) -> dict[str, Any]:
    return {"id": oid, "statement": statement, "status": status, "evidence": evidence or ("Discharged by the source's later check." if status == "discharged" else "Debt remains open in the source reconstruction."), "source_omission": source_omission}


def hs(status: str, constructs: list[str], notes: str) -> dict[str, Any]:
    return {"status": status, "constructs": constructs, "notes": notes}


def step(
    operation_id: str,
    source_span: str,
    result: str,
    *,
    family: str,
    explicitness: str = "explicit",
    arguments: dict[str, Any] | None = None,
    warrant_kind: str = "algebraic_validity",
    warrant: str = "The operation preserves the stated mathematical relation under its applicability conditions.",
    warrant_source: str = "derived",
    preconditions: list[dict[str, Any]] | None = None,
    creates: list[dict[str, Any]] | None = None,
    discharges: list[str] | None = None,
    dependencies: list[str] | None = None,
    verification_status: str = "verified",
    verification_category: str = "MANUAL_SEMANTIC_CHECK",
    verification_backend: str = "audited source reasoning",
    verification_notes: str = "The result follows from the recorded premises and the stated warrant.",
    hml: dict[str, Any] | None = None,
    gaps: list[str] | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    return {
        "operation_id": operation_id,
        "family": family,
        "source_span": source_span,
        "explicitness": explicitness,
        "arguments": arguments or {},
        "warrant": {"kind": warrant_kind, "description": warrant, "source": warrant_source},
        "preconditions": preconditions or [],
        "creates_obligations": creates or [],
        "discharges_obligations": discharges or [],
        "dependencies": dependencies or [],
        "result_statement": result,
        "verification": {"status": verification_status, "category": verification_category, "backend": verification_backend, "notes": verification_notes},
        "hml_support": hml or hs("REPRESENTABLE_ONLY", ["assume"], "The proposition can be written as state, but the operation is not a current trusted rule."),
        "semantic_gap_ids": gaps or [],
        "branch": branch,
    }


def initial(
    *,
    objects: list[str],
    declarations: list[str],
    types_domains: list[str],
    facts: list[tuple[str, str]],
    goals: list[tuple[str, str]],
    constraints: list[str] | None = None,
    definitions: list[str] | None = None,
    assumptions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "objects": objects,
        "declarations": declarations,
        "types_domains": types_domains,
        "facts": [{"id": fid, "statement": statement, "status": "given"} for fid, statement in facts],
        "assumptions": [{"id": f"assumption:{i}", "statement": x, "status": "assumed"} for i, x in enumerate(assumptions or [])],
        "constraints": constraints or [],
        "definitions": definitions or [],
        "goals": [{"id": gid, "statement": statement, "status": "goal_open"} for gid, statement in goals],
        "subgoals": [],
        "scope": ["global"],
        "dependencies": [],
        "open_obligations": [],
        "discharged_obligations": [],
        "epistemic_status": [],
    }


def hml_full(rule: str, notes: str = "Current HML has the corresponding trusted rule.") -> dict[str, Any]:
    return hs("FULL", [rule], notes)


def hml_partial(constructs: list[str], notes: str) -> dict[str, Any]:
    return hs("PARTIAL", constructs, notes)


def hml_repr(constructs: list[str], notes: str) -> dict[str, Any]:
    return hs("REPRESENTABLE_ONLY", constructs, notes)


def hml_absent(notes: str) -> dict[str, Any]:
    return hs("ABSENT", [], notes)


G = {
    "MATH-GOLD-001": {
        "initial": initial(objects=["piecewise function f", "a", "b"], declarations=["a : Real", "b : Real", "f : PiecewiseFunction"], types_domains=["a,b ∈ Real"], facts=[("fact:piecewise", "f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2")], goals=[("goal:answer", "a+b=0")], constraints=["continuity at x=2", "continuity at x=-2"]),
        "steps": [
            step("INTRODUCE_VARIABLE", "For the piecewise function to be continuous, the cases must \"meet\" at $2$ and $-2$.", "continuity reduces to matching adjacent branch values at x=2 and x=-2", family="DECLARATION", warrant_kind="definition_application", warrant="Apply the definition of continuity for a piecewise function at a boundary.", warrant_source="core", hml=hml_repr(["def", "assume"], "Definitions and assumptions can state the branches; no continuity theorem is in the kernel."), gaps=["MATH-GAP-0005"]),
            step("FORMULATE_EQUATION", "For example, $ax+3$ and $x-5$ must be equal when $x=2$.", "2a+3=-3", family="EQUATION_CONSTRUCTION", arguments={"boundary": 2}, warrant_kind="boundary_matching", warrant="Continuity requires equal one-sided branch values at the boundary.", warrant_source="derived", dependencies=["fact:piecewise"], hml=hml_repr(["assume"], "The equation is representable as an assumption, but boundary-continuity construction is not a rule."), gaps=["MATH-GAP-0005"]),
            step("SOLVE", "This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \\Rightarrow a=-3$.", "a=-3", family="ALGEBRAIC_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Subtract 3 and divide by the nonzero coefficient 2.", warrant_source="derived", dependencies=["fact:piecewise"], hml=hml_partial(["subtract_both_sides", "divide_both_sides"], "The transformations are kernel rules; the general solve operation is not."), gaps=["MATH-GAP-0006"]),
            step("FORMULATE_EQUATION", "Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$.", "-7=-4-b", family="EQUATION_CONSTRUCTION", arguments={"boundary": -2}, warrant_kind="boundary_matching", warrant="Continuity requires equal adjacent branch values at the second boundary.", warrant_source="derived", dependencies=["fact:piecewise"], hml=hml_repr(["assume"], "Representable proposition; no continuity/boundary rule."), gaps=["MATH-GAP-0005"]),
            step("SOLVE", "Substituting, we get $-2-5=2(-2)-b$, which implies $b=3$.", "b=3", family="ALGEBRAIC_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Substitute the boundary value and isolate b.", warrant_source="derived", dependencies=["fact:piecewise"], hml=hml_partial(["substitute", "add_both_sides"], "Only local equality transformations are trusted."), gaps=["MATH-GAP-0006"]),
            step("EVALUATE", "So $a+b=-3+3=\\boxed{0}$.", "a+b=0", family="EVALUATION", warrant_kind="exact_arithmetic", warrant="Evaluate the established parameter values exactly.", warrant_source="core", dependencies=["fact:a", "fact:b"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed arithmetic can be checked as evidence; it is not a kernel derivation."), gaps=["MATH-GAP-0006"]),
        ],
        "final_goal": "a+b=0",
    },
    "MATH-GOLD-002": {
        "initial": initial(objects=["x", "y"], declarations=["x : Integer", "y : Integer"], types_domains=["x,y are positive integers"], facts=[("fact:squares", "x²+y²=90"), ("fact:product", "xy=27")], goals=[("goal:answer", "x+y=12")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "Call the two integers $x$ and $y$.", "x and y denote the two positive integers", family="DECLARATION", warrant_kind="variable_binding", warrant="Name the objects already quantified by the problem.", warrant_source="explicit", hml=hs("FULL", ["var"], "HML can declare typed variables.")),
            step("RECORD_GIVEN", "We are given that $x^2 + y^2 = 90$ and that $xy = 27$.", "facts x²+y²=90 and xy=27 are active", family="STATE", warrant_kind="problem_translation", warrant="Translate the given numerical constraints into state facts.", warrant_source="explicit", hml=hml_repr(["assume"], "HML can record the facts but has no source-prose ingestion operation.")),
            step("APPLY_IDENTITY", "Note that $(x + y)^2 = x^2 + y^2 + 2xy = 90 + 2\\cdot 27 = 144$.", "(x+y)²=144", family="ALGEBRAIC_TRANSFORMATION", warrant_kind="polynomial_identity", warrant="Use the square-of-a-sum identity and substitute established facts.", warrant_source="library", dependencies=["fact:squares", "fact:product"], hml=hml_repr(["evidence"], "The exact evaluator cannot establish this open-variable identity; no kernel identity rule covers it."), gaps=["MATH-GAP-0006"]),
            step("EXTRACT_ROOT", "Taking the square root of 144, we see that $x + y = \\boxed{12}$.", "x+y=12", family="ALGEBRAIC_TRANSFORMATION", warrant_kind="nonnegative_root", warrant="Because x and y are positive, x+y is nonnegative, so the principal square root selects 12.", warrant_source="derived", preconditions=[pre("x+y≥0", evidence="x and y are positive integers from the problem.")], creates=[obligation("obl:root_sign", "x+y≥0 selects the principal square root", status="discharged", evidence="x and y are positive integers.")], dependencies=["fact:squares", "fact:product"], verification_category="VERIFIED_EXACT", verification_backend="exact arithmetic plus sign reasoning", hml=hml_partial(["closed_eval_v1", "evidence"], "HML can check closed 144=12², but not the free-variable identity and sign-directed root step."), gaps=["MATH-GAP-0003", "MATH-GAP-0004", "MATH-GAP-0006"]),
        ],
        "final_goal": "x+y=12",
    },
    "MATH-GOLD-003": {
        "initial": initial(objects=["x"], declarations=["x : Real"], types_domains=["x ∈ Real"], facts=[("fact:eq", "2/3=4/(x-5)")], goals=[("goal:answer", "x=11")]),
        "steps": [
            step("CROSS_MULTIPLY", "Multiplying both sides by $x-5$ and by 3 gives $2(x-5) = 4(3)$.", "2(x-5)=12", family="EQUATION_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Multiply both sides by the common factors.", warrant_source="derived", preconditions=[pre("x-5≠0", status="implicit", source_omission=True), pre("3≠0")], creates=[obligation("obl:denominator", "x-5≠0", status="discharged", evidence="The resulting solution x=11 makes x-5=6≠0.", source_omission=True)], dependencies=["fact:eq"], hml=hml_partial(["multiply_both_sides", "partiality"], "HML can multiply both sides; denominator obligations are term-level, but cross-multiplication as a compound operation is absent."), gaps=["MATH-GAP-0003"]),
            step("EXPAND", "Expanding the left side gives $2x-10 = 12$.", "2x-10=12", family="ALGEBRAIC_TRANSFORMATION", warrant_kind="distributive_law", warrant="Apply the distributive law.", warrant_source="library", dependencies=["fact:eq"], hml=hml_repr(["evidence"], "No trusted symbolic expansion rule is registered."), gaps=["MATH-GAP-0006"]),
            step("ADD_BOTH_SIDES", "Adding 10 to both sides gives $2x = 22$", "2x=22", family="EQUATION_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Add the same term to both sides.", warrant_source="core", dependencies=["fact:eq"], hml=hml_full("add_both_sides")),
            step("DIVIDE_BOTH_SIDES", "and dividing by 2 gives $x = \\boxed{11}$.", "x=11", family="EQUATION_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Divide both sides by the nonzero coefficient 2.", warrant_source="core", preconditions=[pre("2≠0")], dependencies=["fact:eq"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_full("divide_both_sides", "The division rule is current; its obligation is discharged by the literal nonzero divisor.")),
        ],
        "final_goal": "x=11",
    },
    "MATH-GOLD-004": {
        "initial": initial(objects=["x"], declarations=["x : Real"], types_domains=["x ∈ Real"], facts=[("fact:abs", "|5x-1|=x+3")], goals=[("goal:answer", "largest solution x=1")]),
        "steps": [
            step("CASE_SPLIT", "We can split the expression $|5x-1|=x+3$ into two separate cases.", "case 1: 5x-1=x+3; case 2: 5x-1=-(x+3)", family="CASE_ANALYSIS", warrant_kind="absolute_value_definition", warrant="Apply the two-branch definition of absolute value.", warrant_source="core", preconditions=[pre("x+3≥0", status="implicit", source_omission=True)], creates=[obligation("obl:abs_case_cover", "the absolute-value branches are exhaustive and disjoint", status="discharged", evidence="The nonnegative/nonpositive definition of absolute value partitions the argument.", source_omission=True)], hml=hml_partial(["scope"], "Lexical scope exists, but no case-split rule proves branch exhaustiveness or manages branch joins."), gaps=["MATH-GAP-0001", "MATH-GAP-0002", "MATH-GAP-0004"] ),
            step("SOLVE_CASE", "5x-1&=x+3", "case 1 yields x=1", family="CASE_ANALYSIS", explicitness="implicit", arguments={"branch": "x≥1/5"}, warrant_kind="equality_preservation", warrant="Solve the branch equation under its sign condition.", warrant_source="derived", dependencies=["fact:abs"], hml=hml_partial(["subtract_both_sides", "divide_both_sides"], "Local algebra is available, but branch-scoped derivation is not a single current rule."), gaps=["MATH-GAP-0001"]),
            step("VERIFY_CANDIDATE", "If we plug this value of $x$ back into the original equation in order to check our answer, we see that $|5(1)-1|=1+3$ or $4=4$.", "candidate x=1 satisfies the original equation", family="VERIFICATION", warrant_kind="substitution_check", warrant="Re-evaluate the original equation at the generated candidate.", warrant_source="explicit", dependencies=["fact:abs"], verification_category="VERIFIED_EXACT", verification_backend="exact arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed candidate checks can be certified, but candidate-generation/branch linkage is not kernel-native."), gaps=["MATH-GAP-0002"] , branch="case 1"),
            step("SOLVE_CASE", "5x-1&=-(x+3)", "case 2 yields x=-1/3", family="CASE_ANALYSIS", explicitness="implicit", arguments={"branch": "x<1/5"}, warrant_kind="equality_preservation", warrant="Solve the second branch equation under its sign condition.", warrant_source="derived", dependencies=["fact:abs"], hml=hml_partial(["add_both_sides", "divide_both_sides"], "Local algebra is available; branch proof remains partial."), gaps=["MATH-GAP-0001"], branch="case 2"),
            step("VERIFY_CANDIDATE", "If we plug $-\\frac13$ back into the initial equation, we get that", "candidate x=-1/3 satisfies the original equation", family="VERIFICATION", warrant_kind="substitution_check", warrant="Re-evaluate the original equation at the second generated candidate.", warrant_source="explicit", dependencies=["fact:abs"], verification_category="VERIFIED_EXACT", verification_backend="exact arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed candidate checks can be certified; branch bookkeeping is external."), gaps=["MATH-GAP-0002"], branch="case 2"),
            step("SELECT_EXTREMUM", "the final answer is the larger of the two", "largest valid solution is x=1", family="GOAL_MANAGEMENT", warrant_kind="finite_order", warrant="Compare the verified finite candidate set.", warrant_source="derived", dependencies=["fact:candidate_1", "fact:candidate_2"], hml=hml_repr(["goal"], "HML has goals but no finite-candidate selection rule."), gaps=["MATH-GAP-0002"]),
        ],
        "final_goal": "largest solution x=1",
    },
    "MATH-GOLD-005": {
        "initial": initial(objects=["A", "B", "J"], declarations=["A : Natural", "B : Natural", "J : Natural"], types_domains=["ages are nonnegative integers"], facts=[], goals=[("goal:answer", "B=3")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "First, let $A = $ Addison's age, $B = $ Brenda's age, and $J = $ Janet's age.", "A, B, J are named age variables", family="DECLARATION", warrant_kind="variable_binding", warrant="Name the quantities in the prose problem.", warrant_source="explicit", hml=hs("FULL", ["var"], "Typed declarations are native; the prose-to-symbol step is external.")),
            step("FORMULATE_EQUATION", "Then, from the statements given, we have the following system of equations:", "A=3B, J=B+6, A=J", family="EQUATION_CONSTRUCTION", warrant_kind="problem_translation", warrant="Translate each verbal relation into an equation.", warrant_source="explicit", hml=hml_repr(["assume"], "HML can record the equations but has no prose relation extractor.")),
            step("SUBSTITUTE", "Since $A=J$, we know that $3B=B+6$.", "3B=B+6", family="SUBSTITUTION", warrant_kind="equality_substitution", warrant="Replace equal quantities in the first relation using A=J.", warrant_source="core", dependencies=["fact:system"], hml=hml_full("substitute", "The trusted substitute rule is structural and local.")),
            step("SOLVE", "Solving this equation, we have that $2B = 6 \\Rightarrow B=3$.", "B=3", family="EQUATION_TRANSFORMATION", warrant_kind="equality_preservation", warrant="Subtract B and divide by the nonzero coefficient 2.", warrant_source="derived", preconditions=[pre("2≠0")], dependencies=["fact:system"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["subtract_both_sides", "divide_both_sides"], "Local transformations are native; the full solve trajectory is not.")),
            step("DISCHARGE_GOAL", "Thus, Brenda is $\\boxed{3}$ years old.", "goal B=3 discharged", family="GOAL_MANAGEMENT", warrant_kind="goal_matching", warrant="The derived value matches the requested quantity.", warrant_source="explicit", dependencies=["fact:B"], hml=hs("FULL", ["goal", "proved"], "Goal discharge is native once a matching verified derivation exists.")),
        ],
        "final_goal": "B=3",
    },
    "MATH-GOLD-006": {
        "initial": initial(objects=["x"], declarations=["x : Real"], types_domains=["x>0 for logarithms"], facts=[("fact:log_eq", "log₂x+log₄x=6")], goals=[("goal:answer", "x=16")]),
        "steps": [
            step("APPLY_DEFINITION", "to turn $\\log_4 x$ into", "log₄x=(1/2)log₂x", family="DEFINITION_APPLICATION", warrant_kind="change_of_base", warrant="Apply the change-of-base theorem with valid positive log arguments and bases not equal to 1.", warrant_source="library", preconditions=[pre("x>0", status="implicit", source_omission=True), pre("2>0 and 2≠1"), pre("4>0 and 4≠1")], dependencies=["fact:log_eq"], hml=hml_repr(["evidence"], "No trusted logarithm theorem/library is present in the core."), gaps=["MATH-GAP-0003", "MATH-GAP-0007"]),
            step("COMBINE_LIKE_TERMS", "That means that $\\frac{3}{2}\\log_2 x=6.", "(3/2)log₂x=6", family="ALGEBRAIC_TRANSFORMATION", explicitness="implicit", warrant_kind="coefficient_collection", warrant="Collect equal logarithm terms.", warrant_source="derived", dependencies=["fact:log_eq"], hml=hml_repr(["evidence"], "Open-variable symbolic normalization is not a trusted kernel rule."), gaps=["MATH-GAP-0007"]),
            step("SOLVE", "Dividing each side by $\\frac{3}{2},", "log₂x=4 and x=2⁴", family="EQUATION_TRANSFORMATION", warrant_kind="inverse_function", warrant="Undo the logarithm using the definition of base-2 logarithm.", warrant_source="library", preconditions=[pre("2>0 and 2≠1")], dependencies=["fact:log_eq"], hml=hml_repr(["evidence"], "Logarithm inversion is not a current HML rule."), gaps=["MATH-GAP-0007"]),
            step("EVALUATE", "Thus, $x = \\boxed{16}", "x=16", family="EVALUATION", warrant_kind="exact_arithmetic", warrant="Evaluate 2⁴ exactly.", warrant_source="core", verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "The closed numeric result is certifiable, separate from logarithm reasoning.")),
        ],
        "final_goal": "x=16",
    },
    "MATH-GOLD-007": {
        "initial": initial(objects=["x", "y"], declarations=["x : Real", "y : Real"], types_domains=["x,y ∈ Real"], facts=[("fact:diff", "x-y=4"), ("fact:cubes", "x³-y³=28")], goals=[("goal:answer", "xy=-3")]),
        "steps": [
            step("SUBSTITUTE", "The first equation gives $x = y+4$.", "x=y+4", family="SUBSTITUTION", warrant_kind="equality_preservation", warrant="Add y to both sides of x-y=4.", warrant_source="core", dependencies=["fact:diff"], hml=hml_partial(["add_both_sides"], "Native equality transformation can express this local step.")),
            step("SUBSTITUTE", "Substituting into the second equation, we get", "(y+4)³-y³=28", family="SUBSTITUTION", warrant_kind="equality_substitution", warrant="Replace x by y+4 in the cubic equation.", warrant_source="core", dependencies=["fact:diff", "fact:cubes"], hml=hml_full("substitute")),
            step("EXPAND", "12y^2 + 48y + 36 = 0.", "12y²+48y+36=0", family="ALGEBRAIC_TRANSFORMATION", explicitness="implicit", warrant_kind="polynomial_expansion", warrant="Expand and collect polynomial terms.", warrant_source="library", dependencies=["fact:cubes"], hml=hml_repr(["evidence"], "No trusted symbolic polynomial expansion rule."), gaps=["MATH-GAP-0006"]),
            step("FACTOR", "Thus, $y^2 + 4y + 3 = 0$, so $(y+1)(y+3) = 0$.", "(y+1)(y+3)=0", family="ALGEBRAIC_TRANSFORMATION", explicitness="implicit", warrant_kind="factorization", warrant="Scale the equation and factor the quadratic.", warrant_source="library", dependencies=["fact:cubes"], hml=hml_repr(["evidence"], "Symbolic factorization is not trusted in current HML."), gaps=["MATH-GAP-0006"]),
            step("CASE_SPLIT", "Therefore, either $y=-1$ and $x=y+4=3$, or $y=-3$ and $x=y+4=1$.", "candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3)", family="CASE_ANALYSIS", warrant_kind="zero_product_property", warrant="A product is zero only when at least one factor is zero, then recover x by substitution.", warrant_source="library", dependencies=["fact:diff", "fact:cubes"], hml=hml_partial(["scope"], "Case scopes exist, but no zero-product/case coverage rule is in the kernel."), gaps=["MATH-GAP-0001", "MATH-GAP-0007"]),
            step("EVALUATE", "Either way, $xy = \\boxed{-3}$.", "both candidates yield xy=-3", family="EVALUATION", warrant_kind="case_invariant", warrant="Evaluate the requested expression in every surviving branch.", warrant_source="derived", dependencies=["fact:candidate_1", "fact:candidate_2"], verification_category="VERIFIED_EXACT", verification_backend="exact arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed branch-local arithmetic is checkable; branch merge is not native."), gaps=["MATH-GAP-0001"]),
        ],
        "final_goal": "xy=-3",
    },
    "MATH-GOLD-008": {
        "initial": initial(objects=["f", "g", "x"], declarations=["f : Function", "g : Function", "x : Real"], types_domains=["f even: f(-u)=f(u)", "g odd: g(-u)=-g(u)"], facts=[("fact:parity_f", "f is even"), ("fact:parity_g", "g is odd")], goals=[("goal:answer", "f(g(x³)) is even")]),
        "steps": [
            step("APPLY_DEFINITION", "Substituting $-x$ for $x$ gives us $f(g(-x^3)) = f(-g(x^3)) = f(g(x^3))$", family="DEFINITION_APPLICATION", result="h(-x)=h(x) for h(x)=f(g(x³))", warrant_kind="parity_definition", warrant="Apply oddness of g and evenness of f to the transformed input.", warrant_source="library", dependencies=["fact:parity_f", "fact:parity_g"], hml=hml_repr(["evidence"], "HML can state the parity claims but has no registered function-parity theorem."), gaps=["MATH-GAP-0007"]),
            step("DISCHARGE_GOAL", "so $f(g(x^3))$ is $\\boxed{\\text{even}}$.", "goal parity even discharged", family="GOAL_MANAGEMENT", warrant_kind="definition_matching", warrant="The transformed expression equals the original under x↦-x.", warrant_source="derived", dependencies=["fact:parity_f", "fact:parity_g"], hml=hml_repr(["goal", "evidence"], "Goal syntax exists; the functional extensionality/parity proof is library-level."), gaps=["MATH-GAP-0007"]),
        ],
        "final_goal": "f(g(x³)) is even",
    },
    "MATH-GOLD-009": {
        "initial": initial(objects=["x", "y", "z"], declarations=["x : PositiveReal", "y : PositiveReal", "z : PositiveReal"], types_domains=["x,y,z>0"], facts=[("fact:product", "xyz=8")], goals=[("goal:answer", "min(x+2y+4z)=12")]),
        "steps": [
            step("APPLY_THEOREM", "By AM-GM,", "x+2y+4z ≥ 3∛((x)(2y)(4z))", family="THEOREM_APPLICATION", warrant_kind="AM_GM", warrant="Apply AM-GM to the three positive quantities x, 2y, and 4z.", warrant_source="library", preconditions=[pre("x>0,y>0,z>0", evidence="Given in the problem."), pre("three positive terms", evidence="x,2y,4z are positive.")], dependencies=["fact:product"], hml=hml_repr(["evidence"], "AM-GM is not a core HML rule or trusted library checker."), gaps=["MATH-GAP-0007"]),
            step("EVALUATE", "= 3 \\sqrt[3]{8xyz} = 3 \\sqrt[3]{8 \\cdot 8} = 12.", "x+2y+4z≥12", family="EVALUATION", warrant_kind="exact_arithmetic", warrant="Substitute xyz=8 and evaluate the exact cube root.", warrant_source="derived", dependencies=["fact:product"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Only the closed numeric subexpression is directly certifiable."), gaps=["MATH-GAP-0007"]),
            step("RECORD_EQUALITY_CONDITION", "Equality occurs when $x = 2y = 4z$ and $xyz = 8.$", "equality condition x=2y=4z", family="THEOREM_APPLICATION", warrant_kind="AM_GM_equality", warrant="Use the equality condition of AM-GM together with the product constraint.", warrant_source="library", dependencies=["fact:product"], hml=hml_repr(["evidence"], "The equality condition requires theorem-library semantics."), gaps=["MATH-GAP-0007"]),
            step("SOLVE", "We can solve to get $x = 4,$ $y = 2,$ and $z = 1,", "witness (x,y,z)=(4,2,1) attains 12", family="CONSTRUCTION", warrant_kind="constraint_solving", warrant="Solve the equality condition and verify the product constraint.", warrant_source="derived", dependencies=["fact:product"], verification_category="VERIFIED_EXACT", verification_backend="exact arithmetic", hml=hml_partial(["evidence"], "HML can record the witness and closed checks but cannot invoke AM-GM."), gaps=["MATH-GAP-0007"]),
        ],
        "final_goal": "min(x+2y+4z)=12",
    },
    "MATH-GOLD-010": {
        "initial": initial(objects=["red marble", "green marble", "blue marble", "three identical yellow marbles"], declarations=["multiset of 6 marbles"], types_domains=["yellow marbles indistinguishable; other colors distinguishable"], facts=[("fact:inventory", "R,G,B,Y,Y,Y")], goals=[("goal:answer", "number of distinct 2-marble groups=7")]),
        "steps": [
            step("CASE_SPLIT", "There are two cases here: either Tom chooses two yellow marbles (1 result), or he chooses two marbles of different colors", family="CASE_ANALYSIS", result="case Y/Y; case two distinct colors", warrant_kind="combinatorial_partition", warrant="Partition the outcomes by whether the indistinguishable yellow multiplicity is used twice.", warrant_source="explicit", hml=hml_partial(["scope"], "Scope exists, but HML has no combinatorial case partition or branch coverage rule."), gaps=["MATH-GAP-0001", "MATH-GAP-0008"]),
            step("COUNT_CASES", "$\\binom{4}{2}=6$ results", family="COMBINATORIAL_REASONING", result="six distinct-color pairs", warrant_kind="combination_count", warrant="Choose two colors from the four available color classes.", warrant_source="library", dependencies=["fact:inventory"], hml=hml_repr(["evidence"], "No combinatorial counting library is trusted by current HML."), gaps=["MATH-GAP-0008"]),
            step("COMBINE_CASE_COUNTS", "The total number of distinct pairs of marbles Tom can choose is", family="COMBINATORIAL_REASONING", explicitness="implicit", result="total=7", warrant_kind="disjoint_sum", warrant="Add counts of disjoint cases.", warrant_source="derived", dependencies=["fact:case_yy", "fact:case_colors"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "The closed addition is checkable; the case semantics are not native."), gaps=["MATH-GAP-0001", "MATH-GAP-0008"]),
        ],
        "final_goal": "number of distinct 2-marble groups=7",
    },
    "MATH-GOLD-011": {
        "initial": initial(objects=["7 men", "3 women", "three selected people"], declarations=["finite population"], types_domains=["sampling without replacement"], facts=[("fact:population", "7 men and 3 women"), ("fact:sample", "sample size 3")], goals=[("goal:answer", "P(at least one woman)=17/24")]),
        "steps": [
            step("COMPLEMENT_COUNT", "We can find the probability that no women are selected and subtract it from 1", family="PROBABILISTIC_REASONING", result="target = 1-P(no women)", warrant_kind="complement_rule", warrant="For a binary event partition, P(at least one woman)=1-P(no woman).", warrant_source="library", dependencies=["fact:population", "fact:sample"], hml=hml_repr(["evidence"], "Probability complement reasoning is not a core HML rule."), gaps=["MATH-GAP-0008"]),
            step("CONDITIONAL_PROBABILITY", "the chance that the first person selected is male is $\\frac{7}{10}$.", family="PROBABILISTIC_REASONING", result="P(first male)=7/10", warrant_kind="uniform_sampling", warrant="Count favorable men over the population size.", warrant_source="derived", dependencies=["fact:population"], hml=hml_repr(["evidence"], "Finite-sampling probability lacks a trusted domain library."), gaps=["MATH-GAP-0008"]),
            step("CONDITIONAL_PROBABILITY", "Then the probability that the second person selected is male is reduced to $\\frac{6}{9}=\\frac{2}{3}$.", family="PROBABILISTIC_REASONING", result="P(second male | first male)=2/3", warrant_kind="without_replacement_update", warrant="Update the population after one male has been selected.", warrant_source="derived", dependencies=["fact:population"], hml=hml_repr(["evidence"], "Conditional probability update is library-level."), gaps=["MATH-GAP-0008"]),
            step("CONDITIONAL_PROBABILITY", "For the third person, the probability is $\\frac{5}{8}$.", family="PROBABILISTIC_REASONING", result="P(third male | first two male)=5/8", warrant_kind="without_replacement_update", warrant="Update counts after two male selections.", warrant_source="derived", dependencies=["fact:population"], hml=hml_repr(["evidence"], "Conditional probability update is library-level."), gaps=["MATH-GAP-0008"]),
            step("MULTIPLY_CONDITIONALS", "So the probability that only men are selected is $$\\frac{7}{10}\\cdot\\frac{2}{3}\\cdot\\frac{5}{8}=\\frac{7}{24}.$$", family="PROBABILISTIC_REASONING", result="P(no women)=7/24", warrant_kind="chain_rule", warrant="Multiply the successive conditional probabilities.", warrant_source="library", dependencies=["fact:population", "fact:sample"], hml=hml_repr(["evidence"], "Conditional-product semantics are not a core rule."), gaps=["MATH-GAP-0008"]),
            step("COMPLEMENT_COUNT", "Now we subtract from 1 to find the probability that at least one woman is selected. The probability is $1-\\frac{7}{24}=\\boxed{\\frac{17}{24}}$.", family="PROBABILISTIC_REASONING", result="P(at least one woman)=17/24", warrant_kind="complement_rule", warrant="Subtract the exact complement from one.", warrant_source="derived", dependencies=["fact:no_women"], verification_category="VERIFIED_EXACT", verification_backend="exact rational arithmetic", hml=hml_partial(["closed_eval_v1"], "Numeric fraction arithmetic is checkable after the probability law is supplied."), gaps=["MATH-GAP-0008"]),
        ],
        "final_goal": "P(at least one woman)=17/24",
    },
    "MATH-GOLD-012": {
        "initial": initial(objects=["three six-sided dice"], declarations=["D1,D2,D3 : {1,2,3,4,5,6}"], types_domains=["independent fair dice"], facts=[("fact:sample_space", "6³ equally likely ordered outcomes"), ("fact:target", "D1+D2+D3=16")], goals=[("goal:answer", "probability=1/36")]),
        "steps": [
            step("BOUND_REASONING", "At least one of the dice must come up 6, since otherwise the best we can do is 15.", family="CASE_ANALYSIS", result="at least one die is 6", warrant_kind="upper_bound", warrant="The sum of three values at most 5 is at most 15.", warrant_source="derived", dependencies=["fact:target"], hml=hml_repr(["assume", "evidence"], "Bound reasoning over finite domains is not a core rule."), gaps=["MATH-GAP-0008"]),
            step("CONSTRAINT_PROPAGATION", "The other two dice must add up to 10.", family="CASE_ANALYSIS", result="remaining two dice sum to 10", warrant_kind="arithmetic_constraint", warrant="Subtract the required 6 contribution from the target sum.", warrant_source="derived", dependencies=["fact:target"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed arithmetic is checkable; finite-domain propagation is not."), gaps=["MATH-GAP-0008"]),
            step("ENUMERATE", "There are two ways two dice add to 10: $4+6$ and $5+5$.", family="CASE_ANALYSIS", result="patterns (6,6,4) and (6,5,5)", warrant_kind="finite_exhaustion", warrant="Enumerate all pairs in {1,…,6} summing to 10, up to order.", warrant_source="derived", creates=[obligation("obl:dice_case_cover", "the listed dice patterns exhaust the finite pairs summing to 10", status="discharged", evidence="The bounded pair enumeration lists 4+6 and 5+5.", source_omission=True)], dependencies=["fact:target"], hml=hml_repr(["scope"], "No finite enumeration rule or completeness certificate exists."), gaps=["MATH-GAP-0001", "MATH-GAP-0004", "MATH-GAP-0008"]),
            step("COUNT_PERMUTATIONS", "A) The dice are 6, 6, 4.", family="COMBINATORIAL_REASONING", result="case A has 3 ordered outcomes", warrant_kind="permutation_count", warrant="Choose which die shows 4; the two 6s are identical.", warrant_source="derived", dependencies=["fact:target"], hml=hml_repr(["evidence"], "Permutation counting is library-level."), gaps=["MATH-GAP-0008"], branch="case A"),
            step("EVALUATE_PROBABILITY", "There are three possible ways this can happen, and the probability of each is $(1/6)^3 = 1/216$.", family="PROBABILISTIC_REASONING", result="P(case A)=3/216=1/72", warrant_kind="uniform_product_space", warrant="Each ordered triple has probability 1/216; multiply by the case multiplicity.", warrant_source="library", dependencies=["fact:sample_space"], hml=hml_repr(["evidence"], "Finite probability and multiplicity need a domain library."), gaps=["MATH-GAP-0008"], branch="case A"),
            step("COUNT_PERMUTATIONS", "B) The dice are 6, 5, 5.", family="COMBINATORIAL_REASONING", result="case B has 3 ordered outcomes", warrant_kind="permutation_count", warrant="Choose which die shows 6; the two 5s are identical.", warrant_source="derived", dependencies=["fact:target"], hml=hml_repr(["evidence"], "Permutation counting is library-level."), gaps=["MATH-GAP-0008"], branch="case B"),
            step("EVALUATE_PROBABILITY", "So, the probability of this case is $3(1/216) = 1/72$.", family="PROBABILISTIC_REASONING", result="P(case B)=3/216=1/72", warrant_kind="uniform_product_space", warrant="Use the same ordered-outcome probability for case B.", warrant_source="library", dependencies=["fact:sample_space"], hml=hml_repr(["evidence"], "Finite probability and multiplicity need a domain library."), gaps=["MATH-GAP-0008"], branch="case B"),
            step("COMBINE_CASE_COUNTS", "Adding the probabilities of these two cases gives us a total probability of $\\frac{1}{72} + \\frac{1}{72} = \\boxed{\\frac{1}{36}}$.", family="PROBABILISTIC_REASONING", result="P(sum=16)=1/36", warrant_kind="disjoint_case_sum", warrant="The cases are disjoint and exhaustive, so add their probabilities.", warrant_source="derived", dependencies=["fact:case_A", "fact:case_B"], verification_category="VERIFIED_EXACT", verification_backend="exact rational arithmetic", hml=hml_partial(["closed_eval_v1"], "The final rational sum is checkable after case semantics are supplied."), gaps=["MATH-GAP-0001", "MATH-GAP-0004", "MATH-GAP-0008"]),
        ],
        "final_goal": "probability=1/36",
    },
    "MATH-GOLD-013": {
        "initial": initial(objects=["four digit positions"], declarations=["digits d1,d2,d3,d4 : {0,…,9}"], types_domains=["d1≠0"], facts=[("fact:palindrome", "d1=d4 and d2=d3")], goals=[("goal:answer", "count=90")]),
        "steps": [
            step("APPLY_DEFINITION", "In a four-digit palindrome, the first digit is the same as the last, and the second digit is the same as the third digit.", family="DEFINITION_APPLICATION", result="free choices are d1 and d2; d4=d1,d3=d2", warrant_kind="palindrome_definition", warrant="Apply the definition of a four-digit palindrome.", warrant_source="explicit", dependencies=["fact:palindrome"], hml=hml_repr(["assume"], "HML can state equalities but has no counting-by-symmetry rule."), gaps=["MATH-GAP-0008"]),
            step("COUNT_CASES", "There are 9 options for the first/last digit (1 through 9 -- the first digit cannot be 0)", family="COMBINATORIAL_REASONING", result="d1 has 9 choices", warrant_kind="leading_digit_constraint", warrant="A four-digit number cannot begin with zero.", warrant_source="explicit", preconditions=[pre("d1≠0")], dependencies=["fact:palindrome"], hml=hml_repr(["evidence"], "Finite digit-choice counting is library-level."), gaps=["MATH-GAP-0008"]),
            step("COUNT_CASES", "and there are 10 options for the second/third digit (0 through 9).", family="COMBINATORIAL_REASONING", result="d2 has 10 choices", warrant_kind="independent_digit_choice", warrant="The repeated inner digit may be any decimal digit.", warrant_source="derived", dependencies=["fact:palindrome"], hml=hml_repr(["evidence"], "Finite digit-choice counting is library-level."), gaps=["MATH-GAP-0008"]),
            step("MULTIPLY_COUNTS", "This gives us $9 \\cdot 10 = \\boxed{90}$ four-digit palindromes.", family="COMBINATORIAL_REASONING", result="count=90", warrant_kind="product_rule", warrant="Multiply independent choices for the two free positions.", warrant_source="library", dependencies=["fact:palindrome"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "The multiplication is closed and checkable; the combinatorial product rule is not native."), gaps=["MATH-GAP-0008"]),
        ],
        "final_goal": "count=90",
    },
    "MATH-GOLD-014": {
        "initial": initial(objects=["digit n"], declarations=["n : Digit"], types_domains=["n∈{0,…,9}"], facts=[("fact:number", "374n"), ("fact:divisor", "18=2·3²")], goals=[("goal:answer", "n=4")]),
        "steps": [
            step("APPLY_DEFINITION", "We know that the prime factorization of 18 is $2\\cdot 3^2$, so in order for the four digit number to be divisible by 18 it must also be divisible by 9 and 2.", family="THEOREM_APPLICATION", result="374n must be divisible by 9 and by 2", warrant_kind="divisibility_factorization", warrant="A number divisible by 18 is divisible by each prime-power factor 2 and 9.", warrant_source="library", dependencies=["fact:number", "fact:divisor"], hml=hml_repr(["evidence"], "Number-theoretic divisibility theorems are not trusted core rules."), gaps=["MATH-GAP-0009"]),
            step("APPLY_THEOREM", "In order for a number to be divisible by 9, the sum of its digits must be divisible by 9 as well.", family="THEOREM_APPLICATION", result="14+n is divisible by 9", warrant_kind="digit_sum_rule", warrant="Apply the base-10 divisibility-by-9 theorem.", warrant_source="library", dependencies=["fact:number"], hml=hml_repr(["evidence"], "Digit-sum divisibility requires a number-theory library."), gaps=["MATH-GAP-0009"]),
            step("BOUND_SEARCH", "Thus, $3+7+4+n$, or $14+n$, must be divisible by 9.", family="CONSTRAINT_REASONING", result="14+n ∈ {18,27} under digit bound", warrant_kind="finite_digit_domain", warrant="Use n∈{0,…,9} to bound the possible multiples of 9.", warrant_source="derived", preconditions=[pre("0≤n≤9")], dependencies=["fact:number"], hml=hml_repr(["evidence"], "Finite constraint search is not a kernel operation."), gaps=["MATH-GAP-0009"]),
            step("SELECT_CANDIDATE", "Since 18 is the smallest multiple of 9 that is greater than 10, $14+n=18$, and $n=18-14=\\boxed{4}$.", family="CONSTRAINT_REASONING", result="n=4", warrant_kind="minimal_candidate", warrant="Select the digit-compatible multiple and compute n.", warrant_source="derived", preconditions=[pre("374n divisible by 2", status="implicit", source_omission=True)], dependencies=["fact:number"], verification_category="VERIFIED_EXACT", verification_backend="exact divisibility check", verification_notes="The source omits the final explicit evenness check; 3744 is even and divisible by 9, so the conclusion is valid.", hml=hml_repr(["evidence"], "Divisibility and finite digit search are library-level."), gaps=["MATH-GAP-0009"]),
        ],
        "final_goal": "n=4",
    },
    "MATH-GOLD-015": {
        "initial": initial(objects=["a", "n"], declarations=["a : Natural", "n : Natural"], types_domains=["a>0, n≥0"], facts=[("fact:congruence_5", "a≡4 mod 5"), ("fact:congruence_7", "a≡6 mod 7")], goals=[("goal:answer", "smallest a=34")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "Let the desired number be $a$.", family="DECLARATION", result="a names the desired positive integer", warrant_kind="variable_binding", warrant="Name the unknown integer.", warrant_source="explicit", hml=hs("FULL", ["var"], "Typed declaration is native.")),
            step("PARAMETERIZE_CONGRUENCE", "The first congruence means that there exists a non-negative integer $n$ such that $a=4+5n$.", family="NUMBER_THEORY", result="a=4+5n for n≥0", warrant_kind="congruence_definition", warrant="Unpack a≡4 (mod 5) into an integer parameterization.", warrant_source="library", dependencies=["fact:congruence_5"], hml=hml_repr(["evidence"], "Congruence parameterization is not a core rule."), gaps=["MATH-GAP-0009"]),
            step("SUBSTITUTE", "Substituting this into the second congruence yields \\[4+5n\\equiv 6\\pmod 7\\implies n\\equiv 6\\pmod 7\\]", family="NUMBER_THEORY", result="n≡6 mod 7", warrant_kind="modular_substitution", warrant="Substitute the parameterization and reduce modulo 7.", warrant_source="library", dependencies=["fact:congruence_5", "fact:congruence_7"], hml=hml_repr(["evidence"], "No trusted modular arithmetic rule."), gaps=["MATH-GAP-0009"]),
            step("BOUND_SEARCH", "So $n$ has a lower bound of $6$.", family="CONSTRAINT_REASONING", result="n≥6", warrant_kind="least_residue", warrant="Use n≥0 and n≡6 mod 7 to identify the least admissible n.", warrant_source="derived", preconditions=[pre("n≥0")], dependencies=["fact:congruence_7"], hml=hml_repr(["evidence"], "Minimality over congruence classes is not native."), gaps=["MATH-GAP-0009"]),
            step("EVALUATE", "Then $n\\ge 6\\implies a=4+5n\\ge 34$.", family="CONSTRAINT_REASONING", result="a≥34", warrant_kind="monotonicity", warrant="The affine expression increases with n.", warrant_source="derived", dependencies=["fact:congruence_5"], hml=hml_repr(["evidence"], "Symbolic monotonicity is not a core rule."), gaps=["MATH-GAP-0006"]),
            step("VERIFY_CANDIDATE", "$\\boxed{34}$ is the smallest solution since it is a lower bound of $a$ and satisfies both original congruences.", family="VERIFICATION", result="a=34 is minimal and satisfies both congruences", warrant_kind="candidate_verification", warrant="Check the lower-bound candidate against both original modular constraints.", warrant_source="explicit", dependencies=["fact:congruence_5", "fact:congruence_7"], verification_category="VERIFIED_EXACT", verification_backend="exact modular arithmetic", hml=hml_repr(["evidence"], "Candidate verification over congruences is not a trusted checker."), gaps=["MATH-GAP-0002", "MATH-GAP-0009"]),
        ],
        "final_goal": "smallest a=34",
    },
    "MATH-GOLD-016": {
        "initial": initial(objects=["sequence of positive integers excluding squares"], declarations=["a_k : Natural"], types_domains=["a_k is increasing; perfect squares omitted"], facts=[("fact:index", "target index k=200")], goals=[("goal:answer", "a_200=214")]),
        "steps": [
            step("COUNT_EXCLUDED", "When 200 is reached in the sequence of non-square positive integers, all the perfect squares from $1^2$ up to $14^2$ have been omitted.", family="SEQUENCE_REASONING", result="14 squares are omitted before the target value", warrant_kind="counting_exclusions", warrant="Count the perfect squares below 200 using 1² through 14².", warrant_source="derived", dependencies=["fact:index"], hml=hml_repr(["evidence"], "Sequence indexing with excluded values is not a core rule."), gaps=["MATH-GAP-0010"]),
            step("INDEX_TRANSLATION", "Therefore, 200 is the 186th term.", family="SEQUENCE_REASONING", result="value 200 has sequence index 186", warrant_kind="index_shift", warrant="Subtract the 14 omitted values from the ambient integer index.", warrant_source="derived", dependencies=["fact:index"], hml=hml_repr(["evidence"], "Index translation is not executable in current HML."), gaps=["MATH-GAP-0010"]),
            step("ADVANCE_SEQUENCE", "The 187th term is 201", family="SEQUENCE_REASONING", result="a_200=214", warrant_kind="successor_iteration", warrant="Advance 14 positions after 200; none of 201–214 is a square.", warrant_source="derived", preconditions=[pre("201,…,214 are nonsquares", status="implicit", source_omission=True)], dependencies=["fact:index"], verification_category="VERIFIED_EXACT", verification_backend="finite exact check", hml=hml_repr(["evidence"], "Finite sequence iteration is not a trusted HML operation."), gaps=["MATH-GAP-0010"]),
        ],
        "final_goal": "a_200=214",
    },
    "MATH-GOLD-017": {
        "initial": initial(objects=["positive factors of 72"], declarations=["m : Natural"], types_domains=["m|72 and m is a perfect cube"], facts=[("fact:factorization", "72=2³·3²")], goals=[("goal:answer", "count=2")]),
        "steps": [
            step("PRIME_FACTORIZE", "Prime factorize $72$ as $2^3\\cdot 3^2$.", family="NUMBER_THEORY", result="72=2³·3²", warrant_kind="unique_factorization", warrant="Use unique prime factorization.", warrant_source="library", hml=hml_repr(["evidence"], "Prime factorization is not a current HML rule."), gaps=["MATH-GAP-0009"]),
            step("APPLY_DEFINITION", "A positive integer is a factor of 72 if and only if the exponents in its prime factorization are less than or equal to the corresponding exponents in the prime factorization of 72.", family="NUMBER_THEORY", result="factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2", warrant_kind="factor_definition", warrant="Apply the prime-exponent characterization of divisors.", warrant_source="library", dependencies=["fact:factorization"], hml=hml_repr(["evidence"], "Divisor-set construction is library-level."), gaps=["MATH-GAP-0009"]),
            step("APPLY_DEFINITION", "Also, a positive integer is a perfect cube if and only if every exponent is a multiple of 3.", family="NUMBER_THEORY", result="e₂,e₃ must be multiples of 3", warrant_kind="perfect_power_definition", warrant="Apply the exponent characterization of perfect cubes.", warrant_source="library", dependencies=["fact:factorization"], hml=hml_repr(["evidence"], "Perfect-power theorem is not in the core."), gaps=["MATH-GAP-0009"]),
            step("COUNT_CASES", "Therefore, in forming a perfect cube factor of 72", family="NUMBER_THEORY", result="admissible exponent choices: e₂∈{0,3}, e₃=0", warrant_kind="finite_constraint_intersection", warrant="Intersect divisor bounds with cube-exponent constraints.", warrant_source="derived", dependencies=["fact:factorization"], hml=hml_repr(["evidence"], "Finite exponent enumeration is library-level."), gaps=["MATH-GAP-0008", "MATH-GAP-0009"]),
            step("COMBINE_CASE_COUNTS", "There are $2\\cdot 1=\\boxed{2}$ ways to make these choices.", family="NUMBER_THEORY", result="count=2", warrant_kind="product_rule", warrant="Multiply independent exponent-choice counts.", warrant_source="derived", dependencies=["fact:factorization"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Numeric multiplication is checkable after number-theory semantics are supplied."), gaps=["MATH-GAP-0009"]),
        ],
        "final_goal": "count=2",
    },
    "MATH-GOLD-018": {
        "initial": initial(objects=["angle 75°"], declarations=["angle : Real"], types_domains=["angles in degrees"], facts=[("fact:angle_split", "75°=45°+30°"), ("fact:special", "tan45°=1, tan30°=1/√3")], goals=[("goal:answer", "tan75°=2+√3")]),
        "steps": [
            step("APPLY_THEOREM", "From the angle addition formula,", family="THEOREM_APPLICATION", result="tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°)", warrant_kind="tangent_addition", warrant="Apply the tangent addition formula; denominator must be nonzero.", warrant_source="library", preconditions=[pre("1-tan45°tan30°≠0", status="implicit", source_omission=True)], hml=hml_repr(["evidence"], "No trusted trigonometric identity library exists in current HML."), gaps=["MATH-GAP-0007"]),
            step("SUBSTITUTE", r"= \frac{1 + \frac{1}{\sqrt{3}}}{1 - \frac{1}{\sqrt{3}}}", family="SUBSTITUTION", result="tan75°=(1+1/√3)/(1-1/√3)", warrant_kind="special_value_substitution", warrant="Substitute exact special-angle values.", warrant_source="library", dependencies=["fact:special"], hml=hml_repr(["evidence"], "Exact radicals are representable, but the trig facts are library-level."), gaps=["MATH-GAP-0007"]),
            step("RATIONALIZE", r"= \frac{\sqrt{3} + 1}{\sqrt{3} - 1}", family="ALGEBRAIC_TRANSFORMATION", result="tan75°=(√3+1)/(√3-1)", warrant_kind="radical_normalization", warrant="Multiply numerator and denominator by √3 to clear the fractional radicals, preserving the ratio because √3-1≠0.", warrant_source="derived", preconditions=[pre("√3-1≠0", status="implicit", source_omission=True)], hml=hml_repr(["evidence"], "Symbolic radical rationalization is not a trusted kernel rule."), gaps=["MATH-GAP-0003", "MATH-GAP-0006"]),
            step("EVALUATE", r"= \frac{3 + 2 \sqrt{3} + 1}{2}", family="EVALUATION", result="tan75°=2+√3", warrant_kind="exact_radical_arithmetic", warrant="Expand and normalize the exact radical expression.", warrant_source="derived", verification_category="VERIFIED_EXACT", verification_backend="exact radical arithmetic", hml=hml_repr(["evidence"], "Closed exact arithmetic is partly available, but symbolic radical normalization is not."), gaps=["MATH-GAP-0006"]),
        ],
        "final_goal": "tan75°=2+√3",
    },
    "MATH-GOLD-019": {
        "initial": initial(objects=["x"], declarations=["x : Complex"], types_domains=["x≠0"], facts=[("fact:reciprocal", "x+1/x=√3")], goals=[("goal:answer", "x¹⁸=-1")]),
        "steps": [
            step("CLEAR_DENOMINATOR", "We can rewrite the given equation as $x^2 - \\sqrt{3} x + 1 = 0$", family="EQUATION_TRANSFORMATION", result="x²-√3x+1=0", warrant_kind="denominator_clearing", warrant="Multiply by x, using x≠0.", warrant_source="derived", preconditions=[pre("x≠0", evidence="The original expression 1/x requires x≠0.")], dependencies=["fact:reciprocal"], hml=hml_partial(["multiply_both_sides", "partiality"], "Multiplication and denominator obligations exist; complex quadratic solving is absent."), gaps=["MATH-GAP-0003", "MATH-GAP-0007"]),
            step("SOLVE", "so by the quadratic formula,", family="THEOREM_APPLICATION", result="x=(√3±i)/2", warrant_kind="quadratic_formula", warrant="Apply the quadratic formula over the complex numbers.", warrant_source="library", dependencies=["fact:reciprocal"], hml=hml_repr(["evidence"], "Quadratic formula and complex-number solving require a library."), gaps=["MATH-GAP-0007"]),
            step("APPLY_IDENTITY", "which means $x = e^{\\pi i/6}$ or $x = e^{11 \\pi i/6}$.", family="THEOREM_APPLICATION", result="two unit-complex candidate forms", warrant_kind="polar_form", warrant="Convert the two complex roots to exponential/polar form.", warrant_source="library", dependencies=["fact:reciprocal"], hml=hml_repr(["evidence"], "Complex polar conversion is not a core HML rule."), gaps=["MATH-GAP-0007"]),
            step("CASE_SPLIT", "If $x = e^{\\pi i/6}$, then", family="CASE_ANALYSIS", result="branch 1 x¹⁸=e^{3πi}=-1", warrant_kind="case_evaluation", warrant="Evaluate the target power in the first root branch.", warrant_source="derived", dependencies=["fact:reciprocal"], hml=hml_partial(["scope"], "Scope exists but no complex-power case evaluator."), gaps=["MATH-GAP-0001", "MATH-GAP-0007"], branch="root 1"),
            step("CASE_SPLIT", "and if $x = e^{11 \\pi i/6}$, then", family="CASE_ANALYSIS", result="branch 2 x¹⁸=e^{33πi}=-1", warrant_kind="case_evaluation", warrant="Evaluate the target power in the second root branch.", warrant_source="derived", dependencies=["fact:reciprocal"], hml=hml_partial(["scope"], "Scope exists but no complex-power case evaluator."), gaps=["MATH-GAP-0001", "MATH-GAP-0007"], branch="root 2"),
            step("COMBINE_CASES", "In either case, $x^{18} = \\boxed{-1}$.", family="GOAL_MANAGEMENT", result="both branches give x¹⁸=-1", warrant_kind="case_invariant", warrant="Merge the two complete root cases because their target values agree.", warrant_source="derived", creates=[obligation("obl:root_case_join", "both complex-root branches are covered before the invariant is global", status="discharged", evidence="The two quadratic roots are enumerated and both yield -1.", source_omission=True)], dependencies=["fact:root_1", "fact:root_2"], hml=hml_repr(["goal"], "No branch-merge or complex-equality rule."), gaps=["MATH-GAP-0001", "MATH-GAP-0004", "MATH-GAP-0007"]),
        ],
        "final_goal": "x¹⁸=-1",
    },
    "MATH-GOLD-020": {
        "initial": initial(objects=["vectors a,b"], declarations=["a,b : Vector"], types_domains=["||a||=3, ||b||=6"], facts=[("fact:norm_a", "||a||=3"), ("fact:norm_b", "||b||=6")], goals=[("goal:answer", "(a+b)·(a-b)=-27")]),
        "steps": [
            step("EXPAND", "Expanding the dot product, we get", family="ALGEBRAIC_TRANSFORMATION", result="(a+b)·(a-b)=a·a+b·a-a·b-b·b", warrant_kind="bilinearity", warrant="Apply bilinearity of the dot product.", warrant_source="library", dependencies=["fact:norm_a", "fact:norm_b"], hml=hml_repr(["evidence"], "Vector bilinearity is not in the HML kernel."), gaps=["MATH-GAP-0007"]),
            step("CANCEL_SYMMETRIC_TERMS", "= \\mathbf{a} \\cdot \\mathbf{a} - \\mathbf{b} \\cdot \\mathbf{b}", family="ALGEBRAIC_TRANSFORMATION", explicitness="implicit", result="cross terms cancel", warrant_kind="dot_product_symmetry", warrant="Use a·b=b·a to cancel the cross terms.", warrant_source="library", dependencies=["fact:norm_a", "fact:norm_b"], hml=hml_repr(["evidence"], "Vector symmetry/cancellation is library-level."), gaps=["MATH-GAP-0007"]),
            step("APPLY_DEFINITION", "= \\|\\mathbf{a}\\|^2 - \\|\\mathbf{b}\\|^2", family="DEFINITION_APPLICATION", explicitness="implicit", result="||a||²-||b||²", warrant_kind="norm_definition", warrant="Use a·a=||a||² and b·b=||b||².", warrant_source="library", dependencies=["fact:norm_a", "fact:norm_b"], hml=hml_repr(["evidence"], "Vector norm definitions are not trusted core constructs."), gaps=["MATH-GAP-0007"]),
            step("EVALUATE", r"= 3^2 - 6^2 = \boxed{-27}.", family="EVALUATION", result="(a+b)·(a-b)=-27", warrant_kind="exact_arithmetic", warrant="Substitute the given norms and evaluate.", warrant_source="derived", dependencies=["fact:norm_a", "fact:norm_b"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "The closed scalar arithmetic is checkable after vector identities are supplied."), gaps=["MATH-GAP-0007"]),
        ],
        "final_goal": "(a+b)·(a-b)=-27",
    },
    "MATH-GOLD-021": {
        "initial": initial(objects=["right triangle", "x"], declarations=["x : Natural"], types_domains=["legs x and x+1; hypotenuse 29"], facts=[("fact:hypotenuse", "c=29"), ("fact:consecutive", "legs are x and x+1")], goals=[("goal:answer", "leg sum=41")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "Let's call the length of the shorter leg $x$. Then the length of the longer leg is $x + 1$.", family="DECLARATION", result="legs x and x+1", warrant_kind="consecutive_integer_definition", warrant="Parameterize consecutive whole-number legs by x and x+1.", warrant_source="explicit", preconditions=[pre("x≥1")], hml=hs("FULL", ["var"], "Variable declarations are native; consecutiveness is a constraint.")),
            step("FORMULATE_EQUATION", "Using the Pythagorean Theorem, we write the equation $x^2 + (x + 1)^2 = 29^2$", family="EQUATION_CONSTRUCTION", result="x²+(x+1)²=29²", warrant_kind="pythagorean_theorem", warrant="Apply the Pythagorean theorem to a right triangle.", warrant_source="library", dependencies=["fact:hypotenuse", "fact:consecutive"], hml=hml_repr(["evidence"], "The theorem is not a trusted HML rule."), gaps=["MATH-GAP-0007"]),
            step("EXPAND", "Expanding $(x + 1)^2$, we get", family="ALGEBRAIC_TRANSFORMATION", result="2x²+2x+1=841", warrant_kind="polynomial_expansion", warrant="Expand the square and evaluate 29².", warrant_source="derived", dependencies=["fact:hypotenuse"], hml=hml_repr(["evidence"], "Symbolic expansion is not a trusted kernel rule."), gaps=["MATH-GAP-0006"]),
            step("FACTOR", "This can be simplified to $2x^2 + 2x = 840$, or $x^2 + x = 420$.", family="ALGEBRAIC_TRANSFORMATION", result="x(x+1)=420", warrant_kind="factorization", warrant="Collect terms, divide by 2, and factor out x.", warrant_source="derived", preconditions=[pre("2≠0")], dependencies=["fact:hypotenuse"], hml=hml_partial(["divide_both_sides"], "The scalar division is native; symbolic factoring is not."), gaps=["MATH-GAP-0006"]),
            step("SELECT_CANDIDATE", "Indeed, $20 \\times 21 = 420$, so the legs must be 20 and 21.", family="CONSTRUCTION", result="legs=(20,21)", warrant_kind="finite_factor_search", warrant="Select the consecutive positive factor pair solving x(x+1)=420.", warrant_source="derived", preconditions=[pre("x and x+1 are positive consecutive integers")], dependencies=["fact:consecutive"], hml=hml_repr(["evidence"], "Finite factor search has no trusted HML rule."), gaps=["MATH-GAP-0009"]),
            step("EVALUATE", "Their sum is $20 + 21 = \\boxed{41}$.", family="EVALUATION", result="leg sum=41", warrant_kind="exact_arithmetic", warrant="Add the two established leg lengths.", warrant_source="derived", verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed arithmetic is checkable."), gaps=[]),
        ],
        "final_goal": "leg sum=41",
    },
    "MATH-GOLD-022": {
        "initial": initial(objects=["circle", "r", "x", "y"], declarations=["r : PositiveReal", "x,y : Real"], types_domains=["x=πr², y=2πr, r>0"], facts=[("fact:sum", "x+y=80π")], goals=[("goal:answer", "r=8")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "If $r$ is the radius of the circle, we know that $x = \\pi r^2$ and $y = 2\\pi r$.", family="DEFINITION_APPLICATION", result="area=πr² and circumference=2πr", warrant_kind="geometric_definition", warrant="Apply the definitions of circle area and circumference.", warrant_source="library", preconditions=[pre("r>0")], hml=hml_repr(["assume"], "Geometric formulas are representable but not a trusted theorem library."), gaps=["MATH-GAP-0007"]),
            step("FORMULATE_EQUATION", "Thus, we have \\begin{align*}", family="EQUATION_CONSTRUCTION", result="r(r+2)=80", warrant_kind="definition_substitution", warrant="Substitute the geometric formulas and cancel π≠0.", warrant_source="derived", preconditions=[pre("π≠0", status="implicit", source_omission=True)], dependencies=["fact:sum"], hml=hml_repr(["evidence"], "Symbolic formula substitution and cancellation are not a single trusted rule."), gaps=["MATH-GAP-0006"]),
            step("FACTOR", "We want to find two integers whose product is 80, such that one integer is two more than the other.", family="ALGEBRAIC_TRANSFORMATION", result="seek consecutive-offset factor pair (r,r+2)", warrant_kind="factor_pair_reasoning", warrant="Interpret the quadratic product constraint over positive r.", warrant_source="implicit", explicitness="implicit", dependencies=["fact:sum"], hml=hml_repr(["evidence"], "Factor-pair search is not a core rule."), gaps=["MATH-GAP-0006", "MATH-GAP-0009"]),
            step("SELECT_CANDIDATE", "We note that 80 can be factored as $8\\cdot 10$. Therefore, $r = \\boxed{8}$.", family="CONSTRUCTION", result="r=8", warrant_kind="positive_root_selection", warrant="Choose the positive factor-pair root; the other quadratic root is negative.", warrant_source="derived", preconditions=[pre("r>0")], dependencies=["fact:sum"], verification_category="VERIFIED_EXACT", verification_backend="exact algebra", hml=hml_repr(["evidence"], "Positive-root selection requires symbolic polynomial reasoning."), gaps=["MATH-GAP-0006"]),
        ],
        "final_goal": "r=8",
    },
    "MATH-GOLD-023": {
        "initial": initial(objects=["sticks 5cm, 9cm, ncm"], declarations=["n : Natural"], types_domains=["n is a whole-number side length"], facts=[("fact:sides", "5,9,n form a triangle")], goals=[("goal:answer", "sum of valid n=81")]),
        "steps": [
            step("APPLY_THEOREM", "Using the Triangle Inequality", family="THEOREM_APPLICATION", result="4<n<14", warrant_kind="triangle_inequality", warrant="A triangle exists exactly when each side is less than the sum of the other two; with sides 5 and 9 this bounds n.", warrant_source="library", dependencies=["fact:sides"], hml=hml_repr(["evidence"], "Triangle inequality is not a trusted core theorem."), gaps=["MATH-GAP-0007"]),
            step("ENUMERATE", "so $n$ can be any integer from $5$ to $13,$ inclusive.", family="CONSTRAINT_REASONING", result="valid n={5,6,7,8,9,10,11,12,13}", warrant_kind="integer_interval_enumeration", warrant="Intersect the open real interval with the integer domain.", warrant_source="derived", preconditions=[pre("n∈Natural")], dependencies=["fact:sides"], hml=hml_repr(["evidence"], "Finite interval enumeration is not native."), gaps=["MATH-GAP-0010"]),
            step("EVALUATE", "The sum can be calculated in several ways, but regardless", family="EVALUATION", explicitness="implicit", result="sum=81", warrant_kind="finite_sum", warrant="Sum every valid integer exactly once.", warrant_source="derived", dependencies=["fact:sides"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "The final arithmetic is checkable; interval derivation is not."), gaps=["MATH-GAP-0010"]),
        ],
        "final_goal": "sum of valid n=81",
    },
    "MATH-GOLD-024": {
        "initial": initial(objects=["closed arithmetic expression"], declarations=[], types_domains=["integer arithmetic"], facts=[("fact:expression", "1+6·2-3+5·4÷2")], goals=[("goal:answer", "value=20")]),
        "steps": [
            step("APPLY_PRECEDENCE", "When solving this problem, we must remember to apply the order of operations.", family="EVALUATION", result="multiplication/division precede addition/subtraction", warrant_kind="operator_precedence", warrant="Apply the conventional precedence relation.", warrant_source="explicit", hml=hml_repr(["closed_eval_v1"], "HML can evaluate a closed expression but does not expose a source-level precedence transition."), gaps=["MATH-GAP-0006"]),
            step("EVALUATE", "First, we perform all cases of multiplication and division from left to right to obtain", family="EVALUATION", result="1+12-3+20÷2", warrant_kind="exact_arithmetic", warrant="Evaluate the multiplication 6·2 while preserving the remaining expression.", warrant_source="explicit", dependencies=["fact:expression"], hml=hml_partial(["closed_eval_v1"], "Exact closed arithmetic is supported as evidence.")),
            step("EVALUATE", "20\\div 2", family="EVALUATION", explicitness="implicit", result="1+12-3+10", warrant_kind="exact_arithmetic", warrant="Evaluate 20÷2 exactly.", warrant_source="explicit", dependencies=["fact:expression"], hml=hml_partial(["closed_eval_v1"], "Exact closed arithmetic is supported as evidence.")),
            step("EVALUATE", "Next, we perform all the required additions and subtractions from left to right.", family="EVALUATION", result="13-3+10=10+10", warrant_kind="operator_precedence", warrant="Evaluate addition and subtraction left-to-right after higher-precedence operations.", warrant_source="explicit", dependencies=["fact:expression"], hml=hml_partial(["closed_eval_v1"], "The evaluator can check the final closed expression, not expose each provenance-preserving microstep.")),
            step("DISCHARGE_GOAL", r"&=\boxed{20}.", family="EVALUATION", explicitness="implicit", result="value=20", warrant_kind="exact_arithmetic", warrant="Evaluate the final closed expression.", warrant_source="explicit", dependencies=["fact:expression"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed exact evaluation is current HML capability.")),
        ],
        "final_goal": "value=20",
    },
    "MATH-GOLD-025": {
        "initial": initial(objects=["phone plans", "x minutes"], declarations=["x : Natural"], types_domains=["x is a whole number of minutes"], facts=[("fact:plan_A", "cost_A=10x cents"), ("fact:plan_B", "cost_B=2000+5x cents")], goals=[("goal:answer", "minimum x=401")]),
        "steps": [
            step("INTRODUCE_VARIABLE", "Let $x$ be the number of minutes that Bob anticipates using.", family="DECLARATION", result="x denotes minutes", warrant_kind="variable_binding", warrant="Name the unknown usage count.", warrant_source="explicit", hml=hs("FULL", ["var"], "Typed variable declaration is native.")),
            step("FORMULATE_EQUATION", "Plan A costs $10x$ cents, while Plan B costs $2000 + 5x$ cents.", family="EQUATION_CONSTRUCTION", result="cost_A=10x; cost_B=2000+5x", warrant_kind="word_problem_modeling", warrant="Translate price schedules into affine cost functions.", warrant_source="explicit", hml=hml_repr(["def", "assume"], "HML can record cost functions but has no prose modeling operation.")),
            step("FORMULATE_INEQUALITY", "We therefore have the inequality", family="INEQUALITY_TRANSFORMATION", result="2000+5x<10x", warrant_kind="comparison_goal", warrant="Plan B is cheaper exactly when its cost is strictly below Plan A.", warrant_source="explicit", dependencies=["fact:plan_A", "fact:plan_B"], hml=hml_repr(["goal", "assume"], "Inequalities are representable; source-model construction is external.")),
            step("SUBTRACT_BOTH_SIDES", "We therefore have the inequality", family="INEQUALITY_TRANSFORMATION", explicitness="implicit", result="x>400", warrant_kind="order_preserving_affine_transform", warrant="Subtract 5x and divide by positive 5, preserving inequality direction.", warrant_source="core", preconditions=[pre("5>0")], dependencies=["fact:plan_A", "fact:plan_B"], hml=hml_partial(["add_inequality", "multiply_inequality"], "Current kernel supports some inequality transformations; this compound normalization is partial."), gaps=["MATH-GAP-0006"]),
            step("ROUND_TO_DOMAIN", "The smallest integer $x$ such that $400 < x$ is $401$.", family="CONSTRAINT_REASONING", result="minimum whole-number x=401", warrant_kind="integer_ceiling", warrant="Select the least natural number strictly above 400.", warrant_source="derived", preconditions=[pre("x∈Natural")], dependencies=["fact:plan_A", "fact:plan_B"], hml=hml_repr(["evidence"], "Integer threshold selection is not a current kernel rule."), gaps=["MATH-GAP-0010"]),
            step("VERIFY_CANDIDATE", "Therefore, Bob must use at least", family="VERIFICATION", result="x=401 satisfies cost_B<cost_A and is minimal", warrant_kind="candidate_verification", warrant="Check the candidate in the original inequality and use the strict threshold for minimality.", warrant_source="derived", creates=[obligation("obl:threshold_minimality", "x=401 is the least natural number satisfying x>400", status="discharged", evidence="The strict inequality gives x>400 and 401 is the next integer.", source_omission=True)], dependencies=["fact:plan_A", "fact:plan_B"], verification_category="VERIFIED_EXACT", verification_backend="exact integer arithmetic", hml=hml_partial(["closed_eval_v1"], "Closed cost comparison is checkable; integer minimality is not a core rule."), gaps=["MATH-GAP-0002", "MATH-GAP-0004", "MATH-GAP-0010"]),
        ],
        "final_goal": "minimum x=401",
    },
}


OP_META: dict[str, dict[str, Any]] = {
    "INTRODUCE_VARIABLE": {"family": "DECLARATION", "description": "Name a mathematical object and assign a type/domain.", "required_inputs": ["source object or quantity"], "allowed_types": ["scalar", "function", "finite object"], "warrant_type": "variable_binding", "scope_behavior": "adds a name to current scope", "hml_rule": "var/param", "hml_support_status": "FULL"},
    "RECORD_GIVEN": {"family": "STATE", "description": "Move source-given information into active state facts.", "required_inputs": ["problem statement"], "allowed_types": ["proposition", "equation"], "warrant_type": "problem_translation", "scope_behavior": "global fact", "hml_rule": "assume", "hml_support_status": "REPRESENTABLE_ONLY"},
    "FORMULATE_EQUATION": {"family": "EQUATION_CONSTRUCTION", "description": "Construct an equation or inequality from verbal/geometric relations.", "required_inputs": ["objects", "relations"], "allowed_types": ["equation", "inequality"], "warrant_type": "problem_translation", "scope_behavior": "global or current branch", "hml_rule": "assume/goal", "hml_support_status": "REPRESENTABLE_ONLY"},
    "FORMULATE_INEQUALITY": {"family": "EQUATION_CONSTRUCTION", "description": "Construct a comparison encoding the requested optimization or threshold.", "required_inputs": ["costs or bounds", "goal relation"], "allowed_types": ["inequality"], "warrant_type": "comparison_goal", "scope_behavior": "global", "hml_rule": "goal/assume", "hml_support_status": "REPRESENTABLE_ONLY"},
    "APPLY_IDENTITY": {"family": "THEOREM_APPLICATION", "description": "Apply a general algebraic or structural identity.", "required_inputs": ["expression", "identity"], "allowed_types": ["expression"], "warrant_type": "identity", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "APPLY_THEOREM": {"family": "THEOREM_APPLICATION", "description": "Invoke a named mathematical theorem with hypotheses.", "required_inputs": ["theorem", "hypotheses", "target"], "allowed_types": ["proposition", "expression"], "warrant_type": "theorem", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "SUBSTITUTE": {"family": "SUBSTITUTION", "description": "Replace equal or defined content in a target expression.", "required_inputs": ["equality/definition", "target"], "allowed_types": ["expression", "proposition"], "warrant_type": "equality_substitution", "scope_behavior": "must avoid binder capture", "hml_rule": "substitute", "hml_support_status": "FULL"},
    "CROSS_MULTIPLY": {"family": "EQUATION_TRANSFORMATION", "description": "Clear denominators by multiplying both sides.", "required_inputs": ["equation", "denominators"], "allowed_types": ["equation"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": "multiply_both_sides + partiality", "hml_support_status": "PARTIAL"},
    "CLEAR_DENOMINATOR": {"family": "EQUATION_TRANSFORMATION", "description": "Remove a denominator under a nonzero precondition.", "required_inputs": ["equation", "nonzero denominator"], "allowed_types": ["equation"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": "multiply_both_sides", "hml_support_status": "PARTIAL"},
    "ADD_BOTH_SIDES": {"family": "EQUATION_TRANSFORMATION", "description": "Add the same term to both sides.", "required_inputs": ["equality", "term"], "allowed_types": ["equation", "inequality"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": "add_both_sides", "hml_support_status": "FULL"},
    "SUBTRACT_BOTH_SIDES": {"family": "EQUATION_TRANSFORMATION", "description": "Subtract the same term from both sides.", "required_inputs": ["equality", "term"], "allowed_types": ["equation", "inequality"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": "subtract_both_sides", "hml_support_status": "FULL"},
    "DIVIDE_BOTH_SIDES": {"family": "EQUATION_TRANSFORMATION", "description": "Divide both sides by a nonzero quantity.", "required_inputs": ["equality", "nonzero divisor"], "allowed_types": ["equation"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": "divide_both_sides", "hml_support_status": "FULL"},
    "EXPAND": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Apply distributivity or polynomial expansion.", "required_inputs": ["expression"], "allowed_types": ["polynomial", "product"], "warrant_type": "distributive_law", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "FACTOR": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Rewrite an expression as a product or factorized form.", "required_inputs": ["expression"], "allowed_types": ["polynomial", "integer"], "warrant_type": "factorization", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "RATIONALIZE": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Clear a radical denominator while preserving an exact ratio.", "required_inputs": ["fraction", "nonzero conjugate"], "allowed_types": ["radical expression"], "warrant_type": "equality_preservation", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COMBINE_LIKE_TERMS": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Collect structurally equivalent terms.", "required_inputs": ["expression"], "allowed_types": ["expression"], "warrant_type": "normalization", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "SOLVE": {"family": "GOAL_MANAGEMENT", "description": "Transform constraints to isolate a target or solve a polynomial.", "required_inputs": ["equations", "target"], "allowed_types": ["equation", "system"], "warrant_type": "constraint_solving", "scope_behavior": "preserves or branches scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "CASE_SPLIT": {"family": "CASE_ANALYSIS", "description": "Partition a problem into explicitly scoped exhaustive branches.", "required_inputs": ["case predicate", "coverage argument"], "allowed_types": ["proposition"], "warrant_type": "case_partition", "scope_behavior": "creates branches", "hml_rule": "scope (no join rule)", "hml_support_status": "PARTIAL"},
    "SOLVE_CASE": {"family": "CASE_ANALYSIS", "description": "Apply local transformations inside one branch.", "required_inputs": ["branch assumption", "equation"], "allowed_types": ["equation"], "warrant_type": "branch_local_validity", "scope_behavior": "branch-local", "hml_rule": "scope + local rules", "hml_support_status": "PARTIAL"},
    "VERIFY_CANDIDATE": {"family": "VERIFICATION", "description": "Substitute a generated candidate into the original constraints.", "required_inputs": ["candidate", "original constraints"], "allowed_types": ["equation", "inequality", "congruence"], "warrant_type": "candidate_verification", "scope_behavior": "branch-local or global", "hml_rule": "closed_eval_v1 only for closed claims", "hml_support_status": "PARTIAL"},
    "SELECT_CANDIDATE": {"family": "CONSTRAINT_REASONING", "description": "Choose admissible candidates using domain, order, or minimality constraints.", "required_inputs": ["candidate set", "domain/order constraint"], "allowed_types": ["finite set", "ordered values"], "warrant_type": "minimality/admissibility", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "SELECT_EXTREMUM": {"family": "GOAL_MANAGEMENT", "description": "Select a maximum/minimum from a verified finite candidate set.", "required_inputs": ["verified candidates", "order"], "allowed_types": ["ordered values"], "warrant_type": "finite_order", "scope_behavior": "merges candidates", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "EXTRACT_ROOT": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Recover a root from a powered equality under sign/domain conditions.", "required_inputs": ["powered equality", "sign/domain condition"], "allowed_types": ["equation", "radical expression"], "warrant_type": "root_extraction", "scope_behavior": "preserves or branches scope", "hml_rule": "closed_eval_v1 only for closed claims", "hml_support_status": "PARTIAL"},
    "BOUND_SEARCH": {"family": "CONSTRAINT_REASONING", "description": "Use a finite domain or lower/upper bound to narrow admissible candidates.", "required_inputs": ["constraint", "bounded domain"], "allowed_types": ["integer", "finite set"], "warrant_type": "bounded_search", "scope_behavior": "prunes candidates", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "EVALUATE": {"family": "EVALUATION", "description": "Compute a closed or instantiated expression exactly.", "required_inputs": ["expression"], "allowed_types": ["numeric", "closed proposition"], "warrant_type": "exact_arithmetic", "scope_behavior": "preserves scope", "hml_rule": "closed_eval_v1 for closed claims", "hml_support_status": "PARTIAL"},
    "DISCHARGE_GOAL": {"family": "GOAL_MANAGEMENT", "description": "Mark a target resolved by a verified result.", "required_inputs": ["goal", "supporting result"], "allowed_types": ["proposition"], "warrant_type": "goal_matching", "scope_behavior": "closes goal", "hml_rule": "proved", "hml_support_status": "PARTIAL"},
    "RECORD_EQUALITY_CONDITION": {"family": "THEOREM_APPLICATION", "description": "Record the equality conditions attached to a bound or theorem.", "required_inputs": ["theorem", "equality conditions"], "allowed_types": ["proposition"], "warrant_type": "theorem_equality_case", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "CONSTRUCTION": {"family": "CONSTRUCTION", "description": "Construct an explicit witness satisfying the active constraints.", "required_inputs": ["constraints", "witness values"], "allowed_types": ["objects", "values"], "warrant_type": "witness_construction", "scope_behavior": "adds witness fact", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COMPLEMENT_COUNT": {"family": "PROBABILISTIC_REASONING", "description": "Compute an event through its complement.", "required_inputs": ["event partition", "complement probability"], "allowed_types": ["probability"], "warrant_type": "complement_rule", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "CONDITIONAL_PROBABILITY": {"family": "PROBABILISTIC_REASONING", "description": "Update a finite probability after observations without replacement.", "required_inputs": ["population state", "event"], "allowed_types": ["probability"], "warrant_type": "conditional_probability", "scope_behavior": "updates state counts", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "MULTIPLY_CONDITIONALS": {"family": "PROBABILISTIC_REASONING", "description": "Multiply a chain of conditional probabilities.", "required_inputs": ["conditional probabilities"], "allowed_types": ["probability"], "warrant_type": "chain_rule", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "MULTIPLY_COUNTS": {"family": "COMBINATORIAL_REASONING", "description": "Multiply independent finite choices.", "required_inputs": ["choice counts"], "allowed_types": ["natural numbers"], "warrant_type": "product_rule", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COUNT_CASES": {"family": "COMBINATORIAL_REASONING", "description": "Count a finite set of cases or choices.", "required_inputs": ["finite domain", "constraints"], "allowed_types": ["natural numbers", "finite sets"], "warrant_type": "finite_counting", "scope_behavior": "may create branches", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COMBINE_CASE_COUNTS": {"family": "COMBINATORIAL_REASONING", "description": "Sum counts from disjoint cases.", "required_inputs": ["disjoint case counts"], "allowed_types": ["natural numbers"], "warrant_type": "disjoint_sum", "scope_behavior": "merges branches", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COUNT_PERMUTATIONS": {"family": "COMBINATORIAL_REASONING", "description": "Count arrangements subject to repeated or distinct objects.", "required_inputs": ["multiset or ordered sample"], "allowed_types": ["natural numbers"], "warrant_type": "permutation_count", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "EVALUATE_PROBABILITY": {"family": "PROBABILISTIC_REASONING", "description": "Evaluate a finite probability from a sample-space model.", "required_inputs": ["sample space", "favorable outcomes"], "allowed_types": ["probability"], "warrant_type": "uniform_product_space", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "BOUND_REASONING": {"family": "CONSTRAINT_REASONING", "description": "Use a bound to eliminate impossible cases.", "required_inputs": ["domain bound", "target"], "allowed_types": ["inequality", "finite domain"], "warrant_type": "upper/lower bound", "scope_behavior": "prunes cases", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "CONSTRAINT_PROPAGATION": {"family": "CONSTRAINT_REASONING", "description": "Propagate a numerical constraint through a structured state.", "required_inputs": ["constraint", "state"], "allowed_types": ["integer", "finite domain"], "warrant_type": "constraint propagation", "scope_behavior": "updates state", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "ENUMERATE": {"family": "CONSTRAINT_REASONING", "description": "Enumerate a finite domain and certify completeness.", "required_inputs": ["finite domain", "coverage criterion"], "allowed_types": ["finite set"], "warrant_type": "finite exhaustion", "scope_behavior": "may create branches", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COMBINE_CASES": {"family": "CASE_ANALYSIS", "description": "Merge complete branches when they imply a common result.", "required_inputs": ["complete branches", "common result"], "allowed_types": ["proposition"], "warrant_type": "case invariant", "scope_behavior": "merges branches", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "APPLY_PRECEDENCE": {"family": "EVALUATION", "description": "Choose the next evaluation layer using operator precedence.", "required_inputs": ["expression", "precedence relation"], "allowed_types": ["numeric expression"], "warrant_type": "operator precedence", "scope_behavior": "preserves scope", "hml_rule": "closed evaluator", "hml_support_status": "PARTIAL"},
    "ROUND_TO_DOMAIN": {"family": "CONSTRAINT_REASONING", "description": "Select the least domain element satisfying a strict threshold.", "required_inputs": ["threshold", "discrete domain"], "allowed_types": ["natural numbers"], "warrant_type": "integer ceiling", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "INDEX_TRANSLATION": {"family": "SEQUENCE_REASONING", "description": "Translate an ambient index after exclusions or offsets.", "required_inputs": ["index", "excluded values"], "allowed_types": ["sequence"], "warrant_type": "index shift", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "COUNT_EXCLUDED": {"family": "SEQUENCE_REASONING", "description": "Count omitted terms before a target sequence position.", "required_inputs": ["sequence rule", "target"], "allowed_types": ["sequence"], "warrant_type": "counting exclusions", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "ADVANCE_SEQUENCE": {"family": "SEQUENCE_REASONING", "description": "Advance through a sequence while maintaining its admissibility rule.", "required_inputs": ["current term", "successor rule"], "allowed_types": ["sequence"], "warrant_type": "successor iteration", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "PRIME_FACTORIZE": {"family": "NUMBER_THEORY", "description": "Represent an integer by prime exponents.", "required_inputs": ["integer"], "allowed_types": ["Natural"], "warrant_type": "unique factorization", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "APPLY_DEFINITION": {"family": "DEFINITION_APPLICATION", "description": "Use a definition to rewrite or constrain an object.", "required_inputs": ["definition", "object"], "allowed_types": ["expression", "proposition"], "warrant_type": "definition", "scope_behavior": "preserves scope", "hml_rule": "def/evidence", "hml_support_status": "PARTIAL"},
    "PARAMETERIZE_CONGRUENCE": {"family": "NUMBER_THEORY", "description": "Replace a congruence with an integer parameterization.", "required_inputs": ["congruence", "residue"], "allowed_types": ["Natural", "Integer"], "warrant_type": "congruence definition", "scope_behavior": "adds parameter", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
    "CANCEL_SYMMETRIC_TERMS": {"family": "ALGEBRAIC_TRANSFORMATION", "description": "Cancel equal cross terms using a symmetry law.", "required_inputs": ["expanded expression", "symmetry law"], "allowed_types": ["vector expression"], "warrant_type": "symmetry", "scope_behavior": "preserves scope", "hml_rule": None, "hml_support_status": "REPRESENTABLE_ONLY"},
}


GAP_META: dict[str, dict[str, Any]] = {
    "MATH-GAP-0001": {"title": "Explicit exhaustive case splitting and branch merge", "classification": "CORE_REASONING_OPERATION", "operation": "CASE_SPLIT", "expected": "Create branch-local assumptions, ensure branches are exhaustive/disjoint, and merge only facts valid in every branch.", "current": "HML has lexical scope blocks and scoped assumptions, but no case-split constructor, coverage proof, or branch-join rule.", "direction": "Add a principled case-analysis/branch-merge semantic only if repeated evidence justifies it; do not add example-specific syntax."},
    "MATH-GAP-0002": {"title": "Candidate generation and original-constraint verification", "classification": "VERIFIER_GAP", "operation": "VERIFY_CANDIDATE", "expected": "A candidate produced by solving or branching is checked against the original equations/inequalities and domain before acceptance.", "current": "closed_eval_v1 checks closed exact propositions; current HML has no generic candidate object or verifier linking candidate provenance to original constraints.", "direction": "Expose candidate verification as a neutral evidence/obligation interface, likely library-backed, without making solver output trusted by assertion."},
    "MATH-GAP-0003": {"title": "Domain and applicability preconditions beyond current partiality", "classification": "PRECONDITION_SYSTEM", "operation": "PRECONDITION_AUDIT", "expected": "Logarithm bases/arguments, radical domains, nonzero denominators, sign conditions, and theorem hypotheses remain explicit and dischargeable.", "current": "HML has require statements, term-level division partiality, and selected rule obligations, but no general domain-condition generator for logs, radicals, squaring, or theorem application.", "direction": "Extend the obligation/precondition interface only after a recurring domain-condition vocabulary is empirically confirmed."},
    "MATH-GAP-0004": {"title": "Proof debt for non-reversible transformations", "classification": "OBLIGATION_SYSTEM", "operation": "OBLIGATION_MANAGEMENT", "expected": "Squaring, absolute-value branching, root extraction, and candidate elimination create obligations that persist until verified.", "current": "HML tracks rule/term obligations, but no generic source action can attach candidate-set or extraneous-solution debt to a transformation.", "direction": "Model transformation-created proof debt as first-class neutral obligations; do not silently mark textbook jumps verified."},
    "MATH-GAP-0005": {"title": "Domain theorem and formula library interface", "classification": "LIBRARY_THEOREM", "operation": "APPLY_THEOREM", "expected": "Named theorems such as continuity boundary matching, AM-GM, Pythagorean theorem, tangent addition, parity, and digit-sum divisibility carry hypotheses and checked conclusions.", "current": "HML can represent propositions and checked closed/definition evidence, but the trusted core has no domain theorem registry or hypothesis-aware theorem evidence.", "direction": "Build a separately audited theorem-library/evidence protocol; keep theorem names out of the core instruction set."},
    "MATH-GAP-0006": {"title": "Open symbolic algebra normalization", "classification": "LIBRARY_THEOREM", "operation": "SYMBOLIC_REWRITE", "expected": "Expansion, factoring, collection, radical normalization, and sign-directed algebraic equivalence are justified over variables.", "current": "HML's trusted kernel is structural and local; the symbolic equivalence checker is explicitly untrusted, while exact evaluation only handles closed claims.", "direction": "Use replayable certified algebra evidence or a library proof object; do not add rewrite rules for the 25 examples."},
    "MATH-GAP-0007": {"title": "Mathematical domain libraries for logs, trig, vectors, parity, optimization, and complex numbers", "classification": "DOMAIN_LIBRARY", "operation": "DOMAIN_REASONING", "expected": "Domain-specific facts and theorem hypotheses are imported as checked knowledge while generic operations remain small.", "current": "The HML type system represents several domains, but the reasoning kernel has no log/trig/vector/AM-GM/complex theorem rules.", "direction": "Separate domain libraries from core semantics and require explicit, replayable evidence."},
    "MATH-GAP-0008": {"title": "Counting and probability reasoning", "classification": "DOMAIN_LIBRARY", "operation": "COMBINATORIAL_REASONING", "expected": "Finite sample spaces, case multiplicities, complements, conditional products, and product/sum rules are represented with exact counts and dependencies.", "current": "HML has probability types/expressions and generic state syntax, but no trusted combinatorial or probability rule set for these transitions.", "direction": "Develop a finite-counting/probability library with explicit sample-space assumptions; do not add probability laws to the kernel."},
    "MATH-GAP-0009": {"title": "Number-theory constraints and finite search", "classification": "DOMAIN_LIBRARY", "operation": "NUMBER_THEORY", "expected": "Prime factorization, congruence solving, digit rules, divisor predicates, and finite minimality checks are certified.", "current": "Natural/integer types are present, but no trusted number-theory theorem or finite-search certificate interface exists.", "direction": "Add audited number-theory evidence as a library capability."},
    "MATH-GAP-0010": {"title": "Sequence indexing, exclusions, and discrete minimality", "classification": "CORE_STATE_REPRESENTATION", "operation": "SEQUENCE_REASONING", "expected": "State records sequence generation rules, omitted values, index translation, and discrete-domain minimality.", "current": "HML can declare values and expressions but has no sequence state object, exclusion set, or index-translation semantics.", "direction": "First test whether a neutral sequence/exclusion state recurs; only then consider a reusable representation extension."},
}


GAP_DETAIL: dict[str, dict[str, str]] = {
    "MATH-GAP-0001": {
        "failure_point": "The source has a finite or conditional partition, but current HML cannot establish coverage/disjointness or promote only branch-invariant facts after a join.",
        "layer_decision": "Core reasoning operation: branch-local scope is already a core concern, and coverage/join changes operational proof-state semantics rather than adding a theorem name.",
        "smallest_remedy": "A generic case-analysis evidence object with predicates, coverage/disjointness proof references, branch scopes, and an invariant-only join.",
        "semantic_effect": "Operational semantics and proof state; it changes which facts are globally established, not surface rendering.",
        "dependencies": "Depends on existing lexical scope, proposition evaluation, and dependency/provenance edges; candidate verification often consumes its branch outputs.",
        "overfit_risk": "High if designed around absolute values or dice syntax; keep predicates and joins generic and library-neutral.",
    },
    "MATH-GAP-0002": {
        "failure_point": "A solver/case step produces a candidate, but current HML has no first-class link from that candidate to the original constraint, domain, and acceptance decision.",
        "layer_decision": "Verifier interface: candidate objects and checks can be expressed as claims/evidence without changing the core expression denotation.",
        "smallest_remedy": "A neutral candidate record plus a verifier obligation that cites the original constraint and reports valid/invalid/undetermined.",
        "semantic_effect": "Proof state and epistemic status; accepted candidate denotation is unchanged.",
        "dependencies": "Depends on provenance, exact/closed evaluation, domain preconditions, and case/solver outputs.",
        "overfit_risk": "Moderate; avoid a protocol tied only to polynomial roots or inequality thresholds.",
    },
    "MATH-GAP-0003": {
        "failure_point": "The trajectory records a condition such as a positive log argument, nonzero denominator, or nonzero rationalizing factor, but current HML does not synthesize/check the domain predicate for the compound operation.",
        "layer_decision": "Precondition system: the missing item is applicability machinery, not a new mathematical theorem or surface keyword.",
        "smallest_remedy": "A general applicability-obligation schema that lets a library theorem or operation declare domain predicates and discharge evidence.",
        "semantic_effect": "Operational legality and proof state; typing may supply some predicates, while denotation remains unchanged.",
        "dependencies": "Depends on type/refinement constraints, partiality checks, theorem-library hypotheses, and candidate verification.",
        "overfit_risk": "Moderate; define predicates compositionally instead of enumerating logs, radicals, and trigonometry separately.",
    },
    "MATH-GAP-0004": {
        "failure_point": "Non-reversible transformations and compressed case reasoning require debt to persist until a sign, coverage, or original-constraint check is discharged; current HML has no generic source-level debt attachment.",
        "layer_decision": "Obligation system: it extends proof-state accounting, not expression syntax or a domain theorem.",
        "smallest_remedy": "Allow any operation to create typed obligations with provenance and explicit discharge evidence, including branch coverage and root-sign debt.",
        "semantic_effect": "Proof state and epistemic status; it affects VERIFIED versus conditional/unsupported status, not mathematical denotation.",
        "dependencies": "Depends on preconditions, candidate verification, case joins, and the existing mandatory-obligation engine.",
        "overfit_risk": "Low to moderate if obligations remain declarative and operation-agnostic; high if every textbook shortcut gets a bespoke obligation class.",
    },
    "MATH-GAP-0005": {
        "failure_point": "The continuity, theorem, or formula step can be written as a proposition, but no current trusted evidence object binds theorem hypotheses to its conclusion.",
        "layer_decision": "Library theorem: the generic APPLY_THEOREM operation belongs in the core; continuity/AM-GM/Pythagorean/etc. facts belong in audited libraries.",
        "smallest_remedy": "A theorem-library manifest and replayable evidence format carrying theorem ID, hypotheses, conclusion, and checker.",
        "semantic_effect": "Denotation is unchanged; operational verification and epistemic status become stronger when evidence is trusted.",
        "dependencies": "Depends on precondition obligations, typed expressions, and dependency/provenance tracking.",
        "overfit_risk": "High if theorem names become core keywords; require generic theorem application with data-driven library entries.",
    },
    "MATH-GAP-0006": {
        "failure_point": "Open-variable expansion, factoring, collection, radical normalization, or monotonicity cannot be certified by the trusted closed evaluator; the symbolic-equivalence checker is not trusted.",
        "layer_decision": "Library/verifier boundary: generic equality reasoning is core, while certified normalization/search is a reusable algebra library or checker.",
        "smallest_remedy": "A replayable symbolic-algebra proof object or certified normal-form checker exposed through evidence.",
        "semantic_effect": "Denotation and verification of open expressions; no new surface syntax is inherently required.",
        "dependencies": "Depends on typed expression normalization, domain conditions, and exact arithmetic leaves.",
        "overfit_risk": "High if rewrite rules are added one by one for Gold-25 identities; use a general certified algebra backend.",
    },
    "MATH-GAP-0007": {
        "failure_point": "The type system can represent logs, vectors, functions, complex values, and propositions, but current trusted rules do not establish their domain-specific identities.",
        "layer_decision": "Domain library: the observed operations share generic APPLY_DEFINITION/APPLY_THEOREM/VERIFY shapes and do not justify core keywords.",
        "smallest_remedy": "Separate audited libraries for recurring domains, each returning explicit theorem/definition evidence and hypotheses.",
        "semantic_effect": "Mostly denotation-level theorem availability and verifier epistemics; the generic core operational semantics need not change.",
        "dependencies": "Depends on the theorem evidence interface, applicability obligations, and typed domain representations.",
        "overfit_risk": "Very high across only 25 examples; wait for cross-domain recurrence before freezing library APIs.",
    },
    "MATH-GAP-0008": {
        "failure_point": "Finite case counts, complements, conditional products, and permutation multiplicities are not checked by any current trusted HML rule despite exact numeric leaves being representable.",
        "layer_decision": "Domain library: sample-space semantics and counting laws are mathematical knowledge over generic state/claims.",
        "smallest_remedy": "A finite counting/probability evidence package with explicit sample space, independence/sampling assumptions, and exact count certificates.",
        "semantic_effect": "Denotation of probability/count claims and their epistemic verification; no new surface keyword is necessary.",
        "dependencies": "Depends on finite-domain state, branch/case joins, exact arithmetic, and theorem-library evidence.",
        "overfit_risk": "High if shaped only around dice/marbles; specify abstract finite sets and measures.",
    },
    "MATH-GAP-0009": {
        "failure_point": "Prime factorization, congruence parameterization, divisibility rules, and finite factor searches require trusted number-theoretic facts and minimality certificates absent from current HML.",
        "layer_decision": "Domain library: the generic operations are parameterize, constrain, enumerate, and verify; the number-theory facts are external knowledge.",
        "smallest_remedy": "An audited number-theory library with factorization/congruence evidence and finite-search/minimality certificates.",
        "semantic_effect": "Denotation and verification of integer claims; generic operational semantics can remain unchanged.",
        "dependencies": "Depends on natural/integer typing, finite search state, candidate verification, and exact arithmetic.",
        "overfit_risk": "High if the API hard-codes digit-sum or cube-factor examples; keep predicates and certificates abstract.",
    },
    "MATH-GAP-0010": {
        "failure_point": "The sequence example needs omitted-value sets, index translation, successor iteration, and discrete minimality as persistent state; current HML has no sequence/exclusion state.",
        "layer_decision": "Core state representation candidate: unlike a theorem, the missing information must survive across transitions and affect later indexing.",
        "smallest_remedy": "First-class neutral sequence metadata (generator/predicate, index convention, exclusions) plus generic finite-index evidence; defer syntax.",
        "semantic_effect": "Proof state and denotation of indexed claims; rendering is secondary.",
        "dependencies": "Depends on finite-domain enumeration, exact arithmetic, and candidate/minimality verification.",
        "overfit_risk": "Very high from one omitted-squares example; validate on recurrence, filtered sequences, and order-statistics examples before core changes.",
    },
}


def snapshot(state: dict[str, Any], state_id: str) -> dict[str, Any]:
    out = copy.deepcopy(state)
    out["id"] = state_id
    return out


def state_change(before: dict[str, Any], after: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    added = [spec["result_id"]]
    removed = [o["id"] for o in spec["creates_obligations"] if o["status"] == "discharged"] + list(spec["discharges_obligations"])
    return {
        "from": before["id"],
        "to": after["id"],
        "added_facts": added,
        "removed_obligations": removed,
        "epistemic_update": f"Established {spec['result_id']}: {spec['result_statement']}",
        "scope_effect": "branch-local" if spec.get("branch") else "global/current scope",
        "dependency_effect": spec["dependencies"],
    }


def build_trajectory(row: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    source = df.iloc[row["row"]]
    problem = str(source["problem"])
    solution = str(source["solution"])
    spec = G[row["problem_id"]]
    state = copy.deepcopy(spec["initial"])
    initial_state = snapshot(state, "S0")
    steps: list[dict[str, Any]] = []
    explicit = 0
    implicit = 0
    source_omissions: list[str] = []
    current_id = "S0"
    seen_facts = {f["id"] for f in state["facts"]}
    for i, raw in enumerate(spec["steps"], 1):
        if raw["source_span"] not in solution:
            raise ValueError(f"{row['problem_id']} step {i} source_span is not an exact solution substring: {raw['source_span']!r}")
        before = snapshot(state, current_id)
        result_id = f"fact:s{i}"
        raw = copy.deepcopy(raw)
        raw["result_id"] = result_id
        fact = {"id": result_id, "statement": raw["result_statement"], "status": "established", "scope": raw.get("branch") or "global"}
        state["facts"].append(fact)
        seen_facts.add(result_id)
        for ob in raw["creates_obligations"]:
            if ob["status"] == "open":
                state["open_obligations"].append(ob)
            else:
                state["discharged_obligations"].append(ob)
            if ob.get("source_omission"):
                source_omissions.append(f"{row['problem_id']}: {ob['statement']}")
        for oid in raw["discharges_obligations"]:
            state["open_obligations"] = [o for o in state["open_obligations"] if o["id"] != oid]
            state["discharged_obligations"].append({"id": oid, "status": "discharged", "evidence": f"Discharged by {result_id}"})
        for p in raw["preconditions"]:
            if p.get("source_omission"):
                source_omissions.append(f"{row['problem_id']}: {p['condition']}")
        state["dependencies"].extend(x for x in raw["dependencies"] if x not in state["dependencies"])
        if raw.get("branch"):
            branch_name = f"branch:{raw['branch']}"
            if branch_name not in state["scope"]:
                state["scope"].append(branch_name)
        next_id = f"S{i}"
        after = snapshot(state, next_id)
        raw["state_before"] = before
        raw["state_after"] = after
        raw["state_change"] = state_change(before, after, raw)
        raw["action"] = {"operation_id": raw.pop("operation_id"), "family": raw.pop("family"), "arguments": raw.pop("arguments")}
        raw["result"] = {"id": result_id, "statement": raw.pop("result_statement"), "status": "established"}
        if raw["explicitness"] == "explicit":
            explicit += 1
        else:
            implicit += 1
        steps.append({"step_id": f"s{i}", **raw})
        current_id = next_id
    final_state = snapshot(state, current_id)
    for goal in final_state["goals"]:
        goal["status"] = "goal_discharged"
    final_state["epistemic_status"].append({"id": "goal_status", "statement": spec["final_goal"], "status": "goal_discharged"})
    operations = sorted({s["action"]["operation_id"] for s in steps})
    gaps = sorted({gap for s in steps for gap in s["semantic_gap_ids"]})
    return {
        "schema_version": "math-discovery-0.1.0",
        "problem_id": row["problem_id"],
        "source_dataset": "Hendrycks MATH train parquet",
        "source_row_id": f"train-row-{row['row']:05d}",
        "source_hash": hashlib.sha256((problem + "\n" + solution).encode("utf-8")).hexdigest(),
        "category": str(source["type"]),
        "level": str(source["level"]),
        "problem": problem,
        "original_solution": solution,
        "selection_reason": row["selection_reason"],
        "initial_state": initial_state,
        "steps": steps,
        "final_state": final_state,
        "goal_status": "discharged",
        "operations_observed": operations,
        "source_quality": {"explicit_steps": explicit, "implicit_steps": implicit, "source_omissions": source_omissions, "solution_variants": "source contains two solution paths" if "Solution 2" in solution else None},
        "hml_gaps": gaps,
        "canonical_verification": {"status": "MANUAL_SEMANTIC_CHECK", "notes": "The trajectory is an audited reconstruction of the worked solution; exact arithmetic subclaims are marked at step level."},
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_state(state: dict[str, Any]) -> str:
    lines = [f"`{state['id']}` scope: {', '.join(state['scope'])}"]
    for key, title in [("objects", "Objects"), ("declarations", "Declarations"), ("types_domains", "Types/domains"), ("facts", "Facts"), ("goals", "Goals"), ("open_obligations", "Open obligations"), ("discharged_obligations", "Discharged obligations"), ("dependencies", "Dependencies")]:
        vals = state.get(key, [])
        if not vals:
            continue
        lines.append(f"**{title}:**")
        for value in vals:
            if isinstance(value, dict):
                lines.append(f"- `{value.get('id','')}` {value.get('statement','')} ({value.get('status','')})")
            else:
                lines.append(f"- {value}")
    return "\n".join(lines)


def render_problem(traj: dict[str, Any]) -> str:
    lines = [f"# {traj['problem_id']}", "", "## Original problem", "", traj["problem"], "", "## Original solution", "", traj["original_solution"], "", "## Canonical initial state", "", render_state(traj["initial_state"]), "", "## Trajectory", ""]
    for n, s in enumerate(traj["steps"], 1):
        lines += [f"### Step {n}: {s['action']['operation_id']}", "", f"**Source span:** {s['source_span']}", "", f"**Explicitness:** `{s['explicitness']}`", "", f"**State before:**\n\n{render_state(s['state_before'])}", "", f"**Arguments:** `{json.dumps(s['action']['arguments'], ensure_ascii=False)}`", "", f"**Warrant:** {s['warrant']['description']} (`{s['warrant']['kind']}`, source `{s['warrant']['source']}`)", "", "**Preconditions:**"]
        lines += [f"- {p['condition']} — `{p['status']}`; {p['evidence']}" for p in s["preconditions"]] or ["- none recorded"]
        lines += ["", "**Obligations created:**"]
        lines += [f"- `{o['id']}` {o['statement']} — `{o['status']}`" for o in s["creates_obligations"]] or ["- none"]
        lines += ["", f"**Dependencies:** {', '.join(s['dependencies']) or 'none'}", "", f"**Result:** `{s['result']['id']}` {s['result']['statement']}", "", f"**Verification:** `{s['verification']['status']}` / `{s['verification']['category']}` — {s['verification']['notes']}", "", f"**HML support:** `{s['hml_support']['status']}`; constructs: {', '.join(s['hml_support']['constructs']) or 'none'}. {s['hml_support']['notes']}", "", f"**Semantic gaps:** {', '.join(s['semantic_gap_ids']) or 'none'}", "", f"**State after:**\n\n{render_state(s['state_after'])}", ""]
    lines += ["## Final state", "", render_state(traj["final_state"]), "", f"**Goal status:** `{traj['goal_status']}`", "", "## Operations observed", "", ", ".join(f"`{x}`" for x in traj["operations_observed"]), "", "## HML gaps exposed", "", ", ".join(traj["hml_gaps"]) or "None"]
    return "\n".join(lines).rstrip() + "\n"


def build_manifest(trajectories: list[dict[str, Any]], df: pd.DataFrame) -> dict[str, Any]:
    records = []
    for t in trajectories:
        records.append({k: t[k] for k in ["problem_id", "source_dataset", "source_row_id", "source_hash", "category", "level", "problem", "original_solution", "selection_reason"]})
    return {"manifest_version": "gold25_math_v0", "source_file": RAW.relative_to(ROOT).as_posix(), "selection_policy": "Deliberate operation-diversity sample; no Asymptote/image-dependent selected record.", "category_targets": {"Algebra": 5, "Intermediate Algebra": 4, "Counting & Probability": 4, "Number Theory": 4, "Precalculus": 3, "Geometry": 3, "Prealgebra": 2}, "records": records}


def audit_markdown(df: pd.DataFrame, trajectories: list[dict[str, Any]]) -> str:
    def stats(series: pd.Series) -> str:
        x = series.fillna("").astype(str).str.len()
        return f"mean {x.mean():.1f}, median {x.median():.0f}, p90 {x.quantile(.9):.0f}, max {x.max():.0f}"
    category = df["type"].value_counts().sort_index()
    levels = df["level"].value_counts().sort_index()
    selected_counts = Counter(t["category"] for t in trajectories)
    patterns = {p: int(df.astype(str).apply(lambda c: c.str.contains(p, case=False, regex=False)).any(axis=1).sum()) for p in ["[asy]", "tabular", "\\begin{array}", "\\includegraphics", "image", "graph", "diagram"]}
    lines = ["# Hendrycks MATH dataset audit", "", "## Provenance", "", f"- Copied parquet: `{RAW.relative_to(ROOT)}`", "- Original: `/Users/moheet/Desktop/train-00000-of-00001-7320a6f3aba8ebd2.parquet`", "- Source: Hendrycks MATH training split, local Desktop copy", f"- Rows: **{len(df):,}**", "- Columns: `problem`, `level`, `type`, `solution`", "- Null values: none in all four columns", "- Duplicate problems: 0; duplicate problem+solution records: 0", "", "## Category distribution", "", "| Category | Rows | Selected Gold-25 |", "|---|---:|---:|"]
    lines += [f"| {k} | {v:,} | {selected_counts.get(k,0)} |" for k, v in category.items()]
    lines += ["", "## Level distribution", "", "| Level | Rows |", "|---|---:|"]
    lines += [f"| {k} | {v:,} |" for k, v in levels.items()]
    lines += ["", "## Length distributions", "", f"- `problem` characters: {stats(df['problem'])}", f"- `solution` characters: {stats(df['solution'])}", "", "## Visual/format markers", "", "| Marker | Rows |", "|---|---:|"]
    lines += [f"| `{k}` | {v:,} |" for k, v in patterns.items()]
    lines += ["", "The 25 selected records contain no `[asy]` or `\\includegraphics` marker in either problem or solution. This is a text-first discovery set, not a claim that visual reasoning is unimportant.", "", "## Selection", "", "Exactly 25 records were selected deliberately for operation diversity. The manifest preserves each problem and solution verbatim; canonical trajectories are generated separately under `data/gold25/trajectories/`."]
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dataset_provenance(df: pd.DataFrame) -> dict[str, Any]:
    original = Path("/Users/moheet/Desktop/train-00000-of-00001-7320a6f3aba8ebd2.parquet")
    if not original.exists():
        raise FileNotFoundError(f"original dataset required for provenance: {original}")
    original_sha = sha256_file(original)
    copy_sha = sha256_file(RAW)
    return {
        "dataset": "Hendrycks MATH",
        "split": "train",
        "source": "local Desktop parquet supplied for this Gold-25 discovery run",
        "original_filename": original.name,
        "original_path": str(original),
        "destination": str(RAW.relative_to(ROOT)),
        "bytes": {"original": original.stat().st_size, "destination": RAW.stat().st_size},
        "sha256": {"original": original_sha, "destination": copy_sha},
        "byte_identical": original.stat().st_size == RAW.stat().st_size and original_sha == copy_sha,
        "row_count": int(len(df)),
        "columns": [str(x) for x in df.columns],
        "categories": {str(k): int(v) for k, v in df["type"].value_counts().sort_index().items()},
        "levels": {str(k): int(v) for k, v in df["level"].value_counts().sort_index().items()},
        "large_dataset_ingestion": False,
        "notes": "The full parquet was audited; only the 25 manifest-selected rows were reconstructed into trajectories.",
    }


def gold25_trajectory_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://hml.reasoning.local/schemas/math-discovery-trajectory.schema.json",
        "title": "Gold-25 neutral mathematical reasoning trajectory",
        "description": "Representation-neutral S0 -> action -> S1 trajectories reconstructed from worked MATH solutions. HML is intentionally not a required rendering.",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "problem_id", "source_dataset", "source_row_id", "source_hash", "category", "level", "problem", "original_solution", "selection_reason", "initial_state", "steps", "final_state", "goal_status", "operations_observed", "source_quality", "hml_gaps", "canonical_verification"],
        "properties": {
            "schema_version": {"const": "math-discovery-0.1.0"},
            "problem_id": {"type": "string", "pattern": "^MATH-GOLD-[0-9]{3}$"},
            "source_dataset": {"type": "string"},
            "source_row_id": {"type": "string"},
            "source_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "category": {"type": "string"},
            "level": {"type": "string"},
            "problem": {"type": "string", "minLength": 1},
            "original_solution": {"type": "string", "minLength": 1},
            "selection_reason": {"type": "string", "minLength": 1},
            "initial_state": {"$ref": "#/$defs/state"},
            "steps": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/step"}},
            "final_state": {"$ref": "#/$defs/state"},
            "goal_status": {"const": "discharged"},
            "operations_observed": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "source_quality": {"type": "object"},
            "hml_gaps": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "canonical_verification": {"type": "object"},
        },
        "$defs": {
            "state": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "objects", "declarations", "types_domains", "facts", "assumptions", "constraints", "definitions", "goals", "subgoals", "scope", "dependencies", "open_obligations", "discharged_obligations", "epistemic_status"],
                "properties": {
                    "id": {"type": "string", "pattern": "^S[0-9]+$"},
                    "objects": {"type": "array"},
                    "declarations": {"type": "array"},
                    "types_domains": {"type": "array"},
                    "facts": {"type": "array", "items": {"type": "object"}},
                    "assumptions": {"type": "array", "items": {"type": "object"}},
                    "constraints": {"type": "array"},
                    "definitions": {"type": "array"},
                    "goals": {"type": "array", "items": {"type": "object"}},
                    "subgoals": {"type": "array"},
                    "scope": {"type": "array"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "open_obligations": {"type": "array", "items": {"type": "object"}},
                    "discharged_obligations": {"type": "array", "items": {"type": "object"}},
                    "epistemic_status": {"type": "array", "items": {"type": "object"}},
                },
            },
            "step": {
                "type": "object",
                "additionalProperties": False,
                "required": ["step_id", "source_span", "explicitness", "action", "warrant", "preconditions", "creates_obligations", "discharges_obligations", "dependencies", "verification", "hml_support", "semantic_gap_ids", "state_before", "state_after", "state_change", "result"],
                "properties": {
                    "step_id": {"type": "string", "pattern": "^s[0-9]+$"},
                    "source_span": {"type": "string", "minLength": 1},
                    "explicitness": {"enum": ["explicit", "implicit"]},
                    "action": {"type": "object"},
                    "warrant": {"type": "object"},
                    "preconditions": {"type": "array", "items": {"type": "object"}},
                    "creates_obligations": {"type": "array", "items": {"type": "object"}},
                    "discharges_obligations": {"type": "array", "items": {"type": "string"}},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "verification": {"type": "object"},
                    "hml_support": {"type": "object"},
                    "semantic_gap_ids": {"type": "array", "items": {"type": "string"}},
                    "state_before": {"$ref": "#/$defs/state"},
                    "state_after": {"$ref": "#/$defs/state"},
                    "state_change": {"type": "object"},
                    "result": {"type": "object"},
                },
            },
        },
    }


def inventory_markdown() -> str:
    return """# Current HML semantic inventory

Pinned implementation: `hml_core` at `5688aba18632b65a8709aa1d85577d31a67dba6a`.
This inventory is based on the actual source tree, not an older specification. HML
core was inspected read-only; this task does not modify it.

## IMPLEMENTED

- Lexer/parser: typed declarations (`var`, `param`, `const`, `rv`), definitions, laws,
  requirements, goals, derivations, proof claims, evidence, underdetermination claims,
  and lexical `scope ... end` blocks.
- AST: typed expressions, propositions, equalities/inequalities, logical connectives,
  quantifiers, functions/definitions, dimensions, quantities, distributions,
  probability expressions, derivative/integral/limit forms, claims, obligations, and
  explicit V2 state/status nodes.
- Type system: scalar refinement types, integers/reals/naturals, booleans, quantities
  and dimensions, vectors/matrices/tensors, sets/products/functions, random variables
  and distributions, and proposition/event forms.
- Reasoning kernel: symmetry, transitivity, add/subtract/multiply/divide both sides,
  substitution, congruence, modus ponens/tollens, conjunction introduction/elimination,
  strict-to-nonstrict weakening, inequality translation/scaling, and generic
  `forall_intro`/`forall_elim`.
- Goal/assumption machinery: labelled claims, ordered premise resolution, no forward or
  circular references, separate established-vs-unestablished claim pools, lexical
  assumption scopes, `goal`, `proved`, `assume`, `require`, `derive`, `evidence`, and
  `undetermined`.
- Verification boundary: statuses are checker-computed; `VERIFIED` requires a checked
  derivation and discharged mandatory obligations. The static trusted certificate
  registry includes exact closed evaluation, definition/function unfolding, and
  two-model propositional underdetermination.
- Dependency/provenance: claim IDs, premise IDs, evidence graph edges, context hashes,
  definition dependency recording, obligation origin and discharge labels, and graph
  validation against cycles.
- Exact evaluator: closed rational/propositional evaluation, bounded definition/function
  unfolding, partiality detection, and fail-closed unsupported results.

## PARTIALLY IMPLEMENTED

- Preconditions/obligations: division partiality, selected inequality sign obligations,
  refinement constraints, type/dimension obligations, and `require` statements exist;
  generic domain conditions for logarithms, radicals, squaring, theorem hypotheses, and
  candidate verification are not synthesized uniformly.
- Scope: lexical scopes and binder capture avoidance exist, but there is no general
  case-split/branch-completeness/branch-join reasoning operation.
- Symbolic algebra: structural kernel transformations exist, but no trusted general
  expansion, factoring, simplification, radical normalization, or solve procedure.
- Library interface: evidence can carry a registered checker, but the registry is static
  and the core does not provide probability, geometry, calculus, trigonometry,
  number-theory, combinatorial, or inequality theorem libraries.
- HML backends can render/round-trip many typed expressions, but representability of an
  expression is not the same as executable proof support.

## REPRESENTABLE BUT NOT EXECUTABLE

- Open-variable algebraic identities and most textbook rewrites.
- Named theorem applications such as AM-GM, Pythagorean theorem, tangent addition,
  parity facts, divisibility rules, triangle inequality, and change of base.
- Finite counting, probability complements/conditionals, combinations, permutations,
  sequence index shifts, modular arithmetic, and discrete minimality.
- Candidate generation/verification workflows and branch-local finite case joins.
- Domain-sensitive logarithm/radical/complex/vector reasoning when no registered
  checker is available.

## NOT IMPLEMENTED

- A generic theorem/library registry with replayable proof objects.
- Case-split semantics with exhaustive/disjoint coverage and safe branch merging.
- A first-class candidate set and `verify_candidate` obligation protocol.
- Sequence/exclusion state and finite search certificates.
- Trusted domain libraries for probability, combinatorics, number theory, geometry,
  trigonometry, vectors, complex analysis, logarithms, AM-GM, and symbolic algebra.
- A generic solver/tactic/search policy. HML records/checks proposed transitions; it does
  not choose the next mathematical action.

## UNKNOWN / NEEDS TESTING

- Whether the existing refinement/obligation machinery can be cleanly reused for the
  broader domain conditions found in MATH without a new state layer.
- Whether a small neutral evidence protocol can cover the observed theorem families
  without overfitting the first 25 examples.
- Whether current backends preserve all future trajectory metadata for branch and
  candidate provenance; this discovery run intentionally does not render Gold-25 to HML.

## Relevant inspected files

`parser/__init__.py`, `lexer/__init__.py`, `ast/nodes.py`, `types.py`,
`reasoning/kernel.py`, `reasoning/check.py`, `reasoning/side_conditions.py`,
`reasoning/binders.py`, `reasoning/certificates/builtin.py`,
`verification/obligations/engine.py`, `verification/obligations/checkers.py`,
`verification/obligations/evaluate.py`, and the pinned HML V2 documentation/tests.

## Discovery implication

The current HML semantic model is approximately right for a small checked transition
kernel: typed state, explicit claims, local rule application, obligations, scope, and
provenance are real strengths. It is underpowered mainly at the library/evidence and
branch/candidate interfaces, not because every textbook phrase needs a new keyword.
"""


def build_registry(trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(s["action"]["operation_id"] for t in trajectories for s in t["steps"])
    examples: defaultdict[str, list[str]] = defaultdict(list)
    domains: defaultdict[str, set[str]] = defaultdict(set)
    for t in trajectories:
        for s in t["steps"]:
            op = s["action"]["operation_id"]
            if t["problem_id"] not in examples[op]:
                examples[op].append(t["problem_id"])
            domains[op].add(t["category"])
    records = []
    for op in sorted(counts):
        meta = copy.deepcopy(OP_META.get(op, {"family": "CANDIDATE", "description": "Observed operation requiring further ontology work.", "required_inputs": [], "allowed_types": [], "warrant_type": "unknown", "scope_behavior": "unknown", "hml_rule": None, "hml_support_status": "UNKNOWN"}))
        records.append({"operation_id": op, "canonical_name": op, **meta, "preconditions": sorted({p["condition"] for t in trajectories for s in t["steps"] if s["action"]["operation_id"] == op for p in s["preconditions"]}), "state_effect": "adds or transforms a fact in the current trajectory state", "may_create_obligation": any(s["creates_obligations"] for t in trajectories for s in t["steps"] if s["action"]["operation_id"] == op), "may_discharge_obligation": any(s["discharges_obligations"] or any(o["status"] == "discharged" for o in s["creates_obligations"]) for t in trajectories for s in t["steps"] if s["action"]["operation_id"] == op), "dependency_behavior": "records cited facts and prior results", "domains_seen": sorted(domains[op]), "examples_gold25": examples[op], "frequency_gold25": counts[op], "verification_backend": sorted({s["verification"]["backend"] for t in trajectories for s in t["steps"] if s["action"]["operation_id"] == op}), "hml_support": sorted({s["hml_support"]["status"] for t in trajectories for s in t["steps"] if s["action"]["operation_id"] == op}), "notes": "Frequency is canonical-step frequency, not source-sentence frequency."})
    return records


def registry_markdown(registry: list[dict[str, Any]]) -> str:
    by_family: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in registry:
        by_family[r["family"]].append(r)
    lines = ["# Gold-25 reasoning operation registry v0", "", "This is an empirical discovery registry, not a completeness claim. Operations are kept separate from mathematical theorem/library names and from surface discourse phrases.", ""]
    for family in sorted(by_family):
        lines += [f"## {family}", ""]
        for r in by_family[family]:
            lines += [f"### `{r['canonical_name']}`", "", f"- Meaning: {r['description']}", f"- Inputs: {', '.join(r['required_inputs']) or 'not yet normalized'}", f"- Preconditions observed: {', '.join(r['preconditions']) or 'none recorded'}", f"- Warrant: `{r['warrant_type']}`", f"- State effect: {r['state_effect']}", f"- Scope: {r['scope_behavior']}", f"- Dependencies: {r['dependency_behavior']}", f"- Obligations: creates={r['may_create_obligation']}; discharges={r['may_discharge_obligation']}", f"- Example(s): {', '.join(r['examples_gold25'])}", f"- Frequency: **{r['frequency_gold25']}**", f"- HML: `{','.join(r['hml_support'])}`; rule/construct `{r['hml_rule'] or 'none'}`", ""]
    return "\n".join(lines).rstrip() + "\n"


def synthesis_markdown(trajectories: list[dict[str, Any]], registry: list[dict[str, Any]]) -> str:
    steps = [s for t in trajectories for s in t["steps"]]
    counts = Counter(s["action"]["operation_id"] for s in steps)
    support = Counter(s["hml_support"]["status"] for s in steps)
    gaps = Counter(g for s in steps for g in s["semantic_gap_ids"])
    families = Counter(s["action"]["family"] for s in steps)
    created = [o for s in steps for o in s["creates_obligations"]]
    discharged = [o for o in created if o["status"] == "discharged"]
    explicit = sum(s["explicitness"] == "explicit" for s in steps)
    implicit = sum(s["explicitness"] == "implicit" for s in steps)
    omissions = sum(len(t["source_quality"]["source_omissions"]) for t in trajectories)
    lines = ["# Gold-25 reasoning synthesis", "", "## A. Operation frequency table", "", "| Operation | Frequency |", "|---|---:|"]
    lines += [f"| `{op}` | {n} |" for op, n in counts.most_common()]
    lines += ["", "## B. Unique operations discovered", "", f"**{len(counts)}** distinct operation IDs appear in **{len(steps)}** canonical transitions. The catalogue is provisional and intentionally separates generic operations from domain theorems.", "", "## C. Operation families", ""]
    lines += [f"- `{family}`: {n} steps" for family, n in families.most_common()]
    lines += ["", "## D. HML coverage", "", "| HML support status | Steps |", "|---|---:|"]
    lines += [f"| `{k}` | {support.get(k,0)} |" for k in ["FULL", "PARTIAL", "REPRESENTABLE_ONLY", "ABSENT", "UNKNOWN"]]
    lines += ["", f"The strict fully-supported step coverage is **{support.get('FULL',0)}/{len(steps)} = {support.get('FULL',0)/len(steps):.1%}**. This is a discovery metric, not a benchmark score; `PARTIAL` means the state/form or a local suboperation exists but the complete semantic transition does not.", "", "## E. Gap distribution", ""]
    lines += [f"- `{GAP_META[g]['classification']}` / {g}: {n} step references" for g, n in gaps.most_common()]
    lines += ["", "## F. Most important semantic gaps", "", "1. Explicit exhaustive case splitting and branch merge (MATH-GAP-0001): recurs across absolute values, roots, dice, and complex candidates.", "2. Domain/precondition and proof-debt handling (MATH-GAP-0003/0004): source solutions often rely on conditions that are not stated or discharged as separate objects.", "3. Theorem/domain library interface (MATH-GAP-0005/0007/0008/0009): most mathematical knowledge is reusable library content, not a reason to grow the core rule registry.", "4. Candidate verification (MATH-GAP-0002): textbook solutions frequently generate candidates and only later check them.", "5. Sequence/exclusion representation (MATH-GAP-0010): discrete index shifts need explicit state, but recurrence across larger data is still untested.", "", "## G. State content analysis", ""]
    state_keys = ["objects", "declarations", "types_domains", "facts", "assumptions", "constraints", "definitions", "goals", "subgoals", "dependencies", "open_obligations", "scope"]
    for key in state_keys:
        n = sum(bool(t["initial_state"].get(key)) or any(bool(s["state_after"].get(key)) for s in t["steps"]) for t in trajectories)
        lines.append(f"- `{key}` appears in {n}/25 trajectories")
    lines += ["", "Facts and goals are universal in this deliberately problem-centered sample. Dependencies are present in every generated state because the trajectory preserves why each result exists. Assumptions and branch scope are common but not universal; obligations are sparse in the source but disproportionately important when transformations are non-reversible.", "", "## H. Reasoning depth", "", "| Problem | Source steps | Canonical steps | Explicit | Implicit | Max dependency depth (approx.) | Branches | Obligations |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for t in trajectories:
        depth = max((len(s["dependencies"]) for s in t["steps"]), default=0)
        branches = len({s.get("branch") for s in t["steps"] if s.get("branch")})
        obs = sum(len(s["creates_obligations"]) for s in t["steps"])
        source_sentences = len([x for x in re.split(r"(?<=[.!?])\s+", t["original_solution"]) if x.strip()])
        lines.append(f"| {t['problem_id']} | {source_sentences} | {len(t['steps'])} | {sum(s['explicitness']=='explicit' for s in t['steps'])} | {sum(s['explicitness']=='implicit' for s in t['steps'])} | {depth} | {branches} | {obs} |")
    lines += ["", "## I. Source quality", "", f"- Explicit reconstructed steps: **{explicit}**", f"- Implicit reconstructed steps: **{implicit}**", f"- Explicitly recorded source omissions/precondition omissions: **{omissions}**", f"- Solutions with alternative paths: **{sum(bool(t['source_quality']['solution_variants']) for t in trajectories)}**", "", "The worked solutions are mathematically useful but compress semantic work. In particular, theorem hypotheses, domain restrictions, branch coverage, candidate verification, and minimality arguments are often implicit. Those omissions are recorded rather than silently repaired.", "", "## Main discovery", "", "The recurring pattern is not a vocabulary list of textbook phrases. It is a compact transition shape: typed objects and constraints, a reusable operation, a warrant/library reference, applicability conditions, proof debt, dependency edges, and a result that must be checked. Current HML already captures the local checked-kernel half of this shape; Gold-25 evidence points primarily toward branch/candidate interfaces and replayable mathematical libraries."]
    return "\n".join(lines) + "\n"


def state_profile_markdown(trajectories: list[dict[str, Any]]) -> str:
    steps = [s for t in trajectories for s in t["steps"]]
    preconditions = [p for s in steps for p in s["preconditions"]]
    obligations = [o for s in steps for o in s["creates_obligations"]]
    branches = sum(any(s.get("branch") for s in t["steps"]) for t in trajectories)
    deps = sum(bool(s["dependencies"]) for s in steps)
    goals = sum(bool(t["initial_state"]["goals"]) for t in trajectories)
    return f"""# Empirical reasoning-state profile v0

This profile is derived from the 25 audited MATH trajectories, not from intuition. The
sample contains {len(steps)} canonical transitions across seven MATH categories.

## 1. Necessary-looking S_t information

| State component | Evidence |
|---|---:|
| Objects/declarations | 25/25 trajectories |
| Types/domains | 25/25 trajectories |
| Active facts/constraints | 25/25 trajectories |
| Explicit goal | {goals}/25 trajectories |
| Dependencies/provenance | {deps}/{len(steps)} transitions cite prior facts or results |
| Scope/branch context | {branches}/25 trajectories contain branch-local reasoning |
| Preconditions | {sum(bool(s['preconditions']) for s in steps)}/{len(steps)} transitions record at least one |
| Obligations | {sum(bool(s['creates_obligations']) for s in steps)}/{len(steps)} transitions create explicit debt |

The evidence supports a state containing typed objects, active facts/constraints, goals,
dependency edges, and a scope context. These are not interchangeable: a theorem
hypothesis may be a fact, a branch assumption, or an obligation depending on how it was
introduced.

## 2. Useful but not universal

- Definitions/functions are essential in the function/parity and formula examples but
  absent from direct arithmetic/counting problems.
- Branch sets are essential for absolute values, roots, complex candidates, and finite
  cases, but not for direct transformations.
- Explicit epistemic status is useful when a step is only conditionally supported or
  when a candidate has been generated but not checked.
- Exact backend evidence is useful for arithmetic leaves, but it does not replace the
  theorem/library warrant that produced the expression.

## 3. What can live outside the core state

Surface prose, source sentence boundaries, textbook discourse markers, and rendering
syntax can live in provenance/views. The theorem name and proof object can be library
artifacts referenced by a generic `APPLY_THEOREM` action. Numeric backend traces can be
verification evidence, not canonical state facts, provided their dependency claims are
retained.

## 4. Are facts enough?

No. Dependencies are structurally important: the same expression has different semantic
status when it is given, derived by a checked rule, produced in a branch, or returned by
an untrusted oracle. The Gold-25 trajectory keeps dependencies on every transition.

## 5. Goals

Goals are explicit in all 25 selected problems because selection deliberately targeted
complete worked answers. This is a selection property, not an estimate for all prose.
Within a trajectory, subgoals/candidate goals appear when solving, branching, or
constructing witnesses.

## 6. Preconditions

Preconditions are material in {sum(bool(s['preconditions']) for s in steps)} of {len(steps)}
steps. The most common are nonzero denominators, positive/log domains, sign conditions,
integer domains, theorem hypotheses, and branch predicates. Several source solutions
omit them; the reconstruction marks those omissions.

## 7. Obligations

The explicit reconstruction creates {len(obligations)} obligations and discharges
{sum(o['status']=='discharged' for o in obligations)}. The small count is misleading:
many obligations are hidden in textbook prose (candidate checking, radical sign,
branch coverage, theorem hypotheses). This is precisely why obligation state should not
be inferred from whether the final numeric answer looks plausible.

## 8. Scope and branches

Branch/scope structure matters in {branches}/25 trajectories. The current HML lexical
scope is a promising primitive, but case coverage and branch joins are not yet encoded.
Facts from one branch must not be promoted to global state without a merge argument.

## 9. Stored mathematical knowledge

Most nontrivial domain work invokes stored knowledge: AM-GM, Pythagorean theorem,
trigonometric identities, parity definitions, divisibility rules, prime factorization,
triangle inequality, finite probability rules, and congruence reasoning. This strongly
supports a small generic operation kernel plus explicit theorem/domain libraries.

## 10. Assessment of current HML

The HML semantic model is approximately right for local checked transitions: typed
claims, explicit goals, rule applications, obligations, scope, and provenance match the
observed shape. It is underpowered at reusable evidence for open symbolic/domain claims,
candidate/branch interfaces, and sequence/finite-search state. The data does not justify
adding textbook theorem names as core keywords.
"""


def gap_markdown(gid: str, meta: dict[str, Any], trajectories: list[dict[str, Any]]) -> str:
    examples = []
    for t in trajectories:
        for s in t["steps"]:
            if gid in s["semantic_gap_ids"]:
                examples.append((t["problem_id"], s["step_id"], s["source_span"]))
    detail = GAP_DETAIL[gid]
    lines = [f"# {gid}: {meta['title']}", "", "- Classification: `" + meta["classification"] + "`", "- Mathematical operation: `" + meta["operation"] + "`", "", "## Evidence in Gold-25", ""]
    lines += [f"- `{pid}` `{sid}` — {span}" for pid, sid, span in examples]
    lines += ["", "## Expected mathematical semantics", "", meta["expected"], "", "## Current HML capability", "", meta["current"], "", "## Exact failure point", "", detail["failure_point"], "", "## Core/library/surface boundary", "", detail["layer_decision"], "", "## Smallest possible remedy", "", detail["smallest_remedy"], "", "## Semantic impact", "", detail["semantic_effect"], "", "## Dependencies on other gaps", "", detail["dependencies"], "", "## Risk of overfitting Gold-25", "", detail["overfit_risk"], "", "## Relevant inspected constructs", "", "- `hml_core/src/hamiltonian_lang/ast/nodes.py`", "- `hml_core/src/hamiltonian_lang/parser/__init__.py`", "- `hml_core/src/hamiltonian_lang/reasoning/kernel.py`", "- `hml_core/src/hamiltonian_lang/reasoning/check.py`", "- `hml_core/src/hamiltonian_lang/reasoning/side_conditions.py`", "- `hml_core/src/hamiltonian_lang/reasoning/certificates/builtin.py`", "- `hml_core/src/hamiltonian_lang/verification/obligations/engine.py`", "", "## Why the gap is not silently repaired", "", "The canonical trajectory records the operation, warrant, preconditions, obligations, dependencies, and verification status independently of HML. The gap is reported rather than represented as a made-up HML rule.", "", "## Proposed direction", "", meta["direction"], ""]
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(RAW)
    if len(df) != 12500 or list(df.columns) != ["problem", "level", "type", "solution"]:
        raise SystemExit("unexpected MATH parquet shape")
    write_json(ROOT / "data/raw/math/math_dataset_provenance.json", dataset_provenance(df))
    write_json(ROOT / "schemas/math-discovery-trajectory.schema.json", gold25_trajectory_schema())
    trajectories = [build_trajectory(row, df) for row in SELECTED]
    if len(trajectories) != 25 or Counter(t["category"] for t in trajectories) != Counter({"Algebra": 5, "Intermediate Algebra": 4, "Counting & Probability": 4, "Number Theory": 4, "Precalculus": 3, "Geometry": 3, "Prealgebra": 2}):
        raise SystemExit("selection category counts are not the declared Gold-25 targets")
    for t in trajectories:
        write_json(TRAJ / f"{t['problem_id']}.json", t)
        (PROBLEM_REPORTS / f"{t['problem_id']}.md").parent.mkdir(parents=True, exist_ok=True)
        (PROBLEM_REPORTS / f"{t['problem_id']}.md").write_text(render_problem(t), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Gold-25 semantic discovery set\n\n"
        "This directory contains exactly 25 neutral reasoning trajectories reconstructed "
        "from the local Hendrycks MATH parquet. The original problem and solution are "
        "preserved in the manifest and each trajectory. No Gold-25 HML renderings are "
        "generated in this discovery mission; HML support and semantic gaps are recorded "
        "as metadata and reports.\n",
        encoding="utf-8",
    )
    manifest = build_manifest(trajectories, df)
    write_json(ROOT / "manifests/gold25_math_v0.json", manifest)
    (ROOT / "reports/math_dataset_audit.md").write_text(audit_markdown(df, trajectories), encoding="utf-8")
    registry = build_registry(trajectories)
    write_json(ROOT / "schemas/reasoning_operation_registry_gold25_v0.json", {"registry_version": "gold25_reasoning_operation_registry_v0", "operations": registry})
    (ROOT / "reports/reasoning_operation_registry_v0.md").write_text(registry_markdown(registry), encoding="utf-8")
    (ROOT / "reports/gold25_reasoning_synthesis.md").write_text(synthesis_markdown(trajectories, registry), encoding="utf-8")
    (ROOT / "reports/reasoning_state_profile_v0.md").write_text(state_profile_markdown(trajectories), encoding="utf-8")
    (ROOT / "reports/current_hml_semantic_inventory.md").write_text(inventory_markdown(), encoding="utf-8")
    for gid, meta in GAP_META.items():
        (GAP_REPORTS / f"{gid}.md").parent.mkdir(parents=True, exist_ok=True)
        (GAP_REPORTS / f"{gid}.md").write_text(gap_markdown(gid, meta, trajectories), encoding="utf-8")
    print(json.dumps({"selected": len(trajectories), "steps": sum(len(t["steps"]) for t in trajectories), "operations": len(registry), "category_counts": Counter(t["category"] for t in trajectories)}, indent=2, default=dict))


if __name__ == "__main__":
    main()
