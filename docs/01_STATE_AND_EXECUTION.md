# HML State and Execution Context

## HOW TO USE THIS FILE

**Readers:** state/execution specialist and project integrator.

**Question answered:** once a mathematical move has been selected, what machine
state exists, what exactly changes, and what must remain invariant?

This file covers deductive state and selected-move execution. Search and discovery
belong primarily in [02_SEARCH_AND_DISCOVERY.md](02_SEARCH_AND_DISCOVERY.md);
meaning and verification in
[03_MEANING_EVIDENCE_AND_VERIFICATION.md](03_MEANING_EVIDENCE_AND_VERIFICATION.md);
implementation decisions in
[04_INTEGRATION_AND_IMPLEMENTATION.md](04_INTEGRATION_AND_IMPLEMENTATION.md).

**Labels:** **EMPIRICAL**, **SOURCE-DERIVED**, **INFERENCE**, **DECISION**, and
**OPEN** distinguish observation from theory and design choice.

## 1. State is a scoped dependency graph

> **EMPIRICAL.** Gold-25 and Gold-125 show that mathematical state cannot be an
> unordered bag of formulas. A fact's status depends on how it was introduced, what
> it depends on, which assumptions and branches are active, and what obligations
> remain open.

The canonical state S_t should make the following recoverable:

| State component | Semantic role |
|---|---|
| objects | Mathematical entities currently in play. |
| declarations | Names, binders, parameters, constants, random variables, and their identity. |
| types/domains | Admissible values and structures; these constrain operations and interpretation. |
| facts | Given, assumed, derived, or verified propositions with epistemic status. |
| assumptions | Scoped premises that may not escape without a valid discharge. |
| constraints | Equations, inequalities, domain conditions, exclusions, and relational restrictions. |
| definitions | Active meanings and version identity; routine deduction must not silently mutate them. |
| goals/subgoals | Claims the trajectory is trying to establish and their status. |
| candidates | Proposed values, witnesses, constructions, or readings not yet promoted to facts. |
| scope | Active binders, assumptions, and lexical/proof frames. |
| branch state | Open cases, branch predicates, local facts, completion, and join eligibility. |
| dependencies | Ancestry edges identifying what supports or constrains each node. |
| obligations | Persistent proof debt, including origin, scope, dependencies, and discharge evidence. |
| epistemic status | What the system is currently licensed to believe about each claim/candidate. |

Conceptually:

    nodes:
      fact, assumption, goal, candidate, obligation,
      definition, constraint, declaration

    edges:
      derived_from, requires, scoped_under, branch_of,
      supports, contradicts, discharges, generated_by

> **DECISION.** This is a semantic graph requirement, not a graph-database
> requirement. Any implementation is acceptable only if ancestry, scope, branch
> locality, and obligation status remain recoverable.

### Empirical support

- **EMPIRICAL:** Gold-125 records 901 dependency edges with maximum fan-in 11.
- **EMPIRICAL:** Gold-25 has dependency/provenance evidence on 105/118 transitions.
- **EMPIRICAL:** Gold-125 state fields include objects, declarations, types/domains,
  facts, assumptions, constraints, definitions, goals, subgoals, candidates,
  branch_state, dependencies, open/discharged obligations, scope, and epistemic status.
- **EMPIRICAL:** only five Gold-125 trajectories contain branch-local steps; rarity
  does not reduce the soundness requirement that local facts must not leak.

## 2. Canonical transition

The basic operational judgement is:

    S_t --a_t--> S_{t+1}

A faithful transition record needs at least:

| Field | Required meaning |
|---|---|
| state_before | Exact active state, including scope and open debt. |
| action / core operation | Generic state/proof effect selected for execution. |
| reasoning mode | Why the action is being attempted now; not the same as its effect. |
| inputs / dependencies | Claims, objects, candidates, definitions, and goals consumed. |
| warrant | Rule, definition, theorem, identity, domain procedure, or backend contract justifying the effect. |
| preconditions | Conditions required before execution under the selected safety policy. |
| obligations created | Proof debt allowed to remain after a provisional transition. |
| obligations discharged | Existing debt closed by named evidence. |
| scope effect | Branch or assumption frames opened, closed, joined, or discharged. |
| goal effect | Goal advanced, created, or discharged. |
| epistemic effect | Candidate proposed, claim derived, verified, rejected, or left unresolved. |
| state delta | Exact additions, removals, status changes, and control-state changes. |
| state_after | Resulting state after applying only legitimate changes. |
| source/evidence provenance | Why this reconstructed move exists and how it was checked. |
| atomicity / uncertainty | Whether the source span is atomic, a macro, or unresolved. |

