# HML Integration and Implementation Context

## HOW TO USE THIS FILE

**Readers:** project head/integrator and implementation agent.

**Purpose:** this is the only canonical context file authorized to recommend what
eventually gets implemented. It translates the evidence and requirements in files
00–03 into gated architecture decisions. It does **not** authorize an HML-core change
by itself.

Read [00_HML_MASTER.md](00_HML_MASTER.md) for the scientific map,
[01_STATE_AND_EXECUTION.md](01_STATE_AND_EXECUTION.md) for state invariants,
[02_SEARCH_AND_DISCOVERY.md](02_SEARCH_AND_DISCOVERY.md) for planner/discovery
requirements, and
[03_MEANING_EVIDENCE_AND_VERIFICATION.md](03_MEANING_EVIDENCE_AND_VERIFICATION.md)
for semantic and verifier contracts.

**Labels:** **EMPIRICAL**, **SOURCE-DERIVED**, **INFERENCE**, **DECISION**,
**HYPOTHESIS**, and **OPEN** preserve evidence strength.

## 1. Current best architecture

> **INFERENCE from Gold-125 plus the supplied Lakatos, Winskel, Blackburn/Bos, and
> FormalMATH synthesis:**

              NATURAL-LANGUAGE PROBLEM
                        │
                        ▼
              INTERPRETATION ENGINE
                 candidate meaning(s)
                        │
                        ▼
                OPEN / NEURAL PLANNER
                   proposed next move
                        │
                        ▼
              TYPED MATHEMATICAL STATE / HML IR
                        │
              generic operation + warrant
                        │
                preconditions + obligations
                        │
                        ▼
                 LIBRARY / BACKEND
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
          PROOF SEARCH       FALSIFICATION SEARCH
              │                   │
              └─────────┬─────────┘
                        ▼
                     VERIFIER
                        │
                        ▼
                EPISTEMIC UPDATE
                        │
                        ▼
                   UPDATED STATE
                        └────────────→ planner continues

Discovery mode additionally permits versioned conjectures, failed branches,
counterexamples, candidate lemmas, definition proposals, diagnoses, and proof repairs.
A verification/promotion boundary prevents those nodes from contaminating deductive
state.

> **DECISION.** HML surface syntax is replaceable. The durable architecture is the
semantic state/event/evidence contract and its conformance tests.

> **CORE PRINCIPLE.** Do not confuse the compact reasoning instruction set with the
> complete mathematical intelligence stack. A small execution kernel can coexist
> with an open, high-entropy search policy.

## 2. Five orthogonal questions for every event

1. **MODE:** why is this event being generated—search, execution, verification,
   modeling, or goal management?
2. **OPERATION:** what generic mathematical state/proof effect occurs?
3. **WARRANT:** why is the effect legitimate, and which knowledge layer supplies it?
4. **STATE/CONTROL EFFECT:** what happens to goals, branches, assumptions,
   obligations, candidates, dependencies, and facts?
5. **EPISTEMIC EFFECT:** what may now be proposed, derived, verified, rejected,
   refuted, underdetermined, or left unresolved?

> **EMPIRICAL.** This decomposition explains 42/43 Gold-125 broad-label
> disagreements. It is therefore more than stylistic normalization.

## 3. Interpretation layer above ontology-v1

> **INFERENCE.** Ontology-v1 begins mostly after a source span has been interpreted.
Add an architectural interpretation boundary with candidate fields such as:

| Field | Meaning |
|---|---|
| reading_id | Stable identity of one candidate/underspecified meaning. |
| semantic_status | Proposed, constrained, aligned, rejected, or unresolved. |
| scope_status / binding_status | Whether quantifier, variable, and attachment choices are resolved. |
| interpretation_constraints | Type, domain, scope, reference, and contextual restrictions. |
| alternative_readings | Competing typed candidates preserved without forced choice. |
| alignment_evidence | Source span, back-translation, judge outputs, and human decision provenance. |

> **MEDIUM CONFIDENCE.** Architecturally reserve this layer now; do not make HML a
general English parser or freeze concrete fields before a source-to-meaning study.

