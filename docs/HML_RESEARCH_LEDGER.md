# HML Research Ledger

## READ THIS FIRST

This repository is a small, source-grounded mathematical reasoning study. Its
canonical object is a neutral state trajectory, not HML text. HML is evaluated as
a rendering, checked-state representation, and verifier-facing intermediate form.

The strongest current result is architectural and provisional: worked solutions
can be decomposed into recurring state/proof/control effects, while named
mathematical knowledge is more naturally represented as warrants, libraries, or
backends. Gold-125 supplies exploratory evidence for 17 adjudicated reusable core
operation values, but 136 of 769 transitions remain unresolved in ontology-v1 and
one annotation review remains open. Ontology stabilization is therefore not
complete, and AMPS has only been audited and prepared for a future bounded study.

Representability != reasoning superiority.

Gold-125 does NOT test whether HML beats generic AST or Structured English after
matched adaptation. No such matched AST/HML/SE benchmark is present in this
repository.

## 1. Central research thesis

Mathematical solutions may use many domain concepts while reusing a comparatively
small set of state/proof/control effects. A typed, provenance-preserving state IR
could make those effects explicit, with theorem and domain knowledge supplied by
libraries and symbolic or numeric backends. The claim under study is not that HML
replaces mathematical thought, nor that a small vocabulary proves mathematical
superiority. It is that a checked intermediate representation may be useful for
faithfully recording and verifying selected reasoning trajectories.

## 2. Current architecture

The working architecture is:

    proposer / planner
          |
    neutral typed mathematical state
          |
    generic reasoning operation
          |
    warrant + preconditions
          |
    obligations and dependencies
          |
    verifier / library / backend
          |
    updated state

The neutral trajectory is the source of truth:

    S0 -> a0 -> S1 -> a1 -> ... -> Sn

HML is a rendering of this trajectory, not the canonical source. An open planner
may select a representation or subgoal; a generic kernel can check a local state
effect; libraries and backends can provide domain-specific or computational
evidence; a verifier can reject unsupported or ill-typed claims.

## 3. Hypotheses

### H1 — state-transition thesis

Mathematical reasoning can be represented usefully as typed state transitions with
explicit preconditions, obligations, dependencies, provenance, and epistemic
status. Gold-25 and Gold-125 support this as a representation hypothesis: all
selected trajectories have neutral state/action records and structural audits pass.
They do not establish completeness for mathematics generally.

### H2 — small-core thesis

After domain names and warrants are factored out, a small reusable set of generic
operations will account for most observed transitions. Gold-125 supports this as
exploratory evidence: 17 operations are retained as adjudicated core candidates,
and the accepted-core saturation curve reaches 15 at 25 trajectories, 17 at 50,
and remains flat through 125. The result is vulnerable to source selection,
annotation conventions, unresolved OTHER labels, and the decision to merge INDUCT.

### H3 — HML semantic representation thesis

Current HML is useful for typed expressions, claims, local proof rules, obligations,
scope, provenance, and fail-closed verification. Gold-10 and Gold-125 support a
hybrid interpretation of HML as a checked reasoning/state IR. They do not show that
HML can faithfully execute every operation observed in worked mathematics.

### H4 — thinking-language thesis

Successful worked solutions contain source-visible planning and representation
choices, but HML is better positioned to record the selected checked trajectory than
to generate open-ended search. Gold-125 found 87 explicit meta records among 769
transitions; the source-only corpus cannot measure failed alternatives. This is
hybrid/inconclusive evidence, not a result that HML cannot express thought.

### H5 — learned-representation thesis

A learned model trained or adapted around this representation will improve reasoning
or verification. Not tested. No training was performed and no model comparison is
present.

## 4. Established positive results

- Gold-10: 10 hand-authored trajectories and 23 transitions were structurally and
  deterministically checked. All ten HML renderings parsed and type-checked at the
  then-pinned HML revision.
- Gold-25: 25 curated trajectories, adversarially audited state/action records,
  explicit dependencies and obligations, and a Gold-25 state profile were built.
- Gold-125: 125 trajectories and 769 source-granularity transitions were audited;
  exact source-span and structural checks passed for the new trajectories.
- The HML implementation already provides typed AST forms, claims, quantifiers,
  lexical scope, obligations, provenance, a closed reasoning kernel, exact closed
  evaluation, definition/function unfolding, and fail-closed unsupported results.
- Separating operation, warrant, knowledge layer, goal effect, scope effect, and
  epistemic effect explains 42 of the 43 broad-label disagreements without changing
  HML or the frozen corpus.
- The HML submodule has remained unchanged and pinned at
  5688aba18632b65a8709aa1d85577d31a67dba6a throughout this study.

