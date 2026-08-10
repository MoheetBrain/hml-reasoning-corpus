# MiniLang ↔ HML semantic mapping

## Conclusion

MiniLang and HML converge on the architecture **small execution/control interface
+ rich typed state + libraries/backends + checker**, but they do not use the same
semantic units. MiniLang commands are deliberately coarse compositions over an
Isabelle proof tree. HML's 17 candidates are factored mathematical/state effects
with separate warrant, knowledge, goal, scope, epistemic, precondition, obligation,
dependency, and delta axes.

There is therefore no valid 10-versus-17 primitive-count contest. MiniLang is strong
independent evidence that HML should implement fewer kernel mechanisms than surface
interface values, especially for DISCHARGE, VERIFY, CONTRADICTION, theorem/definition
application, and backend calculations. It is not evidence to rename or replace the
HML ontology.

The complete machine mapping is
[`hml_mapping.json`](../experiments/minilang_audit/hml_mapping.json).

## MiniLang to HML

| MiniLang semantic operation | Relationship | HML effect(s) | Critical non-operation axes |
|---|---|---|---|
| INTRO | HML_COMPOSITION; SCOPE_EFFECT | DECLARE + RECORD-like deltas | Open binders/assumptions; local epistemic status |
| HAVE | HML_COMPOSITION | CONSTRUCT + RECORD + DISCHARGE | Create goals/debt; block scope; verified promotion |
| CONSIDER∨ | Near 1:1 + composition | CASE_SPLIT + DISCHARGE | Coverage obligation; branch locality; certified join |
| CONSIDER∃ | HML_COMPOSITION | DECLARE + RECORD + DISCHARGE | Existential elimination and witness scope |
| RULE | Near 1:1 | APPLY_THEOREM | Theorem identity/warrant; generated premise obligations |
| CHOOSE | HML_COMPOSITION | CONSTRUCT | Existential refinement; no independent candidate lifecycle |
| SIMPLIFY | MINILANG_COMPOSITION; BACKEND | TRANSFORM/APPLY_DEFINITION/APPLY_THEOREM/EVALUATE/VERIFY/DISCHARGE | Simp-set warrant, backend trace, residual obligations |
| CASE_SPLIT | Near 1:1; backend/library | CASE_SPLIT | Isabelle cases theorem, branch contexts, join proof |
| INDUCT | Near 1:1 surface; backend protocol | unresolved INDUCT + DECLARE/RECORD/CASE_SPLIT/DISCHARGE | Schema choice, IH scope, case obligations, join theorem |
| END/NEXT | GOAL + SCOPE effect; backend | DISCHARGE | Sledgehammer* evidence, block close, sibling navigation |

### Axis-level lessons

- **reasoning_mode:** MiniLang mostly omits why an operation was chosen. Induction
  and contradiction names reveal some strategy, but search intent/progress/relevance
  are not modeled.
- **core_operation:** several commands are macros over multiple HML effects.
- **warrant:** RULE exposes theorem identity; SIMP and END often collapse many
  warrants into backend configuration or generated proof.
- **knowledge_layer:** theorem libraries, simp sets, cases/induct rules, premise
  selection, and ATPs are clearly outside the small control language.
- **goal_effect:** END/NEXT strongly supports treating DISCHARGE and navigation as
  control effects, even when ergonomic syntax remains.
- **scope_effect:** INTRO, HAVE, CONSIDER, CASE_SPLIT, and INDUCT show scope is
  semantic, not rendering.
- **epistemic_effect:** Isabelle owns validity. MiniLang does not expose a generic
  candidate status transition.
- **preconditions:** tactic/rule/type applicability is enforced but usually not
  represented as a uniform first-class object.
- **obligations:** goals are persistent and explicit; domain debts and provenance
  are less explicit.
- **dependencies:** kernel proofs preserve logical support, but the flat MiniLang
  corpus does not expose the neutral dependency graph HML needs.
- **state_delta:** MiniLang has exact executable deltas over its proof tree; it is
  narrower than HML's mathematical state.

## HML to MiniLang

| HML candidate | MiniLang expression | Classification | What is lost/collapsed |
|---|---|---|---|
| DECLARE | INTRO, CONSIDER∃, structured HAVE, DEFINE escape | Composition | General neutral object declaration |
| RECORD | Introduced premise or completed HAVE/CONSIDER fact | Composition | External/source provenance axis |
| MODEL | Already in Isabelle term/context | MINILANG_MISSING | Informal-to-formal modeling phase |
| CONSTRUCT | CHOOSE, terms, DEFINE escape | Composition | Candidate status outside an existential proof |
| TRANSFORM | SIMP/RULE/APPLY/UNFOLD/END | MINILANG_COMPOSITION | Exact transform kind and warrant visibility |
| SUBSTITUTE | SIMP/RULE/term instantiation | BACKEND_OR_LIBRARY | First-class capture/dependency delta |
| APPLY_DEFINITION | SIMP/RULE/END hints; UNFOLD escape | BACKEND_OR_LIBRARY | Dedicated definition-use record |
| APPLY_THEOREM | RULE; theorem hints | Near 1:1 | RULE may infer application mode |
| CASE_SPLIT | CONSIDER∨ or CASE_SPLIT | Near 1:1 | Nothing essential if Isabelle certificate retained |
| ENUMERATE | Cases or backend result | MINILANG_MISSING | Finite collection generation/provenance |
| COUNT | RULE/SIMP/END with library | WARRANT_NOT_OPERATION | Counting meaning is theorem/domain content |
| EVALUATE | SIMP/APPLY/END | BACKEND_OR_LIBRARY | Value/certificate interface |
| BOUND | Proposition content + RULE/SIMP/END | WARRANT_NOT_OPERATION | Bound as explicit mathematical effect |
| SELECT | CHOOSE only in existential goals | MINILANG_MISSING | Generic admissibility/selection/promotion |
| VERIFY | Isabelle checker; explicit HAVE goal | EPISTEMIC_EFFECT | Separate claim/candidate verification transition |
| CONTRADICTION | RULE contradiction theorem | WARRANT_NOT_OPERATION | Contradiction strategy versus resulting goal effect |
| DISCHARGE | END/NEXT or solving RULE/SIMP | GOAL_EFFECT | Evidence remains in Isabelle rather than operation taxonomy |
| INDUCT candidate | INDUCT | Near 1:1 surface, backend protocol | Generalization/schema choice delegated to Isabelle |

