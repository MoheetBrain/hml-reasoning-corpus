# HML state after Gold-125 and ontology-v1

## Status

This is a research handoff, not an HML change proposal. The HML submodule remains
read-only and pinned at
5688aba18632b65a8709aa1d85577d31a67dba6a. No HML syntax, keyword, semantic rule,
test, or implementation file was modified.

The ontology quality gate is **UNSTABLE_REVIEW_REQUIRED**. Gold-125 has 769
transitions, 136 UNRESOLVED transitions (17.69%), 125 frozen OTHER labels (16.25%),
and one annotation error requiring review. AMPS was audited and a prospective
100-topic candidate preview was prepared, but no AMPS trajectories were created.

## 1. Is a compressed mathematical reasoning instruction set still defensible?

Yes, as a provisional interpretation of the selected corpus. Ontology-v1 retains
17 adjudicated generic core operation values after factoring domain warrants,
libraries, backends, modes, and goal effects. Accepted-core saturation reaches 15
by 25 trajectories, 17 by 50, and remains flat through 125; top-5, top-10, and
top-15 coverage is 80.2%, 94.9%, and 99.5% of accepted-core transitions.

This is not a claim that mathematics has only 17 primitives. The result is curated,
source-grounded, unresolved in a material fraction, and not cross-source replicated.
Representability != reasoning superiority.

## 2. Best current estimate of genuine core primitives

The best current estimate is **17 adjudicated KEEP_AS_CORE operation values**, with
18 candidate values visible in the derived view. INDUCT is the one candidate merged
out of the accepted count because the present sample does not establish it as a
distinct primitive rather than a proof-schema specialization. That merge is
reversible and should be tested with a targeted induction sample.

The 17 are DECLARE, RECORD, MODEL, CONSTRUCT, TRANSFORM, SUBSTITUTE,
APPLY_DEFINITION, APPLY_THEOREM, CASE_SPLIT, ENUMERATE, COUNT, EVALUATE, BOUND,
SELECT, VERIFY, CONTRADICTION, and DISCHARGE.

## 3. Which apparent primitives disappeared after separating axes?

TRIG_IDENTITY became TRANSFORM with a trigonometry warrant and DOMAIN_LIBRARY
knowledge. MODULAR_REASONING became TRANSFORM with a modular-arithmetic warrant.
PROBABILITY and related labels became EVALUATE with a probability-law warrant.
SEQUENCE_RECURRENCE became TRANSFORM with a sequence-rule warrant. DIFFERENTIATE
and INTEGRATE became TRANSFORM with calculus-rule warrants; TAKE_LIMIT became
EVALUATE with a calculus-rule warrant. INCLUSION_EXCLUSION and PIGEONHOLE became
COUNT with counting/theorem warrants. OPTIMIZE became BOUND with a goal effect.
DISCHARGE became a goal effect when an underlying operation was visible. SEARCH_META
became a reasoning mode over an underlying construction or case selection.

INDUCT did not disappear from provenance, but was not accepted as a separate core
primitive. OTHER remains explicit and unresolved rather than being forced into a
convenient operation.

## 4. Did the 43 disagreements reveal annotation noise or a deeper ontology problem?

Both, but mostly an ontology-axis problem. Of the 43 disagreements, 42 are explained
by operation/warrant, operation/domain, operation/goal-effect, mode/operation,
granularity, or preserved ambiguity. One is a genuine annotation error: in
MATH-GOLD-043 s1, “make all the amounts of money into integers by considering them
all in cents” was labeled APPLY_THEOREM even though it is a representation/modeling
choice and does not invoke a theorem.

The decomposition is meaningful because the labels predict different facts: an
operation describes the state effect, a warrant describes why it is valid, a layer
describes where knowledge lives, and a goal effect describes proof control. Storing
both labels without this interpretation would not count as adjudication.

## 5. Does the core saturation curve survive adjudication?

Yes in shape, with a lower and more defensible count:

| Trajectories | Accepted core | Candidate core | New accepted core |
|---:|---:|---:|---|
| 25 | 15 | 15 | 15 |
| 50 | 17 | 17 | CONSTRUCT, CONTRADICTION |
| 75 | 17 | 18 | none |
| 100 | 17 | 18 | none |
| 125 | 17 | 18 | none |

