# Gold-25 adversarial semantic audit

This report audits the reconstructed Gold-25 trajectory semantics, not just source-span containment. It covers all 25 selected problems and all 118 canonical transitions. Problem 26 was not processed. No file inside hml_core was modified.

## Executive result

- Transitions audited: 118
- Source spans contained in their original MATH solutions: 118/118
- Dependency references resolvable at the point of use: 118/118
- State-transition invariant failures: 0
- Branch-scope leakage findings: 0
- Independent from-scratch hard audits: 5 (MATH-GOLD-001, MATH-GOLD-004, MATH-GOLD-006, MATH-GOLD-012, MATH-GOLD-019)

The audit treats a transition as semantically valid only when its warrant follows from the active state, its preconditions are visible or explicitly marked as source omissions, its dependencies are available, its result adds exactly the claimed fact, its obligations and scope changes are accounted for, and any branch-local fact is joined only by an operation that cites the relevant branches.

## Generator classification

scripts/build_gold25.py is a Gold-25 curated artifact generator. It hard-codes the deliberate 25-record selection and human-authored G annotations, including operation labels, warrants, dependencies, preconditions, obligations, HML support notes, and gap IDs. It is not a reusable automatic extractor and must not be presented as the scalable extraction engine. A future extractor may reuse the emitted schema and registry, but it needs a separate design and evaluation.

## Mechanical invariants

1. Every source span is checked against the original solution string.
2. Every dependency is checked against an initial fact or an earlier result in the same trajectory.
3. Every state_after contains exactly one newly added result fact and no removed fact; state_change records the same delta.
4. Created obligations are recorded as added obligations even when their status is discharged immediately; only explicit discharges are removed.
5. Explicit DISCHARGE_GOAL transitions update the intermediate goal state, not only final_state.
6. Branch-local dependencies are rejected unless the step is in the same branch or is an explicit branch-join/finite-case combination.

All mechanical invariants passed on the regenerated 118-transition artifact.

## Independent hard-trajectory audits

### MATH-GOLD-001

- Operation audited: continuity at the two piecewise boundaries
- Independent reconstruction: At x=2, 2a+3=-3 gives a=-3. At x=-2, -7=-4-b gives b=3. Therefore a+b=0.
- Semantic checks: The two boundary equations use the adjacent pieces, the arithmetic is correct, and the final sum depends on both solved facts. No branch fact leaks into the other boundary.
- Preconditions: The piecewise definition and real parameter domain are sufficient; continuity is applied at both stated boundaries.
- Verdict: PASS after relabeling s1 as APPLY_DEFINITION and repairing the dependency chain.

### MATH-GOLD-004

- Operation audited: absolute-value sign partition, branch solving, candidate verification, maximum selection
- Independent reconstruction: Any solution needs x+3>=0. Split on 5x-1>=0 or 5x-1<0. The first branch gives x=1; the second gives x=-1/3. Direct substitution validates both, and the larger is 1.
- Semantic checks: The original solution omits the branch sign hypotheses and the right-hand-side domain condition. The reconstruction now records them, scopes both solves and checks, and joins only verified branch candidates.
- Preconditions: The sign of 5x-1 controls the absolute-value definition; x+3 must be nonnegative because it equals an absolute value.
- Verdict: PASS after adding branch scope and missing preconditions; this is a branch-interface/library gap, not an incorrect mathematical answer.

### MATH-GOLD-006

- Operation audited: change of logarithm base, linear isolation, exponentiation
- Independent reconstruction: For x>0, log₄x=(1/2)log₂x, so (3/2)log₂x=6, log₂x=4, and x=2⁴=16.
- Semantic checks: The log domain and base hypotheses are recorded. The source sentence contains three operations after the base conversion; s3 stores the two final consequences as a compound solve macro. The result is valid, but the macro must not be treated as an atomic primitive in a future fine-grained corpus.
- Preconditions: x>0, 3/2≠0, base 2 is positive and not 1, and base 4 is positive and not 1.
- Verdict: PASS as a marked macro; split s3 before using Gold-25 as an atomicity benchmark.

### MATH-GOLD-012

- Operation audited: finite complement bound, exhaustive pair enumeration, permutation multiplicity, uniform probability sum
- Independent reconstruction: Without a 6 the maximum is 15, so at least one die is 6. The other two sum to 10, giving only 4+6 and 5+5. Each pattern has three ordered realizations, each of probability 1/216, so the total is 1/36.
- Semantic checks: The two cases are disjoint and exhaustive within the bounded dice domain. Branch-local multiplicities and probabilities are not reused across branches except by the final sum; sample-space dependence is explicit.
- Preconditions: Three independent standard six-faced dice and the ordered sample space of size 216 are required.
- Verdict: PASS after declaring the enumeration branches and repairing branch-to-join dependencies; probability counting remains library-level.