The transition is faithful only if:

1. the action follows from state_before under its warrant and safety contract;
2. state_after contains every legitimate change and no unrelated change;
3. branch-local or assumption-dependent facts remain scoped;
4. all new facts retain dependency and evidence ancestry;
5. created and discharged obligations are accounted for;
6. epistemic status is verifier-computed or explicitly provisional.

> **EMPIRICAL LIMITATION.** Gold-125 structural checks establish source and state
> consistency under the annotation protocol. They do not prove every source theorem.
> Eighty-nine transitions are marked compound macros and 124 have uncertain atomicity.

## 3. Seventeen adjudicated candidate core effects

> **EMPIRICAL.** Ontology-v1 retains the following 17 KEEP_AS_CORE values after
> separating warrants, libraries, backends, modes, and goal effects. They are
> empirical candidates, **not final or sacred language primitives**.

| Candidate effect | State/execution interpretation |
|---|---|
| DECLARE | Introduce a typed name, object, parameter, or binder. |
| RECORD | Add a given or externally established item with provenance. |
| MODEL | Construct a formal constraint/state representation of source meaning. |
| CONSTRUCT | Create a mathematical object or structured candidate. |
| TRANSFORM | Produce a relation-preserving or warrant-licensed new form. |
| SUBSTITUTE | Replace an occurrence using an equality, assignment, or binder-safe mapping. |
| APPLY_DEFINITION | Unfold or use a definition under its scope and type contract. |
| APPLY_THEOREM | Apply reusable theorem evidence after checking hypotheses. |
| CASE_SPLIT | Begin a case-analysis protocol; the word alone does not certify coverage or joins. |
| ENUMERATE | Generate a finite, provenance-bearing collection under stated bounds. |
| COUNT | Establish a cardinality using a named counting warrant. |
| EVALUATE | Compute a value or closed result through a checked backend/library path. |
| BOUND | Establish or refine an upper/lower/extremal constraint. |
| SELECT | Promote one admissible candidate or branch result under explicit criteria. |
| VERIFY | Check a claim/candidate against evidence or original constraints. |
| CONTRADICTION | Derive inconsistency and reject or close the affected scope. |
| DISCHARGE | Close a goal/obligation/assumption when licensing evidence is present. |

> **OPEN.** Some accepted values may still be composite or better represented as
> state/control effects. In particular, DISCHARGE already also appears naturally as
> a goal effect. The current list is a working interface, not a syntax mandate.

## 4. What disappeared from the core

> **EMPIRICAL.** Named operations often described the knowledge used rather than a
> distinct state effect. Ontology-v1 factors them as follows:

| Surface/named label | Generic effect | Warrant or layer |
|---|---|---|
| TRIG_IDENTITY | TRANSFORM | TRIGONOMETRY_IDENTITY / DOMAIN_LIBRARY |
| MODULAR_REASONING | TRANSFORM | MODULAR_ARITHMETIC / DOMAIN_LIBRARY |
| PROBABILITY, EVALUATE_PROBABILITY | EVALUATE | PROBABILITY_LAW / DOMAIN_LIBRARY |
| SEQUENCE_RECURRENCE | TRANSFORM | SEQUENCE_RULE / DOMAIN_LIBRARY |
| DIFFERENTIATE, INTEGRATE | TRANSFORM | CALCULUS_RULE / DOMAIN_LIBRARY or backend |
| TAKE_LIMIT | EVALUATE | CALCULUS_RULE / DOMAIN_LIBRARY or backend |
| INCLUSION_EXCLUSION, PIGEONHOLE | COUNT | COUNTING_RULE or THEOREM / THEOREM_LIBRARY |
| EXPAND, FACTOR, RATIONALIZE | TRANSFORM | SYMBOLIC_NORMALIZATION / SYMBOLIC_BACKEND |
| APPLY_PRECEDENCE, closed arithmetic | EVALUATE | NUMERIC_EVALUATION / NUMERIC_BACKEND |
| OPTIMIZE | BOUND | goal-directed selection / goal effect |
| SEARCH_META | underlying action varies | reasoning mode, not execution effect |

