# HMLTN VNext Corpus Master

This is the corpus-side authority for the VNext synchronization, regression,
and first 10k curriculum. Historical frozen-HML measurements remain historical;
they are not rewritten as VNext results.

## Authorities

- Corpus build base: `3bbb4256fe424e126ad1058c7bb8223c58b3afeb`
- Corpus data/implementation commit: `09521ae992af5ca583a346da66c93d986e709386`
- HML semantic authority: `68178f07784d2a17a9aed9c4dedbea9c740c97a0`
- HML integration/freeze report: `73184c5ec0959b18ee1e69e2535c95de98f67125`
- Translation contract: `vnext-translation-contract-1.0.0`
- Freeze decision: `VNEXT_SEMANTICS_FROZEN_FOR_DATA_SCALE`

The VNext HML checkout was isolated, pinned, clean, and recursively read-only.
The repository's historical `hml_core` submodule was neither repinned nor
modified.

## Contract attestation

The authoritative handoff copies and their SHA-256 hashes are:

- `CODEX_TRANSLATION_HANDOFF.md`: `e5b718325187a553b52f4251fe2df12f3d0cf343fbacab56785f34fcdef8c937`
- `CODEX_TRANSLATION_CONTRACT.json`: `ae4847d36e7c7b73a5172c75cc62f3980fd07a420b21923b340e001278147fd0`
- `TRANSLATION_GOLDEN_FIXTURES.jsonl`: `410aa477311b25a7f2da99f0ea523e25b848f588c967bb264315034adae0d545`

Golden fixtures passed 20/20: neutral, HML_LINEAR, and HML_TREE round trips
passed 19/19, and the one required refusal passed 1/1. The complete lock is
`contracts/hml_vnext/VNEXT_TRANSLATION_LOCK.json`.

## Historical frozen-HML results

The historical 600-problem census contained 3,978 source transitions. Its
authority classifications after the final corpus rebuild are retained as
metadata: 767 fully representable/backend verified, 1,896 representable but
unverifiable, 427 trusted backend/library required, and 888 records affected by
the three known frozen-HML mechanisms. The earlier direct/downstream figures
were 433/458. These are not VNext refusal counts.

The same historical PRM pilot classified 1,000 records as 166 backend/verifier
gaps, 693 current-known-core gaps, 112 existing semantics, 27 library gaps, and
2 source ambiguities.

## Corpus repair

Explicit neutral premises now cover all 600 problems: 600 `SOURCE_PROBLEM`
premises plus 648 `SOURCE_INITIAL_STATE` premises across 367 problems. Each has
a stable id, proposition, source span/hash, scope, provenance, and dependency
status. No dependency is inferred from linear adjacency.

Source reinspection produced five canonical role corrections, recorded in
`data/synthetic_math_canonicalization_corrections_v1.json`. The required
MIXED-039 ruling is that T008 derives the disjunctive claim `y=\pm x`; it does
not create a candidate. That claim is the common pre-split premise for both
cases. The same full-source pass exposed two candidate-vs-branch corrections in
GEN-087 and two candidate-vs-derived-claim corrections in GEN-094.

Decision D-063 is represented by 16 deterministic `IMPLICIT_LOGICAL_STEP`
records, all ordinary disjunction introduction. They support six source joins:
ALG-097-T014 (2), ALG-099-T015 (2), GEN-054-T018 (2), GEN-062-T013 (2),
GEN-072-T009 (6, including nested joins), and MIXED-039-T014 (2). No other
implicit proof-step family was introduced.

Decision D-062 corrects `FX-OBL-UNKNOWN` to `INVALID / OBLIGATION_DROP` because
the fixture deletes a mandatory obligation. The historical fixture remains
unchanged and HML structural checks were not weakened.

## VNext 600 regression

- Problems / original source transitions: 600 / 3,978
- Faithful original transitions: 3,978
- Inserted protocol transitions: 149
- Accepted semantic records: 4,127
- Source backend annotations: 867 `SYMPY_VERIFIED`
- Formal verification: 0
- VNext verifier result on source transitions: 5 VALID deterministic joins;
  3,973 UNRESOLVED source warrants
- Semantic refusals: 0
- Corpus-information refusals: 0
- Source ambiguities: 0
- Parser / verifier / round-trip failures: 0 / 0 / 0
- Root refusals / downstream-not-attempted: 0 / 0
- HML_LINEAR / HML_TREE / AST / STRUCTURED_NEUTRAL / model-safe exports:
  4,127 each
- Leakage audit: PASS

The previously affected 201 candidate, 166 branch, 63 approximation, and 458
downstream rows are all faithfully represented under VNext. No recurring new
VNext core semantic mechanism was discovered.

## Same PRM800K 1k regression

The exact deterministic pilot remains 1,000 records, 858 source problems, and
907 trajectories, validated 1,000/1,000 against PRM commit
`7ecc794703b2877f63226f2477a49b34f9b25163`.

- Previously core: 693
- Now represented: 670
- Corpus-information refusals: 23 (18 branch opens, 5 joins; one candidate row
  overlaps this source-information issue)
- Total represented / refused: 975 / 25
- Backend gaps: 166
- Library gaps: 27
- Source ambiguities: 2
- Remaining candidate core gaps: 0
- Remaining approximation core gaps: 0
- New recurring core candidates: 0
- Marginal new-core-semantic rate: 0.0

