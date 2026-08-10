# HML Search and Discovery Context

## HOW TO USE THIS FILE

**Readers:** search/discovery specialist and project integrator.

**Question answered:** how does a mathematical system choose what to try next,
rather than merely execute a move already selected?

Execution state belongs in
[01_STATE_AND_EXECUTION.md](01_STATE_AND_EXECUTION.md); meaning and verification
in [03_MEANING_EVIDENCE_AND_VERIFICATION.md](03_MEANING_EVIDENCE_AND_VERIFICATION.md);
implementation gates in
[04_INTEGRATION_AND_IMPLEMENTATION.md](04_INTEGRATION_AND_IMPLEMENTATION.md).

**Labels:** **EMPIRICAL**, **SOURCE-DERIVED**, **INFERENCE**, **HYPOTHESIS**,
**DECISION**, and **OPEN** prevent finished-proof evidence from being confused with
discovery theory.

## 1. Search is not execution

Search/planning asks:

    What should I try next?
    Which representation exposes structure?
    Which subgoal would make progress?
    Which theorem, example, or counterexample should I inspect?

Execution/verification asks:

    Given the selected action and warrant, is the state change legal?
    What facts, obligations, candidates, and statuses change?

> **DECISION.** A search choice may propose a structured action, representation,
> conjecture, or subgoal. It does not become a verified mathematical fact merely
> because it was useful or plausible.

> **INFERENCE.** A compact execution kernel can coexist with a large, high-entropy
> search policy. Discovering a small operation set would not imply a small complete
> mathematical intelligence stack.

## 2. What Gold-125 actually observes

> **EMPIRICAL.** Gold-125's frozen reasoning modes contain 580 EXECUTION, 48
> SEARCH_META, 28 VERIFICATION, and 113 GOAL_MANAGEMENT transitions. A separate
> source-cue analysis records 87 explicit meta records across 769 transitions
> (11.3%); one source span can expose more than one meta function.

| Source-visible meta class | Records | Interpretation |
|---|---:|---|
| CONSIDER_CASES | 27 | Select a partition or case frame. |
| CHOOSE_REPRESENTATION | 27 | Introduce coordinates, variables, units, factorization, or another useful view. |
| CREATE_SUBGOAL | 13 | Replace the current target with a sufficient intermediate target. |
| RECOGNIZE_STRUCTURE | 10 | Notice a recurrence, symmetry, identity pattern, invariant, or known form. |
| USE_SYMMETRY | 7 | Reduce equivalent cases or normalize a configuration. |
| REFRAME | 3 | Replace the task with an equivalent or strategically easier formulation. |

These records show that successful source solutions contain planning. They do not
show the alternatives considered, effort spent, failed proof attempts, rejected
representations, or why a human found the successful move.

> **EMPIRICAL LIMITATION.** MATH solutions preserve polished successful paths.
> Gold-125 must not be described as a discovery-process corpus.

## 3. What AMPS adds—and does not yet add

> **EMPIRICAL.** The AMPS-Khan audit found 103,059 rows and 47,530 rows matching
> planning-language cues such as “first,” “notice,” “we need,” “let's,” “consider,”
> “instead,” “by symmetry,” and “we can rewrite.” A topic-diverse 100-row preview
> was prepared, but no AMPS transition has been annotated.

Pedagogical prose may expose strategy selection more explicitly than competition
solutions. Examples of testable patterns include:

    original problem
          ↓ REFRAME
    easier equivalent problem
          ↓ solve
    map result back

and:

    target structure not visible
          ↓ CHOOSE_REPRESENTATION
    factor / coordinate / normalize
          ↓
    structure becomes recognizable

> **OPEN.** Cue frequency is not semantic frequency. AMPS cannot yet support counts
> of new search operations, because the audit used lexical proxies and created no
> trajectories.

## 4. Finished proof versus discovery process

> **SOURCE-DERIVED — Lakatos.** Mathematical development is not only a static chain
> of deductions. Conjectures, proof attempts, counterexamples, hidden lemmas,
> definition changes, proof criticism, and repair can drive the mathematics.

The source-derived discovery loop is approximately:

    primitive conjecture C@v1
          ↓
    rough proof / thought experiment P1
          ↓ decomposes C into lemmas
    counterexample X
          ↓
    re-examine P1 and locate guilty/hidden lemma L
          ↓
    incorporate a principled condition or repair L
          ↓
    revised conjecture C@v2
          ↓
    new proof attempt

Further discovery can inspect other proofs for the same new lemma, re-check old
consequences, compare theorem refinements exposed by different proofs, and turn
counterexamples into new objects or problems.

> **INFERENCE.** This is better modeled as a versioned discovery-state protocol than
> as a pile of imperative keywords.

## 5. Local and global counterexamples

> **SOURCE-DERIVED — Lakatos.** Counterexamples can have different targets:

- **GLOBAL counterexample:** refutes the overall conjecture.
- **LOCAL counterexample:** attacks a lemma or subclaim used in one proof; the main
  conjecture may survive another proof or a repaired lemma.

