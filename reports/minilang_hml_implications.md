# MiniLang implications for HML

## Scientific verdict

MiniLang is strong independent evidence for HML's existing decomposition:

    high-entropy planner/search
      → small typed execution/control kernel
      → rich state and explicit goals
      → theorem/domain/backend evidence
      → checker-owned epistemic result

It does not validate “mathematics has ten operations,” nor does it falsify HML's 17
empirical candidate effects. The two ontologies describe different layers. MiniLang
compresses formal proof control after modeling; HML's corpus spans informal modeling,
candidate generation, transformation, checking, and explanation.

The strict recommendation is:

> **KEEP HML'S NEUTRAL SEMANTIC AST/STATE AS CANONICAL; IMPLEMENT THE MISSING
> GENERIC CANDIDATE AND CERTIFIED BRANCH/JOIN MECHANISMS; KEEP TEXTUAL HML AS A
> RENDERING; THEN RUN A CONTROLLED AST/TEXT GEMMA ABLATION.**

Do not replace HML's candidate vocabulary with MiniLang's commands. Do not add
Isabelle-specific syntax. Do not alter HML from this report alone.

## Strongest convergence

1. **State is structured and scoped.** MiniLang's semantics are transitions over a
   context-labelled proof tree, not string rewriting.
2. **Operations and knowledge separate.** RULE/SIMP/END are small interfaces over
   theorem libraries, simplifier, premise selection, tactics, and external provers.
3. **Obligations persist as goals.** HAVE, CONSIDER, cases, and induction explicitly
   create subgoals that remain until certified closure.
4. **Validity is checker-owned.** A claim becomes proved only through an Isabelle
   theorem; model output alone has no epistemic authority.
5. **Branch locality is semantic.** Case assumptions and induction hypotheses live
   in branch scopes and are exported only by valid rules.
6. **Certified joins are compact.** CONSIDER∨ uses a proved coverage disjunction and
   elimination theorem; cases/induction use Isabelle theorem schemas.
7. **Small-core compression is real at a control level.** In 290,185 verified proofs,
   1.52M command occurrences have 2.726 bits entropy and effective perplexity 6.62.
8. **Text need not be canonical.** The later AoA result moves the same semantics to
   JSON AST plus interleaved state, reducing interaction overhead.

## Strongest disagreement / missing dimensions

MiniLang intentionally omits or collapses dimensions HML must retain:

- informal problem modeling and interpretation;
- candidate statuses PROPOSED/UNVERIFIED/VERIFIED/REJECTED;
- planner intent, alternatives, relevance, expected progress, and novelty;
- generic domain preconditions and persistent non-goal obligations;
- neutral dependency/provenance/evidence records in the serialized representation;
- independent warrant versus backend identity for broad SIMP/END effects;
- representation-neutral source trajectories;
- process-quality distinctions identified in PRM800K.

MiniLang adds proof-specific machinery that current HML lacks or only partially has:

- executable leftmost-goal tree transitions;
- explicit box/sibling navigation;
- a compact coverage-and-join construction;
- obtain-style existential witness scopes;
- production induction/case adapters to theorem schemas;
- integrated premise-hinted, cached proof search with kernel reconstruction.

## PRM800K boundary

PRM800K showed that validity, progress, novelty, goal relevance, clarity, and
short-horizon verifiability must not collapse. MiniLang chiefly models formal
execution and final proof validity:

- **validity/verifiability:** strong, through Isabelle;
- **progress:** implicit only in remaining subgoal state;
- **novelty:** absent;
- **goal relevance:** not represented beyond tactic applicability/current goal;
- **clarity:** influenced by language design but not an epistemic field;
- **planner intent/alternative choice:** absent;
- **search policy:** largely delegated to model, theorem hints, and automation.

Therefore MiniLang is evidence about **formal proof execution**, not a complete model
of mathematical cognition or natural reasoning quality.

## What changes implementation priority

### Implement after tokens return

Within the already approved HML direction, Claude should implement/test in this order:

1. **Canonical semantic AST/state boundary.** Ensure every operation consumes and
   emits typed semantic state/delta objects; textual HML remains a renderer/parser.
2. **Generic candidate lifecycle (SF-R06/R07).** Proposed, unverified, verified,
   rejected; promotion only by named verifier evidence and original constraints.
3. **Certified branch protocol (SF-R08).** Coverage theorem/obligation, branch-local
   contexts, exact branch result dependencies, close, and certified join. Use
   MiniLang's disjunction-elimination pattern as a test oracle, not copied syntax.