## 5. Negative and null results

- The original Gold-10 CoreGapRate of 3/23 = 13.04% does not survive forensic
  reclassification. The corresponding primary transition split was 11 current-HML,
  2 core-semantic missing, 3 library missing, and 7 translation/canonicalization
  problems. Rates overlap at the report/gap-ID level and are diagnostic only.
- Gold-10 did not establish that arithmetic normalization, definition evaluation, or
  calculus claims require new HML denotation. Existing evaluator/certificate paths
  exist, but the tested trajectory rendering did not connect them to the checked
  derivation path.
- Gold-125 does not establish ontology stabilization: 136/769 = 17.69% remain
  UNRESOLVED, 125 transitions retain the frozen OTHER source label, and one genuine
  annotation error remains for human review.
- Gold-125 does not establish HML superiority over AST, Structured English, or any
  other representation. There is no matched adaptation, task metric, or comparison
  artifact in the repository.
- No Endpoint-A replication artifact or result is present in this repository. Any
  prior Endpoint-A replication failure must be treated as an external or missing
  record, not silently reconstructed here.
- No standalone implication-direction benchmark is present **in this repository** (one exists in the HML repository, and it is negative for HML — see the scope correction at the end of this section). Gold-10 does show that
  modus ponens and modus tollens can be checked, while non-entailment/underdetermination
  required an explicit status/certificate path. This is a local logic result, not a
  broad implication-direction claim.
- No AST/HML/SE scope experiment is present **in this repository** (B2 exists in the HML repository; a generic S-expression scored highest). The repository therefore cannot support
  a comparative scope conclusion beyond the representability audits described here.

> **SCOPE CORRECTION (2026-08-10).** Statements of the form "X is not present" in
> this document mean *not present in this corpus repository*. Several such
> experiments **do exist**, measured, in the production HML repository, and the
> unscoped phrasing was being read programme-wide as though the evidence were
> absent. It is not absent — it is **negative or null for HML**. Recovered from raw
> artifacts, all at small N and none licensing a conclusion either way:
> implication direction, Structured English 5/12 vs HML 1/12 vs generic AST 0/12
> (HML repo `c0e7520`); next-action, an apparent HML advantage that did **not**
> survive independent replication, Δ 0.000 (`b87736a`); quantifier scope, won by a
> generic S-expression with HML between it and Structured English (`22b4bb7`); and
> the saturated HML-EVAL-001 benchmark, paired difference 0.000, CI [0, 0]
> (`82d13ca`). Cross-reference `experiments/project_cognition/project_memory.yaml`.
- The source-only method cannot observe failed search, rejected proof attempts, or
  the distribution of alternative representations.

## 6. Current Gold-125 numbers

| Quantity | Result |
|---|---:|
| Trajectories | 125 |
| Source-granularity transitions | 769 |
| Atomic / compound macro / uncertain atomicity | 556 / 89 / 124 |
| Observed operation labels | 66 |
| Candidate core values before adjudication | 18 |
| Adjudicated KEEP_AS_CORE values | 17 |
| Merged candidate | INDUCT |
| Accepted-core transitions used for top-k | 626 |
| Accepted-core top-5 / top-10 / top-15 coverage | 80.2% / 94.9% / 99.5% |
| Broad disagreements before ontology-v1 | 43 |
| Explained by axes or uncertainty | 42 |
| Genuine semantic disagreement | 1 |
| Annotation errors | 1 |
| UNRESOLVED transitions | 136 / 769 = 17.69% |
| Frozen OTHER source labels | 125 / 769 = 16.25% |
| HML FULL / PARTIAL / REPRESENTABLE_ONLY / ABSENT *(historical, HML `5688aba`)* | 11 / 455 / 303 / 0 |
| HML step-weighted fractions *(historical, HML `5688aba`)* | 1.4% / 59.2% / 39.4% / 0.0% |
| Execution / search-meta / verification / goal-management | 580 / 48 / 28 / 113 |

The HML coverage classification is support evidence, not a benchmark score. FULL,
PARTIAL, and REPRESENTABLE_ONLY are not interchangeable, and REPRESENTABLE_ONLY does
not mean executable or theorem-verified.

## 7. Current reasoning state model

Each transition should carry, where known:

- state_before and state_after, with facts, constraints, goals, assumptions, and
  branch-local scope;
- a neutral action and source provenance;
- reasoning mode and core operation;
- warrant and knowledge layer;
- preconditions and obligations created or discharged;
- dependencies and source evidence;
- goal, scope, and epistemic effects;
- atomicity and uncertainty.

