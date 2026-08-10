# MiniLang translation-failure forensic audit

## Result

The artifact's 14.72% non-success tail does **not** establish that MiniLang's ten
semantic operations are 14.72% incomplete. It is a mixture of missing translation
records, tactic/automation reconstruction failures, translator/interpreter bugs,
scope/case bookkeeping failures, theorem/fact resolution, unsupported Isar surface
forms, resources, and malformed/ambiguous terms.

The strongest potential semantic-model pressure is in branch/case, nested scope,
and induction strata. Even there, the observed diagnostics come from concrete
translator/interpreter code and do not distinguish “transition schema impossible”
from “this implementation reconstructed it incorrectly.” No material core-language
failure rate can be inferred from this artifact.

## Exact denominator

| Outcome | Count | Share of 340,267 source goals |
|---|---:|---:|
| Verified refined translation | 290,185 | 85.2816% |
| Recorded refined failure | 39,504 | 11.6097% |
| No refined row | 10,578 | 3.1087% |
| Total failed/missing | 50,082 | 14.7184% |

The 340,267 count comes from exact `origin` rows in the 5.78 GB SqliteDict database,
not from rounding the paper's “~340K.” A verified refined translation is a generated
MiniLang script that the translator replayed through the MiniLang/Isabelle evaluator
without an error.

The 10,578 missing rows cannot be attributed at goal level because the database has
no `refined` diagnostic for them. They may include upstream theory/translation-stage
failures or targets skipped after larger-context failure. They remain unresolved.

## Diagnostic taxonomy

The following is a deterministic first-match classification of each recorded
refined failure. It is descriptive of error messages, not a causal semantic label.

| Class | Count | Share of 39,504 recorded failures | Typical evidence |
|---|---:|---:|---|
| automation/tactic interaction | 15,262 | 38.63% | proof obligation fails; tactic/rule refinement fails |
| implementation bug | 4,799 | 12.15% | explicit BUG, Subscript/Option/Match/THM/CTERM exceptions |
| unresolved | 4,785 | 12.11% | IGNORE and diagnostics without enough semantics |
| timeout/resource failure | 3,292 | 8.33% | timeout/resource diagnostics |
| nested scope/context | 2,789 | 7.06% | fixed-variable/context/proof-mode/export errors |
| branch/case machinery | 2,614 | 6.62% | unpaired subgoal, case metadata, wrong VARS/case qualifier |
| theorem/premise machinery | 2,335 | 5.91% | undefined facts, `that`, calculations, unification/fact selection |
| unsupported semantic operation | 1,344 | 3.40% | `nitpick`, `refute`, `quickcheck`, `@proof`, specialized methods |
| parser/translator limitation | 1,133 | 2.87% | unsupported command/method, parser/printer failure |
| induction | 602 | 1.52% | notably unsupported `nominal_induct` and induction metadata |
| malformed source/term | 430 | 1.09% | ambiguous/ill-typed/inner-syntax terms during replay |
| unsupported Isar syntax | 110 | 0.28% | brackets, `text_raw`, outer syntax |
| locale/context machinery | 9 | 0.02% | locale activation/declaration conflicts |

The machine source, exact errors, and 165-record stratified sample are in
[`translation_failures.json`](../experiments/minilang_audit/translation_failures.json).
The sample takes 12 stable database-order records per observed class plus 12
missing-record examples. It is designed for breadth and reproducibility, not to
estimate within-class prevalence.

## Forensic interpretation by class

### Automation/tactic interaction

The largest diagnostic has the form “Some proof obligation fails.” The translator's
refinement pass attempts to remove tactics while preserving or supplying premise
hints, then validates the generated script. A failure proves that this reconstruction
did not replay; it does not show that no ten-operation proof exists. Possible causes
include insufficient Sledgehammer* premise selection, unsuitable generated subgoals,
lost tactic behavior, timeout, or translator error.

Classification: primarily **translator/backend limitation**.

### Implementation bugs

Explicit `BUG` diagnostics include unmatched subgoals, case mismatches, failed
printing, unsupported internal states, and impossible-according-to-author assertions.
Standard ML exceptions such as `Subscript`, `Option`, `Match`, `UnequalLengths`,
`CTERM`, and `THM` also indicate implementation paths rather than principled
non-expressibility.

Classification: **implementation defect**. These are valuable engineering targets
for MLML but cannot be counted as language-semantic gaps.

### Nested scope/context

Failures around variable freshness, proof modes, object-logic judgments, assumption
export, and fixed-variable arity touch real semantics. MiniLang's state model does
support nested contexts, and many such proofs translate successfully. The correct
question is whether a specific Isar context behavior can be represented by the
MiniLang tree/export protocol—not whether its current translator did so.

