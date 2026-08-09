# Gold-25 reasoning operation registry v0

This is an empirical discovery registry, not a completeness claim. Operations are kept separate from mathematical theorem/library names and from surface discourse phrases.

## ALGEBRAIC_TRANSFORMATION

### `CANCEL_SYMMETRIC_TERMS`

- Meaning: Cancel equal cross terms using a symmetry law.
- Inputs: expanded expression, symmetry law
- Preconditions observed: none recorded
- Warrant: `symmetry`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-020
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `COMBINE_LIKE_TERMS`

- Meaning: Collect structurally equivalent terms.
- Inputs: expression
- Preconditions observed: none recorded
- Warrant: `normalization`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-006
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `EXPAND`

- Meaning: Apply distributivity or polynomial expansion.
- Inputs: expression
- Preconditions observed: none recorded
- Warrant: `distributive_law`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-003, MATH-GOLD-007, MATH-GOLD-020, MATH-GOLD-021
- Frequency: **4**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `EXTRACT_ROOT`

- Meaning: Recover a root from a powered equality under sign/domain conditions.
- Inputs: powered equality, sign/domain condition
- Preconditions observed: x+y≥0
- Warrant: `root_extraction`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves or branches scope
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-002
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `closed_eval_v1 only for closed claims`

### `FACTOR`

- Meaning: Rewrite an expression as a product or factorized form.
- Inputs: expression
- Preconditions observed: 2≠0
- Warrant: `factorization`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-007, MATH-GOLD-021, MATH-GOLD-022
- Frequency: **3**
- HML: `PARTIAL,REPRESENTABLE_ONLY`; rule/construct `none`

### `RATIONALIZE`

- Meaning: Clear a radical denominator while preserving an exact ratio.
- Inputs: fraction, nonzero conjugate
- Preconditions observed: √3-1≠0
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-018
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## CASE_ANALYSIS

### `CASE_SPLIT`

- Meaning: Partition a problem into explicitly scoped exhaustive branches.
- Inputs: case predicate, coverage argument
- Preconditions observed: x+3≥0
- Warrant: `case_partition`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: creates branches
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-004, MATH-GOLD-007, MATH-GOLD-010, MATH-GOLD-019
- Frequency: **5**
- HML: `PARTIAL`; rule/construct `scope (no join rule)`

### `COMBINE_CASES`

- Meaning: Merge complete branches when they imply a common result.
- Inputs: complete branches, common result
- Preconditions observed: none recorded
- Warrant: `case invariant`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: merges branches
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-019
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `SOLVE_CASE`

- Meaning: Apply local transformations inside one branch.
- Inputs: branch assumption, equation
- Preconditions observed: none recorded
- Warrant: `branch_local_validity`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: branch-local
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-004
- Frequency: **2**
- HML: `PARTIAL`; rule/construct `scope + local rules`

## COMBINATORIAL_REASONING

### `COMBINE_CASE_COUNTS`

- Meaning: Sum counts from disjoint cases.
- Inputs: disjoint case counts
- Preconditions observed: none recorded
- Warrant: `disjoint_sum`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: merges branches
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-010, MATH-GOLD-012, MATH-GOLD-017
- Frequency: **3**
- HML: `PARTIAL`; rule/construct `none`

### `COUNT_CASES`

- Meaning: Count a finite set of cases or choices.
- Inputs: finite domain, constraints
- Preconditions observed: d1≠0
- Warrant: `finite_counting`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: may create branches
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-010, MATH-GOLD-013, MATH-GOLD-017
- Frequency: **4**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `COUNT_PERMUTATIONS`

- Meaning: Count arrangements subject to repeated or distinct objects.
- Inputs: multiset or ordered sample
- Preconditions observed: none recorded
- Warrant: `permutation_count`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-012
- Frequency: **2**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `MULTIPLY_COUNTS`

- Meaning: Multiply independent finite choices.
- Inputs: choice counts
- Preconditions observed: none recorded
- Warrant: `product_rule`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-013
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `none`