The existing state profile found 28/118 Gold-25 transitions with explicit
precondition records and three branch-bearing Gold-25 trajectories. Branch joins,
candidate sets, exhaustive/disjoint coverage, and persistent sequence/exclusion
state remain weakly represented or non-executable. Gold-125 preserves these
limitations rather than treating source text as a theorem replay.

## 8. Current operation ontology

Ontology-v1 is a derived view defined in
schemas/reasoning_ontology_v1.yaml. It separates:

- reasoning_mode: EXECUTION, SEARCH_META, VERIFICATION, MODELING,
  GOAL_MANAGEMENT, or OTHER;
- core_operation: generic state/proof/control effect;
- warrant: definition, theorem, identity, algebraic preservation, domain law,
  exact evaluation, symbolic normalization, or source-grounded evidence;
- knowledge_layer: CORE, THEOREM_LIBRARY, DOMAIN_LIBRARY, SYMBOLIC_BACKEND,
  NUMERIC_BACKEND, SEARCH_META, or UNKNOWN;
- goal_effect, scope_effect, and epistemic_effect;
- preconditions, obligations, dependencies, state delta, provenance, and uncertainty.

The derived view does not overwrite frozen labels. It retains all 769 records and
preserves original labels, modes, warrants, layers, disagreement details, and
uncertainty. INDUCT remains visible as a candidate value but is excluded from the
accepted-core count pending evidence that it is a distinct primitive rather than a
proof-schema specialization of other operations.

## 9. Current semantic gaps

The Gold-125 gap registry identifies recurring classes rather than instructions to
change HML now:

- applicability preconditions and persistent proof obligations recur across domains;
- generic case coverage, branch joins, candidate sets, finite search, and sequence
  or exclusion state are not yet fully executable;
- theorem, domain, probability, calculus, number-theory, and symbolic-algebra
  evidence is library/backend work in most cases;
- some Gold-10 failures were adapter/canonicalization failures because existing HML
  evaluator and certificate facilities were not connected to the trajectory path;
- induction is observed but its primitive status is unresolved in ontology-v1.

The current evidence does not justify adding a bespoke HML keyword for any one MATH
domain. Future gaps must distinguish denotation, operational semantics, epistemic
status, proof state, typing, rendering, and corpus translation.

## 10. Core, library, and backend boundary

HML/core should encode typed state, claims and relations, local generic state/proof
effects, scope, dependencies, obligations, provenance, and checker-computed status.
Candidate generic effects include DECLARE, RECORD, MODEL, CONSTRUCT, TRANSFORM,
SUBSTITUTE, APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, COUNT,
EVALUATE, BOUND, SELECT, VERIFY, CONTRADICTION, and DISCHARGE.

Theorem and domain libraries should provide hypotheses, theorem identities, counting,
probability, modular arithmetic, sequence rules, trigonometric identities, geometry,
and calculus rules. Symbolic and numeric backends should provide exact arithmetic,
normalization, factoring, closed evaluation, algebraic equivalence, and bounded
definition/function unfolding. A library/backend result must remain typed,
provenance-bearing evidence rather than an unchecked trusted assertion.

An open planner or LLM should choose representations, propose cases, select
subgoals, find candidate constructions, and search for applicable warrants. It
should not be confused with the verifier or silently promote a proposal to a proof.

## 11. Thinking/search versus execution

Gold-125 contains 580 EXECUTION, 48 SEARCH_META, 28 VERIFICATION, and 113
GOAL_MANAGEMENT records under the frozen mode annotations. Explicit source-supported
meta operations number 87: recognizing structure, choosing a representation,
considering cases, creating subgoals, using symmetry, and reframing. These counts
describe successful source text, not failed search.

The present architecture should therefore keep planning and checking distinct. A
planner may emit a proposed transition with uncertainty; the state IR records what
was proposed and why; a kernel/library/backend verifies the state effect; the
updated state records obligations and evidence.

## 12. Known annotation and methodology limitations

- Gold-25 and Gold-125 are curated for coverage, not random samples.
- A source sentence can contain multiple mathematical operations; source-span
  granularity is not atomicity.
- Labels are source-grounded annotations, not independent formal proof replay.
- The independent audit compares broad operation families, not full denotational
  theorem proofs.
- There are 43 broad-label disagreements, 42 explained by axes/granularity/etc.,
  and one annotation error requiring review.
- 124 transitions are uncertain in atomicity; 89 are compound macros.
- OTHER and UNRESOLVED preserve missing evidence but materially affect saturation.
- Exact source spans do not prove that every semantic state delta is mathematically
  valid.
- No failed attempts, search alternatives, model calibration, or human inter-rater
  study is included.
- build_gold25.py and the Gold-125 builder are curated artifact generators for the
  named examples, not scalable automatic extraction engines.

## 13. HML coverage limitations