A discovery counterexample should conceptually record:

| Field | Purpose |
|---|---|
| target / target version | Exact conjecture, lemma, definition, or dependency attacked. |
| target level | Global conjecture versus local proof component. |
| witness / model | Concrete object or interpretation exhibiting failure. |
| status | Proposed, checked, verified counterexample, rejected, or unresolved. |
| impact | Refute claim, invalidate one proof path, create repair task, or revise domain. |
| provenance | How the witness was found and checked. |

> **DECISION.** Finding a verified counterexample refutes its exact target. Failing
> to find one is not a proof.

## 6. Failure is informative but not a fact

> **SOURCE-DERIVED / INFERENCE.** A failed proof can reveal missing conditions,
> hidden lemmas, inadequate definitions, useful counterexamples, and alternative
> theorem boundaries. Deleting failure destroys discovery evidence; treating it as a
> deductive premise is unsound.

Two linked epistemic regimes are useful conceptually:

| Deductive state | Discovery state |
|---|---|
| ASSUMED | CONJECTURED |
| DERIVED | HEURISTIC |
| VERIFIED | CANDIDATE_LEMMA |
| REFUTED | REPRESENTATION_PROPOSAL |
| UNDERDETERMINED | DEFINITION_PROPOSAL |
| UNRESOLVED | FAILED_BRANCH / ABANDONED_PATH |
|  | COUNTEREXAMPLE / DIAGNOSIS |

Discovery nodes may inform search but cannot support a deductive proof until a
licensed promotion/verification transition changes their status.

## 7. Hidden lemmas, repair, and concept revision

> **SOURCE-DERIVED — Lakatos.** Proof analysis can expose a hidden lemma whose
> failure explains a counterexample. Incorporating a principled condition can revise
> a conjecture or generate a new concept. Different proofs may expose different
> refinements.

Potential versioned relationships are:

    Concept C@v2 REFINES C@v1
    Conjecture T@v2 RESTRICTS T@v1
    Definition D@v3 GENERALIZES D@v2
    Proof P2 SUPERSEDES failed proof P1

> **DECISION.** Routine deduction uses fixed, identified definitions. Discovery mode
> may propose versioned definitions or concepts, but must never silently mutate a
> library definition already used by a proof.

### Anti-exception-barring guardrail

> **SOURCE-DERIVED — Lakatos.** Monster-barring, exception-barring,
> monster-adjustment, and lemma-incorporation are mathematically different responses
> to counterexamples.

When a repair excludes a witness, record why:

- Does the restriction arise from a failed lemma or proof invariant?
- Does it identify a principled domain boundary?
- Does it improve multiple cases or merely exclude the observed witness?
- Does another proof avoid the restriction?

> **INFERENCE.** Ad-hoc exception barring resembles overfitting a theorem to known
> counterexamples; proof-derived condition repair resembles structural revision.
> This analogy is design guidance, not a formal judgement rule.

## 8. Candidate reusable search semantics

The table below is a research agenda, not a keyword registry.

