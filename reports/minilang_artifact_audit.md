# MiniLang / OOPSLA26 artifact forensic audit

## Result

The supplied archive is the correct Zenodo v2 artifact for *A Minimalist Proof
Language for Neural Theorem Proving over Isabelle/HOL*. Local MD5 exactly matches
the official Zenodo file digest. The artifact is scientifically useful and contains
the language implementation, typed translator AST, translator, full Isabelle/AFP
source/runtime environment, translated proof corpora, training corpora, model
outputs, and evaluation data. It does **not** contain trained model weights.

The central result survives inspection with an important boundary: MiniLang is a
small **proof-control and goal-refinement interface**, not a ten-operation account
of all mathematical intelligence. Its complete proving system is:

    MiniLang control/state transitions
      + Isabelle typed proof context and kernel
      + theorem and simp libraries
      + cases/induct tactics
      + Sledgehammer* premise selection/search/external provers/cache
      = checked proof construction

The audit did not modify `hml_core`, HML production code, frozen trajectories, or
Semantic Firewall fixtures.

## Provenance and identity

| Field | Locally verified value |
|---|---|
| Archive at audit | `/Users/moheet/Downloads/OOPSLA26 Artifact.tar.zst` |
| Archive bytes | 7,112,761,294 |
| SHA-256 | `1562c84524c0851682e47b32243c0e2dcbfb47daaf6820bcb5c216ae8f12bc82` |
| MD5 | `6f5a1fe82aa182945f6520f7682fa05f` |
| Official MD5 match | Yes, exact |
| Local mtime | 2026-08-10 11:06:45 +0100 |
| Compression | Zstandard, one frame, content size 6.62 GiB, XXH64 checksum |
| Archive tree entries | 42,699 |
| Sum of member file bytes | 33,985,167,710 |
| Published identity | Zenodo record 18454706, artifact v2 |
| Artifact publication/update | v2 published 2026-02-04 |
| Paper | arXiv:2507.18885v4; accepted OOPSLA'26 |
| License | AGPL-3.0-or-later; copyright 2025-2026 Qiyuan Xu |
| Embedded source Git SHA | None recoverable: no packaged `.git` metadata or project commit manifest |