Current HML is strong at typed structural representation, local transformations,
logical rules, scope, obligations, provenance, and selected exact checkers. It is
partial at generic domain conditions, branch completeness and joins, candidate
verification, theorem/library replay, symbolic normalization, and domain-specific
calculus/probability/number-theory execution. It is representationally broad but
not a general mathematical solver.

The pinned HML source was inspected read-only. No syntax, keyword, semantic rule,
test, or implementation file was changed by this mission.

## 14. Strongest evidence for HML

The strongest evidence is not the flat operation count. It is the repeated usefulness
of typed state, explicit assumptions, claim dependencies, obligations, lexical scope,
checked local rules, fail-closed status, and provenance across the Gold-10, Gold-25,
and Gold-125 artifacts. The ontology disagreement analysis also shows that named
domain rules can often be factored without changing the generic state effect.

## 15. Strongest threats to HML

The major threats are unresolved transitions, source annotation bias, hidden compound
operations, incomplete branch/candidate semantics, theorem-library dependence, and
the possibility that the apparent small core is an artifact of the chosen labels and
problems. The 17-operation result is exploratory until a second source and a
pre-registered annotation protocol test it. A planner may also carry much of the
actual mathematical difficulty, leaving HML as a useful record but not the source of
reasoning competence.

## 16. Open questions

- Can unresolved Gold-125 transitions be adjudicated without inventing semantics?
- Should induction be a generic proof schema, a library protocol, or a composition
  of existing operations?
- What is the smallest typed protocol for branch coverage, joins, candidate sets,
  finite search, and persistent obligations?
- Can existing HML evaluator/certificate facilities be connected through a neutral
  evidence adapter without core-language changes?
- Does ontology-v1 transfer to AMPS without adding genuinely new core operations?
- How much state metadata is required for faithful rendering and replay?
- What matched evaluation would compare HML, generic AST, and Structured English?

## 17. Kill and pivot criteria

Kill or substantially revise the small-core interpretation if a pre-registered,
cross-source sample produces many high-frequency, domain-independent operations that
cannot be factored into the ontology axes, or if independent adjudicators cannot
agree on state effects and warrants. Pivot toward a library/evidence IR if generic
core operations remain small but most useful verification lives in domain libraries
and backends. Pivot away from HML as the primary reasoning representation if it
cannot preserve state, obligations, dependencies, scope, and epistemic outcomes
without repeated example-specific extensions.

Do not use saturation alone as a success criterion. A flat curve with high
UNRESOLVED, OTHER, or annotation disagreement is not stabilization.

## 18. Dataset and commit provenance

- Corpus repository: local HML reasoning corpus on branch main.
- Gold-125 baseline commit: 3bd3ace09bff3deb20e6f0a0650875a120cc3fd4.
- Pinned HML repository: https://github.com/MoheetBrain/hamiltonian-lang.git.
- Pinned HML commit: 5688aba18632b65a8709aa1d85577d31a67dba6a.
- Gold-10/Gold-25 provenance and frozen hashes are recorded in the existing freeze
  manifest and prior reports.
- AMPS source of truth: /Users/moheet/Desktop/0000.parquet.
- AMPS SHA-256: b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41.
- AMPS copy is recorded under data/raw/amps_khan/ and the Desktop original was not
  modified. The companion CSV was not used as source of truth.

## 19. Completed experiment timeline

1. Repository setup with read-only HML submodule and neutral trajectory policy.
2. Gold-10 construction, HML rendering, verification, and six-gap triage.
3. Gold-25 curated trajectory/state-profile and adversarial semantic audit.
4. HML repin and adapted Gold-10 regression audit without modifying HML in this
   corpus; prior 13.04% headline was reclassified.
5. Gold-125 expansion, exact-source structural audit, independent hard audits,
   operation registry, gap analysis, state profile, and synthesis.
6. Ontology-v1 multi-axis derivation, 43-disagreement matrix, core adjudication,
   saturation plots, and quality gate.
7. AMPS-Khan provenance/distribution audit and 100-row prospective candidate preview;
   no AMPS annotation or trajectory creation because ontology-v1 remains unstable.

## 20. Next experiment

First resolve the one annotation review and reduce or explicitly bound the 136
UNRESOLVED transitions. Then test the same Gold-125 trajectories with an adjudicated
annotation protocol or a small independent sample. Only after that should a bounded
AMPS cross-source sample be annotated. The AMPS test must track new core, meta,
library, backend, warrant, and state-field demands separately, and must not treat new
mathematics as evidence of a new reasoning primitive by itself.

The immediate next decision is therefore not to modify HML. It is to close the
ontology quality gate with evidence, then run a small, auditable cross-source
replication.