The flat curve is exploratory evidence only. It does not survive as a scientific
stabilization result while unresolved and OTHER fractions remain material.

## 6. What should HML itself encode?

HML should encode typed mathematical state, claims and relations, generic local
state/proof/control operations, lexical and branch scope, dependencies, obligations,
provenance, and checker-computed epistemic status. It should preserve a distinction
between proposed, derived, verified, rejected, and underdetermined results. A
neutral trajectory should remain canonical, with HML as a checked rendering.

The next needed capability is not a domain keyword. It is a robust, typed interface
for evidence and state effects that can connect neutral transitions to existing
checkers without silently changing denotation.

## 7. What should live in libraries?

Theorem and domain libraries should provide hypotheses and replayable evidence for
trigonometry, probability, counting, modular arithmetic, sequences, geometry,
calculus, inequalities, and named theorems. Library entries should state their
preconditions and be referenced as warrants. They should not be promoted into core
operations merely because their names appear frequently.

## 8. What should live in symbolic/numeric backends?

Exact closed arithmetic, rational normalization, symbolic equivalence, factoring,
radical and denominator handling, bounded definition/function unfolding, and other
computational certificates belong in symbolic or numeric backends. Existing HML
evaluator and obligation facilities should be connected through evidence adapters
before considering core semantic changes.

## 9. What should remain in an open planner/LLM?

Representation selection, theorem or library search, candidate generation, case
selection, subgoal choice, symmetry recognition, and exploratory alternatives should
remain planner responsibilities. The planner may emit a proposal and its rationale;
it should not assert verification or invent missing preconditions. HML/state IR and
the verifier should make the proposal auditable.

## 10. Is the current best architecture the proposed hybrid?

Yes, provisionally:

    planner
      |
    HML/state IR
      |
    generic reasoning kernel
      |
    library/backend
      |
    verifier
      |
    updated state

This architecture matches the evidence better than treating HML as a complete
open-ended thinker. It remains a hypothesis because no learned model, matched
representation comparison, or cross-source annotated replication has been run.

## 11. What evidence could falsify this architecture?

The architecture would be weakened if a pre-registered cross-source sample produced
many recurring state/proof effects that cannot be represented without domain-specific
core keywords; if libraries/backends could not provide trustworthy evidence with
typed preconditions; if branch, candidate, obligation, or epistemic state could not
be preserved without ad hoc fields; or if independent annotators could not agree on
state deltas and warrants. It would also be weakened if HML added no verification
value beyond a generic AST or Structured English after matched adaptation.

## 12. Is AMPS cross-source replication now justified?

**Audit and preparation: yes. Annotation: no.** The AMPS-Khan parquet contains
103,059 rows, 721 topics, 5 empty/problem-null rows, 21,094 multiple-choice-marker
rows, 3,293 visual-dependent-marker rows, 47,530 planning-cue rows, and a median
solution length of 455 characters. The original SHA-256 is
b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41.

Because ontology-v1 is unstable, the current mission stops at provenance audit and a
100-topic prospective candidate preview. The future AMPS experiment must separately
count new core, meta, library, backend, warrant, and state-field demands. New
mathematics is not automatically a new reasoning primitive. It must not process all
100k rows or train anything.

## Decision and handoff

The strict recommendation is: **REVISE THE CORPUS ONTOLOGY/ANNOTATION PROTOCOL,
THEN RUN A BOUNDED CROSS-SOURCE REPLICATION**. Do not modify HML core now. First
resolve the 43-disagreement handoff, especially MATH-GOLD-043 s1 and the 136
UNRESOLVED transitions. Then annotate a small approved AMPS sample with the same
multi-axis protocol and compare demands across axes.

Supporting artifacts:

- reasoning_ontology_v1.yaml defines the axes and uncertainty contract.
- gold125_label_disagreement_matrix.md/.json preserves every broad disagreement.
- core_operation_adjudication_v1.md records candidate decisions.
- gold125_ontology_v1_saturation.md/.json and reports/figures/ contain the accepted
  core saturation and coverage evidence.
- amps_khan_dataset_audit.md records source provenance and distribution audit.
- amps_khan_candidate_selection_plan.md is prospective only; it is not Gold-100 and
  contains no annotations.