### MATH-GOLD-019

- Operation audited: clear a reciprocal denominator, solve a complex quadratic, convert roots to polar form, evaluate both powers, join invariant
- Independent reconstruction: Since x is nonzero, x+1/x=√3 becomes x²-√3x+1=0. The roots are (√3±i)/2, namely e^(πi/6) and e^(11πi/6); both eighteenth powers equal -1.
- Semantic checks: The denominator precondition is explicit. The two roots are declared as separate branches, each power evaluation depends on the common candidate fact, and the final invariant depends on both branch results. The alternative squaring solution is not mixed into this selected source path.
- Preconditions: x≠0 is required before multiplying by x; complex quadratic and polar-form facts are library warrants, not core transformations.
- Verdict: PASS after declaring root branches and repairing the final join dependencies; complex algebra/polar conversion remains library-level.

## Compressed source spans and atomicity

Exact source containment does not imply one source sentence equals one semantic operation. The following spans were independently expanded and then retained as explicitly documented compound macros in this Gold-25 artifact:

| Trajectory | Step | Canonical action | Atomicity finding |
|---|---|---|---|
| MATH-GOLD-001 | s1 | APPLY_DEFINITION | The source sentence compresses two boundary applications of continuity into one fact. The fact is a conjunction of legitimate boundary equalities; retain as a documented macro for Gold-25. |
| MATH-GOLD-005 | s4 | SOLVE | The source combines solving the second affine equation and identifying B. The result is one justified equality and remains a safe solve macro. |
| MATH-GOLD-006 | s3 | SOLVE | Added the nonzero divisor precondition 3/2≠0 and marked the source's division, logarithm isolation, and exponentiation as a compound macro; split before any fine-grained benchmark. |
| MATH-GOLD-009 | s2 | EVALUATE | The source invokes AM-GM and equality conditions in one sentence. The equality case is represented separately in the following transition. |
| MATH-GOLD-018 | s4 | EVALUATE | The source uses the tangent addition identity and exact special-angle values in one displayed derivation. The final equality is valid as a library-backed macro. |
| MATH-GOLD-022 | s2 | FORMULATE_EQUATION | The source substitutes the geometric definitions into x+y=80π, factors, and cancels π. The nonzero condition is recorded; the compound result is valid. |
| MATH-GOLD-024 | s4 | EVALUATE | The source performs multiple left-to-right additions/subtractions in one sentence. The canonical result preserves the exact intermediate expression and is an arithmetic macro. |
| MATH-GOLD-025 | s4 | SUBTRACT_BOTH_SIDES | The source subtracts 5x and divides by positive 5 in one sentence. The positive divisor precondition is recorded; the inequality result is valid. |

The most consequential macro is MATH-GOLD-006 s3: division, logarithm isolation, and exponentiation are compressed into one result conjunction. That result is valid, but the step is marked MACRO-AUDITED and must be split before using this set to measure atomic operation extraction. No mathematical answer was changed by this decision.

## Corrections applied transparently

The following semantic metadata corrections were applied before this report was generated:

| Trajectory | Step | Correction |
|---|---|---|
| MATH-GOLD-001 | s1 | Changed INTRODUCE_VARIABLE to APPLY_DEFINITION: this transition applies continuity's definition, it does not bind a variable. |
| MATH-GOLD-004 | s1 | Added an explicit branch declaration, the necessary right-hand-side condition x+3>=0, and evidence that the sign partition is exhaustive. |
| MATH-GOLD-004 | s2 | Added the case-1 branch scope and the missing sign precondition 5x-1>=0. |
| MATH-GOLD-004 | s4 | Added the case-2 branch scope and the missing sign precondition 5x-1<0. |
| MATH-GOLD-007 | s1 | Changed SUBSTITUTE to ADD_BOTH_SIDES: the source adds y to both sides rather than substituting an equality. |
| MATH-GOLD-010 | s1 | Recorded the two combinatorial branches explicitly so the later sum has a declared partition. |
| MATH-GOLD-012 | s3 | Recorded the two finite enumeration branches explicitly so the later probability sum has a declared partition. |
| MATH-GOLD-014 | s1 | Changed APPLY_DEFINITION to APPLY_THEOREM: divisibility by prime-power factors is a number-theoretic theorem. |
| MATH-GOLD-015 | s5 | Changed EVALUATE to BOUND_REASONING and added n>=6 and 5>0: this step propagates a congruence-derived lower bound through an affine expression. |
| MATH-GOLD-019 | s3 | Declared the two complex-root candidate branches before evaluating them and joining their common result. |
| MATH-GOLD-022 | s1 | Changed INTRODUCE_VARIABLE to APPLY_DEFINITION: the radius is already given and the step invokes area/circumference definitions. |