The architectural rule is:

    generic operation
      + mathematical warrant
      + knowledge layer / backend
      + state/control effects

not one bespoke core instruction per theorem family.

## 5. Preconditions

> **EMPIRICAL.** Gold-125 records 340 precondition records: 24 satisfied, 10
> implicit, 107 explicit in the source, and 199 UNKNOWN. The UNKNOWN count is a
> measurement of missing applicability evidence, not permission to execute.

Recurring examples include:

- nonzero denominators before cancellation, division, or reciprocals;
- sign conditions for inequality transformations;
- nonnegative radicands and sign choice when extracting roots;
- logarithm bases, arguments, and domain restrictions;
- integer/natural constraints in divisibility, counting, and induction;
- theorem hypotheses, independence assumptions, finite sample-space assumptions;
- branch predicates and exhaustive/disjoint coverage conditions;
- original-problem constraints when generated candidates are checked.

> **INFERENCE.** A precondition is a condition required before an operation may
> execute under a chosen safety contract. It may be established by state, discharged
> by a verifier, or block the step. A system must not infer “source span exists” ⇒
> “all applicability conditions hold.”

## 6. Persistent obligations

> **EMPIRICAL.** Gold-125 records 257 obligations created, 243 with measured
> lifetimes, mean measured lifetime 2.54 steps, maximum lifetime 13 steps, 48
> immediately discharged, and 8 open at final state.

This supports first-class persistent proof debt:

    execute operation
          ↓
    result produced + obligation O created
          ↓
    reasoning continues while O remains OPEN
          ↓
    later evidence E discharges O

A useful conceptual obligation record is:

| Field | Meaning |
|---|---|
| id / proposition | Stable identity and exact debt. |
| generated_by / reason | Operation and safety contract that created it. |
| dependencies / scope | Facts and assumptions under which the debt exists. |
| status | OPEN, DISCHARGED, FAILED, or conservatively UNKNOWN. |
| created_at / discharged_at | Lifetime in trajectory state. |
| discharged_by | Named claim, certificate, library result, or backend evidence. |

> **INFERENCE.** Preconditions and obligations are related but distinct. For
> “divide by x,” x≠0 may be a hard precondition or generated debt depending on the
> operation/backend contract. The semantic model should support both policies rather
> than hard-code one global answer.

> **CURRENT HML.** The pinned implementation has rule-generated obligations,
> propagation, scoped discharge checks, exact checkers, and fail-closed status. It
> does not uniformly synthesize all domain conditions observed in MATH.

## 7. Candidates are not facts

> **EMPIRICAL.** Root extraction, solving, finite search, construction, and
> optimization repeatedly produce candidates that require later checking.

A candidate lifecycle should distinguish:

    PROPOSED
        ↓
    UNVERIFIED
       / \
      ↓   ↓
    VERIFIED   REJECTED

- **PROPOSED:** generated by search, algebra, construction, or a backend.
- **UNVERIFIED:** well-formed and retained, but not licensed as a solution.
- **VERIFIED:** satisfies the original constraints and all required obligations.
- **REJECTED:** contradicted by original constraints, domain conditions, or evidence.

Example:

    square equation → candidates x=3, x=-3
                    → check each against original equation
                    → verified/rejected statuses

> **DECISION.** An algebraic backend must not silently promote every generated root
> to a fact or final solution. Candidate provenance and original-constraint checking
> are part of state.

## 8. Branching, assumptions, and scope

> **EMPIRICAL.** Gold-125 contains 26 branch-local steps in five trajectories,
> maximum recorded branch depth 1, 15 CASE_SPLIT labels, one explicit branch join,
> and zero certified exhaustive partitions or invariant joins. This is evidence of an
> underrepresented protocol, not evidence that joins are easy.

Case reasoning requires at least:

1. declare the partition and any coverage/disjointness obligation;
2. open each branch with its local predicate or assumption;
3. derive branch-local results without leakage;
4. close the branch and record its result/debt;
5. certify required coverage and compatibility;
6. join only claims licensed by every required branch;
7. discharge assumptions when the proof rule permits.

Conceptually:

    CASE_SPLIT on P

      branch A under P       branch B under not P
          derive R               derive R

      JOIN requires coverage(A,B) and licensed R in each branch
      JOIN yields R globally

> **SOURCE-DERIVED — Winskel.** Scope, binding, substitution, and proof rules are
> semantic machinery. Capture avoidance and assumption locality are not rendering
> details.