## 4. Multi-axis candidate event schema

The current event contract should distinguish at least:

| Axis/field | Role | Current confidence |
|---|---|---|
| event_id / trajectory_id / state IDs | Stable event and state identity. | High |
| source_span / provenance | Exact source and canonicalization ancestry. | High |
| reasoning_mode | SEARCH_META, EXECUTION, VERIFICATION, MODELING, GOAL_MANAGEMENT, OTHER. | High as an axis; labels remain revisable. |
| core_operation | Generic state/proof effect; 17 empirical candidates plus unresolved candidate INDUCT. | Medium as vocabulary, high as a separate axis. |
| warrant | Definition, theorem, identity, algebraic/domain rule, backend contract, or unknown. | High |
| knowledge_layer | CORE, THEOREM_LIBRARY, DOMAIN_LIBRARY, SYMBOLIC_BACKEND, NUMERIC_BACKEND, SEARCH_META, UNKNOWN. | High |
| inputs / dependencies | Premises, objects, definitions, candidates, and goals consumed. | High |
| preconditions | Conditions required before execution under the selected contract. | High |
| obligations_created / discharged | Persistent proof debt and named discharge evidence. | High |
| goal_effect | NONE, ADVANCE, CREATE_SUBGOAL, DISCHARGE. | High as an axis; vocabulary may evolve. |
| scope_effect | Branch/assumption open, close, join, introduce, discharge, none, or unknown. | High as an axis; protocol is medium confidence. |
| epistemic_effect | Propose, derive, verify, reject/refute, underdetermine, or remain unresolved. | High |
| state_delta | Exact fact, status, control, candidate, scope, and obligation changes. | High |
| atomicity | ATOMIC, COMPOUND_MACRO, or UNCERTAIN. | High for provenance; improved decomposition is open. |
| uncertainty | CERTAIN, SOURCE_AMBIGUOUS, ANNOTATION_REVIEW, UNRESOLVED, or future aligned equivalents. | High |
| evidence/certificates | Trusted kernel, theorem/library proof object, backend certificate, model/counterexample, human adjudication. | High |

> **DECISION.** Frozen source labels remain provenance. Derived ontology views may
reclassify them but must not rewrite the original trajectory silently.

## 5. State and discovery separation

Deductive state may contain assumed, derived, verified, refuted, underdetermined, and
unresolved nodes. Discovery state may contain conjectures, heuristics, failed branches,
counterexamples, candidate lemmas, representation/definition proposals, diagnoses,
and abandoned paths.

Conceptually:

    discovery graph
          │
    verify / assume / promote
          │
          ▼
    deductive dependency graph

> **DECISION.** Discovery nodes cannot serve as deductive premises until a licensed
status transition promotes them. Failed branches remain inspectable without becoming
facts.

## 6. HIGH CONFIDENCE — make architectural provisions

These requirements are supported by empirical evidence and/or multiple source-derived
semantic arguments. They justify interfaces, tests, and data-model provisions—not
necessarily new syntax.

1. **Canonical typed mathematical state.** Preserve objects, domains, constraints,
   definitions, goals, candidates, branches, obligations, and status.
2. **Explicit dependencies and provenance.** Support ancestry, assumption context,
   source alignment, warrant, and evidence identity.
3. **Scoped assumptions and binders.** Prevent fact leakage and capture; make
   discharge explicit.
4. **Explicit goals and subgoals.** Keep goal control separate from mathematical
   operation labels.
5. **First-class preconditions.** UNKNOWN conditions block or create explicit debt
   according to the operation contract.
6. **Persistent obligations.** Track creation, inheritance, scope, lifetime,
   discharge, and failure.
7. **Candidates distinct from facts.** Preserve proposed/unverified/verified/rejected
   lifecycle and original-constraint checking.
8. **Branch-local state.** No global promotion without coverage/join evidence.
9. **Operation separated from warrant/domain knowledge.** Retain generic effects and
   large libraries/backends.
10. **Verifier-computed epistemic status.** Generation cannot self-certify.
11. **Parsing separated from semantic alignment.** Preserve candidate readings and
   interpretation uncertainty upstream.