### Can the HML 17 collapse?

The evidence supports an **implementation collapse**, not yet an ontology deletion:

1. DISCHARGE should primarily be a goal effect with verifier evidence.
2. VERIFY should primarily be a checker-owned epistemic effect.
3. CONTRADICTION can be a proof mode/warrant plus branch/goal effect.
4. APPLY_DEFINITION is plausibly APPLY_THEOREM/TRANSFORM with a definition warrant.
5. COUNT and BOUND may be stable user-visible mathematical effects implemented by
   generic theorem/backend transitions.
6. EVALUATE may be a backend interface returning value + certificate + obligations,
   not a dedicated kernel reduction.
7. DECLARE/RECORD remain indispensable state deltas even if not execution opcodes.

TRANSFORM must not become an opaque SIMP-like operation that loses warrant,
preconditions, or dependency ancestry. SELECT/VERIFY must not be removed merely
because MiniLang's formal proof distribution does not model exploratory candidates.

## MiniLang versus Semantic Firewall

| Requirement | Classification | Evidence |
|---|---|---|
| SF-R01 dependency preservation | IMPLICIT_IN_ISABELLE | Kernel theorem support exists; neutral dependency DAG absent at surface |
| SF-R02 lexical scope | EXPLICITLY_SUPPORTED | Context tree, BLOCK, obtain, cases, induction exports |
| SF-R03 neutral importer | NOT_APPLICABLE | Isar-specific 26-pass translator |
| SF-R04 preconditions | IMPLICIT_IN_ISABELLE | Type/rule/tactic applicability; no uniform record |
| SF-R05 obligation round-trip | EXPLICITLY_SUPPORTED | Persistent goals/subgoals; metadata round-trip narrower than HML |
| SF-R06 candidate state | ABSENT | No generic candidate lifecycle |
| SF-R07 candidate promotion | ABSENT | Witness checking is not generic promotion |
| SF-R08 certified branch join | EXPLICITLY_SUPPORTED | Disjunction-elimination/cases/induction theorem reconstruction |
| SF-R09 evidence adapter | IMPLICIT_IN_ISABELLE | Theorem values authoritative; no neutral evidence object |
| SF-R10 theorem/domain evidence | DELEGATED_TO_BACKEND | Libraries, simplifier, hammers, premise selection |
| SF-R11 checker-owned status | EXPLICITLY_SUPPORTED | Only kernel theorem completion closes goals |
| SF-R12 exact goal discharge | EXPLICITLY_SUPPORTED | END/NEXT conclusion and stack checks |
| SF-R13 type/domain propagation | IMPLICIT_IN_ISABELLE | HOL types/contexts; domains often propositions/classes |
| SF-R14 domain applicability | DELEGATED_TO_BACKEND | Hypotheses, type classes, simp/rule/ATP |
| SF-R15 renderer separation | ABSENT in this artifact | Concrete text corpus; later AoA provides AST/JSON separation |

No existing SF requirement should be removed or weakened. Evidence priority changes:

- SF-R08 moves up: MiniLang independently demonstrates a compact safe branch/join
  design, with a proof certificate rather than a raw merge.
- SF-R06/R07 remain missing and are not contradicted by MiniLang; its task starts
  after most candidate discovery.
- SF-R09 should preserve kernel/backend evidence identity when wrapping automation.
- SF-R15 is strengthened by external AoA, not by the OOPSLA artifact alone.

## Representation-neutral implications

MiniLang's artifact corpus is concrete text generated from a typed internal AST.
The July 2026 [AoA paper](https://arxiv.org/abs/2607.16372) then exposes a recursive
MiniLang AST through JSON Schema and interleaves proof operations with their subgoal
states in one editable tree. Its authors explicitly report that concrete syntax and
line-number state recovery cause repeated relocation/tool overhead, and report
2.9–6.9× fewer tokens and 3.9–8.9× fewer tool calls for the combined AST/tree-edit
system. They also acknowledge there is no clean ablation separating Minilang from
the tree-edit model.

For HML, the evidence favors:

    canonical neutral semantic AST/state
      → verified operation/evidence interfaces
      → HML text as one rendering

not generic syntax-only AST and not text as the canonical object. This agrees with
the existing neutral trajectory decision; it does not authorize an HML redesign.

## Strict mapping decision

- Preserve the 17 candidates as empirical interface vocabulary pending targeted
  ontology adjudication.
- Implement the smallest generic state/control mechanisms beneath them.
- Treat theorem/domain names as warrants/libraries, never new kernel instructions.
- Prioritize certified branch/join and generic candidate lifecycle because MiniLang
  validates the former and omits the latter.
- Run a targeted induction protocol study before deciding whether INDUCT is syntax,
  a reusable protocol, or a backend theorem-schema call.
- Keep exact evidence/dependency/precondition/obligation axes even where MiniLang's
  ergonomic commands hide them.