## CONSTRAINT_REASONING

### `BOUND_REASONING`

- Meaning: Use a bound to eliminate impossible cases.
- Inputs: domain bound, target
- Preconditions observed: none recorded
- Warrant: `upper/lower bound`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: prunes cases
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-012
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `BOUND_SEARCH`

- Meaning: Use a finite domain or lower/upper bound to narrow admissible candidates.
- Inputs: constraint, bounded domain
- Preconditions observed: 0≤n≤9, n≥0
- Warrant: `bounded_search`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: prunes candidates
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-014, MATH-GOLD-015
- Frequency: **2**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `CONSTRAINT_PROPAGATION`

- Meaning: Propagate a numerical constraint through a structured state.
- Inputs: constraint, state
- Preconditions observed: none recorded
- Warrant: `constraint propagation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: updates state
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-012
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `none`

### `ENUMERATE`

- Meaning: Enumerate a finite domain and certify completeness.
- Inputs: finite domain, coverage criterion
- Preconditions observed: n∈Natural
- Warrant: `finite exhaustion`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: may create branches
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-012, MATH-GOLD-023
- Frequency: **2**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `ROUND_TO_DOMAIN`

- Meaning: Select the least domain element satisfying a strict threshold.
- Inputs: threshold, discrete domain
- Preconditions observed: x∈Natural
- Warrant: `integer ceiling`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-025
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `SELECT_CANDIDATE`

- Meaning: Choose admissible candidates using domain, order, or minimality constraints.
- Inputs: candidate set, domain/order constraint
- Preconditions observed: 374n divisible by 2, r>0, x and x+1 are positive consecutive integers
- Warrant: `minimality/admissibility`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-014, MATH-GOLD-021, MATH-GOLD-022
- Frequency: **3**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## DECLARATION

### `INTRODUCE_VARIABLE`

- Meaning: Name a mathematical object and assign a type/domain.
- Inputs: source object or quantity
- Preconditions observed: r>0, x≥1
- Warrant: `variable_binding`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: adds a name to current scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-001, MATH-GOLD-002, MATH-GOLD-005, MATH-GOLD-015, MATH-GOLD-021, MATH-GOLD-022, MATH-GOLD-025
- Frequency: **7**
- HML: `FULL,REPRESENTABLE_ONLY`; rule/construct `var/param`

## DEFINITION_APPLICATION

### `APPLY_DEFINITION`

- Meaning: Use a definition to rewrite or constrain an object.
- Inputs: definition, object
- Preconditions observed: 2>0 and 2≠1, 4>0 and 4≠1, x>0
- Warrant: `definition`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-006, MATH-GOLD-008, MATH-GOLD-013, MATH-GOLD-014, MATH-GOLD-017, MATH-GOLD-020
- Frequency: **7**
- HML: `REPRESENTABLE_ONLY`; rule/construct `def/evidence`

## EQUATION_CONSTRUCTION

### `FORMULATE_EQUATION`

- Meaning: Construct an equation or inequality from verbal/geometric relations.
- Inputs: objects, relations
- Preconditions observed: π≠0
- Warrant: `problem_translation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: global or current branch
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-001, MATH-GOLD-005, MATH-GOLD-021, MATH-GOLD-022, MATH-GOLD-025
- Frequency: **6**
- HML: `REPRESENTABLE_ONLY`; rule/construct `assume/goal`

### `FORMULATE_INEQUALITY`

- Meaning: Construct a comparison encoding the requested optimization or threshold.
- Inputs: costs or bounds, goal relation
- Preconditions observed: none recorded
- Warrant: `comparison_goal`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: global
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-025
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `goal/assume`

## EQUATION_TRANSFORMATION

### `ADD_BOTH_SIDES`

- Meaning: Add the same term to both sides.
- Inputs: equality, term
- Preconditions observed: none recorded
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-003
- Frequency: **1**
- HML: `FULL`; rule/construct `add_both_sides`