12. **Unknown/unsupported states.** Fail closed rather than force certainty.
13. **Planner separated from verifier.** Creative proposal and conservative belief
   update use different contracts.
14. **Neutral trajectories before renderings.** Derive HML, AST, and Structured
   English views from one canonical source.
15. **Semantic conformance tests.** Plan for type, scope, obligation,
   operational–denotational, and proof-rule soundness checks.

## 7. MEDIUM CONFIDENCE — prototype and test

These candidates are architecturally plausible but should not be frozen without
targeted experiments:

1. semantic reading sets and constraint-based resolution;
2. generic exhaustive/disjoint branch and join certificates;
3. candidate generation/verification protocol;
4. parallel proof and counterexample/model checking;
5. assumption-aware semantic equivalence classes;
6. discovery-state DAG linked to deductive state;
7. induction as a reusable proof schema;
8. proof-failure diagnosis and repair protocol;
9. versioned concepts/definitions in discovery mode;
10. separate validity, consistency, novelty, and goal-relevance evaluation;
11. semantic back-translation/multi-judge quarantine for corpus promotion;
12. library/backend evidence adapters over the existing HML certificate boundary.

Each prototype must define its trusted boundary, failure states, provenance, and
whether it changes denotation, operational behavior, proof licensing, or only
rendering/metadata.

## 8. TEST BEFORE IMPLEMENTATION — no keywords yet

Do not add syntax merely named:

    REFRAME
    WORK_BACKWARDS
    PRUNE / PRUNE_IRRELEVANT_STATE
    RELAX_CONSTRAINT
    STRENGTHEN_HYPOTHESIS
    REPAIR_LEMMA
    REVISE_CONJECTURE
    CHOOSE_REPRESENTATION
    CONCEPT_PROPOSAL
    INDUCT

Also test GENERALIZE, SPECIALIZE, SEEK_COUNTEREXAMPLE,
LOCATE_FAILED_DEPENDENCY, RECOGNIZE_STRUCTURE, and USE_SYMMETRY before treating them
as primitives.

For each candidate determine whether it is:

- a semantic primitive;
- a composition of state effects;
- a planner policy;
- a goal or scope effect;
- a representation proposal;
- warrant/library search;
- metadata useful for training but unnecessary in HML syntax.

## 9. Tiny core, rich libraries, compositional effects

> **DECISION.** Keep large mathematical taxonomies outside the trusted kernel.

Libraries/backends should contain trigonometric identities, probability laws,
combinatorial theorems, number theory, calculus rules, geometry facts, sequence rules,
symbolic algebra, exact arithmetic, and other domain knowledge.

Prefer:

    TRANSFORM + warrant=TRIGONOMETRY_IDENTITY

over:

    TRIG_TRANSFORM, LOG_TRANSFORM, MODULAR_TRANSFORM, ...

unless distinct state semantics are demonstrated empirically. Composition is the
default hypothesis; vocabulary proliferation carries the burden of proof.

## 10. Current ontology gate

> **EMPIRICAL — UNSTABLE_REVIEW_REQUIRED.** Current facts:

- 769 derived Gold-125 transitions;
- 17 adjudicated KEEP_AS_CORE effects and 18 candidate values including INDUCT;
- 136/769 UNRESOLVED = 17.69%;
- 125/769 frozen OTHER = 16.25%;
- 43 independent broad-label disagreements;
- 42 explained by axes/granularity/uncertainty;
- one genuine annotation error/review at MATH-GOLD-043 s1;
- no AMPS trajectories annotated;
- no matched HML/AST/Structured-English experiment.

> **DECISION.** Do not freeze or implement the semantic kernel while this gate
remains open. A flat saturation curve with a material unresolved tail is not success.

## 11. Explicit prohibitions