PRM `{-1,0,+1}` remains human process supervision and never becomes
mathematical evidence. All 975 represented PRM records therefore have an
UNRESOLVED mathematical verifier verdict. The 23 branch residuals lack source
ancestry in the neutral PRM pilot; they are corpus-information refusals, not
language failures.

## Scale gate

All ten gates passed: authority, contract, fixtures, corpus repair, absence of
new recurring core semantics in both regressions, determinism, provenance,
model-input leakage, and HML immutability. Decision: `GO_10K`.

## First 10k VNext curriculum

Source composition is exact: LeanDojo 4,000; PRM800K 2,000; MATH 2,000; AMPS
1,000; synthetic semantic hard tail 1,000. Epistemic composition is 4,000
formally verified, 24 backend verified, 2,000 human process labels, and 3,976
representable-unverified.

The authoritative split is train 8,132 / dev 952 / test 916. Parent theorem,
problem, and trajectory groups are split before atomic rows. Exact signatures
are deduplicated, normalized PRM/MATH/AMPS problem hashes are excluded across
wrappers, and parent-group split leakage is zero.

Difficulty counts are: formal not-applicable 4,000; synthetic mixed 1,000;
AMPS not-provided 1,000; PRM levels 1/2/3/4/5/UNKNOWN =
27/103/255/484/1,128/3; MATH Level 1/2/3/4/5/? =
189/389/443/485/493/1. Domain counts are exact in the manifest. Compactly:
Lean formal 4,000; synthetic math 1,000; MATH Algebra/Counting & Probability/
Geometry/Intermediate Algebra/Number Theory/Prealgebra/Precalculus =
492/198/214/319/231/354/192; PRM those same domains plus UNKNOWN =
208/229/228/676/268/80/308/3; and AMPS 1,000 across 320 source-native topic
labels (192 numeric topic ids covering 748 rows and 128 named topics covering
252 rows). Numeric AMPS topic ids are preserved rather than guessed into
subject names.

Mechanism counts are: ordinary derivation 8,037; candidate create 1,177;
candidate derive/reject/verify-or-promote 0/0/0; branch open/close/join
61/39/8; nested branch 318; implicit weakening 16; explicit exact/approximate/
unannotated numeric status 0/8/9,992; obligations 26; assumptions 318;
goal create/close 292/1,659 (1,951 records with either); scope changes 100;
dependency bins 0/1/2/3+ = 47/9,375/533/45; quantifier operations 0;
theorem/library-backed 0; backend-unverified 3,976; process-negative 800; and
procedural operators 1,000. Zeroes are explicit coverage deficits, not silently
missing measurements.

Eligibility is EXECUTE 4,024; APPLICABILITY 0; JUDGE 6,000; REPAIR 0; and
COMPREHENSION 10,000. There were no trustworthy certified negative/correction
pairs, so REPAIR and candidate rejection/verification coverage was not
synthesized.

All four representation arms contain 10,000 matched rows and pass semantic
parity 10,000/10,000. Per-example safe-input checks pass 10,000/10,000. Nested
snapshots are exact subsets at 100, 250, 1,000, 5,000, and 10,000, with source
ratios 40/20/20/10/10 percent at every rung.

## Reproducibility and handoff

- VNext 600 machine report: `reports/vnext_600_regression.json`
- VNext PRM machine report:
  `experiments/prm800k_audit/results/cross_source_gap_pilot_vnext_1.0.0_summary.json`
- 10k manifest: `data/vnext_10k/manifest.json`
- Full 10k audit data: `data/vnext_10k/full_audit_records.jsonl.gz`
- Authoritative split data: `data/vnext_10k/{train,dev,test}.jsonl.gz`
- Matched safe views: `data/vnext_10k/views/{HML_LINEAR,HML_TREE,AST,STRUCTURED_NEUTRAL}/`
- Nested ordering: `data/vnext_10k/snapshots.json`
- FABLE instructions: `FABLE_VNEXT_10K_HANDOFF.md`

Validation result: 90 corpus tests passed; contract fixtures 20/20 passed;
10k deterministic rebuild was byte-identical; HML checkout and submodule were
clean and unmodified.

## D1/D2 model-export patch

FABLE attestation `435571e` correctly blocked training because EXECUTE views
omitted the exact Lean tactic and AST/STRUCTURED_NEUTRAL were raw objects. Export
implementation commit `a2f992a6d474638814a1f1f7809f4015db3894c5`
repairs only those projections.

Explicit EXECUTE action content is now present on 4,024/4,024 rows: 4,000 exact
pinned Lean tactics and 24 canonical deterministic protocol operations. The
action audit found 4,024 legitimate actions and zero direct target reveals,
ambiguities, exclusions, or missing actions. EXECUTE remains 4,024 with split
counts 3,254/392/378.

All four arms now expose deterministic string `input_text` and `target_text`
fields on 10,000/10,000 rows. Semantic parity passes 10,000/10,000 and a second
build reproduced all 13 generated files byte-for-byte. Canonical transitions,
ids, sources, splits, eligibility, snapshots, and HML authority are unchanged.
The post-patch test result is 92 passed plus 20/20 contract fixtures.

See `FABLE_VNEXT_D1_D2_PATCH.md`, `FABLE_VNEXT_10K_HANDOFF.md`, and
`reports/vnext_10k_d1_d2_patch.json` for the release contract and exact audits.