| Candidate | Semantic purpose | Input → search-state effect | Truth-state change? | Evidence | Current status |
|---|---|---|---|---|---|
| CHOOSE_REPRESENTATION | Expose useful structure in another encoding. | Problem/state → representation proposal and mapping obligations. | No, unless later equivalence is verified. | MATH + AMPS cues | Observed; primitive vs policy unresolved. |
| RECOGNIZE_STRUCTURE | Link current form to a pattern, invariant, recurrence, or known family. | State → structure hypothesis / warrant candidates. | No. | MATH | Observed; likely planner metadata or composition. |
| CREATE_SUBGOAL | Replace progress target with a sufficient intermediate goal. | Goal + state → scoped subgoal and dependency relation. | Goal/control only. | MATH | Observed; reusable control effect. |
| CONSIDER_CASES | Propose a partition worth exploring. | State → case proposal and coverage obligation. | No global truth change. | MATH | Observed; search half of case protocol. |
| USE_SYMMETRY | Normalize equivalent configurations or reduce cases. | State → symmetry choice and equivalence obligation. | No until warrant checked. | MATH + AMPS cues | Observed; may compose representation + theorem use. |
| REFRAME | Replace task with an equivalent/easier one. | Goal → new goal plus equivalence/map-back obligations. | Goal/control only. | MATH + AMPS cues | Sparse observation; test before primitive. |
| WORK_BACKWARDS | Search from target toward sufficient predecessor states. | Goal → predecessor/subgoal candidates. | No. | Source-derived/general heuristic | Theoretical; policy/composition unresolved. |
| GENERALIZE | Propose a broader claim or abstraction. | Claim/examples → conjecture version. | Discovery status only. | Lakatos/Winskel synthesis | Theoretical; high risk as primitive. |
| SPECIALIZE | Restrict claim/state to a useful instance. | Claim/domain → instance goal/candidate. | Goal/control only. | Source-derived/general heuristic | Theoretical; likely composition. |
| STRENGTHEN_HYPOTHESIS | Repair an insufficient proof invariant. | Failed induction/proof → stronger conjecture + new obligations. | Discovery status only. | Winskel + Lakatos | Theoretical; planner decision, not syntax yet. |
| SEEK_COUNTEREXAMPLE | Search for a falsifying witness/model. | Target claim → witness candidates or timeout. | Only verified witness refutes. | Lakatos + Blackburn/Bos + FormalMATH | Strong theoretical support; protocol, not necessarily primitive. |
| LOCATE_FAILED_DEPENDENCY | Diagnose which lemma/edge caused proof failure. | Failed proof graph → guilty/hidden lemma hypothesis. | No. | Lakatos | Theoretical discovery operation. |
| IDENTIFY_FAILED_DEPENDENCY | Equivalent diagnostic family to LOCATE_FAILED_DEPENDENCY. | Failure + dependency graph → diagnosis node. | No. | Lakatos/inference | Merge terminology before implementation. |
| REPAIR_LEMMA | Propose a corrected lemma or proof path. | Failed local claim → versioned repair proposal. | Discovery status only. | Lakatos | Theoretical protocol/composition. |
| REVISE_CONJECTURE | Create a new conjecture version after evidence. | Conjecture + diagnosis → revised claim and relation to old version. | Old truth status unchanged; new claim proposed. | Lakatos | Theoretical protocol. |
| PRUNE_IRRELEVANT_STATE | Focus search on goal-relevant nodes/branches. | Search state → inactive/deprioritized subset with rationale. | No mathematical truth change. | AMPS-style pedagogy + inference | Unannotated; policy candidate. |
| RELAX_CONSTRAINT | Explore a broader or approximate problem. | Goal/constraints → alternate problem and map-back condition. | Discovery status only. | General heuristic | Theoretical; high semantic risk. |
| COMPARE_PROOF_PATHS | Contrast proofs for dependencies and theorem refinements. | Multiple proof DAGs → comparison/repair hypotheses. | No direct truth change. | Lakatos | Theoretical research operation. |

Every candidate must be tested against these questions:

1. Is it a genuine semantic primitive or a policy over existing state operations?
2. Is it a composition, goal effect, representation proposal, or warrant search?
3. Does it change mathematical truth state or only search/control state?
4. Can planner metadata represent it without new language syntax?
5. Does it recur independently across MATH, AMPS, and formal proof states?

## 9. Likely hybrid system

> **INFERENCE.** Current evidence favors:

    open / latent / English-capable planner
                    ↓
    proposed meaning, subgoal, representation, or action
                    ↓
    typed mathematical state with explicit provisional status
                    ↓
    checked execution + evidence + verifier
                    ↓
    new state and feedback to planner

The planner may be neural, symbolic, mixed, or replaceable. HML's durable hypothesis
is the semantic interface and checked state, not necessarily a fixed textual planner
language.

## 10. Strongest evidence search should remain separate

- **EMPIRICAL:** SEARCH_META versus CONSTRUCT was one of the 43 label collisions;
  mode and state effect can both be correct.
- **EMPIRICAL:** successful solutions expose selected representations/subgoals but
  not rejected alternatives.
- **SOURCE-DERIVED — Lakatos:** discovery uses failure, counterexample, diagnosis,
  repair, and concept revision—states not captured by polished proof execution.
- **SOURCE-DERIVED — Winskel:** selecting a strengthened induction hypothesis is an
  artful search decision inside a proof protocol.
- **INFERENCE:** verifier conservatism and planner creativity need different status
  and safety contracts.

## 11. Unknowns

- Which source-visible meta classes are stable across AMPS after semantic annotation?
- What failed-search data can be collected without fabricating hidden reasoning?
- Are representation choice and reframing semantic events or planner metadata?
- How should discovery-state versions interact with deductive dependency graphs?
- Can counterexample and repair quality be evaluated without encoding taste as truth?
- How much planner state must be persisted for reproducibility and training?
- Does explicit search structure help a model compared with latent search under
  matched budgets?

## 12. Tests required before implementation

1. Annotate a bounded AMPS sample with operation, mode, warrant, goal effect, and
   uncertainty separated.
2. Build a targeted proof-state set containing failed branches, counterexamples,
   local/global failure targets, and repair decisions.
3. Compare multiple independent annotations of the same discovery traces.
4. Test whether candidate meta verbs predict distinct state/control effects or merely
   paraphrase planner intent.
5. Test induction with weak versus strengthened hypotheses.
6. Measure search cost, verified progress, failure diagnosis, and overfit repairs—not
   only final answer accuracy.
7. Keep HML, generic AST, Structured English, and hybrid planner renderings matched.

> **DO NOT IMPLEMENT YET.** REFRAME, WORK_BACKWARDS, PRUNE,
> RELAX_CONSTRAINT, STRENGTHEN_HYPOTHESIS, REPAIR_LEMMA,
> REVISE_CONJECTURE, and CHOOSE_REPRESENTATION are research candidates, not approved
> HML keywords.