- Do not add 17 HML keywords merely because there are 17 current candidates.
- Do not implement every Lakatos heuristic as syntax.
- Do not treat theorem or domain names as core operations because they recur.
- Do not silently promote planner proposals, tool outputs, or candidates to proofs.
- Do not let an LLM set VERIFIED.
- Do not treat compiler-valid or parse-valid output as semantically aligned.
- Do not treat failed counterexample search as proof.
- Do not silently resolve ambiguous readings or UNKNOWN preconditions.
- Do not modify frozen Gold trajectories to fit a theoretical architecture.
- Do not claim HML beats generic AST or Structured English.
- Do not process the full AMPS dataset or train from the prospective candidate list.
- Do not modify HML core from this context-building mission.

## 12. Next empirical sequence

> **DECISION — required order.**

1. **Resolve or bound UNRESOLVED and OTHER.** Human-adjudicate the genuine error,
   sample the unresolved tail, separate ambiguity from missing schema/evidence, and
   define an acceptable residual threshold.
2. **Run bounded cross-source AMPS replication.** Use the approved sample only;
   track new core, meta, library, backend, warrant, interpretation, and state-field
   demands separately.
3. **Run targeted proof-state/induction study.** Include base/step goals, weak and
   strengthened hypotheses, assumption discharge, failed steps, and alternative proof
   schemas.
4. **Compare against formal proof states.** Measure source alignment, scope,
   obligations, candidate verification, proof/counterexample results, and tactic
   dependence.
5. **Freeze the semantic kernel only after adjudication.** Publish the evidence,
   residual uncertainties, conformance properties, and migration rules.
6. **Implement approved additions.** Prefer interfaces/protocols and libraries before
   syntax; require soundness and regression tests for trusted-core changes.
7. **Run the matched representation experiment.** Same mathematics, trajectories,
   model, training budget, context/token budget, and inference/search budget across
   HML, generic typed AST/S-expression, Structured English, and a hybrid
   planner→state/verifier system.

## 13. Decisive experiment and measurements

The scientific endgame is not “build a language.” It is a controlled comparison over
the same neutral trajectories.

Measure at least:

- source-to-state semantic alignment;
- next-action accuracy and verified-transition rate;
- complete verified solution rate;
- sample efficiency;
- out-of-distribution compositional generalization;
- deeper dependency-chain and larger-state robustness;
- scope/binding, precondition, obligation, and candidate errors;
- proof versus counterexample success and calibration;
- backend/tactic dependence;
- search, token, and wall-clock cost.

> **KILL / PIVOT RULE.** The HML-specific learning claim is weakened or killed if
matched exposure repeatedly yields generic AST ≥ HML on the tasks HML is intended to
improve. The broader typed semantic-machine/state/verifier architecture can survive
that result, potentially with a different surface representation.

## 14. Implementation acceptance checklist

Before any proposed addition is approved, answer:

1. Which empirical/source-derived requirement motivates it?
2. Is it core, library, backend, planner, interpretation, or rendering?
3. What exact state, denotational, operational, proof, scope, and epistemic effects
   does it have?
4. What preconditions and obligations are generated?
5. What evidence/certificate can a verifier check?
6. What are the unsupported, timeout, ambiguous, and failure outcomes?
7. Can the behavior be composed from existing semantics?
8. Does it preserve neutral-trajectory provenance and alternate renderings?
9. What cross-source recurrence and independent adjudication support it?
10. What regression, conformance, and adversarial tests prevent unsound promotion?

If these questions cannot be answered, record a research gap; do not invent syntax.

## Latest empirical builder handoff — Semantic Firewall

### A. What the experiment established

**EMPIRICAL.** A frozen corpus-side reference checker accepted 80/80 valid FINAL
transitions and detected 80/80 minimally corrupted invalid transitions across
dependency, scope, precondition, obligation, candidate, branch/join, warrant,
epistemic, goal-discharge, and type/domain invariants. FINAL uses 80 unique MATH
Level 4/5 source rows with zero Gold-125 overlap. Against a source-presence control,
relative error reduction was 100%; this is controlled protocol sensitivity, not open
mathematical reasoning accuracy.

### B. What it did not establish

No arbitrary theorem replay, external-model comparison, training result, or pure
HML-vs-generic-AST-vs-Structured-English advantage was established. Current HML needs
a transparent adapter envelope to preserve every neutral candidate and branch field,
so the three prepared representations remain unscored.

### C. Exact high-confidence HML requirements

