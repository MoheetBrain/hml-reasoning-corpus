# HML Master Research Context

## HOW TO USE THIS FILE

**Readers:** all Claude/Codex agents, researchers, and project reviewers.

**Purpose:** recover the current scientific state in 5–10 minutes. Read this file
first, then follow the router at the end. This is an executive map, not the complete
state, discovery, semantics, or implementation specification.

**Evidence labels:** **EMPIRICAL** means observed in this repository;
**SOURCE-DERIVED** means supplied from the named research source;
**INFERENCE** means an architectural implication; **HYPOTHESIS** requires testing;
**DECISION** is a project rule; **OPEN** is unresolved.

## The project in one page

> **HYPOTHESIS — compressed mathematical reasoning.** Mathematics may contain an
> enormous knowledge space—definitions, theorems, formulas, representations, and
> domains—while reusing a substantially smaller set of state/proof/control effects.

> **INFERENCE — likely HML role.** HML is increasingly best understood as a candidate
> semantic mathematical machine and verifier-facing IR: typed evolving state,
> generic operations, explicit scope and dependencies, warrants, preconditions,
> obligations, epistemic status, and verification interfaces. It is not presently a
> complete replacement for open-ended mathematical thought.

> **DECISION.** The canonical research object is a neutral trajectory
> S0 → a0 → S1 → … → Sn. HML concrete syntax is one serialization of that semantic
> object, not the scientific source of truth.

Representability != reasoning superiority.

HML-vs-generic-AST-vs-Structured-English remains untested under matched adaptation.

The current synthesis is:

    MATHEMATICAL REASONING
      = interpretation
      + state
      + search
      + execution
      + evidence / verification

These components interact, but the Gold-125 disagreement analysis shows why they
must not be compressed into one flat operation label.

## Current architecture

> **INFERENCE.** The best current architecture is a loop, not a one-way compiler:

    natural-language problem
              ↓
    candidate meaning(s) / interpretation
              ↓
    open or neural planner
              ↓
    proposed structured action over typed state
              ↓
    generic operation + warrant + preconditions
              ↓
    obligations + library/backend evidence
              ↓
    verifier and falsification checks
              ↓
    epistemic update and new state
              └──────────────→ planner continues

Discovery mode may additionally retain conjectures, failed branches,
counterexamples, proof repairs, and versioned definition proposals. Those objects
must not become deductive premises until verified or explicitly assumed.

## H1–H5

| Hypothesis | Current status | What the evidence says |
|---|---|---|
| **H1 — state-transition thesis** | Supported as representation | **EMPIRICAL:** Gold-25 and Gold-125 preserve typed state, source provenance, dependencies, obligations, goals, and scope usefully. Completeness for mathematics is untested. |
| **H2 — small-core thesis** | Exploratory support | **EMPIRICAL:** 125 curated MATH trajectories are consistent with 17 adjudicated reusable core effects plus warrants/libraries, but 17.69% remain unresolved. Do not say “mathematics has 17 primitives.” |
| **H3 — HML semantic representation thesis** | Provisional support | **EMPIRICAL:** current HML has useful typed AST, claim, rule, scope, obligation, evidence, and fail-closed machinery. Broad executable mathematical coverage remains partial. |
| **H4 — thinking-language thesis** | Hybrid / inconclusive | **EMPIRICAL:** source-visible planning recurs, but successful MATH solutions omit failed search. **INFERENCE:** an open planner feeding a checked IR is more defensible than a closed keyword-only thinker. |
| **H5 — learned-representation thesis** | Not tested | No training or matched HML/AST/Structured-English experiment has been run. H1–H4 do not imply H5. |

## Exact empirical headline

### Gold-10 history

> **EMPIRICAL.** Gold-10 contains 10 trajectories and 23 transitions. Its original
> classification was 11 current-HML, 8 library, 3 core-gap, and 1 ambiguous
> transition, producing the historical 13.04% CoreGapRate. Forensic triage reduced
> the primary core-semantic count to 2/23; after repinning to repaired HML and adding
> corpus-side certificate adapters, no original transition remained classified as a
> new core-semantic requirement. Four full transitions remained library-blocked:
> n+0=n, a probability product law, reciprocal differentiation, and the dependent
> final calculus transition.

This history is a warning: apparent core gaps can be translation, evidence-routing,
library, or epistemic-status problems.

### Gold-25

> **EMPIRICAL.** Gold-25 contains 25 curated MATH trajectories and 118 adversarially
> audited transitions across seven categories. It observed 48 surface operation IDs,
> 105 explicit and 13 implicit reconstructed steps, 28 transitions with recorded
> preconditions, six explicit obligations, and three branch-bearing trajectories.
> Its builder is a curated artifact generator, not an automatic extractor.

### Gold-125