The official [Zenodo record](https://zenodo.org/records/18454706) identifies the
7.1 GB v2 archive, license, related paper, and MLML repository. The current
[arXiv record](https://arxiv.org/abs/2507.18885) reports v4, OOPSLA'26 acceptance,
the ten-operation design, ~340K input proofs, and ~85% translation success.

The immutable detailed manifest is
[`source_manifest.json`](../experiments/minilang_audit/source_manifest.json); the
complete path list is preserved as
[`source_tree.txt.gz`](../experiments/minilang_audit/source_tree.txt.gz). Semantic
source hashes make later substitution detectable.

### Extraction policy

The archive was never fully extracted. A 52 MB semantic/source selection and a
temporary 7 GB quantitative selection were materialized. The latter held the
5.78 GB translation database, two translation JSONLs, four training archives, and
result CSVs. This avoided duplicating the 33.99 GB tar payload.

## What the 33.99 GB payload contains

| Area | Entries | Member bytes | Classification |
|---|---:|---:|---|
| `MLML/` | 42,575 | 30,695,146,690 | Code, full Isabelle/AFP sources and runtime, heaps, databases |
| `results/` | 103 | 2,036,275,624 | Generated translations, model outputs, raw SqliteDict DBs, CSV reports |
| `data/` | 12 | 1,253,033,115 | Generated evaluation and fine-tuning datasets |
| `docs/` | 4 | 406,060 | Reference manual, screenshot, missing-PISA-case list |
| Root README/PDF/license | 4 files | 306,221 | Instructions, paper-like README PDF, AGPL notices |

Large storage is dominated by reusable runtime and generated data, not the
language semantics:

- bundled Isabelle2024: 24.08 GB;
- `MLML/data/translation/results.db`: 5.78 GB;
- bundled AFP 2025-02-12 source: 331.9 MB, plus built heaps elsewhere;
- translated JSONLs: 544.2 MB and 638.4 MB;
- four compressed fine-tuning corpora: approximately 1.19 GB total;
- model outputs and evaluation DB/CSV results: approximately 0.71 GB;
- MiniLang implementation and tests: 3.50 MB;
- Isa-REPL: 270 KB;
- auto_sledgehammer source: 90 KB.

### Content classification

| Requested category | Finding |
|---|---|
| Language definition | Reference manual + paper + executable transitions in `proof.ML` |
| Grammar/parser | Isabelle token/Parse combinators in `proof.ML`; no standalone parser generator |
| AST | Typed Isabelle/ML `ast` (Isar) and `mast` (MiniLang) datatypes in `translator.ML` |
| Isabelle implementation | Complete source in `MLML/contrib/Isa-Mini` |
| Isar → MiniLang translator | 5K+ line `translator.ML`, 26-pass pipeline, tests |
| Translation corpus | 290,185 verified refined rows in `minilang.jsonl`; 289,622 no-SH rows |
| Source Isabelle corpus | Isabelle2024 HOL + AFP 2025-02-12 |
| Translation failures | 39,504 refined failure records + 10,578 goals without a refined row |
| PISA/evaluation data | Four JSONLs and compressed evaluation archive; updated benchmark |
| Training data | Four tarred JSONLs; 321,963 Isar-SH*, 331,767 Isar, 284,542 MiniLang-SH*, 283,511 MiniLang-no-SH examples |
| Model checkpoints | Absent; README links eight Hugging Face repositories |
| Evaluation/inference | Present, including socket REPL evaluators and scripts |
| Sledgehammer integration | `auto_sledgehammer` source, cache, solver, premise-hint handling |
| Experiment logs/results | Generated model outputs, raw DBs, CSVs, error summaries |
| Docker/VM | No artifact VM/container. One unrelated AFP entry contains a Dockerfile. |
| Cached dependencies | Very large: Isabelle distribution, solver binaries, heaps, editor/runtime components |

The artifact's `init.sh` requires at least 30 GB Isabelle heap memory, installs
Isa-Mini 0.3.5 and Isa-REPL 0.10.0, registers AFP/REPL/MiniLang/Sledgehammer
components, and prepares OCaml/Haskell support where available.

## Small semantic sources of truth

The implementation-relevant files are small:

1. `docs/Reference_Manual.pdf` — state tree and user operation semantics.
2. `MLML/contrib/Isa-Mini/library/proof.ML` — executable state, parser, and command
   transitions.
3. `MLML/contrib/Isa-Mini/translator/library/translator.ML` — Isar and MiniLang
   typed ASTs, 26-pass translation, interpreter validation, and printer.
4. `MLML/contrib/auto_sledgehammer/library/sledgehammer_solver.ML` — automation,
   premise selection, external prover reconstruction, and cache behavior.
5. `README.md`, `LICENSE`, `COPYING` — experiment and legal provenance.

Their hashes are in the source manifest. The complete derived semantics are in
[`operation_semantics.json`](../experiments/minilang_audit/operation_semantics.json),
so future HML work does not depend on retaining the 7 GB archive.

## Exact ten semantic operations

The paper's counting convention resolves an apparent manual/implementation
ambiguity. `CONSIDER` has two semantically distinct modes and therefore counts
twice; `NEXT` is an alias/control variant of `END` and does not add an eleventh
semantic operation.

| # | Paper semantic operation | Executable spelling | Essential state effect |
|---:|---|---|---|
| 1 | INTRO | `INTRO` | Move leading binders/premises into local context |
| 2 | HAVE | `HAVE` | Open lemma block, create lemma goals, add certified facts |
| 3 | CONSIDER∨ | `CONSIDER ... \| ...` | Create coverage goal and scoped case branches |
| 4 | CONSIDER∃ | `CONSIDER x where ...` | Prove existence, introduce abstract witness and facts |
| 5 | RULE | `RULE` | Kernel-refine goal by named intro/elim/dest rule |
| 6 | CHOOSE | `CHOOSE` | Supply witness and refine an existential goal |
| 7 | SIMPLIFY | `SIMP` | Delegate checked normalization/refinement to simplifier |
| 8 | CASE_SPLIT | `CASE_SPLIT` | Delegate structural cases and case scopes to Isabelle |
| 9 | INDUCT | `INDUCT` | Delegate induction schema/cases/hypotheses to Isabelle |
| 10 | END | `END` / `NEXT` | Ask Sledgehammer* to close current goal, then close/move |

These operations are not fully orthogonal:

- HAVE composes goal creation, obligation state, scope, fact introduction, and
  later discharge.
- CONSIDER∨ composes case declaration, a coverage obligation, branch scope, and
  certified join.
- END composes automated search, theorem proving, exact discharge, scope closure,
  and navigation.
- SIMPLIFY can instantiate HML-like transform, definition/theorem application,
  evaluation, verification, splitting, or discharge effects.
- INDUCT and CASE_SPLIT are explicit operations whose actual schemas and safety
  come from Isabelle tactics/theorems.
- CONSIDER∃ and CHOOSE are logical duals: obtain an abstract witness from an
  existential fact versus supply a concrete witness to prove an existential goal.

### AST and parser reality

The artifact does contain a real typed AST, but not a portable canonical JSON AST.
`translator.ML` defines:

- a large Isar `ast` with proof blocks, facts, tactics, calculations, locales,
  declarations, scaffolds, and source proof states;
- a MiniLang `mast` with `MINTRO`, `MEND`, `MCONSIDER`, `MSIMP`, `MHAVE`, `MRULE`,
  `MCHOOSE`, `MINDUCT`, `MCASE`, plus pragmatic escape constructors;
- `AST = Isar_AST | Mini_AST | NO_AST`.

Executable text is tokenized with Isabelle's lexer, split at registered command
keywords, parsed with Isabelle combinators, and compiled to functions over
`Minilang.state`. The parser and elaborator therefore inherit Isabelle's term
syntax, types, fact lookup, and context.

### Public semantics versus implementation surface

`proof.ML` registers additional commands: `CRUSH`, `ALL_INTRO`, `HAMMER`, `PRINT`,
`LET`, `APPLY`, `UNFOLD`, `NOTATION`, `OPEN_MODULE`, `DEFINE`, `CONFIG`, and `STEP`.
The verified corpus actually uses seven escape labels:

`APPLY`, `CONFIG`, `DEFINE`, `LET`, `NOTATION`, `OPEN_MODULE`, and `UNFOLD`.

This is disclosed in the paper as a pragmatic translation compromise. Therefore
“290K proofs use only ten surface commands” would be false. The defensible claim is
that the designed declarative interface has ten semantic operations, while the
artifact corpus includes infrequent/fallback access to a broader implementation.

## Proof-state and safety reconstruction

Abstractly, a leaf is `(variables, named hypotheses) ⊢ goal`; internal nodes group
sibling goals under common context; box nodes suppress automatic one-child collapse.
Every operation changes the leftmost applicable node.

Implementation state is more involved:

    state = stack × history table × cache id
    frame = HHF theorem/items | MAGIC callback/printer/parameter | ENDBLK tag
    printable tree = PROP | BUNDL | BLOCK

`MAGIC` callbacks are where completed subproofs become exported theorems, branch
facts, and reconstructed parent goals. `END`/`NEXT` enforce the expected block tag,
call Sledgehammer*, conclude a kernel theorem, and then run callbacks. This is a
real proof-state machine, not a string macro language.

Safety comes from Isabelle:

- types and term elaboration are checked in `Proof.context`;
- rule/simplifier/tactic steps produce kernel theorem states;
- local assumptions are exported using Isabelle scope machinery;
- CONSIDER∨ builds an ex/conj/disj elimination theorem, making coverage explicit;
- structural cases/induction use `Rule_Cases` metadata and theorem exports;
- terminal completion requires a single solved stack/root.

MiniLang does not separately expose HML-style candidate status, generic domain
preconditions, obligation provenance, or a neutral evidence object. The safety may
exist in Isabelle while remaining implicit at the MiniLang surface.

## Corpus measurements

The measured database contains 4,046,638 rows across translation stages.

| Quantity | Exact artifact value |
|---|---:|
| Source `origin` goals | 340,267 |
| Verified `refined` translations | 290,185 |
| Translation success | 85.2816% |
| Recorded refined failures | 39,504 |
| No refined row | 10,578 |
| Failure/missing tail | 50,082 = 14.7184% |
| Serialized commands in verified corpus | 1,519,944 |
| Observed command labels | 17 |
| Mean commands/proof | 5.238 |
| Median / p90 / p95 / p99 | 1 / 12 / 20 / 50 |
| Maximum | 807 |
| Operation entropy | 2.726 bits/command |
| Effective operation perplexity | 6.616 |

Concrete-label coverage is top-1 38.93%, top-3 74.96%, top-5 86.09%, top-10
96.06%. This independently supports a compression phenomenon, but it is not directly
comparable to Gold-125's top-5 80.2%, top-10 94.9%, top-15 99.5%: MiniLang counts
control commands, HML counts reconstructed mathematical transitions, and END/NEXT
alone dominate formal scripts.

Structural observations:

- 90,923 proofs contain NEXT;
- 54,580 contain HAVE;
- 30,685 contain INDUCT;
- 21,442 contain CASE_SPLIT;
- 17,944 contain CONSIDER;
- 427,524 commands are goal-refinement forms (HAVE/CONSIDER/RULE/CASE_SPLIT/INDUCT);
- the printer-indentation depth proxy has median 0, p95 2, p99 3, maximum 107.

The depth figure is explicitly a serialized nested-AST proxy. Exact runtime proof
tree depth and exact theorem dependency fan-in require replay and are not claimed.
Full frequencies, bigrams, trigrams, session profiles, and caveats are in
[`operation_statistics.json`](../experiments/minilang_audit/operation_statistics.json).

## Where the intelligence is hiding

The strongest quantifiable lower bound is that every `END` or `NEXT` executes
`HAMMER_i`, and these labels account for 875,407 / 1,519,944 = **57.59% of all
serialized command occurrences**. This is not “57.59% of reasoning work”: one hammer
call can perform far more search than many explicit commands.

Additional direct delegation includes:

- 32,526 INDUCT and 30,861 CASE_SPLIT commands to Isabelle tactics/rule metadata;
- 12,835 SIMP commands to `auto_tac`/`clarsimp` and simp libraries;
- 69,419 RULE commands to theorem lookup, rule classification, and biresolution;
- 99,725 APPLY escape commands to arbitrary Isabelle methods;
- theorem/fact hints on END, RULE, SIMP, induction, and cases;
- external ATP calls, proof reconstruction, simplifier, fastforce, premise search,
  and a persistent proof cache inside Sledgehammer*.

Thus no scientifically meaningful single percentage of “mathematics hidden in the
backend” can be recovered from command counts or wall time. Defensible bounds are:

- 100% of accepted proof status depends on Isabelle's checker/kernel;
- at least 57.59% of command occurrences invoke Sledgehammer* through END/NEXT;
- every semantic operation relies on Isabelle terms, context, rules, or tactics;
- the relative search effort of user-level versus backend operations is unknown.

The paper's soundness theorem is conditional on Isabelle's simplifier, `cases`,
`induct`, and Sledgehammer* being sound; relative completeness follows because
Sledgehammer* can execute primitive kernel inferences in principle. That is a
soundness/completeness argument for the composed system, not for ten standalone
mathematical opcodes.

## Representative evidence retained

[`representative_examples.jsonl`](../experiments/minilang_audit/representative_examples.jsonl)
contains 78 unique verified proofs covering ten examples for every public concrete
command label (overlap intentionally avoids duplication), plus shortest, longest,
and deepest-proxy cases. Each record includes exact original Isar, exact MiniLang,
source identity/path, operation sequence, selection reason, and SHA-256 provenance.

[`translation_failures.json`](../experiments/minilang_audit/translation_failures.json)
retains 165 diagnostic-stratified failure/missing records with exact source where
available. Retained excerpts remain under the source artifact's AGPL terms, recorded
in `ARTIFACT_LICENSE_NOTICE.txt`.

## Reproducibility and limitations

The standard-library script
[`audit_minilang_artifact.py`](../experiments/minilang_audit/audit_minilang_artifact.py)
recomputes hashes, operation statistics, failure accounting/samples, result-CSV
rates, and representatives from selective extraction.

Limits:

- the package lacks MiniLang/MLML Git metadata, so no exact source commit can be
  recovered;
- exact model optimizer state, training steps, tokenizer-level corpus token counts,
  seeds, and all LLaMA-Factory configs are not packaged;
- the flat corpus does not expose exact runtime tree depth or proof dependency DAG;
- translation success is conditioned on this specific Isabelle/AFP snapshot and
  translator pipeline;
- Sledgehammer is stochastic; the README warns exact reevaluation may vary;
- several top-level result CSVs have forensic anomalies discussed in the learning
  experiment report.

The detailed implications are separated into
[`minilang_hml_mapping.md`](minilang_hml_mapping.md),
[`minilang_translation_failure_audit.md`](minilang_translation_failure_audit.md),
[`minilang_learning_experiment.md`](minilang_learning_experiment.md), and
[`minilang_hml_implications.md`](minilang_hml_implications.md).