1. Preserve existing dependency graph, lexical scope, checker-owned status, and exact
   goal adjudication semantics.
2. Add a versioned neutral-transition importer and narrow trusted evidence adapter.
3. Add one generic first-class candidate lifecycle plus original-constraint checking.
4. Add one generic exhaustive/disjoint branch and safe-join proof protocol reusing
   lexical frames and certificate envelopes.
5. Extend fail-closed precondition and type/domain contracts; keep theorem/domain
   knowledge in libraries.
6. Round-trip obligations and all approved semantic fields losslessly before claiming
   pure-HML representation parity.

### D. Requirement-to-build map

| Requirement | Current support | Gap class | Minimal builder change | Acceptance fixtures |
|---|---|---|---|---|
| Dependencies | supported | `NO_CHANGE_ALREADY_SUPPORTED` | retain graph and premise checks | `FX-DEP-*` |
| Lexical scope | supported | `NO_CHANGE_ALREADY_SUPPORTED` | retain scoped Γ | `FX-SCP-LEGAL`, `FX-SCP-ILLEGAL` |
| Neutral import | partial | `CORPUS_ADAPTER` | versioned lossless importer | `FX-DEP-*`, `FX-OBL-*` |
| Preconditions | partial | `VERIFIER_CHANGE` | extend term/domain contracts fail-closed | `FX-PRE-*` |
| Obligation round-trip | core supported, adapter partial | `CORPUS_ADAPTER` | expose existing lifecycle | `FX-OBL-*` |
| Candidate state | absent | `CORE_STATE_CHANGE` | generic candidate object/lifecycle | `FX-CAN-*` |
| Candidate promotion | absent | `VERIFIER_CHANGE` | check every original constraint | `FX-CAN-*` |
| Branch/join | absent beyond lexical scope | `CORE_PROOF_CHANGE` | certified partition/branch/join protocol | `FX-BRN-*` |
| Evidence envelope adapter | static core boundary exists | `EVIDENCE_ADAPTER` | narrow trusted adapter API | `FX-WAR-*` |
| Theorem/domain evidence | broad libraries absent | `LIBRARY_CHANGE` | minimal replayable entries | `FX-WAR-*`, `FX-TYP-*` |
| Epistemic status | supported for derivations/evidence | `NO_CHANGE_ALREADY_SUPPORTED` | extend ownership rule to new objects | `FX-EPI-*` |
| Goal discharge | supported | `NO_CHANGE_ALREADY_SUPPORTED` | retain exact-target adjudication | `FX-GOL-*` |
| Type/domain propagation | partial | `VERIFIER_CHANGE` | propagate declared types into adapters/checkers | `FX-TYP-*` |
| Lossless HML view | partial | `RENDERER_CHANGE` | render only after semantic objects stabilize | `FX-CAN-*`, `FX-BRN-*` |

Every fixture is tested now against the reference checker by
`tests/test_semantic_firewall.py`. A future HML implementation claiming Semantic
Firewall support must run the same fixtures without rewriting them.

### E. What Claude must not implement yet

Do not implement open proof search or add `REFRAME`, `WORK_BACKWARDS`,
`STRENGTHEN_HYPOTHESIS`, `PRUNE`, `REPAIR_LEMMA`, `REVISE_CONJECTURE`, `INDUCT`, or
domain-specific core keywords. Do not add a user-registerable trusted checker, let
source set `VERIFIED`, ingest broad theorem libraries merely to satisfy this benchmark,
or claim representation superiority.

### F. Immutable handoff

- Experiment commit:
  `80b1640495d6c4ad9acc32da0353ad0c9bf91201`.
- Full report: `reports/semantic_firewall_experiment.md`.
- Machine requirements: `experiments/semantic_firewall/requirements_handoff.json`.
- Fixtures: `experiments/semantic_firewall/acceptance/fixtures.json`.
- Frozen protocol: `experiments/semantic_firewall/freeze_manifest.json`.
- Raw metrics: `experiments/semantic_firewall/results/metrics.json`.
- Pinned HML: `5688aba18632b65a8709aa1d85577d31a67dba6a`.