4. **Evidence adapter (SF-R09).** Wrap backend/kernel results with exact evidence,
   premise, version, and checker status rather than opaque success.
5. **Goal/control factoring.** Make discharge/navigation/scope closure explicit
   effects beneath ergonomic interfaces; avoid a monolithic END analogue.
6. **Generic verified backend contract.** Input state + operation intent + warrant/
   hints → result + residual goals + obligations + certificate + dependencies.
7. **Targeted induction protocol experiment.** Represent target/schema/generalization,
   base/step cases, IH scopes, side obligations, and join; decide only afterward
   whether INDUCT deserves a stable core interface.
8. **Conformance tests.** Nested scope, branch leakage, overlapping/exhaustive cases,
   theorem identity, fact hints, multiple residual goals, backend timeout, and failed
   reconstruction.
9. **AST/text Gemma ablation.** Equal-data/equal-token comparison after the semantic
   firewall is operational.

This is a priority refinement, not authority to modify HML during this audit.

### Explicitly do not implement

- the ten MiniLang names as HML primitives;
- a universal `SIMP`/`END` that hides warrants and proof debt;
- Sledgehammer or Isabelle-specific proof contexts in the HML core;
- implicit branch merge without coverage/join evidence;
- CHOOSE as a replacement for generic candidate state;
- INDUCT syntax before schema/generalization evidence;
- new operations inferred directly from translator error strings;
- text or JSON syntax as the canonical semantic object;
- automated planner/search semantics based on MiniLang frequencies;
- modifications to frozen Gold/PRM/Semantic Firewall data.

## HML candidates that may be redundant at kernel level

These are not deletion decisions:

| Candidate | Likely lower-level factorization |
|---|---|
| DISCHARGE | goal effect + verifier evidence + scope/control delta |
| VERIFY | epistemic effect produced by a checker/evidence adapter |
| CONTRADICTION | proof mode/warrant + theorem application + close/reject effect |
| APPLY_DEFINITION | theorem application/transform with definition warrant |
| COUNT | theorem/domain/backend warrant over generic derive/evaluate |
| BOUND | theorem/domain relation over generic derive/transform |
| EVALUATE | backend call returning checked value/certificate/debt |

DECLARE and RECORD may also be state-delta constructors rather than “reasoning
instructions,” but they remain semantically indispensable. SELECT must survive until
candidate lifecycle evidence says otherwise; MiniLang starts too late in the process
to test it.

## External AoA evidence