### `CLEAR_DENOMINATOR`

- Meaning: Remove a denominator under a nonzero precondition.
- Inputs: equation, nonzero denominator
- Preconditions observed: x≠0
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-019
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `multiply_both_sides`

### `CROSS_MULTIPLY`

- Meaning: Clear denominators by multiplying both sides.
- Inputs: equation, denominators
- Preconditions observed: 3≠0, x-5≠0
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-003
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `multiply_both_sides + partiality`

### `DIVIDE_BOTH_SIDES`

- Meaning: Divide both sides by a nonzero quantity.
- Inputs: equality, nonzero divisor
- Preconditions observed: 2≠0
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-003
- Frequency: **1**
- HML: `FULL`; rule/construct `divide_both_sides`

### `SUBTRACT_BOTH_SIDES`

- Meaning: Subtract the same term from both sides.
- Inputs: equality, term
- Preconditions observed: 5>0
- Warrant: `equality_preservation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-025
- Frequency: **1**
- HML: `PARTIAL`; rule/construct `subtract_both_sides`

## EVALUATION

### `APPLY_PRECEDENCE`

- Meaning: Choose the next evaluation layer using operator precedence.
- Inputs: expression, precedence relation
- Preconditions observed: none recorded
- Warrant: `operator precedence`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-024
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `closed evaluator`

### `EVALUATE`

- Meaning: Compute a closed or instantiated expression exactly.
- Inputs: expression
- Preconditions observed: none recorded
- Warrant: `exact_arithmetic`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-001, MATH-GOLD-006, MATH-GOLD-007, MATH-GOLD-009, MATH-GOLD-015, MATH-GOLD-018, MATH-GOLD-020, MATH-GOLD-021, MATH-GOLD-023, MATH-GOLD-024
- Frequency: **12**
- HML: `PARTIAL,REPRESENTABLE_ONLY`; rule/construct `closed_eval_v1 for closed claims`

## GOAL_MANAGEMENT

### `DISCHARGE_GOAL`

- Meaning: Mark a target resolved by a verified result.
- Inputs: goal, supporting result
- Preconditions observed: none recorded
- Warrant: `goal_matching`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: closes goal
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-005, MATH-GOLD-008, MATH-GOLD-024
- Frequency: **3**
- HML: `FULL,PARTIAL,REPRESENTABLE_ONLY`; rule/construct `proved`

### `SELECT_EXTREMUM`

- Meaning: Select a maximum/minimum from a verified finite candidate set.
- Inputs: verified candidates, order
- Preconditions observed: none recorded
- Warrant: `finite_order`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: merges candidates
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-004
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `SOLVE`

- Meaning: Transform constraints to isolate a target or solve a polynomial.
- Inputs: equations, target
- Preconditions observed: 2>0 and 2≠1, 2≠0
- Warrant: `constraint_solving`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves or branches scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-001, MATH-GOLD-005, MATH-GOLD-006, MATH-GOLD-009, MATH-GOLD-019
- Frequency: **6**
- HML: `PARTIAL,REPRESENTABLE_ONLY`; rule/construct `none`

## NUMBER_THEORY

### `PARAMETERIZE_CONGRUENCE`

- Meaning: Replace a congruence with an integer parameterization.
- Inputs: congruence, residue
- Preconditions observed: none recorded
- Warrant: `congruence definition`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: adds parameter
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-015
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `PRIME_FACTORIZE`

- Meaning: Represent an integer by prime exponents.
- Inputs: integer
- Preconditions observed: none recorded
- Warrant: `unique factorization`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-017
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## PROBABILISTIC_REASONING

### `COMPLEMENT_COUNT`

- Meaning: Compute an event through its complement.
- Inputs: event partition, complement probability
- Preconditions observed: none recorded
- Warrant: `complement_rule`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-011
- Frequency: **2**
- HML: `PARTIAL,REPRESENTABLE_ONLY`; rule/construct `none`

### `CONDITIONAL_PROBABILITY`

- Meaning: Update a finite probability after observations without replacement.
- Inputs: population state, event
- Preconditions observed: none recorded
- Warrant: `conditional_probability`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: updates state counts
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-011
- Frequency: **3**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `EVALUATE_PROBABILITY`

- Meaning: Evaluate a finite probability from a sample-space model.
- Inputs: sample space, favorable outcomes
- Preconditions observed: none recorded
- Warrant: `uniform_product_space`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-012
- Frequency: **2**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `MULTIPLY_CONDITIONALS`

- Meaning: Multiply a chain of conditional probabilities.
- Inputs: conditional probabilities
- Preconditions observed: none recorded
- Warrant: `chain_rule`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-011
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## SEQUENCE_REASONING

### `ADVANCE_SEQUENCE`

- Meaning: Advance through a sequence while maintaining its admissibility rule.
- Inputs: current term, successor rule
- Preconditions observed: 201,…,214 are nonsquares
- Warrant: `successor iteration`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-016
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `COUNT_EXCLUDED`

- Meaning: Count omitted terms before a target sequence position.
- Inputs: sequence rule, target
- Preconditions observed: none recorded
- Warrant: `counting exclusions`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-016
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `INDEX_TRANSLATION`

- Meaning: Translate an ambient index after exclusions or offsets.
- Inputs: index, excluded values
- Preconditions observed: none recorded
- Warrant: `index shift`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-016
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## STATE

### `RECORD_GIVEN`

- Meaning: Move source-given information into active state facts.
- Inputs: problem statement
- Preconditions observed: none recorded
- Warrant: `problem_translation`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: global fact
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-002
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `assume`

## SUBSTITUTION

### `SUBSTITUTE`

- Meaning: Replace equal or defined content in a target expression.
- Inputs: equality/definition, target
- Preconditions observed: none recorded
- Warrant: `equality_substitution`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: must avoid binder capture
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-005, MATH-GOLD-007, MATH-GOLD-015, MATH-GOLD-018
- Frequency: **5**
- HML: `FULL,PARTIAL,REPRESENTABLE_ONLY`; rule/construct `substitute`

## THEOREM_APPLICATION

### `APPLY_IDENTITY`

- Meaning: Apply a general algebraic or structural identity.
- Inputs: expression, identity
- Preconditions observed: none recorded
- Warrant: `identity`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-002, MATH-GOLD-019
- Frequency: **2**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `APPLY_THEOREM`

- Meaning: Invoke a named mathematical theorem with hypotheses.
- Inputs: theorem, hypotheses, target
- Preconditions observed: 1-tan45°tan30°≠0, three positive terms, x>0,y>0,z>0
- Warrant: `theorem`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-009, MATH-GOLD-014, MATH-GOLD-018, MATH-GOLD-023
- Frequency: **4**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

### `RECORD_EQUALITY_CONDITION`

- Meaning: Record the equality conditions attached to a bound or theorem.
- Inputs: theorem, equality conditions
- Preconditions observed: none recorded
- Warrant: `theorem_equality_case`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: preserves scope
- Dependencies: records cited facts and prior results
- Obligations: creates=False; discharges=False
- Example(s): MATH-GOLD-009
- Frequency: **1**
- HML: `REPRESENTABLE_ONLY`; rule/construct `none`

## VERIFICATION

### `VERIFY_CANDIDATE`

- Meaning: Substitute a generated candidate into the original constraints.
- Inputs: candidate, original constraints
- Preconditions observed: none recorded
- Warrant: `candidate_verification`
- State effect: adds or transforms a fact in the current trajectory state
- Scope: branch-local or global
- Dependencies: records cited facts and prior results
- Obligations: creates=True; discharges=True
- Example(s): MATH-GOLD-004, MATH-GOLD-015, MATH-GOLD-025
- Frequency: **4**
- HML: `PARTIAL,REPRESENTABLE_ONLY`; rule/construct `closed_eval_v1 only for closed claims`
