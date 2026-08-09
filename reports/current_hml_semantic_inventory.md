# Current HML semantic inventory

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