> **CURRENT HML.** Lexical scope, binder identity, capture-aware substitution, and
> scoped assumptions exist. General exhaustive/disjoint case certificates and safe
> branch joins remain absent or partial.

## 9. Dependencies and provenance

Facts must retain at least:

- whether they are GIVEN, ASSUMED, DERIVED, VERIFIED, or supplied by a tool;
- the exact premise and definition dependencies;
- active scope and branch ancestry;
- warrant and evidence/certificate identity;
- obligations inherited or discharged;
- source span and canonicalization provenance when corpus-derived.

The same expression has different semantic force when it is a problem given, a
branch assumption, a checked derivation, a candidate, or an untrusted oracle result.

> **DECISION.** State transformations must be dependency-preserving. Removing a
> premise, closing an assumption, or rejecting a candidate must make downstream
> support consequences inspectable.

## 10. Induction is unresolved as a primitive

> **EMPIRICAL.** INDUCT appears in seven Gold-125 transitions across four categories.
> Ontology-v1 preserves it as an 18th candidate value but excludes it from the 17
> accepted-core count because the sample does not establish an independent primitive.

> **SOURCE-DERIVED — Winskel.** Mathematical, structural, and well-founded induction
> are proof methods. The obvious induction hypothesis can be too weak; selecting a
> stronger hypothesis is itself mathematical work.

A possible decomposition is:

    choose proof schema: induction                  [search/control]
      ↓
    create base subgoal                             [state/control]
      ↓
    prove base                                      [execution/verification]
      ↓
    introduce arbitrary index                       [scope]
      ↓
    assume induction hypothesis                     [scope]
      ↓
    create step subgoal                             [state/control]
      ↓
    execute and verify step
      ↓
    if hypothesis is insufficient:
        propose stronger hypothesis                 [search]
        rebuild base/step obligations
      ↓
    discharge assumption and generalize             [proof protocol]

> **OPEN.** Whether induction is a reusable protocol, library proof schema,
> composition of existing effects, or a genuine core operation requires a targeted
> proof-state sample. Do not invent syntax now.

## 11. Operational, denotational, and axiomatic agreement

> **SOURCE-DERIVED — Winskel.** Three semantic views answer different questions:

- **Denotational:** what mathematical object or relation does expression e denote
  under environment ρ?
- **Operational:** what state change does executing a produce?
- **Axiomatic/proof-theoretic:** what conclusion does Γ license under the proof rules?

An expression may parse and type-check yet denote the wrong mathematics. A backend
may compute a result without licensing it as a proof. A proposition may be true in
the intended model while the current proof system cannot establish it.

Future conformance targets include:

- operational–denotational agreement;
- proof-rule soundness relative to denotation;
- type preservation;
- binding and scope preservation;
- dependency and obligation preservation;
- status monotonicity only under licensed evidence.

These are specification goals, not claims that current HML has proved them globally.

## HIGH-CONFIDENCE state/execution requirements

> **DECISION.** Architectural provisions are justified now for:

- canonical typed state and explicit goals/subgoals;
- dependency/provenance ancestry;
- scoped assumptions and branch-local state;
- first-class preconditions and persistent obligations;
- candidate status distinct from fact status;
- operation separated from warrant/library/backend;
- exact state deltas and explicit control effects;
- verifier-computed epistemic outcomes;
- uncertainty and unsupported states rather than fabricated certainty.

## OPEN execution questions

- Which of the 17 candidates are genuinely primitive versus convenient interfaces?
- Can DISCHARGE be only a goal/control effect while retaining ergonomic execution?
- What is the minimal sound branch/join certificate?
- Which preconditions are hard blockers versus deferrable obligations?
- How should obligation inheritance interact with rejected candidates and closed branches?
- Can semantic equivalence safely collapse state nodes without erasing provenance?
- How should induction and strengthened hypotheses be represented compositionally?
- What atomicity model replaces compound source sentences without inventing steps?

## DO-NOT-IMPLEMENT-YET

- Do not add 17 HML keywords because 17 candidate effects survived adjudication.
- Do not add INDUCT or STRENGTHEN_HYPOTHESIS syntax before targeted evidence.
- Do not treat CASE_SPLIT as sufficient without coverage, locality, and join semantics.
- Do not promote domain procedure names into the kernel.
- Do not make UNKNOWN preconditions silently true.
- Do not mutate frozen Gold trajectories to fit this model.
