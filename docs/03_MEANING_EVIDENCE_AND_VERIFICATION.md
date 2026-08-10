# HML Meaning, Evidence, and Verification Context

## HOW TO USE THIS FILE

**Readers:** semantics/verifier specialist and project integrator.

**Question answered:** what does a mathematical claim mean, why is a transition
legal, and what evidence permits the system to believe it?

State mutation belongs in
[01_STATE_AND_EXECUTION.md](01_STATE_AND_EXECUTION.md); planner behavior in
[02_SEARCH_AND_DISCOVERY.md](02_SEARCH_AND_DISCOVERY.md); implementation gates in
[04_INTEGRATION_AND_IMPLEMENTATION.md](04_INTEGRATION_AND_IMPLEMENTATION.md).

**Labels:** **EMPIRICAL**, **SOURCE-DERIVED**, **INFERENCE**, **DECISION**, and
**OPEN** distinguish measured corpus findings from semantic theory.

## 1. Four different questions

A robust mathematical event must answer separately:

1. **What does the source mean?** Interpretation, binding, scope, domain, and
   candidate readings.
2. **What happened?** Generic operation and exact state/control effects.
3. **Why is it legal?** Warrant, preconditions, library/backend contract, and
   evidence/certificate.
4. **What may now be believed?** Conservative epistemic update computed from the
   evidence and unresolved debt.

> **DECISION.** Parsing, typing, denotation, execution, proof licensing, task
> alignment, and final-answer relevance must not collapse into one VALID flag.

## 2. Ontology-v1's orthogonal decomposition

> **EMPIRICAL.** The current derived view separates:

| Axis | Question |
|---|---|
| reasoning_mode | Why is this step being attempted now? |
| core_operation | What reusable mathematical state/proof effect occurs? |
| warrant | What rule, definition, theorem, identity, or computational contract justifies it? |
| knowledge_layer | Does justification live in core, theorem/domain library, backend, or search metadata? |
| preconditions | What must already hold before this action is licensed? |
| evidence/certificate | What inspectable artifact establishes the warrant application or result? |
| goal_effect | Does the event create, advance, or discharge a goal? |
| scope_effect | Does it open, close, join, introduce, or discharge a branch/assumption? |
| epistemic_effect | Does it propose, derive, verify, reject, refute, or leave unresolved? |
| obligations | What proof debt is created, inherited, discharged, failed, or remains open? |
| dependencies/state_delta | What exact ancestry and state change results? |
| atomicity/uncertainty | Is the source effect atomic, compound, ambiguous, or under review? |

The decomposition is semantic, not merely a way to store two competing labels.
Each axis predicts different state or verification behavior.

## 3. The 43-disagreement result

> **EMPIRICAL.** An independent hard audit found 43 broad-operation disagreements.
After ontology-v1 adjudication, 42/43 are explained by orthogonal axes, granularity, or
preserved ambiguity; one remains a genuine annotation error/review.

| Collision cause | Count | What was conflated |
|---|---:|---|
| OPERATION_VS_WARRANT_COLLISION | 14 | Generic effect versus named mathematical justification. |
| OPERATION_VS_GOAL_EFFECT_COLLISION | 13 | Mathematical work versus closing/advancing a goal. |
| GRANULARITY_DISAGREEMENT | 8 | Different operations inside one compressed source span. |
| AMBIGUOUS_SOURCE | 4 | Plausible operation cue without enough evidence for a forced label. |
| OPERATION_VS_DOMAIN_COLLISION | 2 | Generic effect versus named domain procedure. |
| MODE_VS_OPERATION_COLLISION | 1 | Search/planning role versus underlying state effect. |
| ANNOTATION_ERROR | 1 | Frozen label not supported by the source meaning. |

Concrete decompositions:

    core_operation = TRANSFORM
    warrant = TRIGONOMETRY_IDENTITY
    knowledge_layer = DOMAIN_LIBRARY

    core_operation = EVALUATE
    goal_effect = DISCHARGE

    core_operation = CONSTRUCT
    reasoning_mode = SEARCH_META