Classification: **possible model or implementation boundary**, requiring source-
level adjudication. The artifact alone does not establish missing semantics.

### Branch/case machinery

This is the most important semantic-pressure stratum: “Some subgoal is not paired,”
case qualifier loss, undefined cases, wrong parameter counts, and `CASES'` callback
errors. Yet MiniLang has explicit, sound branch machinery: CONSIDER∨ proves coverage
and uses disjunction elimination; CASE_SPLIT/INDUCT use Isabelle case theorems and
exports. The failures more directly show the difficulty of translating Isar's
multi-mode block/case conventions into a leftmost-goal tree.

Classification: **translator/state-reconstruction bugs are demonstrated**; a core
semantic gap is only a hypothesis. This stratum strengthens HML's demand for explicit
branch certificates and tests.

### Theorem/premise machinery

Undefined fact names, pronoun/calculation references, fact-selection errors, and
unification failures occur after Isar's implicit context and chaining are normalized.
The paper itself identifies proof context, implicit facts, and calculations as major
translation complexity. MiniLang can pass named theorem facts to RULE/SIMP/END; the
hard part is recovering exact references and scope.

Classification: **canonicalization/provenance/translator limitation**, not a missing
theorem-application semantic operation.

### Unsupported source operations

The diagnostics contain heterogeneous items:

- `nitpick`, `refute`, and `quickcheck` are counterexample/testing/search commands,
  not sound proof steps whose denotation must appear in a proof kernel;
- `nominal_induct` is a specialized induction method and may require an induction
  library/schema adapter, not a new core operation;
- `@proof`, specialized AFP tactics, and custom methods may be representable through
  APPLY escape hatches or by their resulting theorem, but were outside translator
  support;
- documentary/raw syntax is not semantic proof activity.

Classification: **ambiguous and not demonstrated**. “Unsupported by translator” is
not equivalent to “unsupported by language.”

### Timeouts and resources

These are operational incompleteness of search/evaluation. A timeout cannot prove
non-denotability or missing proof-state semantics.

Classification: **backend/resource limitation**.

### Missing refined records

The no-row stratum has no per-goal cause. It must remain `UNRESOLVED`, and any attempt
to distribute its 10,578 members across semantic categories would fabricate evidence.

## Does the failure expose the ten-operation model?

For a true semantic-model failure, the evidence would need to show all of:

1. the source proof performs a sound, proof-relevant state transition;
2. its mathematical meaning and scope cannot be expressed by any composition of
   the ten operations plus documented theorem/backend interfaces;
3. the obstacle remains after fixing source normalization, fact identity, parser,
   typing, branch metadata, tactic replay, and resources;
4. an escape hatch would change denotation, not merely improve translation;
5. the missing capability generalizes beyond one Isabelle idiom.

No sampled diagnostic establishes all five. Branch/scope/induction samples justify
targeted follow-up, not a language defect verdict.

## What the tail does reveal

The failure tail falsifies several overly broad interpretations:

- A ten-operation interface does not make translation from a rich legacy language
  simple: the translator has 26 passes and 2,153 transformation LoC before parser,
  printer, evaluator, and infrastructure.
- Small control vocabulary does not eliminate context complexity.
- Leftmost-goal normalization is consequential; Isar tactics and blocks can affect
  or reorder multiple goals.
- Theorem/fact identity and implicit chaining are first-class translation problems.
- Branch and induction metadata are difficult even when their proof rules exist.
- Automation success is part of corpus availability; translated data is filtered by
  what the backend can replay.

This last point creates selection effects: the 290,185 successful proofs are not a
random sample of Isabelle reasoning. Longer/more declarative/less-normalizable
proofs fail more often, as the paper reports. Small-core frequency measurements are
therefore evidence from a large filtered corpus, not universal coverage.

## HML implications

No HML core change is authorized by these failures. The evidence supports:

1. preserve exact source → AST → normalized AST → rendering provenance;
2. separate unsupported source syntax from unsupported semantic transition;
3. make branch/case certificates and local fact identity explicit;
4. make theorem/fact references stable rather than pronoun/position-derived;
5. distinguish backend timeout from semantic rejection;
6. retain `UNKNOWN` where no refined diagnostic exists;
7. build conformance tests around nested contexts, multi-goal tactics, case metadata,
   induction hypotheses, locale context, and calculation chains.

Claude should not implement a new HML operation for any raw diagnostic category.
The next useful MiniLang-specific follow-up would manually adjudicate a random,
source-stratified sample from branch/scope/induction failures against the exact Isar
AST and a corrected translator—not alter HML.