The July 2026 [AoA primary paper](https://arxiv.org/abs/2607.16372) is verified. It:

- defines MiniLang AST as a recursive algebraic datatype and JSON Schema;
- has LLMs supply JSON operation trees via tool calls;
- fuses operations and their own subgoal states in one proof tree;
- edits/re-evaluates affected subtrees instead of patching source and querying line
  numbers;
- reports 2.3–4.7× lower normalized API cost, 2.9–6.9× fewer tokens, 3.9–8.9×
  fewer tool calls, and 1.4–2.0× faster runs on common-success sets;
- explicitly acknowledges no clean ablation separates Minilang from tree editing.

This strongly supports semantic AST/state-first interfaces. It does not show JSON is
the canonical mathematical semantics, nor that tree editing alone causes the gains.

## Final scientific questions

### 1. What are MiniLang's exact ten operations?

INTRO, HAVE, CONSIDER-disjunction, CONSIDER-existential, RULE, CHOOSE, SIMPLIFY
(executable keyword `SIMP`), CASE_SPLIT, INDUCT, and END (with NEXT as its
sibling-navigation alias). This is the paper's semantic counting convention.

### 2. Are they truly semantically orthogonal?

No. They have clear user-facing distinctions but several are multi-axis macros.
HAVE, CONSIDER, END/NEXT, SIMPLIFY, CASE_SPLIT, and INDUCT compose goal, scope,
epistemic, warrant, backend, and navigation effects.

### 3. How do they map to HML's 17 candidate effects?

RULE is closest to APPLY_THEOREM; CASE_SPLIT/CONSIDER∨ to CASE_SPLIT; CHOOSE to
CONSTRUCT plus existential refinement; END/NEXT to DISCHARGE plus control; INTRO to
DECLARE/RECORD scope deltas. SIMPLIFY and automation span multiple HML effects.
MODEL, generic candidates, SELECT, explicit VERIFY, ENUMERATE, COUNT, BOUND, and
informal transformations are absent or delegated. The exact bidirectional mapping is
in `hml_mapping.json`.

### 4. Can HML's 17 collapse further?

At the implementation/kernel layer, probably yes: DISCHARGE and VERIFY are effects;
CONTRADICTION is mode/warrant; definition/count/bound/evaluation can use generic
theorem/backend interfaces. At the empirical ontology/interface layer, this audit is
insufficient to delete labels.

### 5. What does HML represent that MiniLang does not?

Neutral source trajectories, informal modeling, explicit candidates and promotion,
generic preconditions/debt, provenance/dependencies/evidence axes, planner/search
intent, and PRM process-quality dimensions.

### 6. What does MiniLang represent that HML does not?

A production executable proof tree with leftmost-goal transitions, box/sibling
control, compact kernel-certified branch joins, obtain scopes, production induction/
case adapters, and tightly integrated Sledgehammer* proof search.

### 7. What percentage of Isabelle proof activity is hidden in backends?

No meaningful work percentage is identifiable. Exactly 57.59% of serialized command
occurrences are END/NEXT and intrinsically invoke Sledgehammer*; further commands
delegate to simplifier, cases/induct tactics, rules, or arbitrary APPLY methods. 100%
of accepted proof status depends on Isabelle. Search/computation effort per command
is unmeasured, so a “backend share of reasoning” percentage would be fabricated.

### 8. Why do ~15% of translations fail?

14.7184% = 39,504 diagnosed refined failures + 10,578 missing refined rows. Diagnosed
causes are dominated by tactic/automation reconstruction, implementation exceptions,
resources, scope/case bookkeeping, fact/context recovery, unsupported source forms,
and unresolved diagnostics. Translation of rich Isar context into a leftmost-goal
normal form is difficult.

### 9. Semantic-language failures or translator failures?

Mostly demonstrated translator/interpreter/backend limitations; 10,578 remain
unknown. Branch/scope/induction clusters are possible semantic pressure but do not
prove absent MiniLang transition schemas. No defensible core-semantic failure rate
can be derived.

### 10. Does the ~340K corpus support the small-core hypothesis?

Yes, at the formal proof-control layer: 290,185 verified scripts compress to 17
observed labels including escape hatches, with effective operation perplexity 6.62
and top-10 concrete coverage 96.06%. It is large independent evidence for a small
interface, not proof that all mathematical reasoning has ten or seventeen primitives.

### 11. What explains the reported performance improvement?

The controlled evidence attributes gains to the combined language representation/
goal-structuring condition and separately to SH*. Fewer proof-syntax errors explain
only a small share; reduced operation failures and hammer failures explain more.
Vocabulary size, semantic orthogonality, length, entropy, obligation shape, and
translation filtering are not individually isolated.

### 12. Which architecture does evidence favor?

**Semantic AST + canonical state/evidence + HML as one rendering.** A generic syntax
AST lacks proof meaning; text is useful but brittle as the canonical object.

### 13. Does AoA strengthen AST/state-first design?

Yes, strongly as system evidence. It verifies the prompt's claim and reports large
interaction-efficiency gains, but its Minilang/tree-edit contributions are coupled.

### 14. Which SF-R requirements change?

No requirement changes definition. SF-R08 certified branch join gains independent
support and priority; SF-R06/R07 candidate lifecycle remain absent and necessary;
SF-R09 evidence wrapping and SF-R15 renderer separation are strengthened. Existing
scope/checker/discharge requirements are corroborated.

### 15. What exactly should Claude implement?

The nine-step ordered list above: semantic AST boundary, candidate lifecycle,
certified branch protocol, evidence adapter, goal/control factoring, verified backend
contract, induction experiment, conformance tests, then controlled Gemma ablation.

### 16. What should Claude explicitly not implement?

No MiniLang syntax clone, opaque universal automation instruction, Isabelle coupling,
uncertified branch merge, candidate collapse into CHOOSE, premature INDUCT primitive,
error-message-derived opcodes, or text-first canonical architecture.

### 17. What is the next decisive Gemma experiment?

An equal-example/equal-token/equal-backend four-cell comparison of flat natural text,
textual HML, generic AST JSON, and semantic AST with explicit state/evidence deltas.
Measure verified success, firewall violations, operation/term/syntax errors, token/tool
cost, state recovery, calibration, and OOD transfer. Add a vocabulary-collapse
ablation over the same semantics to isolate operation count.

## Safe-deletion scientific gate

The repository now contains the archive/version/license/hash manifest, full compressed
tree, semantic-source hashes, ten-operation reconstruction, HML/SF mappings, exact
corpus/failure measurements, stratified failure evidence, experiment reconstruction,
representative source/translation examples, and a reproduction script. Canonical-doc
updates and commit cleanliness are verified separately at finalization.