| Quantity | Exact result |
|---|---:|
| Trajectories | 125 |
| Source-granularity transitions | 769 |
| Atomic / compound macro / uncertain atomicity | 556 / 89 / 124 |
| Observed surface operation labels | 66 |
| Precondition records | 340 |
| Obligations created / measured | 257 / 243 |
| Mean / maximum measured obligation lifetime | 2.54 / 13 steps |
| Dependency edges / maximum fan-in | 901 / 11 |
| Branch-local trajectories / steps | 5 / 26 |
| Explicit branch joins | 1 |
| Certified exhaustive partitions / invariant joins | 0 / 0 |
| Source-visible meta records | 87 / 769 = 11.3% |
| Mode counts: execution / search / verification / goal | 580 / 48 / 28 / 113 |

> **LIMITATION.** Structural and exact-source audits passed, but exact source
> containment is not formal theorem replay. Source sentences can remain compound,
> source mathematics can omit conditions, and successful solutions do not expose
> failed search.

### Ontology-v1

| Quantity | Exact result |
|---|---:|
| Derived transitions | 769 |
| Candidate core values | 18 |
| Adjudicated KEEP_AS_CORE values | 17 |
| Candidate merged pending evidence | INDUCT |
| Broad disagreements before decomposition | 43 |
| Explained by orthogonal axes or preserved uncertainty | 42 |
| Genuine disagreement / annotation review | 1 |
| UNRESOLVED | 136 / 769 = 17.69% |
| Frozen OTHER source labels | 125 / 769 = 16.25% |
| Accepted-core counts at 25 / 50 / 75 / 100 / 125 | 15 / 17 / 17 / 17 / 17 |
| Accepted-core top-5 / top-10 / top-15 coverage | 80.2% / 94.9% / 99.5% |

> **DECISION.** Ontology-v1 is **UNSTABLE_REVIEW_REQUIRED**. A flat curve is not
> stabilization while OTHER and UNRESOLVED remain material and one annotation review
> is open.

## Current HML coverage and implementation boundary

> **EMPIRICAL.** Step-weighted Gold-125 support at the pinned HML revision is:

| Support | Steps | Fraction |
|---|---:|---:|
| FULL | 11 | 1.4% |
| PARTIAL | 455 | 59.2% |
| REPRESENTABLE_ONLY | 303 | 39.4% |
| ABSENT | 0 | 0.0% |

These are semantic-support classes, not performance scores. REPRESENTABLE_ONLY does
not mean executable or theorem-verified.

> **EMPIRICAL — current implementation.** Pinned HML already provides typed
> declarations and expressions; logical, quantified, probability, derivative,
> integral, and limit AST forms; a small checked rule kernel; lexical scope and
> capture-aware binding; goals and assumptions; dependency/evidence graphs;
> checker-computed statuses including underdetermination; exact closed evaluation;
> bounded definition unfolding; and fail-closed unsupported results.

> **EMPIRICAL — missing or partial.** It lacks a general theorem library, broad
> domain checkers, generic exhaustive case/join semantics, a first-class candidate
> verification protocol, general symbolic normalization/solving, and a mathematical
> search policy. Some precondition and obligation synthesis remains incomplete.

> **SOURCE-DERIVED — Winskel.** Syntax, typing, denotation, operational behavior,
> and axiomatic/proof rules answer different questions. HML eventually needs
> conformance between them, not one generic VALID flag.

## Strongest positive evidence

- **EMPIRICAL:** typed state, dependencies, obligations, scope, provenance, and
  checker-owned status recur across Gold-10, Gold-25, and Gold-125.
- **EMPIRICAL:** 42/43 broad label conflicts become intelligible when operation,
  warrant, mode, domain layer, goal effect, granularity, and uncertainty are separated.
- **EMPIRICAL:** named procedures such as trigonometry, modular arithmetic,
  probability, sequences, and calculus often factor into generic effects plus
  library/backend knowledge.
- **SOURCE-DERIVED:** formal semantics supports separating surface syntax from the
  semantic machine and separating operational, denotational, and proof meaning.
- **INFERENCE:** a tiny checked kernel plus rich libraries is a viable architecture
  worth falsifying across sources.

## Strongest negative and null evidence

- **EMPIRICAL:** 136 transitions remain unresolved and 125 retain OTHER; the ontology
  is not scientifically frozen.
- **EMPIRICAL:** Gold-125 is curated and source-grounded, not random, inter-annotated,
  or formally replayed end to end.
- **EMPIRICAL:** MATH exposes successful proofs, not failed search or concept repair.
- **EMPIRICAL:** no AMPS trajectory has been annotated; the 100-row list is only a
  prospective candidate preview.
- **EMPIRICAL:** no Endpoint-A replication artifact, standalone implication-direction
  benchmark, or matched AST/HML/Structured-English scope experiment exists in this
  repository. Gold-10 only supplies local modus-ponens, modus-tollens, and certified
  underdetermination evidence.