The genuine error is MATH-GOLD-043 s1: converting money amounts to cents was
labeled APPLY_THEOREM even though the source describes a representation/modeling
choice. The frozen annotation remains preserved for provenance and review.

> **LIMITATION.** Explaining a label conflict is not proof that the reconstructed
transition is mathematically valid. State entailment, scope, conditions, obligations,
and evidence still require independent checking.

## 4. Language interpretation is not inference

> **SOURCE-DERIVED — Blackburn & Bos.** Natural-language interpretation and
inference over a semantic representation are distinct computational stages.

For HML:

    source language
          ↓
    candidate or underspecified meaning(s)
          ↓
    typing, binding, domain, context, and alignment checks
          ↓
    resolved or still-ambiguous semantic object
          ↓
    mathematical reasoning

This separation permits failure diagnosis:

- **interpretation error:** the formal object does not preserve source meaning;
- **reasoning error:** the selected transition is invalid over an adequate meaning;
- **evidence error:** a valid-looking result lacks a trustworthy warrant/certificate;
- **task error:** the proof establishes something other than the original target.

> **INFERENCE.** Gold-125 largely starts after source interpretation. Ontology-v1
does not yet constitute a natural-language semantic parser.

## 5. Underspecified and multiple meanings

> **SOURCE-DERIVED — Blackburn & Bos.** Scope ambiguity can be represented by an
underspecified constrained meaning rather than forcing one early reading or adding an
ad-hoc mechanism for every construction.

Potential upstream states include:

    SCOPE_UNRESOLVED
    BINDING_UNRESOLVED
    TYPE_UNRESOLVED
    DOMAIN_UNRESOLVED
    REFERENCE_AMBIGUOUS
    MULTIPLE_READINGS

Conceptually:

    READING_SET {R1, R2, ...}
      + binding/scope/type/domain constraints
      + source-alignment evidence

Candidate readings can be filtered by typing, domain constraints, consistency,
contextual knowledge, and verified semantic equivalence. They should not be silently
collapsed because a parser needs one AST.

> **MEDIUM-CONFIDENCE INFERENCE.** This interpretation layer belongs upstream of
the current ontology-v1 event, with fields such as reading_id, semantic_status,
scope_status, binding_status, interpretation constraints, alternatives, and alignment
evidence. Exact schema and syntax remain open.

## 6. Denotation, model, and satisfaction

> **SOURCE-DERIVED — Blackburn & Bos / Winskel.** A proposition obtains meaning
relative to an interpretation/model and variable assignment. For example, x>3 is not
truth-evaluable without enough information about x, its domain, and active assumptions.

Conceptually:

    M, ρ ⊨ P

State must therefore make the relevant domain/structure, assignment, definitions,
problem givens, and assumptions recoverable. Denotation is not optional prose.

> **SOURCE-DERIVED — Winskel.** Operational execution and proof rules must be
sound relative to denotation. A computation that returns a value is not automatically
a proof; a semantically true proposition may remain unproved by the available rules.

## 7. Semantic rather than string equivalence

> **SOURCE-DERIVED / INFERENCE.** Different strings may denote the same object:

    2x + 2
    x + x + 2
    2(x + 1)
    (x + 1) + (x + 1)

Where a trustworthy equivalence backend applies, candidate results can be clustered
by semantic class rather than raw text. This may support deduplication, voting, state
normalization, and dependency comparison.

> **DECISION.** Never assert equivalence merely because expressions look similar or
a backend times out. Equivalence evidence must report assumptions, domain,
approximation, and unsupported forms. Provenance must survive normalization.

## 8. Consistency, entailment, informativeness, and relevance

> **SOURCE-DERIVED — Blackburn & Bos.** Consistency, entailment, and
informativity are distinct inference tasks.