Dependency provenance was also repaired systematically. The final artifact cites only available initial facts or earlier results, including the formerly invalid candidate/root join references. The per-transition ledger below is the authoritative post-correction record.

### Dependency normalization by trajectory

- MATH-GOLD-001: s3, s5, s6
- MATH-GOLD-002: s3, s4
- MATH-GOLD-003: s2, s3, s4
- MATH-GOLD-004: s2, s3, s4, s5, s6
- MATH-GOLD-005: s2, s3, s4, s5
- MATH-GOLD-006: s2, s3, s4
- MATH-GOLD-007: s2, s3, s4, s5, s6
- MATH-GOLD-008: s2
- MATH-GOLD-009: s2, s3, s4
- MATH-GOLD-010: s2, s3
- MATH-GOLD-011: s2, s3, s4, s5, s6
- MATH-GOLD-012: s2, s3, s4, s5, s6, s7, s8
- MATH-GOLD-013: s2, s3, s4
- MATH-GOLD-014: s2, s3, s4
- MATH-GOLD-015: s3, s4, s5, s6
- MATH-GOLD-016: s2, s3
- MATH-GOLD-017: s2, s3, s4, s5
- MATH-GOLD-018: s1, s2, s3, s4
- MATH-GOLD-019: s2, s3, s4, s5, s6
- MATH-GOLD-020: s1, s2, s3, s4
- MATH-GOLD-021: s3, s4, s5, s6
- MATH-GOLD-022: s2, s3, s4
- MATH-GOLD-023: s2, s3
- MATH-GOLD-024: s2, s3, s4, s5
- MATH-GOLD-025: s2, s3, s4, s5, s6

These changes correct labels, preconditions, scopes, state accounting, and provenance. They do not modify the HML submodule or invent HML syntax.

## Gap disposition after semantic audit

| Existing gap | Revised class | Audit disposition | Boundary decision |
|---|---|---|---|
| MATH-GAP-0001 | CORE_SEMANTIC_MISSING | Genuine repeated capability need | Core proof-state semantics for generic case coverage and invariant-only branch joins; not an absolute-value keyword |
| MATH-GAP-0002 | CORE_SEMANTIC_MISSING | Valid verifier/interface gap | Candidate records and original-constraint checks can be a neutral evidence protocol over generic state |
| MATH-GAP-0003 | CORE_SEMANTIC_MISSING | Valid applicability gap, not a core denotation bug | Generic precondition/obligation interface; domain predicates supplied by libraries |
| MATH-GAP-0004 | CORE_SEMANTIC_MISSING | Valid proof-state gap | Operation-agnostic obligation debt and discharge evidence; no example-specific rule |
| MATH-GAP-0005 | LIBRARY_MISSING | Library gap | Theorem/definition registry with hypothesis-aware evidence |
| MATH-GAP-0006 | LIBRARY_MISSING | Library/verifier gap | Certified symbolic-algebra evidence, not a pile of core rewrites |
| MATH-GAP-0007 | LIBRARY_MISSING | Domain-library gap | Logs, trigonometry, vectors, complex numbers, optimization, and formulas stay outside core |
| MATH-GAP-0008 | LIBRARY_MISSING | Domain-library gap | Abstract finite counting/probability evidence over explicit sample spaces |
| MATH-GAP-0009 | LIBRARY_MISSING | Domain-library gap | Number-theory and finite-minimality certificates |
| MATH-GAP-0010 | TRAJECTORY_SCHEMA_PROBLEM | Potential trajectory-state/schema gap | Validate sequence/exclusion state on more examples before changing HML core |

No CORE_SEMANTIC_BUG was found in the audited mathematical transitions. Several current-HML gaps are real missing interfaces, but the evidence points to generic proof-state, verifier, or library capabilities rather than a fundamentally wrong HML denotation.
No gap was classified SURFACE_SYNTAX_ONLY, TRANSLATION/CANONICALIZATION_PROBLEM, or FALSE_GAP. The separate MATH-GOLD-006 macro finding is a canonicalization/schema warning, not a false mathematical gap.

## All-transition audit ledger