- **SOURCE-DERIVED — FormalMATH:** compilation and semantic alignment can diverge
  sharply; broad automation can hide reasoning structure; human adjudication remains
  material in benchmark construction.
- **OPEN:** the planner may contain most of the mathematical intelligence while HML
  remains a useful record/checking interface rather than a reasoning advantage.

## Central scientific threats

1. **Annotation artifact:** the apparent small core may reflect label design,
   source granularity, or forced normalization.
2. **Unresolved tail:** saturation may be artificially flat because difficult cases
   remain OTHER/UNRESOLVED.
3. **Distribution bias:** curated competition solutions may underrepresent pedagogy,
   formal proof states, and discovery failures.
4. **Search displacement:** a compact execution kernel may coexist with a large,
   high-entropy planner; the kernel is not the complete intelligence stack.
5. **Backend masking:** strong tactics or CAS calls may solve tasks without exposing
   whether explicit reasoning semantics helped.
6. **Representation control:** generic typed AST or Structured English may equal or
   outperform HML under matched adaptation.

## Provenance

- Gold-125 baseline corpus commit:
  3bd3ace09bff3deb20e6f0a0650875a120cc3fd4.
- Ontology-v1 and AMPS-audit commit:
  033308051c08790010eafc8f18a2058ef90f6ee0.
- Authoritative HML repository:
  https://github.com/MoheetBrain/hamiltonian-lang.git.
- Pinned HML commit:
  5688aba18632b65a8709aa1d85577d31a67dba6a.
- AMPS source-of-truth SHA-256:
  b48c40afd262a8ac587504bc3008a2b0d688c0144b5d9fddd083f0b576a5df41.
- AMPS audit: 103,059 rows, 721 topics, 47,530 planning-cue rows; no trajectories
  created and no training performed.

## Next scientific questions

1. Can the 136 UNRESOLVED transitions be adjudicated or bounded without inventing
   semantics?
2. Does the 17-effect result survive an independently annotated AMPS sample?
3. Is INDUCT a primitive, a proof protocol, or a composition whose hypothesis choice
   belongs to search?
4. What is the minimal sound branch/join and candidate-verification protocol?
5. Can interpretation errors be separated experimentally from reasoning errors?
6. Can proof search and counterexample/model search produce conservative epistemic
   updates over the same state?
7. After semantic stabilization, does HML beat matched generic AST or Structured
   English on learning, verification, compositional generalization, or cost?

## Router

- For detailed state and execution semantics, read
  [01_STATE_AND_EXECUTION.md](01_STATE_AND_EXECUTION.md).
- For search, discovery, conjecture, failure, and repair, read
  [02_SEARCH_AND_DISCOVERY.md](02_SEARCH_AND_DISCOVERY.md).
- For meaning, warrants, evidence, alignment, and verification, read
  [03_MEANING_EVIDENCE_AND_VERIFICATION.md](03_MEANING_EVIDENCE_AND_VERIFICATION.md).
- For architecture and gated implementation decisions, read
  [04_INTEGRATION_AND_IMPLEMENTATION.md](04_INTEGRATION_AND_IMPLEMENTATION.md).

## External MiniLang convergence — 2026-08-10

> **EXTERNAL ARTIFACT EVIDENCE.** The audited OOPSLA26 v2 artifact (Zenodo
> 18454706; archive SHA-256
> `1562c84524c0851682e47b32243c0e2dcbfb47daaf6820bcb5c216ae8f12bc82`)
> contains 290,185 verifier-accepted Isabelle-to-MiniLang translations. Its paper
> interface has ten semantic operations, while successful executable renderings use
> 17 labels once pragmatic escape commands are counted.

Independent formal-proof evidence therefore supports a **small execution/control
vocabulary**: 1,519,944 serialized commands have 2.726 bits of label entropy and
effective label perplexity 6.62. This converges with Gold-125's long-tail compression,
but the percentages are not directly comparable: MiniLang commands are coarse proof
control compositions; HML's 17 are finer candidate state effects factored from
warrant, scope, goal, epistemic, and rendering axes.

The scientific impact is architectural, not a mandate to rename or collapse HML.
MiniLang's complete system is its control language **plus** Isabelle proof state,
kernel, libraries, simplifier, tactics, premise selection, and Sledgehammer. The
14.7184% failed-or-missing translation tail is dominated by translator, replay,
automation, implementation, and resource diagnostics; it does not establish a
14.7184% core-semantic gap rate. The later AoA lineage strengthens an AST/state-first
interface hypothesis, but neither study isolates semantic minimality from concrete
representation and backend effects. Canonical typed semantic state should therefore
remain primary, with textual HML treated as one renderer pending a matched ablation.

Detailed evidence is frozen in `reports/minilang_*.md` and
`experiments/minilang_audit/` at commit
`a417890bbc24cd7bf444c2d1f4a622a22cffb653`.