For HML, evaluate a candidate on separate dimensions:

| Dimension | Question |
|---|---|
| validity / entailment | Does the active state and warrant license the claim? |
| consistency | Is the candidate compatible with the active state/model? |
| novelty / information gain | Does it add information rather than repeat an equivalent fact? |
| goal relevance | Does it advance the active goal or a justified subgoal? |

Goal relevance is an HML architectural extension, not attributed directly to
Blackburn & Bos.

A step may be valid but useless, novel but false, goal-relevant but unsupported, or
consistent but redundant. One fuzzy “good step” score would erase these differences.

## 9. Proof search and falsification search

> **SOURCE-DERIVED — Blackburn & Bos.** Theorem proving and model building can
provide complementary evidence directions.

> **SOURCE-DERIVED — FormalMATH.** Negation-based disproof is a useful asymmetric
filter: proving ¬T rejects T; failure to prove ¬T does not establish T.

Generalized architecture:

                        CLAIM P
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
             PROVE P          SEARCH COUNTEREXAMPLE
          kernel/Lean/SMT       model/numeric/symbolic
                │                     │
                └──────────┬──────────┘
                           ▼
                 conservative status update

Safe asymmetries:

- a verified proof can establish P under its exact assumptions and scope;
- a verified counterexample can refute its exact target;
- no counterexample found does not prove P;
- prover timeout does not make P false;
- model-builder timeout does not make P true;
- incompatible results signal a semantic, implementation, or context defect requiring
  adjudication.

## 10. Knowledge and provenance classes

> **SOURCE-DERIVED — Blackburn & Bos / INFERENCE.** Background knowledge needs
provenance classes. A mathematical analogue is:

| Knowledge class | Examples |
|---|---|
| LOGIC / CORE KERNEL | Equality preservation, modus ponens, binder-safe substitution. |
| DEFINITIONS | Function, object, relation, and concept definitions. |
| THEOREM_LIBRARY | Named reusable theorem with explicit hypotheses and evidence. |
| DOMAIN_LIBRARY | Probability, trigonometry, geometry, calculus, sequences, number theory. |
| PROBLEM_GIVENS | Data and assumptions supplied by the current task. |
| DERIVED_FACTS | Claims established in the current dependency graph. |
| SYMBOLIC_BACKEND | Equivalence, normalization, factoring, solving certificates. |
| NUMERIC_BACKEND | Exact/controlled evaluation, interval or finite checks. |
| SEARCH_META / HEURISTICS | Representation and subgoal proposals; never proof by themselves. |

A conclusion should identify which classes were used. “The model said so” is not a
warrant.

## 11. FormalMATH alignment lesson

> **SOURCE-DERIVED — FormalMATH.** Compiler validity and semantic alignment to the
original mathematics are separate gates. The supplied research packet reports a
benchmark-construction funnel of approximately 92.4% compiler-valid, 31.7% surviving
semantic verification, 30.1% surviving negation filtering, and a final manually
validated subset around 21.7% of the starting pool.

These are properties of that pipeline, not universal mathematical rates. Their value
for HML is methodological:

    PARSES
      ≠ PRESERVES SOURCE MEANING
      ≠ PROVES THE CLAIM
      ≠ ANSWERS THE ORIGINAL TASK

FormalMATH also motivates:

- multiple candidate formalizations rather than one forced parse;
- semantic back-translation or explanation as an alignment filter;
- negation/counterexample-based rejection;
- domain-specific evaluation and explicit domain-bias measurement;
- human adjudication for benchmark-quality semantic migrations;
- tracking broad automation/tactic dependence because it can hide reasoning structure;
- testing machine-oriented representations independently from pedagogical prose.

The supplied source summary also reports a strongest evaluated prover result of
16.46% on the full FormalMATH benchmark. That figure is benchmark- and setup-specific;
it is evidence that formal proof remains difficult, not an HML performance baseline.