| Trajectory | Step | Action | Audit status | Warrant | Preconditions | Obligations | Dependencies | Scope | State delta | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| MATH-GOLD-001 | s1 | APPLY_DEFINITION | CORRECTED / MACRO-AUDITED | definition_application | none | none | none | global/current | +fact:s1 | continuity reduces to matching adjacent branch values at x=2 and x=-2 |
| MATH-GOLD-001 | s2 | FORMULATE_EQUATION | PASS | boundary_matching | none | none | fact:piecewise | global/current | +fact:s2 | 2a+3=-3 |
| MATH-GOLD-001 | s3 | SOLVE | PASS | equality_preservation | none | none | fact:s2 | global/current | +fact:s3 | a=-3 |
| MATH-GOLD-001 | s4 | FORMULATE_EQUATION | PASS | boundary_matching | none | none | fact:piecewise | global/current | +fact:s4 | -7=-4-b |
| MATH-GOLD-001 | s5 | SOLVE | PASS | equality_preservation | none | none | fact:s4 | global/current | +fact:s5 | b=3 |
| MATH-GOLD-001 | s6 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s3, fact:s5 | global/current | +fact:s6 | a+b=0 |
| MATH-GOLD-002 | s1 | INTRODUCE_VARIABLE | PASS | variable_binding | none | none | none | global/current | +fact:s1 | x and y denote the two positive integers |
| MATH-GOLD-002 | s2 | RECORD_GIVEN | PASS | problem_translation | none | none | none | global/current | +fact:s2 | facts x²+y²=90 and xy=27 are active |
| MATH-GOLD-002 | s3 | APPLY_IDENTITY | PASS | polynomial_identity | none | none | fact:s2 | global/current | +fact:s3 | (x+y)²=144 |
| MATH-GOLD-002 | s4 | EXTRACT_ROOT | PASS | nonnegative_root | x+y≥0 [satisfied] | +obl:root_sign [discharged] | fact:s3 | global/current | +fact:s4; +obl:root_sign | x+y=12 |
| MATH-GOLD-003 | s1 | CROSS_MULTIPLY | PASS | equality_preservation | x-5≠0 [implicit]; 3≠0 [satisfied] | +obl:denominator [discharged] | fact:eq | global/current | +fact:s1; +obl:denominator | 2(x-5)=12 |
| MATH-GOLD-003 | s2 | EXPAND | PASS | distributive_law | none | none | fact:s1 | global/current | +fact:s2 | 2x-10=12 |
| MATH-GOLD-003 | s3 | ADD_BOTH_SIDES | PASS | equality_preservation | none | none | fact:s2 | global/current | +fact:s3 | 2x=22 |
| MATH-GOLD-003 | s4 | DIVIDE_BOTH_SIDES | PASS | equality_preservation | 2≠0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | x=11 |
| MATH-GOLD-004 | s1 | CASE_SPLIT | CORRECTED | absolute_value_definition | x+3≥0 [implicit] | +obl:abs_case_cover [discharged] | none | global/current | +fact:s1; +obl:abs_case_cover | case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) |
| MATH-GOLD-004 | s2 | SOLVE_CASE | CORRECTED | equality_preservation | 5x-1≥0 [implicit] | none | fact:s1 | case 1 | +fact:s2 | case 1 yields x=1 |
| MATH-GOLD-004 | s3 | VERIFY_CANDIDATE | PASS | substitution_check | none | none | fact:s2 | case 1 | +fact:s3 | candidate x=1 satisfies the original equation |
| MATH-GOLD-004 | s4 | SOLVE_CASE | CORRECTED | equality_preservation | 5x-1<0 [implicit] | none | fact:s1 | case 2 | +fact:s4 | case 2 yields x=-1/3 |
| MATH-GOLD-004 | s5 | VERIFY_CANDIDATE | PASS | substitution_check | none | none | fact:s4 | case 2 | +fact:s5 | candidate x=-1/3 satisfies the original equation |
| MATH-GOLD-004 | s6 | SELECT_EXTREMUM | PASS | finite_order | none | none | fact:s3, fact:s5 | global/current | +fact:s6 | largest valid solution is x=1 |
| MATH-GOLD-005 | s1 | INTRODUCE_VARIABLE | PASS | variable_binding | none | none | none | global/current | +fact:s1 | A, B, J are named age variables |
| MATH-GOLD-005 | s2 | FORMULATE_EQUATION | PASS | problem_translation | none | none | fact:s1 | global/current | +fact:s2 | A=3B, J=B+6, A=J |
| MATH-GOLD-005 | s3 | SUBSTITUTE | PASS | equality_substitution | none | none | fact:s2 | global/current | +fact:s3 | 3B=B+6 |
| MATH-GOLD-005 | s4 | SOLVE | MACRO-AUDITED | equality_preservation | 2≠0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | B=3 |
| MATH-GOLD-005 | s5 | DISCHARGE_GOAL | PASS | goal_matching | none | none | fact:s4 | global/current | +fact:s5 | goal B=3 discharged |
| MATH-GOLD-006 | s1 | APPLY_DEFINITION | PASS | change_of_base | x>0 [implicit]; 2>0 and 2≠1 [satisfied]; 4>0 and 4≠1 [satisfied] | none | fact:log_eq | global/current | +fact:s1 | log₄x=(1/2)log₂x |
| MATH-GOLD-006 | s2 | COMBINE_LIKE_TERMS | PASS | coefficient_collection | none | none | fact:s1 | global/current | +fact:s2 | (3/2)log₂x=6 |
| MATH-GOLD-006 | s3 | SOLVE | MACRO-AUDITED | inverse_function | 3/2≠0 [satisfied]; 2>0 and 2≠1 [satisfied] | none | fact:s2 | global/current | +fact:s3 | log₂x=4 and x=2⁴ |
| MATH-GOLD-006 | s4 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s3 | global/current | +fact:s4 | x=16 |
| MATH-GOLD-007 | s1 | ADD_BOTH_SIDES | CORRECTED | equality_preservation | none | none | fact:diff | global/current | +fact:s1 | x=y+4 |
| MATH-GOLD-007 | s2 | SUBSTITUTE | PASS | equality_substitution | none | none | fact:s1, fact:cubes | global/current | +fact:s2 | (y+4)³-y³=28 |
| MATH-GOLD-007 | s3 | EXPAND | PASS | polynomial_expansion | none | none | fact:s2 | global/current | +fact:s3 | 12y²+48y+36=0 |
| MATH-GOLD-007 | s4 | FACTOR | PASS | factorization | none | none | fact:s3 | global/current | +fact:s4 | (y+1)(y+3)=0 |
| MATH-GOLD-007 | s5 | CASE_SPLIT | PASS | zero_product_property | none | none | fact:s4 | global/current | +fact:s5 | candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3) |
| MATH-GOLD-007 | s6 | EVALUATE | PASS | case_invariant | none | none | fact:s5 | global/current | +fact:s6 | both candidates yield xy=-3 |
| MATH-GOLD-008 | s1 | APPLY_DEFINITION | PASS | parity_definition | none | none | fact:parity_f, fact:parity_g | global/current | +fact:s1 | h(-x)=h(x) for h(x)=f(g(x³)) |
| MATH-GOLD-008 | s2 | DISCHARGE_GOAL | PASS | definition_matching | none | none | fact:s1 | global/current | +fact:s2 | goal parity even discharged |
| MATH-GOLD-009 | s1 | APPLY_THEOREM | PASS | AM_GM | x>0,y>0,z>0 [satisfied]; three positive terms [satisfied] | none | fact:product | global/current | +fact:s1 | x+2y+4z ≥ 3∛((x)(2y)(4z)) |
| MATH-GOLD-009 | s2 | EVALUATE | MACRO-AUDITED | exact_arithmetic | none | none | fact:s1 | global/current | +fact:s2 | x+2y+4z≥12 |
| MATH-GOLD-009 | s3 | RECORD_EQUALITY_CONDITION | PASS | AM_GM_equality | none | none | fact:s1, fact:product | global/current | +fact:s3 | equality condition x=2y=4z |
| MATH-GOLD-009 | s4 | SOLVE | PASS | constraint_solving | none | none | fact:s3, fact:product | global/current | +fact:s4 | witness (x,y,z)=(4,2,1) attains 12 |
| MATH-GOLD-010 | s1 | CASE_SPLIT | CORRECTED | combinatorial_partition | none | none | none | global/current | +fact:s1 | case Y/Y; case two distinct colors |
| MATH-GOLD-010 | s2 | COUNT_CASES | PASS | combination_count | none | none | fact:s1 | global/current | +fact:s2 | six distinct-color pairs |
| MATH-GOLD-010 | s3 | COMBINE_CASE_COUNTS | PASS | disjoint_sum | none | none | fact:s1, fact:s2 | global/current | +fact:s3 | total=7 |
| MATH-GOLD-011 | s1 | COMPLEMENT_COUNT | PASS | complement_rule | none | none | fact:population, fact:sample | global/current | +fact:s1 | target = 1-P(no women) |
| MATH-GOLD-011 | s2 | CONDITIONAL_PROBABILITY | PASS | uniform_sampling | none | none | fact:population, fact:sample | global/current | +fact:s2 | P(first male)=7/10 |
| MATH-GOLD-011 | s3 | CONDITIONAL_PROBABILITY | PASS | without_replacement_update | none | none | fact:s2 | global/current | +fact:s3 | P(second male \| first male)=2/3 |
| MATH-GOLD-011 | s4 | CONDITIONAL_PROBABILITY | PASS | without_replacement_update | none | none | fact:s3 | global/current | +fact:s4 | P(third male \| first two male)=5/8 |
| MATH-GOLD-011 | s5 | MULTIPLY_CONDITIONALS | PASS | chain_rule | none | none | fact:s2, fact:s3, fact:s4 | global/current | +fact:s5 | P(no women)=7/24 |
| MATH-GOLD-011 | s6 | COMPLEMENT_COUNT | PASS | complement_rule | none | none | fact:s5 | global/current | +fact:s6 | P(at least one woman)=17/24 |
| MATH-GOLD-012 | s1 | BOUND_REASONING | PASS | upper_bound | none | none | fact:target | global/current | +fact:s1 | at least one die is 6 |
| MATH-GOLD-012 | s2 | CONSTRAINT_PROPAGATION | PASS | arithmetic_constraint | none | none | fact:s1 | global/current | +fact:s2 | remaining two dice sum to 10 |
| MATH-GOLD-012 | s3 | ENUMERATE | CORRECTED | finite_exhaustion | none | +obl:dice_case_cover [discharged] | fact:s2 | global/current | +fact:s3; +obl:dice_case_cover | patterns (6,6,4) and (6,5,5) |
| MATH-GOLD-012 | s4 | COUNT_PERMUTATIONS | PASS | permutation_count | none | none | fact:s3 | case A | +fact:s4 | case A has 3 ordered outcomes |
| MATH-GOLD-012 | s5 | EVALUATE_PROBABILITY | PASS | uniform_product_space | none | none | fact:s4, fact:sample_space | case A | +fact:s5 | P(case A)=3/216=1/72 |
| MATH-GOLD-012 | s6 | COUNT_PERMUTATIONS | PASS | permutation_count | none | none | fact:s3 | case B | +fact:s6 | case B has 3 ordered outcomes |
| MATH-GOLD-012 | s7 | EVALUATE_PROBABILITY | PASS | uniform_product_space | none | none | fact:s6, fact:sample_space | case B | +fact:s7 | P(case B)=3/216=1/72 |
| MATH-GOLD-012 | s8 | COMBINE_CASE_COUNTS | PASS | disjoint_case_sum | none | none | fact:s5, fact:s7 | global/current | +fact:s8 | P(sum=16)=1/36 |
| MATH-GOLD-013 | s1 | APPLY_DEFINITION | PASS | palindrome_definition | none | none | fact:palindrome | global/current | +fact:s1 | free choices are d1 and d2; d4=d1,d3=d2 |
| MATH-GOLD-013 | s2 | COUNT_CASES | PASS | leading_digit_constraint | d1≠0 [satisfied] | none | fact:s1 | global/current | +fact:s2 | d1 has 9 choices |
| MATH-GOLD-013 | s3 | COUNT_CASES | PASS | independent_digit_choice | none | none | fact:s1 | global/current | +fact:s3 | d2 has 10 choices |
| MATH-GOLD-013 | s4 | MULTIPLY_COUNTS | PASS | product_rule | none | none | fact:s2, fact:s3 | global/current | +fact:s4 | count=90 |
| MATH-GOLD-014 | s1 | APPLY_THEOREM | CORRECTED | divisibility_factorization | none | none | fact:number, fact:divisor | global/current | +fact:s1 | 374n must be divisible by 9 and by 2 |
| MATH-GOLD-014 | s2 | APPLY_THEOREM | PASS | digit_sum_rule | none | none | fact:s1 | global/current | +fact:s2 | 14+n is divisible by 9 |
| MATH-GOLD-014 | s3 | BOUND_SEARCH | PASS | finite_digit_domain | 0≤n≤9 [satisfied] | none | fact:s2 | global/current | +fact:s3 | 14+n ∈ {18,27} under digit bound |
| MATH-GOLD-014 | s4 | SELECT_CANDIDATE | PASS | minimal_candidate | 374n divisible by 2 [implicit] | none | fact:s3 | global/current | +fact:s4 | n=4 |
| MATH-GOLD-015 | s1 | INTRODUCE_VARIABLE | PASS | variable_binding | none | none | none | global/current | +fact:s1 | a names the desired positive integer |
| MATH-GOLD-015 | s2 | PARAMETERIZE_CONGRUENCE | PASS | congruence_definition | none | none | fact:congruence_5 | global/current | +fact:s2 | a=4+5n for n≥0 |
| MATH-GOLD-015 | s3 | SUBSTITUTE | PASS | modular_substitution | none | none | fact:s2, fact:congruence_7 | global/current | +fact:s3 | n≡6 mod 7 |
| MATH-GOLD-015 | s4 | BOUND_SEARCH | PASS | least_residue | n≥0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | n≥6 |
| MATH-GOLD-015 | s5 | BOUND_REASONING | CORRECTED | monotonicity | n≥6 [satisfied]; 5>0 [satisfied] | none | fact:s4 | global/current | +fact:s5 | a≥34 |
| MATH-GOLD-015 | s6 | VERIFY_CANDIDATE | PASS | candidate_verification | none | none | fact:s5, fact:congruence_5, fact:congruence_7 | global/current | +fact:s6 | a=34 is minimal and satisfies both congruences |
| MATH-GOLD-016 | s1 | COUNT_EXCLUDED | PASS | counting_exclusions | none | none | fact:index | global/current | +fact:s1 | 14 squares are omitted before the target value |
| MATH-GOLD-016 | s2 | INDEX_TRANSLATION | PASS | index_shift | none | none | fact:s1 | global/current | +fact:s2 | value 200 has sequence index 186 |
| MATH-GOLD-016 | s3 | ADVANCE_SEQUENCE | PASS | successor_iteration | 201,…,214 are nonsquares [implicit] | none | fact:s2 | global/current | +fact:s3 | a_200=214 |
| MATH-GOLD-017 | s1 | PRIME_FACTORIZE | PASS | unique_factorization | none | none | none | global/current | +fact:s1 | 72=2³·3² |
| MATH-GOLD-017 | s2 | APPLY_DEFINITION | PASS | factor_definition | none | none | fact:s1 | global/current | +fact:s2 | factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 |
| MATH-GOLD-017 | s3 | APPLY_DEFINITION | PASS | perfect_power_definition | none | none | fact:s1 | global/current | +fact:s3 | e₂,e₃ must be multiples of 3 |
| MATH-GOLD-017 | s4 | COUNT_CASES | PASS | finite_constraint_intersection | none | none | fact:s2, fact:s3 | global/current | +fact:s4 | admissible exponent choices: e₂∈{0,3}, e₃=0 |
| MATH-GOLD-017 | s5 | COMBINE_CASE_COUNTS | PASS | product_rule | none | none | fact:s4 | global/current | +fact:s5 | count=2 |
| MATH-GOLD-018 | s1 | APPLY_THEOREM | PASS | tangent_addition | 1-tan45°tan30°≠0 [implicit] | none | fact:angle_split | global/current | +fact:s1 | tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) |
| MATH-GOLD-018 | s2 | SUBSTITUTE | PASS | special_value_substitution | none | none | fact:s1, fact:special | global/current | +fact:s2 | tan75°=(1+1/√3)/(1-1/√3) |
| MATH-GOLD-018 | s3 | RATIONALIZE | PASS | radical_normalization | √3-1≠0 [implicit] | none | fact:s2 | global/current | +fact:s3 | tan75°=(√3+1)/(√3-1) |
| MATH-GOLD-018 | s4 | EVALUATE | MACRO-AUDITED | exact_radical_arithmetic | none | none | fact:s3 | global/current | +fact:s4 | tan75°=2+√3 |
| MATH-GOLD-019 | s1 | CLEAR_DENOMINATOR | PASS | denominator_clearing | x≠0 [satisfied] | none | fact:reciprocal | global/current | +fact:s1 | x²-√3x+1=0 |
| MATH-GOLD-019 | s2 | SOLVE | PASS | quadratic_formula | none | none | fact:s1 | global/current | +fact:s2 | x=(√3±i)/2 |
| MATH-GOLD-019 | s3 | APPLY_IDENTITY | CORRECTED | polar_form | none | none | fact:s2 | global/current | +fact:s3 | two unit-complex candidate forms |
| MATH-GOLD-019 | s4 | CASE_SPLIT | PASS | case_evaluation | none | none | fact:s3 | root 1 | +fact:s4 | branch 1 x¹⁸=e^{3πi}=-1 |
| MATH-GOLD-019 | s5 | CASE_SPLIT | PASS | case_evaluation | none | none | fact:s3 | root 2 | +fact:s5 | branch 2 x¹⁸=e^{33πi}=-1 |
| MATH-GOLD-019 | s6 | COMBINE_CASES | PASS | case_invariant | none | +obl:root_case_join [discharged] | fact:s4, fact:s5 | global/current | +fact:s6; +obl:root_case_join | both branches give x¹⁸=-1 |
| MATH-GOLD-020 | s1 | EXPAND | PASS | bilinearity | none | none | none | global/current | +fact:s1 | (a+b)·(a-b)=a·a+b·a-a·b-b·b |
| MATH-GOLD-020 | s2 | CANCEL_SYMMETRIC_TERMS | PASS | dot_product_symmetry | none | none | fact:s1 | global/current | +fact:s2 | cross terms cancel |
| MATH-GOLD-020 | s3 | APPLY_DEFINITION | PASS | norm_definition | none | none | fact:s2 | global/current | +fact:s3 | \|\|a\|\|²-\|\|b\|\|² |
| MATH-GOLD-020 | s4 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s3, fact:norm_a, fact:norm_b | global/current | +fact:s4 | (a+b)·(a-b)=-27 |
| MATH-GOLD-021 | s1 | INTRODUCE_VARIABLE | PASS | consecutive_integer_definition | x≥1 [satisfied] | none | none | global/current | +fact:s1 | legs x and x+1 |
| MATH-GOLD-021 | s2 | FORMULATE_EQUATION | PASS | pythagorean_theorem | none | none | fact:hypotenuse, fact:consecutive | global/current | +fact:s2 | x²+(x+1)²=29² |
| MATH-GOLD-021 | s3 | EXPAND | PASS | polynomial_expansion | none | none | fact:s2 | global/current | +fact:s3 | 2x²+2x+1=841 |
| MATH-GOLD-021 | s4 | FACTOR | PASS | factorization | 2≠0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | x(x+1)=420 |
| MATH-GOLD-021 | s5 | SELECT_CANDIDATE | PASS | finite_factor_search | x and x+1 are positive consecutive integers [satisfied] | none | fact:s4 | global/current | +fact:s5 | legs=(20,21) |
| MATH-GOLD-021 | s6 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s5 | global/current | +fact:s6 | leg sum=41 |
| MATH-GOLD-022 | s1 | APPLY_DEFINITION | CORRECTED | geometric_definition | r>0 [satisfied] | none | none | global/current | +fact:s1 | area=πr² and circumference=2πr |
| MATH-GOLD-022 | s2 | FORMULATE_EQUATION | MACRO-AUDITED | definition_substitution | π≠0 [implicit] | none | fact:s1, fact:sum | global/current | +fact:s2 | r(r+2)=80 |
| MATH-GOLD-022 | s3 | FACTOR | PASS | factor_pair_reasoning | none | none | fact:s2 | global/current | +fact:s3 | seek consecutive-offset factor pair (r,r+2) |
| MATH-GOLD-022 | s4 | SELECT_CANDIDATE | PASS | positive_root_selection | r>0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | r=8 |
| MATH-GOLD-023 | s1 | APPLY_THEOREM | PASS | triangle_inequality | none | none | fact:sides | global/current | +fact:s1 | 4<n<14 |
| MATH-GOLD-023 | s2 | ENUMERATE | PASS | integer_interval_enumeration | n∈Natural [satisfied] | none | fact:s1 | global/current | +fact:s2 | valid n={5,6,7,8,9,10,11,12,13} |
| MATH-GOLD-023 | s3 | EVALUATE | PASS | finite_sum | none | none | fact:s2 | global/current | +fact:s3 | sum=81 |
| MATH-GOLD-024 | s1 | APPLY_PRECEDENCE | PASS | operator_precedence | none | none | none | global/current | +fact:s1 | multiplication/division precede addition/subtraction |
| MATH-GOLD-024 | s2 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s1, fact:expression | global/current | +fact:s2 | 1+12-3+20÷2 |
| MATH-GOLD-024 | s3 | EVALUATE | PASS | exact_arithmetic | none | none | fact:s2 | global/current | +fact:s3 | 1+12-3+10 |
| MATH-GOLD-024 | s4 | EVALUATE | MACRO-AUDITED | operator_precedence | none | none | fact:s3 | global/current | +fact:s4 | 13-3+10=10+10 |
| MATH-GOLD-024 | s5 | DISCHARGE_GOAL | PASS | exact_arithmetic | none | none | fact:s4 | global/current | +fact:s5 | value=20 |
| MATH-GOLD-025 | s1 | INTRODUCE_VARIABLE | PASS | variable_binding | none | none | none | global/current | +fact:s1 | x denotes minutes |
| MATH-GOLD-025 | s2 | FORMULATE_EQUATION | PASS | word_problem_modeling | none | none | fact:s1 | global/current | +fact:s2 | cost_A=10x; cost_B=2000+5x |
| MATH-GOLD-025 | s3 | FORMULATE_INEQUALITY | PASS | comparison_goal | none | none | fact:s2 | global/current | +fact:s3 | 2000+5x<10x |
| MATH-GOLD-025 | s4 | SUBTRACT_BOTH_SIDES | MACRO-AUDITED | order_preserving_affine_transform | 5>0 [satisfied] | none | fact:s3 | global/current | +fact:s4 | x>400 |
| MATH-GOLD-025 | s5 | ROUND_TO_DOMAIN | PASS | integer_ceiling | x∈Natural [satisfied] | none | fact:s4 | global/current | +fact:s5 | minimum whole-number x=401 |
| MATH-GOLD-025 | s6 | VERIFY_CANDIDATE | PASS | candidate_verification | none | +obl:threshold_minimality [discharged] | fact:s5 | global/current | +fact:s6; +obl:threshold_minimality | x=401 satisfies cost_B<cost_A and is minimal |

## Handoff recommendation

Do not fix HML core merely to make these 25 curated trajectories render. The minimum semantically justified next work is: (1) keep generic case coverage/join and obligation interfaces under HML-core review, (2) build separate theorem/domain/verifier libraries, and (3) revise the trajectory schema to represent compound macros and source omissions explicitly before any scale-up. Then rerun the same Gold-25 as a regression set. Do not process Gold-26 or larger data in this mission.