The supplied source summary reports that natural-language solution guidance reduced
formal proof success in one tested setup. This does not imply “English is bad.” It
supports only the hypothesis that human pedagogical prose may differ from an optimal
machine proof/search representation.

## 12. Conservative epistemic statuses

The following conceptual statuses separate generation from belief:

| Status | Meaning |
|---|---|
| PROPOSED | Well-formed candidate meaning, action, claim, or witness; no proof claim. |
| DERIVED | Produced by a named transition, possibly with open obligations; not necessarily fully verified. |
| VERIFIED | Checked by trusted kernel/certificate and all mandatory debt discharged in the recorded context. |
| REFUTED | Exact target contradicted by checked proof, model, or counterexample. |
| UNDERDETERMINED | Checked evidence establishes both admissible support directions/models required by the protocol; not mere ignorance. |
| UNRESOLVED | Available evidence cannot decide, is unsupported, ambiguous, or outside the trusted fragment. |
| UNSUPPORTED | A proposed claim lacks an applicable trusted warrant/evidence path. |
| TIMEOUT | A bounded search/check did not finish; no truth conclusion follows. |

> **CURRENT HML.** The pinned implementation already distinguishes proposed,
checked/verified/rejected claim states and goal outcomes including proved, refuted,
unsubstantiated, and certified underdetermination. Failed search remains UNKNOWN/OPEN,
never automatically UNDERDETERMINED.

> **DECISION.** VERIFIED is a verifier-owned outcome. An LLM, parser, renderer,
library caller, or untrusted backend must never assert VERIFIED merely because it
generated a plausible step or successful-looking answer.

## 13. Verification architecture

A transition-verification path should check, in order or as a dependency graph:

1. source/semantic alignment and selected reading identity;
2. parsing, binding, scope, and typing;
3. operation applicability and preconditions;
4. exact dependency and state-before availability;
5. warrant identity and knowledge-layer contract;
6. evidence/certificate validity and context hash;
7. state delta, branch locality, and candidate status;
8. obligation creation, inheritance, discharge, and failure;
9. goal and epistemic effects;
10. optional parallel proof and falsification checks;
11. task alignment: the verified result answers the original target.

Broad automation may be useful, but benchmark records should retain backend/tactic
dependence, assumptions, obligations, provenance, and structural error type.

## 14. Library/backend boundary

> **EMPIRICAL / DECISION.** Core supplies generic typed state/proof machinery.
Theorem and domain libraries supply reusable mathematical knowledge and hypotheses.
Symbolic and numeric backends supply checked computational certificates. Search/meta
proposes actions and warrants but cannot certify them.

Current HML's static trusted certificate registry and exact evaluator show that this
boundary is implementable in principle. Missing broad libraries are not evidence for
one new core keyword per theorem family.

## 15. Semantic-alignment requirements

High-confidence requirements are:

- interpretation status distinct from inference status;
- explicit binding, scope, domain, assumptions, and definitions;
- alternative or underspecified readings rather than forced certainty;
- operation, warrant, knowledge layer, and control effects stored separately;
- dependency/provenance classes for every believed claim;
- certificate context and assumption tracking;
- conservative, verifier-owned epistemic updates;
- explicit unsupported, timeout, ambiguous, and underdetermined outcomes;
- semantic equivalence only within a documented trusted fragment;
- human review for frozen-corpus semantic migrations.

## 16. Unresolved questions

- What minimal interpretation schema captures ambiguity without becoming a general
  natural-language formalizer?
- How should candidate readings be promoted, merged, or rejected?
- Which equivalence backends are trustworthy for which domains and assumptions?
- How are consistency, novelty, and goal relevance measured without confusing them
  with validity?
- What proof objects should theorem/domain libraries expose?
- How should proof and counterexample search share resource limits and context?
- Which verifier disagreements indicate source ambiguity versus implementation bugs?
- What human-adjudication protocol is sufficient to freeze ontology migrations?
